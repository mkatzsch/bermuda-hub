"""Speciality Cinema, Hamilton: what's playing and showtimes.

Developed by AiTide Ltd. | www.AiTide.com
Version: 0.2
Last Updated: 2026-11-16

Change Log
  0.2  2026-11-16  Board parser rewritten against the real page (WordPress blog list: each film is a
                   div.wpbaw-blog-list with .wpbaw-blog-categories (Now Playing / Next Attractions /
                   Coming Soon), .wpbaw-blog-title a, and .wpbaw-blog-short-content reading
                   "Start Date: Friday, November 6 -- End Date: Thursday, November 19 -- Genres: Animation
                   synopsis..."). Showtimes: the Get Tickets buttons are off screen in the ticketing
                   page's layout, so Playwright now clicks them through the page's own script
                   (element.click()) instead of a simulated mouse, which is what failed on 16 Nov.
  0.1  2026-11-15  First release.

Sources:
  1. https://specialitycinema.bm/whats-playing/ (static HTML, requests).
  2. https://omniwebticketing.com/speciality/?schdate=YYYY-MM-DD (dynamic, Playwright). Showtimes are
     only published about four days ahead; without Playwright films keep their run dates with status "check".

Output is the FILMS array the page expects:
  {title, rating, runtime, genre, family, start:[m,d], end:[m,d]|null, times:{"m-d":"6:15pm"}, aud, syn, link, tba}
"""
from __future__ import annotations

import re
from datetime import date, timedelta

from bs4 import BeautifulSoup

from ..util import clean, get, parse_date

WHATS_PLAYING = "https://specialitycinema.bm/whats-playing/"
TICKETING = "https://omniwebticketing.com/speciality/"
FAMILY_WORDS = ("animation", "family", "kids", "pixar", "disney", "dreamworks", "cat in the hat", "minions", "lego", "muppet")
RATING_MAP = {"restricted": "R (Restricted)", "parents strongly cautioned": "PG-13 (Parents strongly cautioned)",
              "parental guidance": "PG (Parental guidance)", "general audience": "G (General audience)"}
SECTION = {"now playing": "now", "next attraction": "next", "coming soon": "soon"}


