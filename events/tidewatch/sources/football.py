"""BFA football: fixtures, results and computed league tables.

Developed by AiTide Ltd. | www.AiTide.com
Version: 0.2
Last Updated: 2026-11-16

Inputs (plain files in data/, easy to edit by hand):
  football_fixtures.txt   one fixture per line: month-day|kick off|home|away|venue|competition|flag
                          (the same format the page used; seeded from the BFA 2026/27 schedule PDF)
  football_results.csv    competition,date,home,score,away,where  with score like "3 to 1"

Outputs:
  fixtures_as_events()    calendar entries for the sports view (cat football)
  tables()                the LEAGUES entries for prem and first, recomputed from the results CSV
                          (3 points a win, 1 a draw; ordered by points, goal difference, goals for)

Keeping results fresh: nobody publishes a 2026/27 table, so results come from Bernews and the
Royal Gazette match reports. `tidewatch football-news` prints the recent "Football:" headlines
and links so the scores can be added to the CSV in a minute, and if an API key is set it will
extract them with a small model call per article (see cli.py).
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

from ..util import clean, fmt_date_long, get

BFA_PDF = "https://cloudfront.bernews.com/wp-content/uploads/2026/09/BFA-Senior-Schedule-2026-2027-FINAL.pdf"
PREM = ["Dandy Town Hornets", "Devonshire Cougars", "North Village Rams", "St George's Colts", "PHC Zebras",
        "Somerset Trojans", "Devonshire Colts", "X-Roads Warriors", "Paget Lions", "Young Men's Social Club"]
FIRST = ["Somerset Eagles", "Hamilton Parish", "Southampton Rangers", "St David's", "Vasco da Gama", "Wolves", "Boulevard Blazers"]


def load_fixtures(path: Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) < 6:
            continue
        md, t, home, away, venue, comp = parts[:6]
        flag = parts[6] if len(parts) > 6 else ""
        m, d = (int(x) for x in md.split("-"))
        out.append({"m": m, "d": d, "t": t, "home": home, "away": away, "venue": venue, "comp": comp, "flag": flag})
    return out


def fixtures_as_events(path: Path, season_year_for_month) -> list[tuple[int, dict]]:
    """Returns (year, event) pairs. season_year_for_month(m) -> year."""
    out = []
    for f in load_fixtures(path):
        tbd = f["flag"] == "TBD" or f["venue"].lower().startswith("venue")
        name = f"{f['home']} {f['away']}" if f["away"].startswith("(") else f"{f['home']} v {f['away']}"
        extra = {"DH": " Part of a double header, so there is a second game the same evening.",
                 "derby": " A big one: local rivals, expect a crowd."}.get(f["flag"], "")
        ev = {"m": f["m"], "d": f["d"], "cat": "football", "t": "" if f["t"] == "TBD" else f["t"], "name": name,
              "time": "Time not published" if f["t"] == "TBD" else f"Kick off {f['t']}", "venue": f["venue"],
              "ages": "All ages, bring a chair", "cost": "Gate entry, usually $10 or less, kids free at most clubs",
              "status": "check" if tbd else "ok",
              "note": f"{f['comp']}.{extra} Fixtures move at short notice; check the Royal Gazette Friday What's On Where before you go.",
              "link": BFA_PDF}
        out.append((season_year_for_month(f["m"]), ev))
    return out


def load_results(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _score(s: str) -> tuple[int, int] | None:
    m = re.search(r"(\d+)\s*(?:to|-|–)\s*(\d+)", s or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def table(results: list[dict], teams: list[str]) -> list[list]:
    stat = {t: dict(p=0, w=0, d=0, l=0, gf=0, ga=0) for t in teams}
    for r in results:
        sc = _score(r["score"])
        if not sc or r["home"] not in stat or r["away"] not in stat:
            continue
        h, a = sc
        for team, gf, ga in ((r["home"], h, a), (r["away"], a, h)):
            s = stat[team]
            s["p"] += 1
            s["gf"] += gf
            s["ga"] += ga
            if gf > ga:
                s["w"] += 1
            elif gf == ga:
                s["d"] += 1
            else:
                s["l"] += 1
    rows = []
    for t, s in stat.items():
        pts = 3 * s["w"] + s["d"]
        rows.append([t, s["p"], s["w"], s["d"], s["l"], s["gf"], s["ga"], pts, s["gf"] - s["ga"]])
    rows.sort(key=lambda r: (-r[7], -r[8], -r[5], r[0]))
    out, pos = [], 0
    for i, r in enumerate(rows):
        if i == 0 or (r[7], r[8], r[5]) != (rows[i - 1][7], rows[i - 1][8], rows[i - 1][5]):
            pos = i + 1
        out.append([pos] + r[:8])
    return out


def tables(results_path: Path, existing: list[dict]) -> list[dict]:
    """Recompute the prem and first LEAGUES entries, leaving the others (cups, basketball...) as they are."""
    res = load_results(results_path)
    by = defaultdict(list)
    for r in res:
        by[r["competition"]].append(r)
    out = []
    for L in existing:
        if L["id"] in ("prem", "first"):
            teams = PREM if L["id"] == "prem" else FIRST
            rows = by.get(L["id"], [])
            L = dict(L)
            L["cols"] = ["Pos", "Team", "P", "W", "D", "L", "GF", "GA", "Pts"]
            L["rows"] = table(rows, teams)
            L["results"] = [[r["date"], r["home"], r["score"], r["away"], r["where"]] for r in rows][:12]
            L["asof"] = f"Computed from {len(rows)} reported results, as of {fmt_date_long(date.today())}."
        elif L["id"] == "cups":
            L = dict(L)
            rows = by.get("cups", [])
            if rows:
                L["results"] = [[r["date"], r["home"], r["score"], r["away"], r["where"]] for r in rows][:12]
        out.append(L)
    return out


def football_news(limit: int = 15) -> list[tuple[str, str]]:
    """Recent Bernews football headlines (title, url), for keeping the results CSV current."""
    try:
        html = get("https://bernews.com/tag/bermuda-football/", ttl_hours=1)
    except Exception as e:
        print(f"[football] {e}")
        return []
    out = []
    for m in re.finditer(r'<a[^>]+href="(https://bernews\.com/20\d\d/\d\d/[^"]+)"[^>]*>([^<]*Football[^<]*)</a>', html, re.I):
        pair = (clean(m.group(2)), m.group(1))
        if pair not in out:
            out.append(pair)
        if len(out) >= limit:
            break
    return out
