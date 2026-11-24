# Bermuda Deals collector

A small Python project that collects Bermuda grocery, retail and restaurant prices every morning and builds `report.html`, the same page that is published as the "Bermuda Grocery Deals" artifact.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.1 | Last Updated: 2026-11-17

## Setup (once)
1. Double-click `install.bat`. It registers a Windows scheduled task ("Bermuda Deals collector", daily at 6:00 am) and runs the first collection, which takes a few minutes because it downloads every Sargasso Sea menu.
2. Open `report.html` to see the page. `log.txt` shows what each run did; `status.json` shows which sources succeeded.

## What runs daily (no Claude, no tokens)
- MarketPlace bi-weekly ad and shelf prices for the staples basket (Freshop API, Hamilton store)
- Miles Market and Pronto shelf prices for the same basket
- Lindo's newest specials posts and Supermart's weekly flyer: the images are downloaded into `flyers/` for the weekly read
- Red Laser sale items, Gosling's sale collection, Masters / Phoenix / P-Tech / Annex Toys promotion images
- Sargasso Sea restaurant list every day; full menus every 28 days (or `run.bat --menus`)
- Facebook pages (grocery stores, farms, Hamilton shops, restaurants) read signed out by Playwright into `data/<date>/facebook.json`: weekly tier on Mondays, monthly tier on the first Monday of the month, parked tier on the first Monday of January, April, July and October. `run.bat --facebook` reads the weekly tier any day; `--facebook-all` every tier. The page list and tiers are in `config.json` under `facebook`; a page with `"url": null` is skipped until the address is filled in. Image-only posts are screenshotted into `flyers/facebook/`.
- Island restaurant directory from OpenStreetMap (`data/places.json`, every place tagged restaurant, fast food, cafe, bar or pub, merged with the Sargasso list) and menus read from each restaurant's own website (`data/menus_own.json`; HTML, PDF or image menus, the images through the OCR module), with the Sargasso markup per item in `data/markup.json`. Both refresh every 28 days with the Sargasso menus; `run.bat --places` or `--own-menus` any day, `--own-menus-only NAME` for one site. The site list is `config.json` `restaurants` (kind auto, html, pdf, image or skip); places.json supplies any website not listed.
- Every price goes into `history.csv`, which drives the "Price moves" section (day-to-day changes and 90-day lows)

## What the weekly Claude step still does
Reads the flyer images in `flyers/` and writes `data/flyers/lindos.json` and `supermart.json`; summarises `data/facebook_latest.json` (and looks at any screenshots in `flyers/facebook/`); updates `editorial.json` (best buys commentary, farms, other stores, retail shop sweep, eats deals); runs `build.py`; publishes `report.html` to the artifact link.

## Files
- `collect.py` daily entry point; `build.py` offline page builder (safe to run any time)
- `bgd/` source modules: `freshop.py`, `pronto.py`, `sargasso.py`, `retail.py`, `flyers.py`, `ocr.py`, `facebook.py`, `places.py`, `menus_own.py`, `staples.py`, `history.py`, `util.py`
- `config.json` the staples basket and matching rules (edit `q`, `must`, `any`, `not` if a row keeps matching the wrong product)
- `editorial.json` Claude-written cards and prose, dated by `asof`; cards older than 12 days are dropped from the page automatically
- `template.html` the page layout; the data block is filled by `build.py`
- `data/<date>/` daily snapshots, `data/menus.json` Sargasso menus, `data/flyers/` transcriptions, `flyers/` downloaded images

## Dependencies
Python 3.9+ with `requests` and `beautifulsoup4` (both come with Anaconda, which is what `run.bat` uses), plus `easyocr` and `pytesseract` for the flyer OCR and `playwright` for the Facebook sweep, `pdfplumber` for PDF menus (`pip install playwright` then `playwright install chromium`, once).
