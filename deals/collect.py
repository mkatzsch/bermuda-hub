"""Bermuda Deals collector: pulls every structured price source, stores a dated snapshot, then rebuilds report.html.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.4
Last Updated: 2026-11-24

Change Log
  1.4  2026-11-24  Gorham's weekly flyer page (gorhams.bm/weekly-flyer) joins the promotion image downloads, saved
                   in flyers/gorhams/ like the Masters posters.
  1.3  2026-11-17  Island restaurant directory from OpenStreetMap (bgd/places.py, data/places.json) and menus read
                   from each restaurant's own website (bgd/menus_own.py: HTML, PDF, image via the OCR module) with
                   the Sargasso markup per item in data/markup.json. Both refresh on the 28 day menu cycle;
                   --places and --own-menus force them, --own-menus-only NAME reads one site.
  1.2  2026-11-17  Facebook sweep (bgd/facebook.py): Playwright reads every page in config.json "facebook" signed out
                   on its tier day and writes data/<date>/facebook.json, so the weekly model step summarises text
                   instead of browsing. --facebook forces the weekly tier today, --facebook-all every tier.
  1.1  2026-11-16  OCR step after the flyer downloads (bgd/ocr.py): EasyOCR then Tesseract read the Lindo's and
                   Supermart images locally and write data/flyers/*.json, so the weekly model read is only a check.
                   --no-ocr skips it.
  1.0  2026-11-15  First release. MarketPlace and Miles (Freshop), Pronto (Eddress), Sargasso Sea menus,
                   Red Laser, Gosling's, Masters and Phoenix promo images, Lindo's and Supermart flyer images,
                   Price Rite deals page, daily history.csv, then build.py.

Dependencies: Python 3.9+, requests, beautifulsoup4 (both ship with Anaconda), playwright for the Facebook sweep
(pip install playwright, then playwright install chromium). config.json for the staples
basket and store ids; editorial.json and data/flyers/*.json are written by the weekly Claude step.

Usage:  python collect.py            daily run (menus refreshed when older than config menus_refresh_days)
        python collect.py --menus    force a full Sargasso menu crawl
        python collect.py --no-build skip the page build
        python collect.py --no-ocr   skip the flyer OCR (for instance before easyocr is installed)
        python collect.py --ocr-only just re-read the already downloaded flyer images
        python collect.py --facebook read the weekly-tier Facebook pages today (--facebook-all reads every tier)
        python collect.py --facebook-only  just the Facebook sweep, nothing else
        python collect.py --places       refresh the island restaurant directory from OpenStreetMap today
        python collect.py --own-menus    read every restaurant website menu today (--own-menus-only NAME for one)
"""
import sys, os, json, datetime as dt, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bgd.util import log, today, day_dir, save_json, load_json, ROOT, DATA
from bgd import freshop, pronto, sargasso, retail, flyers, staples, history, ocr, facebook, places, menus_own

CFG = load_json(os.path.join(ROOT, "config.json"), {})
LATEST = os.path.join(DATA, "latest")


def step(name, fn, status, *a, **k):
    try:
        r = fn(*a, **k)
        status["ok"].append(name)
        return r
    except Exception as e:
        log("%s FAILED: %s" % (name, e))
        log(traceback.format_exc().strip().splitlines()[-1])
        status["failed"].append("%s: %s" % (name, e))
        return None


def price_staples(status):
    """Price the staples basket at MarketPlace, Miles and Pronto. Returns {key: {store: hit}}."""
    out = {r["key"]: {} for r in CFG["staples"]}
    clients = {}
    for code in ("mp", "ml"):
        st = CFG["stores"][code]
        try:
            clients[code] = freshop.Freshop(st["freshop_app"], st["freshop_store"])
        except Exception as e:
            log("%s session failed: %s" % (st["name"], e)); status["failed"].append("%s session: %s" % (code, e))
    for rule in CFG["staples"]:
        for code, cl in clients.items():
            try:
                out[rule["key"]][code] = staples.pick(rule, cl.search(rule["q"]))
            except Exception as e:
                log("%s search %s failed: %s" % (code, rule["q"], e))
        try:
            out[rule["key"]]["pr"] = staples.pick(rule, pronto.search(rule["q"]))
        except Exception as e:
            log("pronto search %s failed: %s" % (rule["q"], e))
    n = sum(1 for k in out for s in out[k] if out[k][s] and out[k][s].get("price") is not None)
    log("Staples: %d of %d store prices found" % (n, len(out) * 3))
    return out


