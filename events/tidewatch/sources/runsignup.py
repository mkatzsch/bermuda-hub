"""RunSignup races in Bermuda (5Ks, fun runs, triathlons, swims, bike races).

Developed by AiTide Ltd. | www.AiTide.com
Version: 0.2
Last Updated: 2026-11-22

Change Log
  0.2  2026-11-22  The description is turned into plain text before it is shortened. It used to be cut at 300
                   characters first, which left half an HTML tag on the page.
  0.1  2026-11-15  First release.

RunSignup has a public JSON API that needs no key for race search:
  https://runsignup.com/Rest/races?format=json&country=BM&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&results_per_page=100
Each race returns name, next_date, address (city, street), url and a description. This is the
cleanest source in the whole planner, so it is a good first one to run when testing.
"""
from __future__ import annotations

import json
from datetime import date, timedelta

import requests

from ..util import UA, clean, parse_time, window

API = "https://runsignup.com/Rest/races"


def fetch(cfg: dict | None = None) -> list[dict]:
    w = window()
    start = date(w[0][0], w[0][1], 1)
    end = date(w[-1][0], w[-1][1], 28) + timedelta(days=7)
    params = {"format": "json", "country": "BM", "start_date": start.isoformat(), "end_date": end.isoformat(),
              "results_per_page": 100, "include_event_days": "T", "sort": "date ASC"}
    try:
        r = requests.get(API, params=params, headers={"User-Agent": UA}, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[runsignup] {e}")
        return []
    out = []
    for item in data.get("races", []):
        race = item.get("race", item)
        nd = race.get("next_date") or ""
        try:
            m, d, y = nd.split("/")
            when = date(int(y), int(m), int(d))
        except Exception:
            continue
        addr = race.get("address") or {}
        venue = clean(", ".join(x for x in (addr.get("name"), addr.get("street"), addr.get("city")) if x))
        desc = clean(race.get("description") or "")[:300].rstrip()
        events = race.get("events") or []
        times = ", ".join(sorted({parse_time(e.get("start_time", "")) for e in events if parse_time(e.get("start_time", ""))}))
        out.append({
            "date": when, "end": None, "name": clean(race.get("name", "")), "time": times.split(",")[0] if times else "",
            "time_text": times or "See registration page", "venue": venue or "Bermuda", "cost": "Entry fee on RunSignup",
            "ages": "All ages" if any(k in desc.lower() for k in ("kids", "junior", "family", "youth")) else "",
            "note": desc, "link": race.get("url", ""), "source": "runsignup", "source_key": str(race.get("race_id", "")),
            "raw": f"{race.get('name','')} {desc}",
        })
    return out
