"""Bermuda Hub orchestrator: one scheduled run for the deals collector and the what's-on planner.

Developed by AiTide Ltd. | www.AiTide.com
Version: 1.18
Last Updated: 2026-11-22

Change Log
  1.18 2026-11-22  Weather tab extras: feels like and a comfort word, a line on the rain over the coming hours,
                   Go / Maybe / Skip for beach, boat, snorkel, run and laundry, dials for wind, sun, UV and moon,
                   a sea state card, the best daytime low tide for the beach, rain for the tank, the NHC tropics
                   outlook in hurricane season (GitHub Pages copy only), and links to live cameras.
  1.17 2026-11-22  Tide graph: the rise and fall at St George's across today and tomorrow against the clock, each
                   high and low labelled, with a line at the time now and whether the tide is rising or falling.
  1.16 2026-11-22  Weather scene redrawn as Harbour Road at dusk: proper Bermuda cottages (stepped hip roofs,
                   chimneys, shutters, arched doors) in two rows on a hillside, a moongate, hibiscus hedge, palms.
  1.15 2026-11-22  Weather tab restyled as a tropical neon dusk: purple to pink to orange sky, striped setting sun,
                   palm silhouettes, glowing script headings (Yellowtail, with Outfit for the rest), teal and hot
                   pink accents. The Bermuda houses with white stepped roofs stay. One palette for light and dark.
  1.14 2026-11-22  Weather tab redesign: a Bermuda scene at the top (pastel houses, white stepped roofs, the sea, a
                   sky that follows the conditions and the time of day), its own island palette in light and dark,
                   Fraunces for headings. Radar and Windy share one map panel with a Radar / Windy toggle, and the
                   radar has plus and minus buttons that step through the five views.
  1.13 2026-11-22  Live radar moved to the top of the Weather tab, straight under the headline.
  1.12 2026-11-22  Weather tab: Windy forecast map (Wind, Gusts, Rain, Waves buttons) under the live radar, on the
                   GitHub Pages copy. It is the official Windy embed, centred on Bermuda, wind in knots.
  1.11 2026-11-22  Live radar: five view buttons that step outward (Parishes, Satellite, 100 km, 250 km, 500 km),
                   each its own BWS animation. The last view picked is remembered on that device.
  1.10 2026-11-22  Weather tab: live Bermuda Weather Service radar animation (100 km) on the GitHub Pages copy. The
                   page finds the newest frames itself, so it stays current between laptop runs. The artifact
                   copy keeps the links only, because the artifact viewer blocks outside images.
                   GitHub Pages home page: docs/index.html is now a copy of hub.html, so Weather and Explore
                   have their data there (the laptop front door has none inside it).
  1.9  2026-11-22  GitHub: the built pages are copied to docs/ (the folder GitHub Pages serves) and each run
                   commits and pushes with the git that GitHub Desktop installed. A failed push is logged, never fatal.
  1.8  2026-11-21  Explore tab: forts and batteries, wrecks, abandoned sites, from events/data/explore.json
                   (filters, cards, a detail sheet; coordinates kept for the map once the site is on GitHub).
  1.7  2026-11-21  Weather tab: BWS warnings, latest conditions, headline, today and tonight, hourly strip, the
                   week, marine with seas inside and outside the reef, tides, radar links. Built from
                   events/data/weather.json.
  1.6  2026-11-21  Weather collected every morning (tidewatch weather) and the planner re-rendered daily.
  1.5  2026-11-21  List tab on the Hub: a shared grocery list (artifact db capability, both of them edit it
                   from their phones, kept across republishes) with this week's best buys per store as one
                   tap adds, tick in the aisle, clear ticked. site/index.html shows it read only.
  1.4  2026-11-21  Links inside the embedded pages are handed to the front door to open: the artifact viewer
                   lets the outer page open a new tab but not a nested frame, so ticket and venue links did
                   nothing on the published Hub.
  1.3  2026-11-16  site/hub.html: one self contained page with the planner and the deals page folded inside
                   (each as an inline frame), the file that becomes the single Bermuda Hub artifact.
  1.2  2026-11-16  Report planner step failures instead of "ok".
  1.1  2026-11-16  Nightly backup of the data that only exists on this laptop to OneDrive (BermudaHub-backup).
  1.0  2026-11-16  First release. Wraps deals/collect.py (daily) and events/ Tidewatch (Mondays and
                   Fridays), copies both pages into site/ and writes the front door site/index.html.

Usage:  python run.py            deals every day; events only on Mondays and Fridays
        python run.py --all      both, now
        python run.py --deals    deals only
        python run.py --events   events only
        python run.py --build    rebuild the pages from existing data, no collection

Dependencies: deals/ (BermudaDeals collector, its own config.json and data/), events/ (Tidewatch, its
own config.yaml and data/tidewatch.sqlite). Output: site/deals.html, site/planner.html, site/index.html.
"""
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DEALS = os.path.join(ROOT, "deals")
EVENTS = os.path.join(ROOT, "events")
SITE = os.path.join(ROOT, "site")
DOCS = os.path.join(ROOT, "docs")  # what GitHub Pages serves: a copy of site/ made at the end of every run
LOG = os.path.join(ROOT, "log.txt")
EVENT_DAYS = (0, 4)  # Monday, Friday


def log(msg: str) -> None:
    line = "[%s] %s" % (dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(cmd: list[str], cwd: str, label: str) -> bool:
    log("%s: %s" % (label, " ".join(cmd)))
    r = subprocess.run([sys.executable] + cmd, cwd=cwd)
    log("%s: %s" % (label, "ok" if r.returncode == 0 else "exit %d" % r.returncode))
    return r.returncode == 0


def deals(collect: bool) -> None:
    if collect:
        run(["collect.py"], DEALS, "deals collect")
    else:
        run(["build.py"], DEALS, "deals build")
    src = os.path.join(DEALS, "report.html")
    if os.path.exists(src):
        shutil.copy(src, os.path.join(SITE, "deals.html"))


def events(collect: bool) -> None:
    db = os.path.join(EVENTS, "data", "tidewatch.sqlite")
    if not os.path.exists(db):
        run(["-m", "tidewatch", "seed"], EVENTS, "events seed")
    ok = run(["-m", "tidewatch", "run" if collect else "render"], EVENTS, "events " + ("run" if collect else "render"))
    if not ok:
        log("events: one or more steps failed; see run_output.txt for the lines starting with !!")


BACKUP_ITEMS = [
    "events/data/tidewatch.sqlite", "events/config.yaml", "events/data/football_fixtures.txt", "events/data/football_results.csv",
    "events/data/manual_events.json", "events/data/manual_blocks.json", "events/data/weather.json",
    "deals/history.csv", "deals/editorial.json", "deals/config.json", "deals/status.json",
    "deals/data/latest.json", "deals/data/menus.json", "deals/data/menus_meta.json", "deals/data/flyers",
]


def backup() -> None:
    """Copy the files that exist nowhere else to OneDrive. Code is backed up by GitHub; flyer images and
    the rendered pages are rebuildable, so they stay local. Skipped quietly when OneDrive is not present."""
    base = os.environ.get("OneDrive") or os.environ.get("OneDriveCommercial") or os.environ.get("OneDriveConsumer")
    if not base or not os.path.isdir(base):
        log("backup: no OneDrive folder found, skipped")
        return
    dest = os.path.join(base, "BermudaHub-backup")
    n = 0
    for rel in BACKUP_ITEMS:
        src = os.path.join(ROOT, rel)
        if not os.path.exists(src):
            continue
        tgt = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(tgt), exist_ok=True)
        if os.path.isdir(src):
            shutil.copytree(src, tgt, dirs_exist_ok=True)
        else:
            shutil.copy2(src, tgt)
        n += 1
    # keep the last 14 daily deal snapshots too
    snaps = os.path.join(ROOT, "deals", "data")
    if os.path.isdir(snaps):
        days = sorted(d for d in os.listdir(snaps) if len(d) == 10 and d[4] == "-")[-14:]
        for d in days:
            shutil.copytree(os.path.join(snaps, d), os.path.join(dest, "deals", "data", d), dirs_exist_ok=True)
    log("backup: %d items copied to %s" % (n, dest))


def find_git() -> str | None:
    """git on the PATH, or the copy GitHub Desktop installs under the user's profile."""
    import glob
    if shutil.which("git"):
        return "git"
    for pat in (os.path.join(os.environ.get("LOCALAPPDATA", ""), "GitHubDesktop", "app-*", "resources", "app", "git", "cmd", "git.exe"),
                os.path.join(os.environ.get("PROGRAMFILES", ""), "Git", "cmd", "git.exe")):
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


def publish_github() -> None:
    """Copy site/ to docs/, commit everything the ignore file allows, push. Skipped when the folder is not a repository."""
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        log("github: not a repository yet, skipped")
        return
    git = find_git()
    if not git:
        log("github: git not found (install GitHub Desktop or Git for Windows), skipped")
        return
    os.makedirs(DOCS, exist_ok=True)
    for name in os.listdir(SITE):
        src = os.path.join(SITE, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(DOCS, name))
    hub = os.path.join(SITE, "hub.html")
    if os.path.isfile(hub):  # the Pages home page is the full Hub: site/index.html has no weather or explore data inside
        shutil.copy2(hub, os.path.join(DOCS, "index.html"))
    with open(os.path.join(DOCS, ".nojekyll"), "w") as f:  # serve files as they are
        f.write("")
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    def g(*args):
        return subprocess.run([git, "-C", ROOT] + list(args), capture_output=True, text=True)
    g("add", "-A")
    r = g("commit", "-m", "Build " + stamp)
    if r.returncode != 0 and "nothing to commit" in (r.stdout + r.stderr):
        log("github: nothing new to commit")
    elif r.returncode != 0:
        log("github: commit failed: " + (r.stderr or r.stdout).strip()[:200])
        return
    r = g("push")
    if r.returncode == 0:
        log("github: pushed build " + stamp)
    else:
        log("github: push failed (open GitHub Desktop and press Push origin): " + (r.stderr or r.stdout).strip()[-200:])


