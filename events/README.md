# Tidewatch

Developed by AiTide Ltd. | www.AiTide.com
Version: 0.1
Last Updated: 2026-11-15

The Bermuda Month Planner as a plain Python pipeline: scrape the structured sources, store events in
SQLite, compute the sky layer and the football tables, render the same HTML page, and run it on a
schedule. No agent, no tokens, except an optional small model call for listings the keyword rules
cannot place.

## Change Log
- 0.1 (2026-11-15): first cut. Seeds from the hand built page (787 events), scrapers for RunSignup,
  ptix.bm, gotobermuda.com, the Speciality Cinema board and showtimes, BFA fixtures and tables, the
  sky layer, renderer, GitHub Actions workflow, Fabric notebook, parser tests.

## What it does

```
tidewatch seed       load data/seed.json into data/tidewatch.sqlite (run once)
tidewatch run        scrape + sky + films + football + render   (the scheduled job)
tidewatch render     write site/index.html from the database
tidewatch probe ptix show what a scraper sees (use this when a site changes)
tidewatch stats      row counts by view and source
```

Views and data flow:

```
runsignup API ─┐
ptix.bm        ├─ sources/*.py ─ classify.py ─┐
gotobermuda    ┘  (one dict per listing)     │        store.py (SQLite)        render.py
cinema board + showtimes (Playwright) ────── films ──┤  events / blocks / films ─┼─► site/index.html
data/football_fixtures.txt + results.csv ─ football ─┤  leagues / meta         │  (same page, same look)
PyEphem ───────────────────────────────────── sky ───┘                         │
data/seed.json (the hand built page) ─ seed ─────────┘
```

The page template (`template/planner.html`) is the live artifact with its data region replaced by
`{{DATA}}`. The renderer emits that region as the same JavaScript constants, so the page's CSS and
behaviour are untouched and the output is byte for byte the same shape.

## Running it on your laptop

```
python -m venv .venv && .venv\Scripts\activate      (Windows)   or   source .venv/bin/activate
pip install -r requirements.txt
pip install playwright && playwright install chromium   (optional, for cinema showtimes)
python -m tidewatch seed
python -m tidewatch run
start site\index.html
```

Start with `python -m tidewatch probe runsignup`, which uses a clean JSON API and should return a
dozen races immediately. Then `probe ptix` and `probe gotobermuda`. If a probe returns listings with
empty dates or venues, send me the `raw:` lines and I will adjust the regexes; the parsers are
anchored on link patterns rather than CSS classes so they survive most redesigns.

## Keeping the hand curated parts current

Some things no scraper can do. They live in plain files and the database and take a minute each:

- `data/football_fixtures.txt`: the BFA schedule, one line per game. `tidewatch football-news`
  prints the week's match report headlines; add scores to `data/football_results.csv` and the
  tables recompute.
- The `blocks` table (watch lists, weekly tables, venues, "looked for, nothing", sources) is edited
  in SQLite or by re-running `seed` after editing `data/seed.json`. A tiny admin page is the obvious
  next step.
- School breaks: `breaks` in `config.yaml`.
- Facebook and Instagram flyers: not scraped. The pragmatic route is a weekly ten minute pass in
  Claude in Chrome that adds them to the database, or the optional vision step (not built yet).

## GitHub Actions (free, no server)

Push this folder to a repository, enable Pages (Settings, Pages, Source: GitHub Actions), and the
workflow in `.github/workflows/refresh.yml` runs Monday and Friday mornings, commits the SQLite file
back so history accumulates, and publishes `site/` to `https://<org>.github.io/tidewatch/`.
Run it by hand from the Actions tab with "Run workflow".

## Microsoft Fabric

`fabric/tidewatch_refresh.ipynb` is a notebook that clones the repo, runs the same `run` command,
keeps the SQLite file in the Lakehouse Files area, writes `index.html` next to it, and lands the
events as a Delta table `tidewatch_events` for Power BI. Attach a Lakehouse, set the repo URL in
cell 3, and schedule it from the notebook's Run settings. Pause the capacity between runs to keep
the bill at a few dollars a month.

## Optional model fallback

Set `classify.use_model: true` in `config.yaml` and `ANTHROPIC_API_KEY` in the environment (a
repository secret on GitHub, a Key Vault reference on Fabric). Only listings the keyword rules
cannot place are sent, one short call each, to a small model with a fixed JSON schema.

## Layout

```
tidewatch/            package: cli, store, util, classify, render, sources/
template/planner.html page template
data/seed.json        the hand built page's data, imported once
data/football_*.txt|csv
fabric/               notebook
.github/workflows/    schedule
tests/                parser tests (python -m pytest)
```