def main(argv):
    force_menus = "--menus" in argv
    do_build = "--no-build" not in argv
    do_ocr = "--no-ocr" not in argv
    fb_force = "all" if "--facebook-all" in argv else ("--facebook" in argv or "--facebook-only" in argv)
    if "--facebook-only" in argv:
        facebook.run(CFG.get("facebook"), today(), force=fb_force or True)
        return 0
    if "--own-menus-only" in argv:
        name = argv[argv.index("--own-menus-only") + 1] if len(argv) > argv.index("--own-menus-only") + 1 else None
        menus_own.run(CFG.get("restaurants"), today(), load_json(os.path.join(DATA, "places.json"), {}), None, CFG.get("ocr"), only=name)
        return 0
    if "--ocr-only" in argv:
        d = today(); ddir = day_dir(d)
        ld = load_json(os.path.join(ddir, "lindos_posts.json"), {})
        sm = load_json(os.path.join(ddir, "supermart_flyer.json"), {})
        ocr.run(ld, sm, ROOT, CFG.get("ocr"), log)
        if do_build:
            import build; build.main()
        return 0
    d = today()
    ddir = day_dir(d)
    status = {"date": d.isoformat(), "started": dt.datetime.now().isoformat(timespec="seconds"), "ok": [], "failed": []}
    log("=== collect %s ===" % d)

    # 1. MarketPlace bi-weekly ad
    def mp_ad():
        cl = freshop.Freshop(CFG["stores"]["mp"]["freshop_app"], CFG["stores"]["mp"]["freshop_store"])
        return cl.circular()
    ad = step("marketplace_ad", mp_ad, status)
    if ad:
        save_json(os.path.join(ddir, "marketplace_ad.json"), ad)

    # 2. Staples at three stores
    sp = step("staples", price_staples, status, status)
    if sp:
        save_json(os.path.join(ddir, "staples.json"), sp)
        rows = []
        for key, stores_ in sp.items():
            for code, hit in stores_.items():
                if hit and hit.get("price") is not None:
                    rows.append([d.isoformat(), code, key, "%.2f" % hit["price"], ("OOS " if hit["oos"] else "") + hit["name"][:60]])
        if ad:
            for it in ad["items"]:
                rows.append([d.isoformat(), "mp", "sale:" + it["item"][:50].lower(), "%.2f" % float(it["price"]), it.get("finish") or ""])
        history.append(rows)

    # 3. Flyer sources (images) and Price Rite
    ld = step("lindos", flyers.lindos, status)
    if ld: save_json(os.path.join(ddir, "lindos_posts.json"), ld)
    sm = step("supermart", flyers.supermart, status)
    if sm: save_json(os.path.join(ddir, "supermart_flyer.json"), sm)
    prc = step("pricerite", flyers.pricerite, status)
    if prc: save_json(os.path.join(ddir, "pricerite.json"), prc)
    if do_ocr:
        step("flyer_ocr", ocr.run, status, ld, sm, ROOT, CFG.get("ocr"), log)
    # 3b. Facebook pages (weekly tier on Mondays, monthly on the first Monday, parked quarterly; --facebook forces)
    step("facebook", facebook.run, status, CFG.get("facebook"), d, fb_force)

    # 4. Retail web stores
    rl = step("redlaser", retail.redlaser, status)
    if rl is not None: save_json(os.path.join(ddir, "redlaser.json"), rl)
    gs = step("goslings", retail.goslings, status)
    if gs is not None: save_json(os.path.join(ddir, "goslings.json"), gs)
    promos = {}
    for name, url in (("masters", "https://masters.bm/special-promotions/"), ("phoenix", "https://www.phoenixstores.com/promotions-2/"),
                      ("ptech", "https://www.ptech.bm/promotions-2/"), ("annextoys", "https://www.annextoys.bm/promotions/"), ("gorhams", "https://gorhams.bm/weekly-flyer")):
        promos[name] = step("promo_" + name, retail.promo_images, status, name, url) or []
    save_json(os.path.join(ddir, "promo_images.json"), promos)

    # 5. Sargasso Sea stores daily, menus when stale
    stores_ = step("sargasso_stores", sargasso.stores, status)
    if stores_:
        save_json(os.path.join(ddir, "sargasso_stores.json"), stores_)
        menus_path = os.path.join(DATA, "menus.json")
        meta = load_json(os.path.join(DATA, "menus_meta.json"), {})
        age = (d - dt.date.fromisoformat(meta["read"])).days if meta.get("read") else 999
        if force_menus or age >= int(CFG.get("menus_refresh_days", 28)) or not os.path.exists(menus_path):
            menus = step("sargasso_menus", sargasso.crawl, status, stores_)
            if menus:
                save_json(menus_path, menus)
                save_json(os.path.join(DATA, "menus_meta.json"), {"src": "Sargasso Sea app", "read": d.isoformat(), "stores": len(menus)})
        else:
            log("Sargasso menus are %d days old, next refresh at %s days" % (age, CFG.get("menus_refresh_days", 28)))

    # 6. Island restaurant directory and own-website menus, on the same 28 day cycle (or --places / --own-menus)
    cycle = int(CFG.get("menus_refresh_days", 28))
    pl = load_json(os.path.join(DATA, "places.json"), {})
    page_age = (d - dt.date.fromisoformat(pl["read"])).days if pl.get("read") else 999
    if "--places" in argv or page_age >= cycle:
        pl = step("places", places.run, status, d, stores_) or pl
    mo = load_json(os.path.join(DATA, "menus_own.json"), {})
    mo_age = min([(d - dt.date.fromisoformat(v["read"])).days for v in mo.values() if v.get("read")] or [999])
    if "--own-menus" in argv or mo_age >= cycle:
        step("own_menus", menus_own.run, status, CFG.get("restaurants"), d, pl, None, CFG.get("ocr"))

    status["finished"] = dt.datetime.now().isoformat(timespec="seconds")
    save_json(os.path.join(ROOT, "status.json"), status)
    # "latest" pointer: a copy of today's folder name
    save_json(os.path.join(DATA, "latest.json"), {"date": d.isoformat()})
    log("collect done: %d ok, %d failed" % (len(status["ok"]), len(status["failed"])))

    if do_build:
        import build
        build.main()


if __name__ == "__main__":
    main(sys.argv[1:])
