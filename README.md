# Bermuda Hub

Developed by AiTide Ltd. | www.AiTide.com
Version: 1.0
Last Updated: 2026-11-16

One folder, one scheduled run, one front door for the two Bermuda pages:

- **What's on** (`events/`, the Tidewatch planner): kids, adults, sports, music and nightlife, movies.
- **Deals** (`deals/`, the BermudaDeals collector): groceries, retail, eats with menus.

```
BermudaHub/
  run.py        orchestrator: deals daily, planner Mondays and Fridays, then site/index.html
  run.bat       what the Windows task calls
  install.bat   one time: moves data from the old BermudaDeals folder, installs packages,
                replaces the old task with "Bermuda Hub" (daily 6:00 am, wake enabled), runs once
  site/         index.html (front door with the What's on / Deals switch), planner.html, deals.html
  events/       Tidewatch, unchanged apart from writing to ../site/planner.html
  deals/        BermudaDeals, unchanged; its data/, flyers/ and history.csv live inside it
  .github/      GitHub Actions version of the same run (publishes site/ to GitHub Pages)
  fabric/       notebook version of the planner run
```

## Change Log
- 1.3 (2026-11-16): flyer OCR. `deals/bgd/ocr.py` reads the Lindo's and Supermart images locally
  (EasyOCR first, Tesseract as the second opinion on doubtful lines, PaddleOCR and a vision model as
  optional extras) and writes `deals/data/flyers/*.json` itself. The top half of that file is project
  neutral and can be copied into other builds. Needs `pip install -r deals\requirements.txt`.
- 1.2 (2026-11-16): planner scrapers rewritten against the live markup (ptix cards, gotobermuda's
  Algolia index, Speciality Cinema board and ticketing page); step failures now reported.
- 1.1 (2026-11-16): nightly OneDrive backup of the database, history and editorial files.
- 1.0 (2026-11-16): first merge. Both projects kept intact under one orchestrator and one Windows task.
  Shared storage (one SQLite for events and prices, a shared shop and venue directory) is the next step.

## Install on the laptop
1. Put this folder at `C:\Users\Matt\Documents\BermudaHub`, next to the existing `BermudaDeals` folder.
2. Double click `install.bat`. It moves the deals data across, installs the planner's packages, swaps the
   scheduled task, and runs everything once (a few minutes).
3. Open `site\index.html`.

The old `BermudaDeals` folder is left with only code in it afterwards and can be deleted.

## Daily operation
`run.py` with no arguments does what the schedule needs: deals every day, planner on Mondays and Fridays,
front door rebuilt each time. `run.py --all` forces both. `run.py --build` rebuilds the pages from the data
already on disk without touching the internet.

## What still needs Claude
Facebook pages, the retail promo images, and a weekly check of the OCR flyer read
(`deals/data/flyers/lindos_ocr.json` and `supermart_ocr.json` keep every line with its confidence, so
the check is a scan for low numbers rather than a re-read). The weekly Claude task writes
`deals/editorial.json` and publishes the two pages to the artifact links. Everything else is Python.

## OCR notes
- `python -m bgd.ocr <image>` (run inside `deals`) prints every line a reader saw, with its confidence,
  and the items made from them. Use it to check a flyer by hand.
- `python collect.py --ocr-only` re-reads the already downloaded flyer images and rebuilds the page.
- `config.json` may carry `"ocr": {"min_conf": 0.45, "tesseract": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe", "vision": false}`.
- A hand checked `lindos.json` for the current flyer is never overwritten by the OCR read of the same flyer.