def parse_whats_playing(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    films: list[dict] = []
    seen: set[str] = set()
    for card in soup.select("div.wpbaw-blog-list"):
        t = card.select_one(".wpbaw-blog-title a")
        if not t:
            continue
        title = clean(t.get_text(" "))
        if not title or title in seen:
            continue
        seen.add(title)
        cat = clean((card.select_one(".wpbaw-blog-categories") or t).get_text(" ")).lower()
        section = next((v for k, v in SECTION.items() if k in cat), "soon")
        body = clean((card.select_one(".wpbaw-blog-short-content") or card).get_text(" "))
        sm = re.search(r"Start Date:\s*([A-Za-z]+,?\s*[A-Za-z]+\s*\d{1,2}(?:st|nd|rd|th)?(?:,?\s*\d{4})?)", body, re.I)
        em = re.search(r"End Date:\s*([A-Za-z]+,?\s*[A-Za-z]+\s*\d{1,2}(?:st|nd|rd|th)?(?:,?\s*\d{4})?)", body, re.I)
        start = parse_date(sm.group(1)) if sm else (date.today() if section == "now" else None)
        end = parse_date(em.group(1)) if em else None
        G = r"(?:Animation|Action|Adventure|Comedy|Drama|Horror|Thriller|Romance|Family|Documentary|Musical|Sci-?Fi|Fantasy|Epic|Crime|Mystery|War|Western|Biography|History|Sport)"
        gm = re.search(r"Genres?:\s*(" + G + r"(?:\s*[/,&]\s*" + G + r")*)", body, re.I)
        genre = clean(gm.group(1)).title() if gm else ""
        syn = body
        for cut in (r"^.*?Genres?:\s*[A-Za-z /,&-]+?\s+(?=[A-Z])", r"^.*?End Date:[^A-Z]*[A-Za-z]+,?\s*[A-Za-z]+\s*\d+\w*\s*"):
            syn2 = re.sub(cut, "", syn, count=1)
            if syn2 != syn:
                syn = syn2
                break
        syn = clean(syn)[:260]
        films.append({
            "title": title, "rating": "Not yet rated locally", "runtime": "", "genre": genre,
            "family": any(w in f"{title} {genre}".lower() for w in FAMILY_WORDS) or "sensory-friendly" in title.lower(),
            "start": [start.month, start.day] if start else None, "end": [end.month, end.day] if end else None,
            "times": {}, "aud": "", "syn": syn or "See the cinema listing.",
            "link": t.get("href") or WHATS_PLAYING, "tba": section == "soon" and not sm,
        })
    return films


def showtimes_playwright(days_ahead: int = 6) -> dict[str, dict[str, dict]]:
    """{title: {"m-d": {"time": "6:15pm", "aud": "Auditorium 2", "rating": "...", "runtime": "..."}}}.
    Returns {} if Playwright is not installed."""
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        print("[cinema] playwright not installed; skipping showtimes (pip install playwright && playwright install chromium)")
        return {}
    out: dict[str, dict[str, dict]] = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 2000})
        for i in range(days_ahead):
            d = date.today() + timedelta(days=i)
            try:
                page.goto(f"{TICKETING}?schdate={d:%Y-%m-%d}", wait_until="networkidle", timeout=45000)
            except Exception as e:
                print(f"[cinema] {d}: {e}")
                continue
            btns = page.locator("button", has_text="Get Tickets")
            n = btns.count()
            for j in range(n):
                try:
                    btns.nth(j).evaluate("b => b.click()")  # the page's own handler; the button is off screen for a mouse click
                except Exception as e:
                    print(f"[cinema] click {j}: {e}")
                    continue
                page.wait_for_timeout(1200)
                body = page.inner_text("body")
                k = body.find("Select Performance")
                seg = [s.strip() for s in body[k:k + 900].split("\n") if s.strip()] if k >= 0 else []
                if len(seg) < 2:
                    continue
                title = re.sub(r"\(\s*Closed Caption\s*\)", "", seg[1]).strip()
                times = [s for s in seg if re.fullmatch(r"\d{1,2}:\d{2}(am|pm)", s, re.I)]
                aud = next((s for s in seg if s.lower().startswith("auditorium")), "")
                rating = next((RATING_MAP[r] for r in RATING_MAP if any(r in s.lower() for s in seg)), "")
                runtime = next((s for s in seg if re.fullmatch(r"\d+\s*hr(?:s)?\s*\d*\s*min?", s, re.I)), "")
                if times:
                    out.setdefault(title, {})[f"{d.month}-{d.day}"] = {"time": ", ".join(t.lower() for t in times), "aud": aud, "rating": rating, "runtime": runtime}
        browser.close()
    return out


def fetch(cfg: dict | None = None) -> list[dict]:
    try:
        films = parse_whats_playing(get(WHATS_PLAYING, ttl_hours=12))
    except Exception as e:
        print(f"[cinema] {e}")
        return []
    times = {}
    if (cfg or {}).get("showtimes", True):
        try:
            times = showtimes_playwright()
        except Exception as e:
            print(f"[cinema] showtimes skipped: {e}")
    for f in films:
        key = next((t for t in times if t.lower()[:12] == f["title"].lower()[:12]), None)
        if key:
            f["times"] = {k: v["time"] for k, v in times[key].items()}
            any_v = next(iter(times[key].values()))
            f["aud"] = any_v.get("aud", "")
            f["rating"] = any_v.get("rating") or f["rating"]
            f["runtime"] = any_v.get("runtime") or f["runtime"]
            if not f["start"]:
                first = min(times[key], key=lambda k: tuple(map(int, k.split("-"))))
                f["start"] = list(map(int, first.split("-")))
                f["tba"] = False
    print(f"[cinema] {len(films)} films on the board, {sum(1 for f in films if f['times'])} with showtimes")
    return films
