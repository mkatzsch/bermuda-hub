"""Decide which views and categories a scraped listing belongs in.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 0.2
Last Updated: 2026-11-20

Change Log
  0.2  2026-11-20  Seasonal key is "xmas" (the page renamed it from "hallow" in November); Christmas and
                   Thanksgiving keywords added for kids and adults.
  0.1  2026-11-15  First release.

Two layers:
  1. Keyword rules (free, deterministic). Cover the common cases.
  2. Optional model call for anything the rules leave as "unsure" (set ANTHROPIC_API_KEY and
     classify.use_model: true in config.yaml). One short call per unsure listing with a strict JSON
     schema, using a small model. A few cents per run at most.

A listing can land in several views (a family concert is kids, adults and music).
"""
from __future__ import annotations

import json
import os
import re

# view -> category -> keywords
RULES: dict[str, dict[str, list[str]]] = {
    "kids": {
        "xmas": ["christmas", "santa", "xmas", "festive", "carol", "nutcracker", "gingerbread", "thanksgiving", "holiday market",
                 "halloween", "trick or treat", "trunk or treat", "spook", "pumpkin", "haunted", "costume"],  # the seasonal key: the page renames it each season
        "camp": ["camp", "mid-term", "midterm", "half term", "school holiday"],
        "story": ["library", "story time", "storytime", "lego", "steam club", "book"],
        "water": ["swim", "sail", "kayak", "paddle", "snorkel", "aquarium", "dolphin", "turtle", "boat tour", "glass bottom"],
        "build": ["cooking", "baking", "workshop", "craft", "make", "build", "robot", "coding", "stem"],
        "nature": ["farm", "hike", "garden", "cave", "bird", "nature", "beach clean", "trail", "zoo"],
        "sport": ["football", "soccer", "rugby", "cricket", "gymnastics", "karate", "tennis", "golf", "race", "5k", "fun run", "family day", "tournament", "scrimm"],
        "arts": ["art", "paint", "theatre", "theater", "dance", "music lesson", "choir", "museum", "gallery", "exhibition"],
        "fest": ["festival", "fair", "parade", "fireworks", "carnival", "show", "magic", "circus", "market", "lighting", "santa", "christmas"],
    },
    "adults": {
        "music": ["live music", "band", "dj", "concert", "jazz", "karaoke", "open mic", "party", "cruise", "boat party"],
        "arts": ["art", "exhibition", "gallery", "theatre", "theater", "play", "musical", "film", "cinema", "museum"],
        "food": ["dinner", "brunch", "tasting", "wine", "rum", "chef", "menu", "feast", "takeout", "lobster", "thanksgiving"],
        "sport": ["5k", "10k", "half marathon", "triathlon", "race", "regatta", "championship", "tournament", "match"],
        "outdoors": ["hike", "walk", "clean", "boat", "dive", "snorkel", "sunset", "garden"],
        "talk": ["talk", "lecture", "seminar", "workshop", "class", "course", "panel", "book launch"],
        "xmas": ["christmas", "santa", "xmas", "festive", "carol", "thanksgiving", "halloween"],
    },
    "sports": {
        "football": ["football", "soccer", "premier division", "first division", "fa cup", "dudley eve"],
        "rugby": ["rugby"],
        "basketball": ["basketball", "netball", "volleyball", "ball hockey", "field hockey"],
        "running": ["5k", "10k", "marathon", "run", "walk", "triathlon"],
        "sailing": ["sail", "regatta", "gig", "rowing", "yacht"],
        "golf": ["golf", "tennis", "pickleball", "squash"],
        "motor": ["kart", "motocross", "motorsport", "powerboat", "harness"],
        "other": ["swim", "cycling", "bike", "athletics", "cross country", "boxing", "mma", "fight"],
    },
    "music": {
        "boat": ["ubervida", "cruise", "boat party", "afro boat"],
        "dj": ["dj", "club night", "afrique", "brunch", "emo night", "rave", "house music"],
        "jazz": ["jazz", "philharmonic", "orchestra", "chamber", "classical", "choir", "carol"],
        "open": ["open mic", "karaoke", "salsa", "bachata", "jam night", "quiz"],
        "concert": ["concert", "musical", "live at", "in concert", "show", "theatre", "theater", "illusion", "comedy"],
        "live": ["live music", "band", "acoustic", "sax", "guitar"],
        "xmas": ["christmas", "tree lighting", "carol", "new year", "nye", "boxing day", "santa"],
    },
}

KIDS_BLOCK = ["18+", "21+", "adults only", "adult only", "strictly adults", "over 18", "nightclub", "burlesque"]


def classify(text: str, *, default_view: str | None = None) -> dict[str, str]:
    """Return {view: category} for every view the text qualifies for."""
    t = (text or "").lower()
    out: dict[str, str] = {}
    for view, cats in RULES.items():
        if view == "kids" and any(b in t for b in KIDS_BLOCK):
            continue
        best, best_n = None, 0
        for cat, kws in cats.items():
            n = sum(1 for k in kws if re.search(r"\b" + re.escape(k) + r"\b", t))
            if n > best_n:
                best, best_n = cat, n
        if best:
            out[view] = best
    if default_view and default_view not in out:
        out[default_view] = next(iter(RULES[default_view]))  # first category as a fallback
    return out


MODEL_PROMPT = """You classify Bermuda event listings for a what's-on planner with five views.
Views and their categories:
kids: xmas, arts, sport, fest, nature, camp, story, water, build (only if children 10 and under can attend)
adults: music, arts, food, sport, outdoors, talk, xmas
sports: football, rugby, basketball, running, sailing, golf, motor, other (only for sporting fixtures and race days)
music: concert, dj, live, boat, jazz, open, xmas (only for music, nightlife, theatre and festive events)
Return ONLY JSON of the form {"views": {"kids": "fest", "adults": "music"}, "family_friendly": true}.
Leave a view out if the listing does not belong there.
Listing:
"""


def classify_with_model(text: str, model: str = "claude-haiku-4-5") -> dict[str, str] | None:
    """Optional model fallback. Returns None if no API key or on any error, so the caller can
    fall back to the rules. Imported lazily so the package works without the SDK."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic  # type: ignore
    except ImportError:
        return None
    try:
        client = anthropic.Anthropic()
        msg = client.messages.create(model=model, max_tokens=200, messages=[{"role": "user", "content": MODEL_PROMPT + text[:1500]}])
        raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        data = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
        views = data.get("views", {})
        return {v: c for v, c in views.items() if v in RULES and c in RULES[v]}
    except Exception:
        return None
