"""ptix.bm (Premier Tickets) listing scraper.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 0.2
Last Updated: 2026-11-16

Change Log
  0.2  2026-11-16  Rewritten against the real markup: each listing is a div.show-module holding
                   a[href=/Event/<id>/slug or /Show/<id>/slug], img[alt=title], .left-content
                   (.title = weekday, .sub-title = "Dec 13", .sub-title-end-time = end date for runs)
                   and .right-content (.title = name, .sub-title = venue, .sub-title = time).
                   Sold out listings carry class overlay-sold-out.
  0.1  2026-11-15  Link anchored guess, found nothing on the live page.

Pages: https://www.ptix.bm/ (all), /category/events, https://kids.ptix.bm/. No year on the cards, so
parse_date rolls dates that look more than 60 days past into next year.
Multi day shows produce one listing per day, which is the planner's rule.
"""
from __future__ import annotations

import re

from bs4 import BeautifulSoup

from ..util import clean, daterange, get, parse_date, parse_time

LIST_URLS = [
    "https://www.ptix.bm/",
    "https://www.ptix.bm/category/events",
    "https://kids.ptix.bm/",
]
LINK_RE = re.compile(r"/(Event|Show)/(\d+)", re.I)


def parse(html: str, base: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    seen: set[str] = set()
    out: list[dict] = []
    for mod in soup.select("div.show-module"):
        a = mod.find("a", href=LINK_RE)
        if not a:
            continue
        m = LINK_RE.search(a["href"])
        key = f"{m.group(1).lower()}:{m.group(2)}"
        if key in seen:
            continue
        right = mod.select_one(".right-content")
        left = mod.select_one(".left-content")
        if not right or not left:
            continue
        title_el = right.select_one(".title")
        title = clean(title_el.get_text(" ")) if title_el else ""
        if not title:
            img = mod.find("img", alt=True)
            title = clean(img["alt"]) if img else ""
        if not title:
            continue
        subs = [clean(x.get_text(" ")) for x in right.select(".sub-title")]
        time_text = next((s for s in subs if re.search(r"\d(:\d{2})?\s*(AM|PM)", s, re.I)), "")
        venue = next((s for s in subs if s and s != time_text), "")
        day_txt = clean((left.select_one(".sub-title") or left).get_text(" "))
        start = parse_date(day_txt)
        end = None
        end_el = left.select_one(".sub-title-end-time")
        if end_el:
            end = parse_date(clean(end_el.get_text(" ")).lstrip("- "))
        if not start:
            continue
        seen.add(key)
        href = a["href"]
        link = href if href.startswith("http") else base.rstrip("/") + "/" + href.lstrip("/")
        sold_out = "overlay-sold-out" in " ".join(mod.get("class", []))
        out.append({
            "date": start, "end": end if end and end > start else None, "name": title,
            "time": parse_time(time_text), "time_text": time_text, "venue": venue,
            "cost": "Sold out" if sold_out else "Tickets via ptix", "sold_out": sold_out, "ages": "", "note": "",
            "link": link, "source": "ptix", "source_key": key,
            "raw": f"{title} {day_txt} {' '.join(subs)}",
        })
    return out


def expand(listings: list[dict]) -> list[dict]:
    """One row per day for ranged listings (cap at 10 days so a season pass does not flood the grid)."""
    out = []
    for L in listings:
        if L.get("end") and (L["end"] - L["date"]).days <= 10:
            days = list(daterange(L["date"], L["end"]))
            for i, d in enumerate(days):
                row = dict(L, date=d, end=None)
                if i == 0 and len(days) >= 3:
                    row["name"] = f"{L['name']} (opens)"
                out.append(row)
        elif L.get("end"):
            out.append(dict(L, end=None, note=f"Runs to {L['end']:%d %b}. "))
        else:
            out.append(dict(L, end=None))
    return out


def fetch(cfg: dict | None = None) -> list[dict]:
    rows: list[dict] = []
    for url in LIST_URLS:
        try:
            html = get(url)
        except Exception as e:  # one dead listing page should not stop the run
            print(f"[ptix] {url}: {e}")
            continue
        base = url.split("/", 3)[0] + "//" + url.split("/", 3)[2]
        rows.extend(parse(html, base))
    return expand(rows)
