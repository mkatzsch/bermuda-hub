"""gpass.bm (G-Pass) events and experiences listing.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 0.1
Last Updated: 2026-11-21

Change Log
  0.1  2026-11-21  Discovery release. Fetches https://gpass.bm/ and its events pages, keeps the raw HTML in
                   data/gpass_raw/ so the card parser can be written against the real markup, and makes a loose
                   first pass: any link whose path looks like an event with a date in the text near it.

Pages: https://gpass.bm/ (home), https://gpass.bm/events (guessed), plus any link on the home page whose text or
path mentions events, experiences, tickets, register or upcoming. Matt gets the G-Pass newsletter ("Events,
experiences & what's coming next in Bermuda"); its "view online" pages are per issue and not scraped.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

from ..util import clean, get, parse_date, parse_time

HOME = "https://gpass.bm/"
GUESSES = ["https://gpass.bm/events", "https://gpass.bm/experiences", "https://gpass.bm/upcoming"]
RAW_DIR = Path("data/gpass_raw")
DATE_RE = re.compile(r"\b(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*(?:\s+\d{4})?|"
                     r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?|"
                     r"(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*,?\s+\d{1,2}\s+[a-z]+)\b", re.I)


def _save(name: str, url: str, html: str) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / f"{name}.html").write_text(f"<!-- {url} -->\n" + html, encoding="utf-8")


def discover(home_html: str) -> list[str]:
    soup = BeautifulSoup(home_html, "lxml")
    urls: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = clean(a.get_text(" ")).lower()
        if href.startswith(("#", "mailto:", "javascript:")):
            continue
        url = href if href.startswith("http") else HOME.rstrip("/") + "/" + href.lstrip("/")
        if "gpass.bm" not in url:
            continue
        if re.search(r"event|experience|ticket|register|upcoming|calendar|what", text + " " + href, re.I):
            if url not in urls:
                urls.append(url)
    return urls[:12]


def parse(html: str, base: str) -> list[dict]:
    """Loose first pass: event-looking links with a date in the surrounding card text."""
    soup = BeautifulSoup(html, "lxml")
    out: list[dict] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not re.search(r"/(event|e|experience|ticket|register)s?/", href, re.I) and not re.search(r"/[^/]+-\d{2,}/?$", href):
            continue
        url = href if href.startswith("http") else base.rstrip("/") + "/" + href.lstrip("/")
        if url in seen:
            continue
        card = a
        for _ in range(4):  # climb to the card that holds the date text
            if card.parent is None:
                break
            card = card.parent
            txt = clean(card.get_text(" "))
            if DATE_RE.search(txt) and len(txt) < 600:
                break
        txt = clean(card.get_text(" "))
        m = DATE_RE.search(txt)
        if not m:
            continue
        d = parse_date(m.group(1))
        if not d:
            continue
        title = clean(a.get_text(" ")) or clean((a.find("img") or {}).get("alt", "") if a.find("img") else "")
        if not title or len(title) < 3:
            h = card.find(["h1", "h2", "h3", "h4"])
            title = clean(h.get_text(" ")) if h else ""
        if not title:
            continue
        seen.add(url)
        tm = re.search(r"\d{1,2}(?::\d{2})?\s*(?:am|pm)", txt, re.I)
        out.append({"date": d, "end": None, "name": title[:120], "time": parse_time(tm.group(0)) if tm else "",
                    "time_text": tm.group(0) if tm else "", "venue": "", "cost": "Tickets via G-Pass", "ages": "", "note": "",
                    "link": url, "source": "gpass", "source_key": url, "raw": txt[:400]})
    return out


def fetch(cfg: dict | None = None) -> list[dict]:
    rows: list[dict] = []
    try:
        home = get(HOME)
        _save("home", HOME, home)
        rows.extend(parse(home, HOME))
        urls = discover(home) + GUESSES
    except Exception as e:
        print(f"[gpass] home: {e}")
        urls = list(GUESSES)
    done = {HOME}
    for i, url in enumerate(urls):
        if url in done:
            continue
        done.add(url)
        try:
            html = get(url)
        except Exception as e:
            print(f"[gpass] {url}: {e}")
            continue
        _save(f"page{i}", url, html)
        rows.extend(parse(html, HOME))
    uniq = {}
    for r in rows:
        uniq.setdefault(r["source_key"], r)
    print(f"[gpass] {len(done)} pages read, {len(uniq)} event links with dates")
    return list(uniq.values())