def front_door() -> None:
    """site/index.html: a shell with a What's on / Deals switch that loads the two pages (for the laptop),
    and site/hub.html: the same shell with both pages embedded, one file that can be published anywhere."""
    stamp = dt.date.today().strftime("%d %b %Y").lstrip("0")
    html = FRONT.replace("{{STAMP}}", stamp)
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    pages = {}
    for name in ("planner", "deals"):
        fp = os.path.join(SITE, name + ".html")
        if os.path.exists(fp):
            with open(fp, encoding="utf-8") as f:
                html_in = f.read()
            # a nested frame may not open new windows in the artifact viewer, so links are passed up to the front door
            relay = ("<script>document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href]');"
                     "if(!a)return;var h=a.getAttribute('href')||'';if(!/^https?:/i.test(h))return;e.preventDefault();"
                     "try{parent.postMessage({hubOpen:a.href},'*')}catch(x){}},true);</script>")
            html_in = html_in.replace("</body>", relay + "</body>", 1) if "</body>" in html_in else html_in + relay
            pages[name] = html_in.replace("</script", "<\\/script")  # keep the embedded page out of its holder tag
    if len(pages) == 2:
        best = best_buys(os.path.join(SITE, "deals.html"))
        hub = html.replace("<title>Bermuda Hub</title>", "<title>Bermuda Hub</title>" + "".join(
            '\n<script type="text/plain" id="page-%s">%s</script>' % (n, pages[n]) for n in ("planner", "deals"))
            + '\n<script type="application/json" id="best-buys">%s</script>' % json.dumps(best, ensure_ascii=False).replace("</", "<\\/")
            + '\n<script type="application/json" id="weather-data">%s</script>' % json.dumps(weather_doc(), ensure_ascii=False).replace("</", "<\\/")
            + '\n<script type="application/json" id="explore-data">%s</script>' % json.dumps(explore_doc(), ensure_ascii=False).replace("</", "<\\/"))
        swap = "f.srcdoc=document.getElementById('page-'+p).textContent.replace(/<\\\\\\/script/g,'</script')"
        assert "f.src=p+'.html'" in hub, "front door template changed: the page swap no longer matches"
        hub = hub.replace("f.src=p+'.html'", swap)
        hub = hub.replace('<iframe id="f" src="planner.html" title="page"></iframe>', '<iframe id="f" title="page"></iframe>')
        with open(os.path.join(SITE, "hub.html"), "w", encoding="utf-8") as f:
            f.write(hub)
        log("hub.html written, %d KB" % (len(hub.encode("utf-8")) // 1024))


def explore_doc() -> dict:
    fp = os.path.join(EVENTS, "data", "explore.json")
    if not os.path.exists(fp):
        return {}
    try:
        with open(fp, encoding="utf-8") as f:
            return json.load(f)
    except ValueError:
        return {}


def weather_doc() -> dict:
    fp = os.path.join(EVENTS, "data", "weather.json")
    if not os.path.exists(fp):
        return {}
    try:
        with open(fp, encoding="utf-8") as f:
            w = json.load(f)
    except ValueError:
        return {}
    w.pop("raw_pages", None)
    if "now" in w and isinstance(w["now"], dict):
        w["now"].pop("rows", None)
    return w


STORES = {"mp": "MarketPlace", "ld": "Lindo's", "sm": "Supermart", "ml": "Miles", "pr": "Pronto", "prc": "Price Rite", "ar": "Arnold's"}


def best_buys(deals_html: str, n: int = 16) -> dict:
    """This week's best buys from the deals page's own data block, for the List tab."""
    out = {"asof": "", "items": []}
    if not os.path.exists(deals_html):
        return out
    with open(deals_html, encoding="utf-8") as f:
        h = f.read()
    m = re.search(r'<script id="data" type="application/json">(.*?)</script>', h, re.S)
    if not m:
        return out
    try:
        d = json.loads(m.group(1).replace("<\\/", "</"))
    except ValueError:
        return out
    out["asof"] = d.get("asof") or ""
    seen = set()
    for b in d.get("best") or []:
        name = (b.get("n") or "").strip()
        key = name.lower()
        if not name or key in seen:
            continue
        seen.add(key)
        out["items"].append({"store": STORES.get(b.get("s"), b.get("s") or ""), "code": b.get("s") or "", "price": b.get("p") or "",
                             "unit": b.get("u") or "", "name": name, "why": (b.get("w") or "")[:220]})
        if len(out["items"]) >= n:
            break
    return out


FRONT = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bermuda Hub</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Yellowtail&display=swap">
<style>
:root{--bg:#f6f3ec;--ink:#1b1b1f;--line:#d9d4c7;--accent:#0b6fb3;--accent-ink:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#15161a;--ink:#f1efe8;--line:#34363d;--accent:#5db3ff;--accent-ink:#0b1a2a}}
:root[data-theme=dark]{--bg:#15161a;--ink:#f1efe8;--line:#34363d;--accent:#5db3ff;--accent-ink:#0b1a2a}
html,body{margin:0;background:var(--bg);color:var(--ink);font:15px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
#app{display:flex;flex-direction:column;height:100vh;height:100dvh;overflow:hidden}
header{flex:none;display:flex;align-items:center;gap:14px;padding:10px 16px;border-bottom:1px solid var(--line)}
h1{font-size:17px;margin:0;font-weight:800;letter-spacing:.01em}
.seg{display:inline-flex;border:1.5px solid var(--line);border-radius:999px;padding:3px;gap:3px;margin-left:auto;max-width:100%;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.seg::-webkit-scrollbar{display:none}
.seg button{border:0;background:transparent;color:var(--ink);font:700 14px inherit;padding:7px 14px;border-radius:999px;cursor:pointer;white-space:nowrap;flex:none}
@media (max-width:640px){header{flex-wrap:wrap;gap:8px 14px}.seg{margin-left:0;width:100%;justify-content:flex-start}}
.seg button[aria-pressed=true]{background:var(--accent);color:var(--accent-ink)}
small{opacity:.65}
iframe{display:block;width:100%;flex:1 1 auto;min-height:0;border:0}
[hidden]{display:none!important}
#list{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch}
.lwrap{max-width:720px;margin:0 auto;padding:14px 16px 60px;display:flex;flex-direction:column;gap:12px}
.lnote{color:var(--ink);opacity:.7;font-size:13px;margin:0}
#ladd{display:flex;gap:6px;flex-wrap:wrap}
#ladd input{flex:1 1 180px;font:inherit;padding:10px 12px;border:1.5px solid var(--line);border-radius:10px;background:transparent;color:var(--ink)}
#ladd select{font:inherit;padding:10px;border:1.5px solid var(--line);border-radius:10px;background:transparent;color:var(--ink)}
#ladd button,.lbtns button{font:700 14px inherit;padding:10px 16px;border:0;border-radius:999px;background:var(--accent);color:var(--accent-ink);cursor:pointer}
.lbtns{display:flex;gap:8px}
.lbtns .ghost{background:transparent;color:var(--ink);border:1.5px solid var(--line)}
.lgroup{margin-top:6px}
.lgroup h3{font-size:12px;letter-spacing:.08em;text-transform:uppercase;opacity:.65;margin:10px 0 4px}
.litem{display:flex;align-items:center;gap:10px;padding:10px 4px;border-bottom:1px solid var(--line)}
.litem input{width:22px;height:22px;flex:none}
.litem .n{flex:1;font-size:16px}
.litem.done .n{text-decoration:line-through;opacity:.5}
.litem .p{font-size:13px;opacity:.7;white-space:nowrap}
.litem .x{border:0;background:transparent;color:var(--ink);opacity:.5;font-size:18px;cursor:pointer;padding:4px 8px}
h2{font-size:18px;margin:18px 0 0}
.bcard{display:flex;gap:10px;align-items:flex-start;padding:10px 0;border-bottom:1px solid var(--line)}
.bcard .b{flex:1}
.bcard .b .t{font-weight:700}
.bcard .b .s{font-size:13px;opacity:.75}
.bcard .b .w{font-size:13px;opacity:.65;margin-top:3px}
.bcard button{flex:none;font:700 20px inherit;width:40px;height:40px;border-radius:50%;border:1.5px solid var(--accent);background:transparent;color:var(--accent);cursor:pointer}
.bcard button[disabled]{opacity:.4}
#weather{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;--w-bg:#170f3a;--w-ink:#fdf3ff;--w-soft:#cdbbea;--w-card:#241552;--w-line:#4b2d8a;--w-sea:#2af0d9;--w-deep:#2af0d9;--w-pink:#ff4fa3;--w-sand:#4d1c63;--w-night-ink:#fdf3ff;--w-water:#16356b;background:linear-gradient(#170f3a,#2a1058 55%,#3d1260);color:var(--w-ink)}
.wwrap{max-width:760px;margin:0 auto;padding:14px 16px 60px;display:flex;flex-direction:column;gap:16px}
.wwarn{background:#ffd166;color:#1b1b1f;border-radius:14px;padding:10px 14px;font-weight:700}
.wwarn small{display:block;font-weight:400;opacity:.8}
.whero{position:relative;border-radius:22px;overflow:hidden;min-height:300px;box-sizing:border-box;color:#fff;padding:18px 20px 150px;background:linear-gradient(#3a1a7a 0%,#b02a9a 38%,#ff5f8f 64%,#ffb25e 100%);box-shadow:0 0 0 1.5px #ff4fa3,0 10px 40px rgba(255,79,163,.28)}
.whero.cloud{background:linear-gradient(#34205f,#7a4a8f 55%,#e08aa6)}
.whero.rain{background:linear-gradient(#1d1640,#4a2f73 58%,#9a5f9c)}
.whero.night{background:linear-gradient(#0a0624,#2a1160 68%,#6a2385)}
.wscene{position:absolute;inset:0;width:100%;height:100%;display:block}
.wnow{position:relative;display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;text-shadow:0 0 18px rgba(255,79,163,.75),0 1px 3px rgba(20,5,45,.6)}
.wnow .big{font:800 68px/0.9 Outfit,"Segoe UI",sans-serif;letter-spacing:-.03em}
.wnow .sky{font:700 24px/1.1 Outfit,"Segoe UI",sans-serif}
.wnow .meta{font-size:14px;width:100%;margin-top:6px;font-weight:600}
.whead{font:400 40px/1.1 Yellowtail,"Segoe Script",cursive;margin-top:4px;color:#fff;text-shadow:0 0 14px rgba(255,79,163,.9),0 0 34px rgba(255,79,163,.5)}
.wsyn{color:var(--w-soft);font-size:15px;line-height:1.5;margin:0;max-width:68ch}
.wcards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
.wcard{background:var(--w-card);border:1px solid var(--w-line);border-radius:18px;padding:14px 16px}
.wcard h3{margin:0 0 4px;font:700 19px/1.2 Outfit,"Segoe UI",sans-serif}
.wcard .hl{font-weight:700;margin-bottom:6px;color:var(--w-deep)}
.wcard p{margin:0;font-size:14px;line-height:1.45}
.wcard.day{background:linear-gradient(135deg,#ffb25e,#ff5f8f);border-color:transparent;color:#2a0b3d}
.wcard.day .hl{color:#2a0b3d}
.wcard.eve{background:linear-gradient(135deg,#2b1570,#0f6f8f);border-color:transparent;color:var(--w-night-ink)}
.wcard.eve .hl{color:#8ff7ea}
.wcard.sea{background:linear-gradient(160deg,#16356b,#0e5f7a);border-color:transparent}
.wstrip{display:flex;gap:8px;overflow-x:auto;padding:4px 0 8px;-webkit-overflow-scrolling:touch}
.whr{flex:none;width:60px;text-align:center;background:var(--w-card);border:1px solid var(--w-line);border-radius:16px;padding:8px 2px;font-size:12px}
.whr .t{font:700 18px/1.3 Outfit,"Segoe UI",sans-serif}
.whr .r{color:var(--w-sea);font-weight:700}
.whr .w{color:var(--w-soft)}
.whr.now{background:var(--w-sand);border-color:var(--w-pink)}
.wweek{display:flex;flex-direction:column;background:var(--w-card);border:1px solid var(--w-line);border-radius:18px;padding:4px 16px}
.wday{display:grid;grid-template-columns:96px 1fr 70px;gap:10px;align-items:baseline;padding:11px 0;border-bottom:1px solid var(--w-line);font-size:14px}
.wday:last-child{border-bottom:0}
.wday .d{font:700 16px/1.2 Outfit,"Segoe UI",sans-serif}
.wday .hl{text-align:right;white-space:nowrap;font-weight:700;color:var(--w-deep)}
.wday .tx{color:var(--w-soft)}
.wnext{margin:-6px 0 0;font-size:16px;font-weight:600;color:#8ff7ea}
.wacts{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}
.wact{background:var(--w-card);border:1.5px solid var(--w-line);border-radius:16px;padding:10px 8px;text-align:center;display:flex;flex-direction:column;gap:2px}
.wact b{font-size:14px}
.wact .v{font:800 17px/1.2 Outfit,"Segoe UI",sans-serif}
.wact .y{font-size:11px;color:var(--w-soft);line-height:1.25}
.wact.go{border-color:#2af0d9}.wact.go .v{color:#2af0d9}
.wact.maybe{border-color:#fff27a}.wact.maybe .v{color:#fff27a}
.wact.skip{border-color:#ff4fa3}.wact.skip .v{color:#ff7ab8}
.wdials{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.wdial{background:var(--w-card);border:1px solid var(--w-line);border-radius:18px;padding:12px 10px;text-align:center}
.wdial h3{margin:0 0 4px;font:700 14px/1.2 Outfit,"Segoe UI",sans-serif;color:var(--w-soft)}
.wdial svg{display:block;width:100%;max-width:130px;height:auto;margin:0 auto;font-family:Outfit,"Segoe UI",sans-serif}
.wdial p{margin:6px 0 0;font-size:12.5px;line-height:1.3}
.wseac{grid-column:1/-1}
.wsea{display:grid;grid-template-columns:120px 1fr 78px;gap:10px;align-items:center;font-size:14px;margin:6px 0}
.wsea .trk{height:12px;border-radius:999px;background:rgba(255,255,255,.14);overflow:hidden}
.wsea .trk i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,#2af0d9,#ff4fa3)}
.wsea b{text-align:right}
.wtank .big{font:800 40px/1 Outfit,"Segoe UI",sans-serif;color:#2af0d9;margin-bottom:6px}
.wtrop{display:block;border-radius:18px;overflow:hidden;border:1.5px solid var(--w-line);background:#fff}
.wtrop img{display:block;width:100%;height:auto}
@media (max-width:620px){.wacts{grid-template-columns:repeat(3,1fr)}.wdials{grid-template-columns:repeat(2,1fr)}.wsea{grid-template-columns:104px 1fr 70px}}
.wtg{background:var(--w-card);border:1.5px solid #2af0d9;border-radius:18px;padding:10px 12px;box-shadow:0 8px 34px rgba(42,240,217,.14)}
.wtgs{overflow-x:auto;-webkit-overflow-scrolling:touch}
.wtgs svg{display:block;width:100%;min-width:640px;height:auto;font-family:Outfit,"Segoe UI",sans-serif}
.wtides{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.wtide{background:var(--w-water);border-radius:16px;padding:10px 12px;font-size:13px;line-height:1.6}
.wtide b{display:block;margin-bottom:2px;font:700 16px/1.2 Outfit,"Segoe UI",sans-serif}
.wtide .hi{font-weight:700}
.wlinks a{display:inline-block;margin:0 12px 6px 0;color:var(--w-deep);font-weight:700;text-decoration:none}
h2.w{font:400 30px/1.15 Yellowtail,"Segoe Script",cursive;margin:12px 0 0;color:#fff;text-shadow:0 0 12px rgba(42,240,217,.85),0 0 30px rgba(42,240,217,.4)}
.wsrc{font-size:12px;color:var(--w-soft);margin:0}
.wmap{background:var(--w-card);border:1.5px solid #2af0d9;box-shadow:0 8px 34px rgba(42,240,217,.18);border-radius:22px;padding:12px;display:flex;flex-direction:column;gap:10px}
.wmtog{display:inline-flex;align-self:flex-start;background:var(--w-water);border-radius:999px;padding:4px;gap:4px}
.wmtog button,.wrseg button{font-family:inherit;font-weight:700;font-size:14px;padding:7px 18px;border-radius:999px;border:0;background:none;color:var(--w-ink);cursor:pointer}
.wmtog button[aria-pressed="true"],.wrseg button[aria-pressed="true"]{background:var(--w-deep);color:var(--w-bg)}
.wrseg{display:flex;flex-wrap:wrap;gap:4px}
.wrseg button{font-size:13px;padding:5px 12px;background:var(--w-water)}
.wradar{position:relative;border-radius:16px;overflow:hidden;background:#0b1820;min-height:120px}
.wradar img{display:block;width:100%;height:auto}
.wrview{position:absolute;left:10px;top:10px;background:rgba(8,30,45,.78);color:#fff;font-weight:700;font-size:13px;padding:5px 12px;border-radius:999px}
.wrzoom{position:absolute;right:10px;top:10px;display:flex;flex-direction:column;border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.35)}
.wrzoom button{width:42px;height:42px;border:0;background:#fff;color:#12344a;font-family:inherit;font-weight:700;font-size:26px;line-height:1;cursor:pointer}
.wrzoom button+button{border-top:1px solid #d5dde2}
.wrzoom button[disabled]{color:#a9b7c0;cursor:default}
.wrbar{display:flex;align-items:center;gap:10px;font-size:13px}
.wrbar button{font-family:inherit;font-weight:700;font-size:13px;padding:5px 14px;border-radius:999px;border:1px solid var(--w-line);background:none;color:inherit;cursor:pointer}
.wrbar .t{font-weight:700}
.wrbar .n{color:var(--w-soft)}
.wwf{display:block;width:100%;height:460px;border:0;border-radius:16px}
#weather button:focus-visible,#weather a:focus-visible{outline:3px solid var(--w-pink);outline-offset:2px}
@media (max-width:520px){.wnow .big{font-size:56px}.whead{font-size:32px}.wwf{height:380px}}
#explore{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch}
.xwrap{max-width:760px;margin:0 auto;padding:14px 16px 60px;display:flex;flex-direction:column;gap:12px}
.xchips{display:flex;gap:8px;flex-wrap:wrap}
.xchips button{border:1.5px solid var(--line);background:transparent;color:var(--ink);border-radius:999px;padding:7px 14px;font:700 13px inherit;cursor:pointer}
.xchips button[aria-pressed=true]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.xcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
.xcard{border:1.5px solid var(--line);border-radius:12px;padding:12px 14px;text-align:left;background:transparent;color:var(--ink);cursor:pointer;font:inherit;display:flex;flex-direction:column;gap:4px}
.xcard .k{font-size:11px;letter-spacing:.08em;text-transform:uppercase;opacity:.6}
.xcard .n{font-weight:800;font-size:16px;line-height:1.2}
.xcard .m{font-size:13px;opacity:.75}
.xcard .a{font-size:13px}
.xcard.ok{border-left:4px solid #2e9e5b}
.xcard.look{border-left:4px solid #d9a300}
.xcard.no{border-left:4px solid #8d9aa5}
#xdlg{border:0;border-radius:16px;padding:0;max-width:min(560px,calc(100vw - 32px));width:100%;background:var(--bg);color:var(--ink);box-shadow:0 10px 30px rgba(0,0,0,.3)}
#xdlg::backdrop{background:rgba(10,25,35,.55)}
.xsheet{padding:22px;display:flex;flex-direction:column;gap:10px}
.xsheet h2{font-size:22px;margin:0;line-height:1.15}
.xsheet .k{font-size:12px;letter-spacing:.06em;text-transform:uppercase;opacity:.6}
.xsheet dl{display:grid;grid-template-columns:auto 1fr;gap:4px 14px;margin:0;font-size:14px}
.xsheet dt{opacity:.65;font-weight:700}
.xsheet dd{margin:0}
.xsheet p{margin:0;font-size:15px}
.xsheet .acts{display:flex;gap:10px;flex-wrap:wrap;margin-top:6px}
.xsheet .acts a,.xsheet .acts button{border:0;border-radius:999px;padding:9px 16px;font:700 14px inherit;cursor:pointer;background:var(--accent);color:var(--accent-ink);text-decoration:none}
.xsheet .acts button{background:transparent;border:1.5px solid var(--line);color:var(--ink)}
.xsheet .src{font-size:12px;opacity:.6}
</style></head><body><div id="app">
<header><h1>Bermuda Hub</h1><small>updated {{STAMP}}</small>
<div class="seg" role="group"><button data-p="planner" aria-pressed="true">What's on</button><button data-p="deals" aria-pressed="false">Deals</button><button data-p="list" aria-pressed="false">List</button><button data-p="weather" aria-pressed="false">Weather</button><button data-p="explore" aria-pressed="false">Explore</button></div></header>
<iframe id="f" src="planner.html" title="page"></iframe>
<section id="explore" hidden><div class="xwrap" id="xp"><p class="lnote">Nothing to explore in this build yet.</p></div>
<dialog id="xdlg"><div class="xsheet" id="xsheet"></div></dialog></section>
<section id="weather" hidden><div class="wwrap" id="wx"><p class="lnote">No weather in this build yet.</p></div></section>
<section id="list" hidden>
  <div class="lwrap">
    <p class="lnote" id="lstatus">Loading the shared list...</p>
    <form id="ladd" autocomplete="off"><input id="lname" placeholder="Add something (e.g. bananas)" maxlength="80" required><select id="lstore"><option value="">Any store</option><option>MarketPlace</option><option>Lindo's</option><option>Supermart</option><option>Miles</option><option>Pronto</option><option>Price Rite</option><option>Arnold's</option></select><button type="submit">Add</button></form>
    <div id="litems"></div>
    <div class="lbtns"><button type="button" id="lclear">Clear ticked</button><button type="button" id="lclearall" class="ghost">Clear all</button></div>
    <h2>This week's best buys</h2>
    <p class="lnote" id="lbestnote"></p>
    <div id="lbest"></div>
  </div>
</section>
<script>
const f=document.getElementById('f');
const listSec=document.getElementById('list'), wxSec=document.getElementById('weather'), xpSec=document.getElementById('explore');
function go(p){const isList=p==='list', isWx=p==='weather', isXp=p==='explore';listSec.hidden=!isList;wxSec.hidden=!isWx;xpSec.hidden=!isXp;f.hidden=isList||isWx||isXp;if(!isList&&!isWx&&!isXp)f.src=p+'.html';document.querySelectorAll('.seg button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.p===p?'true':'false'));try{localStorage.setItem('hub-page',p)}catch(e){}location.hash=p}
document.querySelector('.seg').addEventListener('click',e=>{const b=e.target.closest('button');if(b)go(b.dataset.p)});
window.addEventListener('message',e=>{const u=e.data&&e.data.hubOpen;if(typeof u!=='string'||!/^https?:/i.test(u))return;const a=document.createElement('a');a.href=u;a.target='_blank';a.rel='noopener';document.body.appendChild(a);a.click();a.remove()});
let p='planner';try{p=localStorage.getItem('hub-page')||p}catch(e){}
if(['#deals','#planner','#list','#weather','#explore'].includes(location.hash))p=location.hash.slice(1);
go(p);

// ---- Explore tab: forts, wrecks, abandoned places
(function(){
  let X={};try{X=JSON.parse(document.getElementById('explore-data').textContent.replace(/<\\\\\\//g,'</'))}catch(e){}
  const el=document.getElementById('xp'); if(!X||!X.sites||!X.sites.length)return;
  const esc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const kinds=X.kinds||{}; let kind='all';
  const cls=s=>/^(no\b|not |closed|private|by boat only, no|not open|not accessible)/i.test(s.access)?'no':/look only|from a boat|from the ferry|from the harbour|visible from|seen from|^dive/i.test(s.access+' '+s.kids)?'look':'ok';
  function render(){
    const list=X.sites.filter(s=>kind==='all'||s.kind===kind);
    el.innerHTML='<div class="xchips"><button data-k="all" aria-pressed="'+(kind==='all')+'">All ('+X.sites.length+')</button>'+Object.keys(kinds).map(k=>'<button data-k="'+k+'" aria-pressed="'+(kind===k)+'">'+esc(kinds[k])+' ('+X.sites.filter(s=>s.kind===k).length+')</button>').join('')+'</div>'
      +'<p class="lnote">Green: you can go. Amber: see it from outside or the water, or it is a dive. Grey: closed or private. Tap a card for the story and how to get there.</p>'
      +'<div class="xcards">'+list.map((s,i)=>'<button type="button" class="xcard '+cls(s)+'" data-id="'+esc(s.id)+'"><span class="k">'+esc(kinds[s.kind]||s.kind)+' · '+esc(s.parish)+'</span><span class="n">'+esc(s.name)+'</span><span class="m">'+esc(s.era)+'</span><span class="a">'+esc(s.kids)+'</span></button>').join('')+'</div>'
      +'<p class="wsrc">'+esc(X.note||'')+'</p>';
  }
  render();
  el.addEventListener('click',e=>{
    const c=e.target.closest('.xchips button');if(c){kind=c.dataset.k;render();return}
    const card=e.target.closest('.xcard');if(!card)return;
    const s=X.sites.find(x=>x.id===card.dataset.id);if(!s)return;
    const dlg=document.getElementById('xdlg'), sh=document.getElementById('xsheet');
    sh.innerHTML='<span class="k">'+esc(kinds[s.kind]||s.kind)+' · '+esc(s.parish)+'</span><h2>'+esc(s.name)+'</h2><dl><dt>When</dt><dd>'+esc(s.era)+'</dd><dt>Getting there</dt><dd>'+esc(s.access)+'</dd><dt>With kids</dt><dd>'+esc(s.kids)+'</dd><dt>Look for</dt><dd>'+esc(s.see)+'</dd></dl><p>'+esc(s.story)+'</p>'
      +'<div class="acts"><a href="https://www.google.com/maps?q='+encodeURIComponent(s.lat+','+s.lon)+'" target="_blank" rel="noopener">Map'+(s.approx?' (approximate)':'')+'</a><button type="button" id="xclose">Close</button></div>'
      +'<p class="src">'+(s.links||[]).map(l=>'<a href="'+esc(l[1])+'" target="_blank" rel="noopener">'+esc(l[0])+'</a>').join(' · ')+'</p>';
    try{dlg.showModal()}catch(x){dlg.setAttribute('open','')}
    document.getElementById('xclose').onclick=()=>dlg.close();
  });
  document.getElementById('xdlg').addEventListener('click',e=>{if(e.target.id==='xdlg')e.target.close()});
})();

// ---- Weather tab, from the Bermuda Weather Service pages the laptop fetched this morning
(function(){
  let W={};try{W=JSON.parse(document.getElementById('weather-data').textContent.replace(/<\\\\\\//g,'</'))}catch(e){}
  const el=document.getElementById('wx'); if(!W||!W.forecast||!W.forecast.length)return;
  const esc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const arrow=d=>'↑↗→↘↓↙←↖'[Math.round(((d||0)%360)/45)%8];
  const now=new Date(); const pad=n=>String(n).padStart(2,'0');
  const nowKey=now.getFullYear()+'-'+pad(now.getMonth()+1)+'-'+pad(now.getDate())+'T'+pad(now.getHours());
  let h=[];
  if(W.hourly){const i=W.hourly.findIndex(r=>r.t.slice(0,13)>=nowKey);h=W.hourly.slice(Math.max(0,i),Math.max(0,i)+24);}
  const hr=t=>{const n=+t.slice(11,13);return n===0?'12am':n<12?n+'am':n===12?'12pm':(n-12)+'pm'};
  const today=W.forecast[0]||{}, tonight=W.forecast[1]||{};
  const sun=(W.days&&W.days[0])||{};
  const todayIso=now.getFullYear()+'-'+pad(now.getMonth()+1)+'-'+pad(now.getDate());
  const tides=(W.tides||[]).filter(d=>d.date>=todayIso).slice(0,4);
  // The picture at the top, Harbour Road at dusk: two rows of Bermuda cottages with white stepped roofs on a hillside,
  // a moongate, a hibiscus hedge, palms and the harbour, under a striped setting sun. The sky follows the latest
  // airport report and the time of day in Bermuda (rain streaks, a moon and lit windows at night).
  const bdaNow=now.toLocaleTimeString('en-GB',{timeZone:'Atlantic/Bermuda',hour:'2-digit',minute:'2-digit'});
  const skyTxt=((W.now&&W.now.sky)||(today.lines||[]).join(' ')||'').toLowerCase();
  const night=!!(sun.sunrise&&sun.sunset&&(bdaNow<sun.sunrise||bdaNow>sun.sunset));
  const mood=night?'night':/rain|shower|drizzle|thunder/.test(skyTxt)?'rain':/overcast|cloud|fog|mist|haze/.test(skyTxt)?'cloud':'sun';
  function scene(){
    const dark=night||mood==='rain', f=n=>(+n).toFixed(1);
    // one Bermuda cottage: pastel wall with a shaded side, white stepped hip roof, chimney, top hinged shutters, arched door
    const house=(x,base,w,h,col,shade)=>{
      const side=w*0.28, rh=h*0.62, ov=5, top=base-h, rx0=x-ov, rx1=x+w+ov, px0=x+w*0.24, px1=x+w*0.9, ry=top-rh, sx=x+w+side+ov;
      let s='<rect x="'+x+'" y="'+top+'" width="'+w+'" height="'+h+'" fill="'+col+'"/><rect x="'+(x+w)+'" y="'+top+'" width="'+f(side)+'" height="'+h+'" fill="'+shade+'"/>';
      s+='<path d="M'+rx0+' '+top+' L'+f(px0)+' '+f(ry)+' L'+f(px1)+' '+f(ry)+' L'+rx1+' '+top+' Z" fill="#fffdf8"/><path d="M'+rx1+' '+top+' L'+f(px1)+' '+f(ry)+' L'+f(sx)+' '+top+' Z" fill="#e9dff2"/>';
      for(let i=1;i<5;i++){const t=i/5, yy=top-rh*t;s+='<path d="M'+f(rx0+(px0-rx0)*t)+' '+f(yy)+' L'+f(rx1+(px1-rx1)*t)+' '+f(yy)+' L'+f(sx+(px1-sx)*t)+' '+f(yy)+'" stroke="#cdbfe0" stroke-width="1.1" fill="none"/>';}
      s+='<rect x="'+rx0+'" y="'+(top-1.5)+'" width="'+(w+2*ov)+'" height="3.4" fill="#fffdf8"/><rect x="'+rx0+'" y="'+(top+1.9)+'" width="'+(w+2*ov)+'" height="1.6" fill="'+shade+'" opacity=".7"/>';
      const cx=x+w*0.66;
      s+='<path d="M'+f(cx)+' '+f(ry+rh*0.42)+' L'+f(cx+2)+' '+f(ry-rh*0.2)+' L'+f(cx+11)+' '+f(ry-rh*0.2)+' L'+f(cx+13)+' '+f(ry+rh*0.42)+' Z" fill="#fffdf8"/><rect x="'+f(cx)+'" y="'+f(ry-rh*0.2-3)+'" width="13" height="3.5" fill="#fffdf8"/>';
      const pane=dark?'#ffe27a':'#3a1f6e', ww=w*0.17, wh=h*0.36, wy=base-h*0.74;
      for(const wx of [x+w*0.13,x+w*0.70]){
        s+='<rect x="'+f(wx-1.5)+'" y="'+f(wy-1.5)+'" width="'+f(ww+3)+'" height="'+f(wh+3)+'" fill="#fffdf8"/><rect x="'+f(wx)+'" y="'+f(wy)+'" width="'+f(ww)+'" height="'+f(wh)+'" fill="'+pane+'"/>';
        s+='<path d="M'+f(wx-2)+' '+f(wy-1)+' L'+f(wx+ww+2)+' '+f(wy-1)+' L'+f(wx+ww+4)+' '+f(wy+wh*0.42)+' L'+f(wx-4)+' '+f(wy+wh*0.42)+' Z" fill="#1c8f8a"/>';
      }
      const dw=w*0.17, dx=x+w*0.415, dh=h*0.56;
      s+='<path d="M'+f(dx)+' '+base+' V'+f(base-dh+dw/2)+' A'+f(dw/2)+' '+f(dw/2)+' 0 0 1 '+f(dx+dw)+' '+f(base-dh+dw/2)+' V'+base+' Z" fill="#fffdf8"/><path d="M'+f(dx+2)+' '+base+' V'+f(base-dh+dw/2+1)+' A'+f(dw/2-2)+' '+f(dw/2-2)+' 0 0 1 '+f(dx+dw-2)+' '+f(base-dh+dw/2+1)+' V'+base+' Z" fill="#1c8f8a"/>';
      return s;
    };
    const palm=(x,y,h,lean,sw)=>{
      const tx=x+lean*h*0.22, ty=y-h;
      let p='<path d="M'+x+' '+y+' Q'+f(x+lean*h*0.02)+' '+f(y-h*0.55)+' '+f(tx)+' '+f(ty)+'" stroke="#1a0b3a" stroke-width="'+sw+'" fill="none" stroke-linecap="round"/>';
      for(const [dx,dy] of [[-.42,.06],[-.34,-.18],[-.1,-.3],[.2,-.26],[.42,-.04],[.36,.2],[-.3,.22]])
        p+='<path d="M'+f(tx)+' '+f(ty)+' Q'+f(tx+dx*h*0.5)+' '+f(ty+dy*h-h*0.14)+' '+f(tx+dx*h)+' '+f(ty+dy*h+h*0.1)+' Q'+f(tx+dx*h*0.55)+' '+f(ty+dy*h+h*0.02)+' '+f(tx)+' '+f(ty+4)+' Z" fill="#1a0b3a"/>';
      return p;
    };
    // sky: the big striped sun going down behind the houses, a moon at night, pink streaks in the rain
    let b='';
    if(mood==='sun'||mood==='cloud'){
      b+='<defs><linearGradient id="wsg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff27a"/><stop offset="1" stop-color="#ff4fa3"/></linearGradient><clipPath id="wsc"><circle cx="420" cy="210" r="92"/></clipPath></defs><g clip-path="url(#wsc)"'+(mood==='cloud'?' opacity=".55"':'')+'>';
      let y=118, band=38.6, gap=2;
      while(y<302){b+='<rect x="328" y="'+f(y)+'" width="184" height="'+f(band)+'" fill="url(#wsg)"/>';y+=band+gap;band=Math.max(4,band*0.78);gap+=1.5;}
      b+='</g>';
    }
    if(mood==='night')b+='<circle cx="600" cy="70" r="40" fill="#ff4fa3" opacity=".16"/><circle cx="600" cy="70" r="24" fill="#fdf3ff"/>';
    if(mood==='rain'){for(let i=0;i<30;i++){const rx=24+i*25, ry=20+((i*47)%130);b+='<line x1="'+rx+'" y1="'+ry+'" x2="'+(rx-8)+'" y2="'+(ry+20)+'" stroke="#ffb3e6" stroke-width="1.6" stroke-linecap="round" opacity=".55"/>';}}
    b+='<path d="M0 222 Q120 176 260 196 T520 186 T760 200 V300 H0 Z" fill="#4a1d7a"/>';
    for(const h of [[60,214,46,26,'#ffc7dd','#d79ab8'],[150,206,40,24,'#fff1b8','#d9c98a'],[246,210,44,26,'#b9f3e4','#8fcab9'],[560,204,42,24,'#c5e4ff','#98b9d9'],[650,212,46,26,'#ffc7dd','#d79ab8']])b+='<g opacity=".85">'+house(...h)+'</g>';
    b+='<path d="M0 252 Q90 214 200 232 T420 236 T640 226 T760 238 V300 H0 Z" fill="#2c1160"/>';
    for(const h of [[96,250,84,50,'#ff8fb5','#d9608c'],[236,254,74,46,'#ffe37a','#d9b84a'],[372,256,90,54,'#7ff0d8','#4fc1ab'],[520,252,78,48,'#ffb08a','#d98562'],[640,256,70,44,'#9fd3ff','#6fa6d9']])b+=house(...h);
    b+='<path d="M326 258 A20 21 0 1 1 356 258" fill="none" stroke="#e9dff2" stroke-width="7"/><path d="M326 258 A20 21 0 1 1 356 258" fill="none" stroke="#b9a8d6" stroke-width="7" stroke-dasharray="1.2 6"/>';
    for(let x=0;x<760;x+=38)b+='<ellipse cx="'+(x+14)+'" cy="262" rx="26" ry="10" fill="#1d6b57"/><circle cx="'+(x+6)+'" cy="258" r="2.6" fill="#ff4fa3"/><circle cx="'+(x+24)+'" cy="261" r="2.2" fill="#ff7ab8"/>';
    b+=palm(34,268,100,1,6)+palm(726,268,160,-1,7)+palm(470,262,96,1,5);
    const sea=dark?['#16b9c9','#12b0c4','#1b2a7a']:['#2af0d9','#2af0d9','#0b6fa8'];
    b+='<defs><linearGradient id="wse" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="'+sea[1]+'"/><stop offset="1" stop-color="'+sea[2]+'"/></linearGradient></defs><rect y="268" width="760" height="32" fill="url(#wse)"/>';
    let d='M0 266';for(let i=0;i<8;i++)d+=' q47.5 -4 95 0';
    b+='<path d="'+d+' V276 H0 Z" fill="'+sea[0]+'"/>';
    if(mood==='sun'||mood==='cloud')[[360,120],[340,160],[380,90],[350,130]].forEach((r,i)=>{b+='<rect x="'+r[0]+'" y="'+(276+i*6)+'" width="'+r[1]+'" height="2" fill="#fff27a" opacity="'+f(0.6-i*0.12)+'"/>'});
    b+='<rect y="298" width="760" height="2" fill="#ff4fa3"/>';
    return '<svg class="wscene" viewBox="0 0 760 300" preserveAspectRatio="xMidYMax slice" aria-hidden="true">'+b+'</svg>';
  }
  // ---- Derived readings for the extra cards: the model row for this hour, feels like, comfort, daytime outlook, seas.
  const cur=h[0]||{};
  const num=t=>{const m=String(t==null?'':t).match(/-?[0-9]+(?:[.][0-9]+)?/);return m?+m[0]:null};
  const tNow=cur.temp!=null?cur.temp:num(W.now&&W.now.temp), rhNow=cur.rh!=null?cur.rh:num(W.now&&W.now.rh);
  const obsKt=(()=>{const m=String((W.now&&W.now.wind)||'').match(/([0-9]+) ?KT/i);return m?+m[1]:null})();
  const ktNow=cur.wind!=null?cur.wind:obsKt;
  const vap=(tNow!=null&&rhNow!=null)?rhNow/100*6.105*Math.exp(17.27*tNow/(237.7+tNow)):null;
  const feels=cur.feels!=null?cur.feels:(vap!=null?tNow+0.33*vap-0.70*(ktNow||0)*0.5144-4:null);
  const dew=cur.dew!=null?cur.dew:(vap!=null?237.7*Math.log(vap/6.105)/(17.27-Math.log(vap/6.105)):null);
  const comfort=dew==null?'':dew<13?'crisp':dew<16?'comfortable':dew<19?'a little humid':dew<22?'sticky':dew<24?'muggy':'oppressive';
  const pts16=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
  const t12h=t=>{const hh=+t.slice(0,2);return (hh%12||12)+':'+t.slice(3,5)+(hh<12?' am':' pm')};
  const hm=t=>(+t.slice(0,2))*60+(+t.slice(3,5));
  // daytime rows still to come today; after sunset, tomorrow's daytime
  const bdaDay=now.toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'});
  const late=!!(sun.sunset&&bdaNow>sun.sunset);
  const dayIso=late&&W.days&&W.days[1]?W.days[1].date:bdaDay;
  const dayRows=(W.hourly||[]).filter(r=>r.t.slice(0,10)===dayIso&&+r.t.slice(11,13)>=7&&+r.t.slice(11,13)<=18&&(late||r.t.slice(11,13)>=bdaNow.slice(0,2)));
  const mx=(k)=>dayRows.length?Math.max(...dayRows.map(r=>r[k]==null?0:r[k])):null;
  const dWind=mx('wind'), dRain=mx('rain'), dUv=mx('uv'), dTemp=mx('temp');
  const marineTxt=((W.marine&&W.marine.periods&&W.marine.periods[late?1:0])||{lines:[]}).lines.join(' ');
  const reef=w=>{const m=marineTxt.match(new RegExp(w+' the reef ([0-9]+)(?: to ([0-9]+))? ?ft','i'));return m?[+m[1],+(m[2]||m[1])]:null};
  const seaIn=reef('inside'), seaOut=reef('outside');
  const warned=(W.warnings||[]).some(w=>/small craft|gale|storm|hurricane/i.test(w.title||''));
  // 1. What the rain is doing over the coming hours, from the hourly model
  const rainLine=(()=>{
    if(!h.length||h[0].rain==null)return '';
    const p=h[0].rain, at=r=>hr(r.t).replace('am',' am').replace('pm',' pm');
    if(p>=55){const e=h.find(r=>r.rain<35);return 'Rain likely this hour ('+p+'%)'+(e?', easing around '+at(e)+'.':', and staying that way into tomorrow.');}
    if(p<35){const e=h.find(r=>r.rain>=55);return e?'Dry for now. Showers more likely from '+at(e)+'.':'Dry for now, and nothing much on the way in the next 24 hours.';}
    const e=h.find(r=>r.rain<35), u=h.find(r=>r.rain>=55);
    return 'A shower is possible this hour ('+p+'%)'+(u?', more likely from '+at(u)+'.':e?', clearing up around '+at(e)+'.':'.');
  })();
  // 7. Go, maybe or skip for five things people actually plan around
  const acts=(()=>{
    if(dWind==null)return [];
    const so=seaOut?seaOut[1]:null, si=seaIn?seaIn[1]:null, W_=Math.round(dWind), R_=Math.round(dRain||0);
    const v=(skip,maybe,why)=>({v:skip?'skip':maybe?'maybe':'go',why:why});
    return [
      ['Beach',v(R_>=60||W_>=22,R_>=35||W_>=15||(dTemp!=null&&dTemp<21),R_>=35?R_+'% chance of rain':W_>=15?'wind to '+W_+' kt':'light wind, mostly dry')],
      ['Boat',v(warned||W_>=20||(so!=null&&so>=8),W_>=13||(so!=null&&so>=5),warned?'warning in force':so!=null?so+' ft outside the reef, '+W_+' kt':'wind to '+W_+' kt')],
      ['Snorkel',v((si!=null&&si>=3)||W_>=18,(si!=null&&si>=2)||W_>=12,si!=null?si+' ft inside the reef':'wind to '+W_+' kt')],
      ['Run',v((feels!=null&&feels>=32)||R_>=70,R_>=40||(dew!=null&&dew>=22),R_>=40?R_+'% chance of rain':comfort?comfort+' air':'fine')],
      ['Laundry',v(R_>=50,R_>=30,R_+'% chance of rain')]];
  })();
  const word={go:'Go',maybe:'Maybe',skip:'Skip'};
  // 3, 4, 6, 11. Four small dials: wind, sun, UV, moon
  function dials(){
    let o='';
    if(ktNow!=null){const d=cur.dir!=null?cur.dir:null, nm=d!=null?pts16[Math.round(d/22.5)%16]:String((W.now&&W.now.wind)||'').split(' ')[0];
      o+='<div class="wdial"><h3>Wind</h3><svg viewBox="0 0 120 120" role="img" aria-label="Wind from '+esc(nm)+' at '+Math.round(ktNow)+' knots"><circle cx="60" cy="60" r="50" fill="none" stroke="#4b2d8a" stroke-width="2"/>'+
        [['N',60,20],['E',104,64],['S',60,108],['W',16,64]].map(a=>'<text x="'+a[1]+'" y="'+a[2]+'" text-anchor="middle" font-size="11" font-weight="800" fill="#cdbbea">'+a[0]+'</text>').join('')+
        (d!=null?'<g transform="rotate('+(d+180)+' 60 60)"><path d="M60 96 V34" stroke="#2af0d9" stroke-width="4" stroke-linecap="round"/><path d="M60 18 L70 38 H50 Z" fill="#2af0d9"/></g>':'')+
        '<circle cx="60" cy="60" r="21" fill="#241552"/><text x="60" y="62" text-anchor="middle" font-size="19" font-weight="800" fill="#fff">'+Math.round(ktNow)+'</text><text x="60" y="74" text-anchor="middle" font-size="9" font-weight="700" fill="#cdbbea">kt</text></svg><p>From the '+esc(nm)+(cur.gust!=null?', gusts '+Math.round(cur.gust)+' kt':'')+'</p></div>';}
    if(sun.sunrise&&sun.sunset){const a=hm(sun.sunrise), b=hm(sun.sunset), n=hm(bdaNow), fr=Math.min(1,Math.max(0,(n-a)/(b-a))), ang=Math.PI*(1-fr), sx=60+48*Math.cos(ang), sy=84-48*Math.sin(ang), up=n>=a&&n<=b, left=b-n;
      o+='<div class="wdial"><h3>Sun</h3><svg viewBox="0 0 120 100" role="img" aria-label="Sunrise '+t12h(sun.sunrise)+', sunset '+t12h(sun.sunset)+'"><path d="M12 84 A48 48 0 0 1 108 84" fill="none" stroke="#4b2d8a" stroke-width="2" stroke-dasharray="3 5"/><path d="M4 84 H116" stroke="#ff4fa3" stroke-width="2"/>'+
        (up?'<circle cx="'+sx.toFixed(1)+'" cy="'+sy.toFixed(1)+'" r="15" fill="#ffb25e" opacity=".3"/><circle cx="'+sx.toFixed(1)+'" cy="'+sy.toFixed(1)+'" r="9" fill="#fff27a"/>':'<circle cx="60" cy="92" r="9" fill="#fff27a" opacity=".35"/>')+
        '<text x="12" y="98" text-anchor="middle" font-size="9" font-weight="700" fill="#cdbbea">'+t12h(sun.sunrise).replace(' am','')+'</text><text x="108" y="98" text-anchor="middle" font-size="9" font-weight="700" fill="#cdbbea">'+t12h(sun.sunset).replace(' pm','')+'</text></svg><p>'+
        (up?Math.floor(left/60)+' h '+(left%60)+' min of daylight left':n<a?'Sunrise at '+t12h(sun.sunrise):'Sun is down. Up again at '+t12h((W.days&&W.days[1]&&W.days[1].sunrise)||sun.sunrise))+'</p></div>';}
    const uvRows=(W.hourly||[]).filter(r=>r.t.slice(0,10)===bdaDay&&r.uv!=null), uvMax=uvRows.length?Math.max(...uvRows.map(r=>r.uv)):num(today.uv);
    if(uvMax!=null){const hot=uvRows.filter(r=>r.uv>=3), cat=uvMax<3?'Low':uvMax<6?'Moderate':uvMax<8?'High':uvMax<11?'Very high':'Extreme', px=10+100*Math.min(11,uvMax)/11;
      o+='<div class="wdial"><h3>UV</h3><svg viewBox="0 0 120 100" role="img" aria-label="UV index peaks at '+Math.round(uvMax)+', '+cat+'"><defs><linearGradient id="wuv" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2af0d9"/><stop offset=".35" stop-color="#fff27a"/><stop offset=".65" stop-color="#ffb25e"/><stop offset="1" stop-color="#ff4fa3"/></linearGradient></defs><text x="60" y="46" text-anchor="middle" font-size="34" font-weight="800" fill="#fff">'+Math.round(uvMax)+'</text><text x="60" y="62" text-anchor="middle" font-size="11" font-weight="700" fill="#cdbbea">'+cat+'</text><rect x="10" y="76" width="100" height="8" rx="4" fill="url(#wuv)"/><circle cx="'+px.toFixed(1)+'" cy="80" r="7" fill="#fff" stroke="#241552" stroke-width="3"/></svg><p>'+
        (hot.length?'Sunscreen from '+hr(hot[0].t).replace('am',' am').replace('pm',' pm')+' to '+hr(String(hot[hot.length-1].t).slice(0,11)+pad(+hot[hot.length-1].t.slice(11,13)+1)+':00').replace('am',' am').replace('pm',' pm'):'No sunscreen needed today')+'</p></div>';}
    {const P=29.530588853, age=((Date.now()/86400000-10962.76)%P+P)%P, fr=age/P, lit=(1-Math.cos(2*Math.PI*fr))/2, R=30, rx=(R*Math.abs(Math.cos(2*Math.PI*fr))).toFixed(1);
      const name=fr<0.03||fr>0.97?'New moon':fr<0.22?'Waxing crescent':fr<0.28?'First quarter':fr<0.47?'Waxing gibbous':fr<0.53?'Full moon':fr<0.72?'Waning gibbous':fr<0.78?'Last quarter':'Waning crescent';
      const path=fr<0.5?'M60 20 A30 30 0 0 1 60 80 A'+rx+' 30 0 0 '+(fr<0.25?0:1)+' 60 20 Z':'M60 20 A30 30 0 0 0 60 80 A'+rx+' 30 0 0 '+(fr>0.75?1:0)+' 60 20 Z';
      const toFull=((P/2-age)%P+P)%P, toNew=P-age, nextIsFull=toFull<toNew, dd=new Date(Date.now()+(nextIsFull?toFull:toNew)*86400000);
      o+='<div class="wdial"><h3>Moon</h3><svg viewBox="0 0 120 100" role="img" aria-label="'+name+', '+Math.round(lit*100)+' percent lit"><circle cx="60" cy="50" r="38" fill="#ff4fa3" opacity=".12"/><circle cx="60" cy="50" r="30" fill="#3a2a6e"/><path d="'+path+'" fill="#fdf3ff"/></svg><p>'+name+', '+Math.round(lit*100)+'% lit. '+(nextIsFull?'Full':'New')+' moon '+dd.toLocaleDateString('en-GB',{timeZone:'Atlantic/Bermuda',weekday:'short',day:'numeric',month:'short'})+'</p></div>';}
    return o?'<div class="wdials">'+o+'</div>':'';
  }
  // 9. Sea state at a glance, from the BWS marine forecast
  function seaCard(){
    if(!seaIn&&!seaOut)return '';
    const bar=(lab,v)=>v?'<div class="wsea"><span>'+lab+'</span><div class="trk"><i style="width:'+Math.min(100,v[1]/12*100).toFixed(0)+'%"></i></div><b>'+(v[0]===v[1]?v[1]:v[0]+' to '+v[1])+' ft</b></div>':'';
    return '<div class="wcard sea wseac"><h3>Sea state '+(late?'tonight':'today')+'</h3>'+bar('Inside the reef',seaIn)+bar('Outside the reef',seaOut)+'<p>'+(W.climate&&W.climate.sea_surface?'Water '+esc(W.climate.sea_surface.split('/')[0].trim().replace(' C','°C'))+'. ':'')+(warned?'A marine warning is in force.':'No marine warnings.')+'</p></div>';
  }
  // 8. Rain for the tank: month so far, and what that is off a roof
  function tankCard(){
    const mm=num(W.climate&&W.climate.rain_month); if(mm==null)return '';
    const gal=Math.round(mm*24.54), mname=now.toLocaleDateString('en-GB',{timeZone:'Atlantic/Bermuda',month:'long'});
    return '<h2 class="w">Rain for the tank</h2><div class="wcard wtank"><div class="big">'+mm+' mm</div><p>'+(mm/25.4).toFixed(2)+' inches at the airport so far in '+mname+'. That is roughly '+gal.toLocaleString('en-US')+' US gallons caught by every 1,000 square feet of roof.</p></div>';
  }
  // Tide graph: the rise and fall at St George's over today and tomorrow, drawn from the BWS high and low times
  // (a smooth curve between each high and low), with a line at the time now in Bermuda.
  function tideGraph(){
    const bdaDate=now.toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'});
    const dayNo=s=>Math.round(Date.UTC(+s.slice(0,4),+s.slice(5,7)-1,+s.slice(8,10))/86400000);
    const d0=dayNo(bdaDate), ev=[];
    for(const d of (W.tides||[]))for(const e of d.events){const m=(dayNo(d.date)-d0)*1440+(+e.time.slice(0,2))*60+(+e.time.slice(3,5));ev.push({m:m,ft:+e.ft,kind:e.kind,time:e.time});}
    ev.sort((a,b)=>a.m-b.m);
    const SPAN=2880, inwin=ev.filter(e=>e.m>=0&&e.m<=SPAN);
    if(ev.length<3||inwin.length<3)return '';
    const hAt=m=>{for(let i=0;i<ev.length-1;i++){const a=ev[i],b=ev[i+1];if(m>=a.m&&m<=b.m)return a.ft+(b.ft-a.ft)*(1-Math.cos(Math.PI*(m-a.m)/(b.m-a.m)))/2;}return null};
    const VW=720, VH=222, L=10, R=710, T=44, B=146;
    const lo=Math.min(...ev.map(e=>e.ft))-0.2, hi=Math.max(...ev.map(e=>e.ft))+0.2;
    const X=m=>L+(R-L)*m/SPAN, Y=ft=>B-(B-T)*(ft-lo)/(hi-lo);
    const t12=t=>{const hh=+t.slice(0,2);return (hh%12||12)+':'+t.slice(3,5)+(hh<12?' am':' pm')};
    let pts=[];
    for(let m=0;m<=SPAN;m+=10){const v=hAt(m);if(v!=null)pts.push([X(m),Y(v)]);}
    if(pts.length<2)return '';
    const line='M'+pts.map(p=>p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' L');
    let s='<svg viewBox="0 0 '+VW+' '+VH+'" role="img" aria-label="Tide height at St George&#39;s over today and tomorrow">';
    s+='<defs><linearGradient id="wtg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2af0d9" stop-opacity=".55"/><stop offset="1" stop-color="#2af0d9" stop-opacity=".04"/></linearGradient></defs>';
    const names=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'], wd=new Date(bdaDate+'T12:00:00Z').getUTCDay();
    for(let k=0;k<=8;k++){const m=k*360, x=X(m), hh=(k*6)%24, lab=hh===0?(k===8?'':names[(wd+k/4)%7]):hh===6?'6 am':hh===12?'noon':'6 pm';
      s+='<path d="M'+x.toFixed(1)+' '+(T-14)+' V'+(B+8)+'" stroke="#fdf3ff" stroke-width="'+(hh===0?1.2:0.6)+'" opacity="'+(hh===0?0.45:0.18)+'"/>';
      if(lab)s+='<text x="'+(x+(hh===0?4:0)).toFixed(1)+'" y="'+(VH-10)+'" text-anchor="'+(hh===0?'start':'middle')+'" font-size="12" font-weight="'+(hh===0?800:600)+'" fill="'+(hh===0?'#fdf3ff':'#cdbbea')+'">'+lab+'</text>';}
    s+='<path d="'+line+' L'+pts[pts.length-1][0].toFixed(1)+' '+(B+8)+' L'+pts[0][0].toFixed(1)+' '+(B+8)+' Z" fill="url(#wtg)"/>';
    s+='<path d="'+line+'" fill="none" stroke="#2af0d9" stroke-width="7" opacity=".25" stroke-linecap="round"/><path d="'+line+'" fill="none" stroke="#2af0d9" stroke-width="2.6" stroke-linecap="round"/>';
    for(const e of inwin){const x=Math.min(R-34,Math.max(L+34,X(e.m))), y=Y(e.ft), up=e.kind==='High';
      s+='<circle cx="'+X(e.m).toFixed(1)+'" cy="'+y.toFixed(1)+'" r="4.5" fill="'+(up?'#fff27a':'#ff4fa3')+'"/>';
      s+='<text x="'+x.toFixed(1)+'" y="'+(up?y-22:y+19).toFixed(1)+'" text-anchor="middle" font-size="12" font-weight="800" fill="#fdf3ff">'+t12(e.time)+'</text>';
      s+='<text x="'+x.toFixed(1)+'" y="'+(up?y-9:y+32).toFixed(1)+'" text-anchor="middle" font-size="11" font-weight="600" fill="#cdbbea">'+(up?'High ':'Low ')+e.ft+' ft</text>';}
    const nm=(+bdaNow.slice(0,2))*60+(+bdaNow.slice(3,5)), nv=hAt(nm);
    let cap='';
    if(nv!=null){const later=hAt(nm+20), dir=later==null?'':later>nv?'rising':'falling', nx=X(nm);
      s+='<path d="M'+nx.toFixed(1)+' '+(T-14)+' V'+(B+8)+'" stroke="#ff4fa3" stroke-width="2"/><circle cx="'+nx.toFixed(1)+'" cy="'+Y(nv).toFixed(1)+'" r="6" fill="#ff4fa3" stroke="#fff" stroke-width="2"/>';
      s+='<text x="'+Math.min(R-20,Math.max(L+20,nx)).toFixed(1)+'" y="'+(T-20)+'" text-anchor="middle" font-size="12" font-weight="800" fill="#ff4fa3">Now</text>';
      const nxt=ev.find(e=>e.m>nm);
      cap='About '+nv.toFixed(1)+' ft and '+dir+' now'+(nxt?', '+nxt.kind.toLowerCase()+' tide at '+t12(nxt.time):'')+'.';}
    s+='</svg>';
    if(sun.sunrise&&sun.sunset){const a=hm(sun.sunrise), b=hm(sun.sunset), lowDay=ev.find(e=>e.kind==='Low'&&e.m>nm&&e.m<SPAN&&(e.m%1440)>=a&&(e.m%1440)<=b);
      if(lowDay)cap+=' Most sand showing at the beach: '+t12(lowDay.time)+(lowDay.m>=1440?' tomorrow':' today')+' ('+lowDay.ft+' ft).';}
    return '<div class="wtg"><div class="wtgs">'+s+'</div><p class="wsrc">'+cap+' Heights between the listed highs and lows are a smooth estimate, not a measurement.</p></div>';
  }
  let html='';
  for(const w of (W.warnings||[]))html+='<div class="wwarn">'+esc(w.title)+(w.valid?'<small>'+esc(w.valid)+'</small>':'')+'</div>';
  if(W.now&&W.now.temp){
    const bits=[];
    if(feels!=null)bits.push('Feels like '+Math.round(feels)+'°'+(comfort?' and '+comfort:''));
    bits.push('wind '+esc(W.now.wind),'humidity '+esc(W.now.rh));
    if(W.climate&&W.climate.sea_surface)bits.push('sea '+esc(W.climate.sea_surface.split('/')[0]));
    html+='<div class="whero '+mood+'"><div class="wnow"><span class="big">'+esc((W.now.temp.split('/')[0]||'').replace('°C','°'))+'</span><span class="sky">'+esc(W.now.sky)+'</span><span class="meta">'+bits.join(', ')+'<br>At the airport, '+esc(W.now.time)+'</span></div>'+scene()+'</div>';
  }
  if(W.headline)html+='<div class="whead">'+esc(W.headline)+'</div>';
  if(rainLine)html+='<p class="wnext">'+esc(rainLine)+'</p>';
  if(acts.length)html+='<div class="wacts" role="list" aria-label="'+(late?'Tomorrow':'Today')+' at a glance">'+acts.map(a=>'<div class="wact '+a[1].v+'" role="listitem"><b>'+a[0]+'</b><span class="v">'+word[a[1].v]+'</span><span class="y">'+esc(a[1].why)+'</span></div>').join('')+'</div>';
  html+='<div id="wradar"></div>';
  if(W.synopsis)html+='<p class="wsyn">'+esc(W.synopsis)+'</p>';
  html+='<div class="wcards">';
  for(const [p,cls] of [[today,'day'],[tonight,'eve']]){ if(!p.label)continue; html+='<div class="wcard '+cls+'"><h3>'+esc(p.label)+'</h3><div class="hl">'+esc(p.high?'High '+p.high:'')+esc(p.low?(p.high?', ':'')+'Low '+p.low:'')+(p.uv?', UV '+esc(p.uv):'')+'</div><p>'+esc((p.lines||[]).join(' '))+'</p></div>'; }
  html+='</div>';
  if(h.length){html+='<h2 class="w">Next 24 hours</h2><div class="wstrip">'+h.map((r,i)=>'<div class="whr'+(i===0?' now':'')+'"><div>'+hr(r.t)+'</div><div class="t">'+Math.round(r.temp)+'°</div><div class="r">'+(r.rain!=null?r.rain+'%':'')+'</div><div class="w">'+Math.round(r.wind)+' '+arrow(r.dir)+'</div></div>').join('')+'</div><p class="wsrc">Rain chance and wind in knots from the Open-Meteo model. The words on this page are the Bermuda Weather Service, which is the one to trust when they disagree.</p>';}
  html+=dials();
  const week=W.forecast.slice(2);
  if(week.length){html+='<h2 class="w">The week</h2><div class="wweek">'+week.map(p=>'<div class="wday"><span class="d">'+esc(p.label)+'</span><span class="tx">'+esc((p.lines||[])[0]||'')+'</span><span class="hl">'+esc(p.high?p.high.split(' / ')[0]:'')+(p.low?' / '+esc(p.low.split(' / ')[0]):'')+'</span></div>').join('')+'</div>';}
  if(W.marine&&W.marine.periods&&W.marine.periods.length){html+='<h2 class="w">On the water</h2>'+(W.marine.synopsis?'<p class="wsyn">'+esc(W.marine.synopsis)+'</p>':'')+'<div class="wcards">'+seaCard()+W.marine.periods.slice(0,3).map(p=>'<div class="wcard sea"><h3>'+esc(p.label)+'</h3><p>'+esc((p.lines||[]).join(' '))+'</p></div>').join('')+'</div>';}
  if(tides.length){html+='<h2 class="w">Tides at St George&#39;s</h2>'+tideGraph()+'<div class="wtides">'+tides.map(d=>'<div class="wtide"><b>'+esc(d.day)+'</b>'+d.events.map(e=>'<div class="'+(e.kind==='High'?'hi':'')+'">'+esc(e.kind)+' '+esc(e.time)+' <span style="opacity:.6">'+esc(e.ft)+' ft</span></div>').join('')+'</div>').join('')+'</div>';}
  html+=tankCard()+'<div id="wtropics"></div>';
  const CAMS=[['Hamilton Harbour, RHADC','https://www.webcamtaxi.com/en/bermuda/paget-parish/rhadc-hamilton-harbor-cam.html'],['St George&#39;s Harbour','https://www.skylinewebcams.com/webcam/bermuda/st-george-s-parish/st-george-s-parish/st-george-s-harbour.html'],['King&#39;s Square, St George&#39;s','https://www.skylinewebcams.com/webcam/bermuda/st-george-s-parish/st-george-s-parish/st-george-s-town-square-bermuda.html']];
  html+='<h2 class="w">Live cameras</h2><div class="wlinks">'+CAMS.map(c=>'<a href="'+c[1]+'" target="_blank" rel="noopener">'+c[0]+' ↗</a>').join('')+'</div>';
  if(W.radar&&W.radar.links)html+='<h2 class="w">More from the weather service</h2><div class="wlinks">'+W.radar.links.map(l=>'<a href="'+esc(l.url)+'" target="_blank" rel="noopener">'+esc(l.name)+' ↗</a>').join('')+'</div>';
  html+='<p class="wsrc">Bermuda Weather Service forecast issued '+esc(W.issued)+(W.next_update?', next update '+esc(W.next_update):'')+'. Collected '+esc(W.asof)+'.</p>';
  el.innerHTML=html;
  // ---- Live map panel, GitHub Pages copy only (the artifact viewer blocks outside pictures and frames, so that copy
  // keeps the links). One panel, two modes: Radar (Bermuda Weather Service pictures) and Windy (forecast map).
  // BWS names each radar frame by its UTC time and drops old ones, so the page works out the recent names itself
  // and keeps the ones that load. Plus zooms in toward the parishes, minus zooms out to 500 km.
  const box=document.getElementById('wradar'), host=location.hostname;
  if(box&&(host.endsWith('github.io')||host==='localhost'||host==='127.0.0.1'||location.protocol==='file:')){
    const BASE='https://weather.bm/images/';
    const VIEWS=[
      {k:'parish',label:'Parishes',dir:'Radar/RadarParish/',suf:'_ParishRadar.png',step:6,ph:1,note:'Rainfall radar over the parishes'},
      {k:'sat',label:'Satellite',dir:'Satellite/LocalVisIRRadarSferic/',suf:'_SAT004.jpeg',step:5,ph:0,note:'Satellite cloud with radar and lightning'},
      {k:'r100',label:'100 km',dir:'Radar/CurrentRadarAnimation_100km_sri/',suf:'_100km_sri.png',step:6,ph:1,note:'Rainfall radar, 100 km'},
      {k:'r250',label:'250 km',dir:'Radar/CurrentRadarAnimation_250km_sri/',suf:'_250km_sri.png',step:6,ph:1,note:'Rainfall radar, 250 km'},
      {k:'r500',label:'500 km',dir:'Radar/CurrentRadarAnimation_500km_dBZ_0deg/',suf:'_500km_dBz_0deg.png',step:6,ph:0,note:'Radar reflectivity, 500 km'}];
    const LAYERS=[['wind','Wind'],['gust','Gusts'],['rain','Rain'],['waves','Waves']];
    const windySrc=o=>'https://embed.windy.com/embed.html?type=map&location=coordinates&metricRain=default&metricTemp=default&metricWind=kt&zoom=8&overlay='+o+'&product=ecmwf&level=surface&lat=32.31&lon=-64.76&message=true';
    const stampAt=d=>{const s=d.toISOString();return s.slice(0,10)+'-'+s.slice(11,13)+s.slice(14,16)};
    const probe=u=>new Promise(res=>{const im=new Image();im.onload=()=>res(im.naturalWidth>1?u:null);im.onerror=()=>res(null);im.src=u});
    const clock=u=>{const n=u.slice(u.lastIndexOf('/')+1);const d=new Date(n.slice(0,10)+'T'+n.slice(11,13)+':'+n.slice(13,15)+':00Z');
      return d.toLocaleTimeString('en-US',{timeZone:'Atlantic/Bermuda',hour:'numeric',minute:'2-digit'}).toLowerCase()};
    const keep=(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}}, recall=k=>{try{return localStorage.getItem(k)}catch(e){return null}};
    const $=id=>document.getElementById(id);
    let vi=Math.max(0,VIEWS.findIndex(v=>v.k===recall('hub-radar-view')));
    let mode=recall('hub-map-mode')==='windy'?'windy':'radar';
    let layer=LAYERS.some(l=>l[0]===recall('hub-windy-layer'))?recall('hub-windy-layer'):'wind';
    let frames=[], i=0, playing=true, timer=null, started=false, token=0;
    async function find(v){
      const all=[];for(let k=0;k<75;k++){const d=new Date(Date.now()-k*60000);all.push({u:BASE+v.dir+stampAt(d)+v.suf,m:d.getUTCMinutes()});}
      let hits=(await Promise.all(all.filter(x=>x.m%v.step===v.ph).map(x=>probe(x.u)))).filter(Boolean);
      if(hits.length<2)hits=(await Promise.all(all.map(x=>probe(x.u)))).filter(Boolean);
      return Array.from(new Set(hits)).sort().slice(-10);
    }
    function show(){
      $('wrimg').src=frames[i];
      $('wrtime').textContent=clock(frames[i]);
      $('wrn').textContent=(i+1)+' of '+frames.length;
    }
    function tick(){
      clearTimeout(timer); if(!playing||mode!=='radar'||frames.length<2)return;
      i=(i+1)%frames.length; show();
      timer=setTimeout(tick,i===frames.length-1?1800:500);
    }
    function shell(){
      box.innerHTML='<div class="wmap"><div class="wmtog" role="group" aria-label="Map"><button type="button" data-m="radar">Radar</button><button type="button" data-m="windy">Windy</button></div>'+
        '<div id="wmradar"><div class="wradar"><img id="wrimg" alt=""><span class="wrview" id="wrview"></span><div class="wrzoom"><button type="button" id="wrin" aria-label="Zoom in" title="Zoom in">+</button><button type="button" id="wrout" aria-label="Zoom out" title="Zoom out">−</button></div></div>'+
        '<div class="wrbar" style="margin-top:10px"><button id="wrplay" type="button">Pause</button><span class="t" id="wrtime"></span><span class="n" id="wrn"></span></div></div>'+
        '<div id="wmwindy" hidden><div class="wrseg" role="group" aria-label="Windy layer" style="margin-bottom:10px">'+LAYERS.map(l=>'<button type="button" data-o="'+l[0]+'">'+l[1]+'</button>').join('')+'</div><iframe class="wwf" id="wwf" title="Windy forecast map for Bermuda"></iframe></div>'+
        '<p class="wsrc" id="wrnote"></p></div>';
      box.querySelector('.wmtog').addEventListener('click',e=>{const b=e.target.closest('button[data-m]');if(!b)return;mode=b.dataset.m;keep('hub-map-mode',mode);paint()});
      $('wrin').addEventListener('click',()=>{if(vi>0){vi--;keep('hub-radar-view',VIEWS[vi].k);load()}});
      $('wrout').addEventListener('click',()=>{if(vi<VIEWS.length-1){vi++;keep('hub-radar-view',VIEWS[vi].k);load()}});
      $('wrplay').addEventListener('click',e=>{playing=!playing;e.target.textContent=playing?'Pause':'Play';if(playing)tick();else clearTimeout(timer)});
      $('wmwindy').addEventListener('click',e=>{const b=e.target.closest('button[data-o]');if(!b)return;layer=b.dataset.o;keep('hub-windy-layer',layer);paint(true)});
    }
    function paint(force){
      if(!$('wrimg'))shell();
      box.querySelectorAll('.wmtog button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.m===mode?'true':'false'));
      $('wmradar').hidden=mode!=='radar'; $('wmwindy').hidden=mode!=='windy';
      if(mode==='windy'){
        clearTimeout(timer);
        box.querySelectorAll('#wmwindy button[data-o]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.o===layer?'true':'false'));
        const f=$('wwf'); if(force||!f.getAttribute('src'))f.src=windySrc(layer);
        $('wrnote').textContent='Forecast model map from Windy.com. Press play on the map to run the days ahead. For rain falling right now, switch to Radar.';
      }else load();
    }
    async function load(){
      const v=VIEWS[vi], mine=++token;
      $('wrview').textContent=v.label; $('wrin').disabled=vi===0; $('wrout').disabled=vi===VIEWS.length-1;
      $('wrnote').textContent='Loading '+v.label+'...';
      const got=await find(v);
      if(mine!==token||mode!=='radar')return;
      clearTimeout(timer);
      if(!got.length){$('wrnote').textContent='No '+v.label+' pictures from the Bermuda Weather Service in the last hour. Zoom in or out, or use the links at the bottom of the page.';return;}
      frames=got; i=frames.length-1; show();
      $('wrimg').alt=v.note+', Bermuda Weather Service';
      $('wrnote').textContent=v.note+' from the Bermuda Weather Service, last hour, newest picture held longest. Plus zooms in, minus zooms out.';
      if(playing)timer=setTimeout(tick,1800);
    }
    function tropics(){
      const tb=$('wtropics'), mth=+now.toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'}).slice(5,7); if(!tb)return;
      if(mth<6||mth>11){tb.innerHTML='<h2 class="w">Tropics</h2><p class="wsyn">Hurricane season runs from 1 June to 30 November. Nothing to track right now.</p>';return;}
      tb.innerHTML='<h2 class="w">Tropics</h2><a class="wtrop" href="https://www.nhc.noaa.gov/gtwo.php?basin=atlc&amp;fdays=7" target="_blank" rel="noopener"><img alt="National Hurricane Center seven day tropical weather outlook for the Atlantic" loading="lazy" src="https://www.nhc.noaa.gov/xgtwo/two_atl_7d0.png?h='+Math.floor(Date.now()/3600000)+'"></a><p class="wsrc">Seven day outlook from the US National Hurricane Center, updated about every six hours in season. Tap the map for the full discussion.</p>';
    }
    const wait=setInterval(()=>{
      if(wxSec.hidden||started)return;
      started=true; clearInterval(wait); paint(); tropics();
      setInterval(()=>{if(!document.hidden&&!wxSec.hidden&&mode==='radar')load()},6*60000);
    },400);
  }
})();

// ---- Shared grocery list (artifact db capability). Works for anyone invited who can write; read only otherwise.
(function(){
  const status=document.getElementById('lstatus'), items=document.getElementById('litems'), bestEl=document.getElementById('lbest');
  const BEST=(()=>{try{return JSON.parse(document.getElementById('best-buys').textContent.replace(/<\\\\\\//g,'</'))}catch(e){return {asof:'',items:[]}}})();
  document.getElementById('lbestnote').textContent=BEST.items.length?('From the deals page'+(BEST.asof?' ('+BEST.asof+')':'')+'. Tap + to add one to the list.'):'No best buys in this build yet.';
  let db=null, canWrite=false, rows=[];
  const esc=t=>String(t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  function renderBest(){
    bestEl.innerHTML=BEST.items.map((b,i)=>'<div class="bcard"><div class="b"><div class="t">'+esc(b.name)+'</div><div class="s">'+esc(b.store)+' $'+esc(b.price)+' '+esc(b.unit)+'</div><div class="w">'+esc(b.why)+'</div></div><button type="button" data-i="'+i+'" aria-label="Add to list"'+(canWrite?'':' disabled')+'>+</button></div>').join('');
  }
  function render(){
    if(!rows.length){items.innerHTML='<p class="lnote">Nothing on the list.</p>';return}
    const groups={};
    for(const r of rows){(groups[r.store||'Any store']=groups[r.store||'Any store']||[]).push(r)}
    items.innerHTML=Object.keys(groups).sort().map(g=>'<div class="lgroup"><h3>'+esc(g)+'</h3>'+groups[g].map(r=>'<div class="litem'+(r.done?' done':'')+'" data-id="'+esc(r.id)+'"><input type="checkbox"'+(r.done?' checked':'')+(canWrite?'':' disabled')+' aria-label="Done"><span class="n">'+esc(r.name)+'</span>'+(r.note?'<span class="p">'+esc(r.note)+'</span>':'')+(canWrite?'<button class="x" type="button" aria-label="Remove">&times;</button>':'')+'</div>').join('')+'</div>').join('');
  }
  renderBest(); render();
  async function start(){
    if(!window.claude||typeof claude.use!=='function'){status.textContent='The shared list only works on the published Hub link (not the local copy).';return}
    db=await claude.use('db');
    if(!db){status.textContent='Sign in to the Hub link to see the shared list.';return}
    const user=await claude.use('user');
    const cw=user?await user.can('data.write'):null;
    canWrite=cw!==false;  // null: not told, keep the inputs and let a refused write decide
    if(!canWrite)status.textContent='You can see the list but not change it (ask Matt to share the Hub with you as an Editor).';
    renderBest(); render();
    let timer=setTimeout(()=>{status.textContent='The list cannot be reached yet; it may be out of date.'},10000);
    db.collection('list').orderBy('ts').limit(300).onSnapshot(snap=>{
      rows=snap.docs.map(d=>Object.assign({id:d.id},d.data()));
      if(!snap.metadata.fromCache){clearTimeout(timer);status.textContent=canWrite?'Shared with everyone who has the Hub. Tick things off as you shop.':status.textContent}
      render();
    },e=>{clearTimeout(timer);status.textContent='The shared list is unavailable right now.';});
  }
  async function add(name,store,note){
    if(!db||!name)return;
    try{await db.collection('list').add({name:name.slice(0,80),store:store||'',note:note||'',done:false,ts:Date.now()})}
    catch(e){if(e&&e.code==='invalid_argument'){canWrite=false;status.textContent='You can see the list but not change it (ask Matt to share the Hub with you as an Editor).';renderBest();render()}else status.textContent='Could not add that just now.'}
  }
  document.getElementById('ladd').addEventListener('submit',async e=>{e.preventDefault();const n=document.getElementById('lname');const v=n.value.trim();if(!v)return;n.value='';await add(v,document.getElementById('lstore').value,'')});
  bestEl.addEventListener('click',async e=>{const b=e.target.closest('button[data-i]');if(!b)return;const it=BEST.items[+b.dataset.i];b.disabled=true;await add(it.name,it.store,'$'+it.price+' '+it.unit);b.disabled=!canWrite});
  items.addEventListener('change',async e=>{const cb=e.target;if(cb.type!=='checkbox'||!db)return;const id=cb.closest('.litem').dataset.id;try{await db.doc('list/'+id).update({done:cb.checked})}catch(x){}});
  items.addEventListener('click',async e=>{const x=e.target.closest('.x');if(!x||!db)return;const id=x.closest('.litem').dataset.id;try{await db.doc('list/'+id).delete()}catch(y){}});
  document.getElementById('lclear').addEventListener('click',async()=>{if(!db)return;for(const r of rows.filter(r=>r.done)){try{await db.doc('list/'+r.id).delete()}catch(e){}}});
  document.getElementById('lclearall').addEventListener('click',async()=>{if(!db||!rows.length||!confirm('Clear the whole list?'))return;for(const r of rows){try{await db.doc('list/'+r.id).delete()}catch(e){}}});
  start();
})();
</script></div></body></html>
"""


def main(argv: list[str]) -> int:
    os.makedirs(SITE, exist_ok=True)
    build_only = "--build" in argv
    want_deals = "--deals" in argv or "--all" in argv or not any(a in argv for a in ("--events",))
    want_events = "--events" in argv or "--all" in argv or (dt.date.today().weekday() in EVENT_DAYS and "--deals" not in argv)
    log("=== hub run %s ===" % " ".join(argv))
    if want_deals:
        deals(collect=not build_only)
    if want_events:
        events(collect=not build_only)
    elif not build_only:
        # not a planner day: still refresh the weather and re-render (today's date, cinema board unchanged)
        db = os.path.join(EVENTS, "data", "tidewatch.sqlite")
        if os.path.exists(db):
            run(["-m", "tidewatch", "weather"], EVENTS, "weather")
            run(["-m", "tidewatch", "render"], EVENTS, "events render")
        else:
            events(collect=False)
    elif not os.path.exists(os.path.join(SITE, "planner.html")):
        events(collect=False)
    front_door()
    backup()
    publish_github()
    log("hub done")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
