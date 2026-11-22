"""Shared helpers: HTTP with polite headers and caching, date parsing, month window.

Developed by AiTide Ltd. | www.AiTide.com
Version: 0.2
Last Updated: 2026-11-16

Change Log
  0.2  2026-11-16  fmt_day/fmt_time helpers; strftime("%-d") is Linux only and broke the Windows run.
  0.1  2026-11-15  First release.
"""
from __future__ import annotations

import calendar
import hashlib
import json
import re
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

UA = "Tidewatch/0.1 (+https://www.aitide.com; personal what's-on planner; contact mkatzsch@aitide.com)"
CACHE_DIR = Path(".cache")

MONTH_NAMES = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
MONTH_NAMES.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})
MONTH_NAMES["sept"] = 9


def get(url: str, *, ttl_hours: float = 6, timeout: int = 30, params: dict | None = None) -> str:
    """GET with a file cache so re-runs inside a day do not re-hit the sites."""
    CACHE_DIR.mkdir(exist_ok=True)
    key = hashlib.sha1((url + json.dumps(params or {}, sort_keys=True)).encode()).hexdigest()
    cached = CACHE_DIR / f"{key}.html"
    if cached.exists() and (time.time() - cached.stat().st_mtime) < ttl_hours * 3600:
        return cached.read_text(encoding="utf-8")
    r = requests.get(url, params=params, headers={"User-Agent": UA, "Accept-Language": "en"}, timeout=timeout)
    r.raise_for_status()
    cached.write_text(r.text, encoding="utf-8")
    time.sleep(1.0)  # be a polite guest on small Bermuda servers
    return r.text


def window(today: date | None = None, months: int = 3) -> list[tuple[int, int]]:
    """(year, month) tuples for the current month plus the next months-1."""
    today = today or date.today()
    out = []
    y, m = today.year, today.month
    for _ in range(months):
        out.append((y, m))
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return out


def first_weekday_sunday0(year: int, month: int) -> int:
    """Weekday index of the 1st with Sunday = 0, which is what the page's MONTHS table uses."""
    return (calendar.weekday(year, month, 1) + 1) % 7


_DATE_PATTERNS = [
    # Sat, Nov 21, 2026  |  Nov 21, 2026  |  November 21 2026
    re.compile(r"(?:(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*,?\s+)?(?P<mon>[A-Za-z]{3,9})\.?\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?,?\s*(?P<year>\d{4})?", re.I),
    # 21 November 2026 | 21 Nov
    re.compile(r"(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+(?P<mon>[A-Za-z]{3,9})\.?,?\s*(?P<year>\d{4})?", re.I),
    # 2026-11-21 | 11/21/2026
    re.compile(r"(?P<year>\d{4})-(?P<mon>\d{1,2})-(?P<day>\d{1,2})"),
    re.compile(r"(?P<mon>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4})"),
]


def parse_date(text: str, default_year: int | None = None) -> date | None:
    """Best effort date from free text. Returns the first date found.
    If the year is missing, uses default_year, and rolls forward a year when the date is more than
    60 days in the past (a December listing read in January means next December is not intended,
    but a January listing read in December is next year)."""
    if not text:
        return None
    for pat in _DATE_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        mon = m.group("mon")
        if mon.isdigit():
            month = int(mon)
        else:
            month = MONTH_NAMES.get(mon.lower()[:3]) or MONTH_NAMES.get(mon.lower())
        if not month:
            continue
        day = int(m.group("day"))
        year = int(m.group("year")) if m.group("year") else (default_year or date.today().year)
        try:
            d = date(year, month, day)
        except ValueError:
            continue
        if not m.group("year") and (date.today() - d).days > 60:
            d = date(year + 1, month, day)
        return d
    return None


def parse_time(text: str) -> str:
    """Short time string like '7pm' or '6:30pm' from free text, or ''."""
    m = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM|a\.m\.|p\.m\.)", text or "")
    if not m:
        return ""
    h, mins, ap = m.group(1), m.group(2), m.group(3).lower().replace(".", "")
    return f"{int(h)}{':' + mins if mins and mins != '00' else ''}{ap}"


def daterange(a: date, b: date):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)


def fmt_day(d) -> str:
    """'9 Nov' without a leading zero, on every platform."""
    return f"{d.day} {d.strftime('%b')}"


def fmt_date_long(d) -> str:
    return f"{d.day} {d.strftime('%B %Y')}"


def fmt_time(t) -> str:
    """'6:15pm' or '7pm' from a datetime, on every platform."""
    h = t.hour % 12 or 12
    ap = "am" if t.hour < 12 else "pm"
    return f"{h}:{t.minute:02d}{ap}" if t.minute else f"{h}{ap}"


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()
