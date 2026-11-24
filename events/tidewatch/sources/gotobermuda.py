"""gotobermuda.com events (Bermuda Tourism Authority) via its Algolia search index.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 0.2
Last Updated: 2026-11-16

Change Log
  0.2  2026-11-16  The listing page is filled client side by Algolia InstantSearch, so the HTML only
                   carries one featured card. The page embeds a public search-only app id, key and
                   index name (drupalSettings: algolia_app_id, algolia_api_key, algolia_index). This
                   version reads those from the page each run (so a key rotation does not break it)
                   and queries the index directly for structured JSON.
  0.1  2026-11-15  HTML parse of the listing page; found one event.

Record fields vary by index version, so the mapper looks for the usual names (title, start/end date,
venue, url, description). `tidewatch probe gotobermuda` prints the first raw record when the mapping
comes back empty, so the field names can be fixed in one place.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime

import requests

from ..util import UA, clean, daterange, get, parse_date, parse_time

LIST_URL = "https://www.gotobermuda.com/experiences/events"
BASE = "https://www.gotobermuda.com"

TITLE_KEYS = ("title", "name", "event_title")
# Real field names on the EVENTS2025 index (seen 16 Nov 2026): title, field_new_date, field_new_date_day,
# field_new_date_range, field_dates, event_times, venue, location, url, body, website, host_title,
# field_recurrence, event_category, time_of_year, image_url, objectID.
START_KEYS = ("field_new_date", "field_dates", "field_new_date_range", "field_new_date_day",
              "startDate", "start_date", "date_start", "field_event_date", "start", "date", "event_date", "datetime_start")
END_KEYS = ("field_new_date_range", "endDate", "end_date", "date_end", "end", "datetime_end")
VENUE_KEYS = ("venue", "location", "venue_name", "field_location", "place", "address", "host_title")
URL_KEYS = ("url", "path", "alias", "link", "field_url", "website")
DESC_KEYS = ("description", "summary", "body", "teaser", "field_summary")
TIME_KEYS = ("event_times", "time", "times", "event_time", "field_time", "hours")

LAST_RAW: dict | None = None
SAMPLE = "data/gotobermuda_sample.json"  # first raw record, written whenever mapping finds nothing


def _range(v: str) -> tuple[date | None, date | None]:
    """'Nov 20, 2026 - Nov 22, 2026', '2026-11-20 to 2026-11-22', or a single date."""
    if not v:
        return None, None
    parts = re.split(r"\s+(?:-|–|to|through)\s+", v, maxsplit=1)
    a = _date(parts[0].strip())
    b = _date(parts[1].strip()) if len(parts) > 1 else None
    return a, b


def settings(html: str) -> dict:
    """Pull the Algolia credentials out of the page."""
    out = {}
    for key in ("algolia_app_id", "algolia_api_key", "algolia_index"):
        m = re.search(r'"%s"\s*:\s*"([^"]+)"' % key, html)
        if m:
            out[key] = m.group(1)
    return out


def _pick(rec: dict, keys) -> str:
    for k in keys:
        v = rec.get(k)
        if isinstance(v, dict):
            v = v.get("value") or v.get("name") or v.get("title") or v.get("url")
        if isinstance(v, list) and v:
            v = v[0] if not isinstance(v[0], dict) else (v[0].get("value") or v[0].get("name") or "")
        if v:
            return clean(str(v))
    return ""


def _date(v: str) -> date | None:
    if not v:
        return None
    if re.fullmatch(r"\d{9,13}", v):  # unix seconds or millis
        n = int(v)
        return datetime.utcfromtimestamp(n / 1000 if n > 10**11 else n).date()
    return parse_date(v)


def query(app_id: str, api_key: str, index: str, pages: int = 5) -> list[dict]:
    hits: list[dict] = []
    for page in range(pages):
        r = requests.post(
            f"https://{app_id}-dsn.algolia.net/1/indexes/{index}/query",
            headers={"X-Algolia-Application-Id": app_id, "X-Algolia-API-Key": api_key, "User-Agent": UA, "Content-Type": "application/json"},
            data=json.dumps({"params": f"query=&hitsPerPage=200&page={page}"}), timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        hits.extend(data.get("hits", []))
        if page >= data.get("nbPages", 1) - 1:
            break
    return hits


def _first_date(h: dict, keys) -> tuple[date | None, date | None]:
    """Try each key; a value may be a timestamp, a date string, a 'from - to' range, or a list of those."""
    for k in keys:
        v = h.get(k)
        vals = v if isinstance(v, list) else [v]
        for x in vals:
            if isinstance(x, dict):
                x = x.get("value") or x.get("start") or x.get("date")
            if x in (None, "", 0):
                continue
            a, b = _range(str(x))
            if a:
                return a, b
    return None, None


def map_hit(h: dict) -> dict | None:
    title = _pick(h, TITLE_KEYS)
    start, end = _first_date(h, START_KEYS)
    if not title or not start:
        ds = h.get("dates") or h.get("event_dates") or []
        if isinstance(ds, list) and ds:
            start = _date(_pick(ds[0] if isinstance(ds[0], dict) else {"date": ds[0]}, START_KEYS + ("date",)))
        if not title or not start:
            return None
    if not end:
        end = _first_date(h, END_KEYS)[1] or _first_date(h, ("endDate", "end_date", "date_end", "end", "datetime_end"))[0]
    url = _pick(h, URL_KEYS)
    if url and not url.startswith("http"):
        url = BASE + ("/" if not url.startswith("/") else "") + url
    text = f"{title} {_pick(h, DESC_KEYS)}"
    return {
        "date": start, "end": end if end and end > start else None, "name": title,
        "time": parse_time(_pick(h, TIME_KEYS) or _pick(h, DESC_KEYS)), "time_text": _pick(h, TIME_KEYS),
        "venue": _pick(h, VENUE_KEYS), "cost": "", "ages": "All ages" if re.search(r"family|kids|children|all ages", text, re.I) else "",
        "note": _pick(h, DESC_KEYS)[:240], "link": url or LIST_URL, "source": "gotobermuda",
        "source_key": str(h.get("objectID", "")), "raw": text,
    }


def fetch(cfg: dict | None = None) -> list[dict]:
    global LAST_RAW
    try:
        html = get(LIST_URL)
    except Exception as e:
        print(f"[gotobermuda] {e}")
        return []
    st = settings(html)
    if len(st) < 3:
        print("[gotobermuda] Algolia settings not found on the page; site may have changed")
        return []
    try:
        hits = query(st["algolia_app_id"], st["algolia_api_key"], st["algolia_index"])
    except Exception as e:
        print(f"[gotobermuda] Algolia query failed: {e}")
        return []
    LAST_RAW = hits[0] if hits else None
    out = []
    for h in hits:
        r = map_hit(h)
        if not r:
            continue
        if r["end"] and (r["end"] - r["date"]).days > 10:
            r["note"] = (f"Runs {r['date']:%d %b} to {r['end']:%d %b}. " + r["note"]).strip()
            r["end"] = None
            out.append(r)
        elif r["end"]:
            days = list(daterange(r["date"], r["end"]))
            for i, d in enumerate(days):
                out.append(dict(r, date=d, end=None, name=r["name"] + (" (opens)" if i == 0 and len(days) >= 3 else "")))
        else:
            out.append(r)
    if hits and not out:
        print("[gotobermuda] records found but none mapped; first record keys:", sorted(hits[0].keys()))
    if hits:
        try:  # keep a sample so the mapping can be checked without running a probe
            import os
            os.makedirs(os.path.dirname(SAMPLE), exist_ok=True)
            with open(SAMPLE, "w", encoding="utf-8") as f:
                json.dump({k: v for k, v in hits[0].items() if k != "_highlightResult"}, f, indent=1, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"[gotobermuda] sample not written: {e}")
    return out
