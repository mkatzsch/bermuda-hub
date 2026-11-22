"""Tidewatch command line.

Developed by AiTide Ltd. | www.AiTide.com
Version: 0.4
Last Updated: 2026-11-21

Change Log
  0.4  2026-11-21  "weather" step: Bermuda Weather Service pages and an Open-Meteo hourly strip, kept as
                   data/weather.json and meta "weather" for the Hub's Weather tab.
  0.3  2026-11-16  "manual" command and step in "run": merges data/manual_events.json and
                   data/manual_blocks.json, the hand off files the Claude Facebook pass writes.
  0.2  2026-11-16  Windows safe date formatting, failures reported, probe command.
  0.1  2026-11-15  First release.

  tidewatch manual          merge data/manual_events.json (events found by hand or by the Claude Facebook
                            pass) and data/manual_blocks.json (WATCH, WEEKLY, VENUES, NOTFOUND, SOURCES
                            overrides) into the database; also runs inside "run"
  tidewatch seed            load data/seed.json (the hand built page) into the database, once
  tidewatch scrape          run every source scraper, classify, upsert, retire stale rows
  tidewatch sky             recompute the moon and glow worm layer for the window
  tidewatch films           refresh the cinema board (and showtimes if Playwright is installed)
  tidewatch football        rebuild fixtures and tables from the data files
  tidewatch render          write site/index.html from the database
  tidewatch run             scrape + sky + films + football + render (what the schedule calls)
  tidewatch probe <source>  print what a scraper sees, for fixing parsers when a site changes
  tidewatch football-news   print recent Bernews football headlines to update the results CSV
  tidewatch stats           row counts by view and source

Dependencies: config.yaml beside the package (paths, which sources to run, school breaks).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import yaml

from . import classify as cls
from .render import render
from .sources import REGISTRY, cinema, football, sky, weather
from .store import BLOCK_KINDS, SUFFIX, VIEWS, Store
from .util import window

ROOT = Path(__file__).resolve().parent.parent


def load_cfg(path: Path | None = None) -> dict:
    p = path or ROOT / "config.yaml"
    cfg = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
    cfg.setdefault("db", "data/tidewatch.sqlite")
    cfg.setdefault("template", "template/planner.html")
    cfg.setdefault("out", "site/index.html")
    cfg.setdefault("sources", list(REGISTRY))
    cfg.setdefault("breaks", {})
    cfg.setdefault("classify", {"use_model": False})
    for k in ("db", "template", "out"):
        cfg[k] = str((ROOT / cfg[k]).resolve())
    return cfg


def year_for_month(today: date):
    """Map a month number to the year it falls in within the three month window."""
    w = window(today)
    table = {m: y for y, m in w}

    def f(m: int) -> int:
        return table.get(m, today.year + (1 if m < today.month else 0))
    return f


def cmd_seed(cfg: dict, args) -> None:
    store = Store(cfg["db"])
    seed = json.loads((ROOT / "data/seed.json").read_text(encoding="utf-8"))
    months = seed["MONTHS"]
    year_of = {int(m): v["year"] for m, v in months.items()}
    n = 0
    for view in VIEWS:
        sfx = SUFFIX[view]
        for kind in BLOCK_KINDS:
            store.set_block(view, kind, seed[f"{kind}_{sfx}"])
        key = "SCREENINGS_V" if view == "movies" else f"EVENTS_{sfx}"
        for ev in seed[key]:
            y = year_of.get(int(ev["m"]), date.today().year)
            store.upsert_event(view, y, ev, source="seed", seen="2026-11-13")
            n += 1
    store.set_json("films", seed["FILMS"])
    store.set_json("leagues", seed["LEAGUES"])
    store.set_meta("seeded", {"when": date.today().isoformat(), "events": n})
    print(f"seeded {n} events from the hand built page")


def cmd_scrape(cfg: dict, args) -> None:
    store = Store(cfg["db"])
    today = date.today()
    yfm = year_for_month(today)
    seen = today.isoformat()
    use_model = bool(cfg.get("classify", {}).get("use_model"))
    for name in cfg["sources"]:
        fn = REGISTRY.get(name)
        if not fn:
            print(f"unknown source {name}")
            continue
        rows = fn(cfg.get(name, {}))
        added = 0
        for L in rows:
            d = L["date"]
            if (d.year, d.month) not in window(today):
                continue
            views = cls.classify(f"{L['name']} {L.get('venue','')} {L.get('note','')} {L.get('raw','')}")
            if not views and use_model:
                views = cls.classify_with_model(L.get("raw") or L["name"]) or {}
            if not views:
                views = {"adults": "arts"}  # park it somewhere visible rather than lose it
            for view, cat in views.items():
                ev = {"m": d.month, "d": d.day, "cat": cat, "t": L.get("time", ""), "name": L["name"],
                      "time": L.get("time_text") or L.get("time") or "See listing", "venue": L.get("venue", ""),
                      "ages": L.get("ages", ""), "cost": L.get("cost", ""), "status": "ok",
                      "note": L.get("note", ""), "link": L.get("link", "")}
                store.upsert_event(view, d.year, ev, source=L["source"], source_key=L.get("source_key", ""), seen=seen)
                added += 1
        retired = store.retire_missing(name, seen) if rows else 0
        print(f"[{name}] {len(rows)} listings -> {added} rows upserted, {retired} retired")


def cmd_sky(cfg: dict, args) -> None:
    store = Store(cfg["db"])
    months = window()
    evs = sky.build(months)
    yfm = year_for_month(date.today())
    for view in ("kids", "adults"):
        store.deactivate(view, "sky", "seed")
        for ev in evs:
            store.upsert_event(view, yfm(ev["m"]), ev, source="sky")
        store.retire_missing("sky", date.today().isoformat(), view)
    print(f"sky: {len(evs)} entries per view")


def cmd_films(cfg: dict, args) -> None:
    store = Store(cfg["db"])
    films = cinema.fetch(cfg.get("cinema", {}))
    if films:
        store.set_json("films", films)
        print(f"films: {len(films)} titles, {sum(1 for f in films if f['times'])} with showtimes")
    else:
        print("films: nothing fetched, keeping the previous board")


def cmd_football(cfg: dict, args) -> None:
    store = Store(cfg["db"])
    yfm = year_for_month(date.today())
    pairs = football.fixtures_as_events(ROOT / "data/football_fixtures.txt", yfm)
    for y, ev in pairs:
        store.upsert_event("sports", y, ev, source="football")
    store.retire_missing("football", date.today().isoformat(), "sports")
    store.set_json("leagues", football.tables(ROOT / "data/football_results.csv", store.get_json("leagues")))
    print(f"football: {len(pairs)} fixtures, tables recomputed")


MANUAL_EVENTS = Path("data/manual_events.json")
MANUAL_BLOCKS = Path("data/manual_blocks.json")


def cmd_manual(cfg: dict, args) -> None:
    """data/manual_events.json: [{"view": "kids", "m": 12, "d": 5, "cat": "fest", "name": ..., "t": "10am",
    "time": ..., "venue": ..., "ages": ..., "cost": ..., "status": "ok", "note": ..., "link": ..., "year": 2026}]
    One object per view per day. "year" is optional (worked out from the month). A row with "remove": true
    deactivates the event of that view, date and name whatever its source.
    data/manual_blocks.json: {"kids": {"WATCH": [...], "WEEKLY": [...], "VENUES": [...], "NOTFOUND": [...],
    "SOURCES": [...]}, ...} replaces those blocks whole; leave a kind out to keep what is there."""
    store = Store(cfg["db"])
    with store.tx() as c:  # retired category keys from earlier runs
        c.execute("UPDATE events SET cat='xmas' WHERE cat='hallow' AND view IN ('kids','adults')")
    yfm = year_for_month(date.today())
    n = 0
    if MANUAL_EVENTS.exists():
        rows = json.loads(MANUAL_EVENTS.read_text(encoding="utf-8"))
        for r in rows:
            view = r.get("view", "kids")
            year = int(r.get("year") or yfm(int(r["m"])))
            if r.get("remove"):
                with store.tx() as c:
                    c.execute("UPDATE events SET active=0 WHERE view=? AND year=? AND m=? AND d=? AND name=?",
                              (view, year, int(r["m"]), int(r["d"]), r["name"]))
                continue
            ev = {k: r.get(k, "") for k in ("m", "d", "cat", "t", "name", "time", "venue", "ages", "cost", "status", "note", "link")}
            ev["status"] = ev["status"] or "ok"
            ev["time"] = ev["time"] or ev["t"] or "See listing"
            store.upsert_event(view, year, ev, source="manual")
            n += 1
    b = 0
    if MANUAL_BLOCKS.exists():
        blocks = json.loads(MANUAL_BLOCKS.read_text(encoding="utf-8"))
        for view, kinds in blocks.items():
            for kind, value in kinds.items():
                store.set_block(view, kind.upper(), value)
                b += 1
    print(f"manual: {n} events merged, {b} blocks replaced")


def cmd_weather(cfg: dict, args) -> None:
    store = Store(cfg["db"])
    w = weather.fetch(cfg.get("weather", {}))
    store.set_meta("weather", w)


def cmd_render(cfg: dict, args) -> None:
    store = Store(cfg["db"])
    out = render(store, Path(cfg["template"]), Path(cfg["out"]), breaks=cfg.get("breaks", {}))
    print(f"rendered {out} ({out.stat().st_size // 1024} KB)")


def cmd_run(cfg: dict, args) -> None:
    failed = []
    for fn in (cmd_scrape, cmd_sky, cmd_films, cmd_football, cmd_weather, cmd_manual, cmd_render):
        try:
            fn(cfg, args)
        except Exception as e:  # keep going; a dead site must not stop the render
            print(f"!! {fn.__name__}: {e}")
            failed.append(fn.__name__.replace("cmd_", ""))
    Store(cfg["db"]).set_meta("last_run", {"date": date.today().isoformat(), "failed": failed})
    print("run complete" + (f", with failures in: {', '.join(failed)}" if failed else ", all steps ok"))
    if failed:
        raise SystemExit(2)


def cmd_probe(cfg: dict, args) -> None:
    fn = REGISTRY.get(args.source)
    if not fn:
        print(f"unknown source {args.source}; choose from {list(REGISTRY)}")
        return
    rows = fn(cfg.get(args.source, {}))
    print(f"{len(rows)} listings")
    if args.source == "gotobermuda":
        from .sources import gotobermuda as g
        print("first raw record:", json.dumps(g.LAST_RAW, indent=1)[:1500] if g.LAST_RAW else "none")
    for L in rows[: args.n]:
        print("-" * 70)
        print(f"{L['date']}  {L.get('time','')}  {L['name']}")
        print(f"  venue: {L.get('venue','')}  cost: {L.get('cost','')}  link: {L.get('link','')}")
        print(f"  raw: {L.get('raw','')[:300]}")
        print(f"  classify: {cls.classify(L['name'] + ' ' + L.get('raw',''))}")


def cmd_football_news(cfg: dict, args) -> None:
    for title, url in football.football_news():
        print(f"{title}\n  {url}")


def cmd_stats(cfg: dict, args) -> None:
    store = Store(cfg["db"])
    for k, v in sorted(store.counts().items()):
        print(f"{k:28} {v}")
    print("last run:", store.get_meta("last_run"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="tidewatch")
    ap.add_argument("--config", type=Path)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("seed", "scrape", "sky", "films", "football", "weather", "manual", "render", "run", "football-news", "stats"):
        sub.add_parser(name)
    p = sub.add_parser("probe")
    p.add_argument("source")
    p.add_argument("-n", type=int, default=8)
    args = ap.parse_args(argv)
    cfg = load_cfg(args.config)
    {"seed": cmd_seed, "scrape": cmd_scrape, "sky": cmd_sky, "films": cmd_films, "football": cmd_football,
     "render": cmd_render, "run": cmd_run, "manual": cmd_manual, "weather": cmd_weather, "probe": cmd_probe, "football-news": cmd_football_news, "stats": cmd_stats}[args.cmd](cfg, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
