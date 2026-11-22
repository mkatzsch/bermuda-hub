"""Bermuda Hub orchestrator: one scheduled run for the deals collector and the what's-on planner.

Developed by AiTide Ltd. | www.AiTide.com
Version: 1.11
Last Updated: 2026-11-22

Change Log
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
#weather{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch}
.wwrap{max-width:760px;margin:0 auto;padding:14px 16px 60px;display:flex;flex-direction:column;gap:14px}
.wwarn{background:#ffd166;color:#1b1b1f;border-radius:12px;padding:10px 14px;font-weight:700}
.wwarn small{display:block;font-weight:400;opacity:.8}
.wnow{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}
.wnow .big{font-size:46px;font-weight:800;letter-spacing:-.02em;line-height:1}
.wnow .sky{font-size:18px;font-weight:700}
.wnow .meta{opacity:.7;font-size:14px;width:100%}
.whead{font-size:20px;font-weight:800;line-height:1.2}
.wsyn{opacity:.8;font-size:14px;margin:0}
.wcards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px}
.wcard{border:1.5px solid var(--line);border-radius:12px;padding:12px 14px}
.wcard h3{margin:0 0 4px;font-size:13px;letter-spacing:.08em;text-transform:uppercase;opacity:.65}
.wcard .hl{font-weight:700;margin-bottom:4px}
.wcard p{margin:0;font-size:14px}
.wstrip{display:flex;gap:6px;overflow-x:auto;padding:4px 0 8px;-webkit-overflow-scrolling:touch}
.whr{flex:none;width:58px;text-align:center;border:1.5px solid var(--line);border-radius:10px;padding:6px 2px;font-size:12px}
.whr .t{font-weight:700;font-size:15px}
.whr .r{color:#0b6fb3;font-weight:700}
.whr .w{opacity:.75}
.whr.now{border-color:var(--accent);background:color-mix(in srgb,var(--accent) 12%,transparent)}
.wweek{display:flex;flex-direction:column}
.wday{display:grid;grid-template-columns:90px 1fr 70px;gap:10px;align-items:baseline;padding:8px 0;border-bottom:1px solid var(--line);font-size:14px}
.wday .d{font-weight:700}
.wday .hl{text-align:right;white-space:nowrap;font-weight:700}
.wday .tx{opacity:.85}
.wtides{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}
.wtide{border:1.5px solid var(--line);border-radius:10px;padding:8px 10px;font-size:13px}
.wtide b{display:block;margin-bottom:4px}
.wtide .hi{font-weight:700}
.wlinks a{display:inline-block;margin:0 10px 6px 0;color:var(--accent);font-weight:700;text-decoration:none}
h2.w{font-size:16px;margin:8px 0 0}
.wsrc{font-size:12px;opacity:.6}
.wradar{max-width:720px}
.wrseg{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.wrseg button{font:inherit;font-size:13px;font-weight:700;padding:5px 12px;border-radius:999px;border:1.5px solid var(--line);background:none;color:inherit;cursor:pointer}
.wrseg button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.wradar img{display:block;width:100%;height:auto;border-radius:12px;border:1.5px solid var(--line);background:#000}
.wrbar{display:flex;align-items:center;gap:10px;margin:6px 0 2px;font-size:13px}
.wrbar button{font:inherit;font-weight:700;padding:4px 12px;border-radius:999px;border:1.5px solid var(--line);background:none;color:inherit;cursor:pointer}
.wrbar .t{font-weight:700}
.wrbar .n{opacity:.6}
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
  const mToday=(W.marine&&W.marine.periods||[])[0]||{}, mTonight=(W.marine&&W.marine.periods||[])[1]||{};
  const sun=(W.days&&W.days[0])||{};
  const todayIso=now.getFullYear()+'-'+pad(now.getMonth()+1)+'-'+pad(now.getDate());
  const tides=(W.tides||[]).filter(d=>d.date>=todayIso).slice(0,4);
  let html='';
  for(const w of (W.warnings||[]))html+='<div class="wwarn">'+esc(w.title)+(w.valid?'<small>'+esc(w.valid)+'</small>':'')+'</div>';
  if(W.now&&W.now.temp)html+='<div class="wnow"><span class="big">'+esc((W.now.temp.split('/')[0]||'').replace('°C','°'))+'</span><span class="sky">'+esc(W.now.sky)+'</span><span class="meta">Wind '+esc(W.now.wind)+' · humidity '+esc(W.now.rh)+' · at the airport, '+esc(W.now.time)+(W.climate&&W.climate.sea_surface?' · sea '+esc(W.climate.sea_surface.split('/')[0]):'')+(sun.sunrise?' · sun '+esc(sun.sunrise)+' to '+esc(sun.sunset):'')+'</span></div>';
  if(W.headline)html+='<div class="whead">'+esc(W.headline)+'</div>';
  if(W.synopsis)html+='<p class="wsyn">'+esc(W.synopsis)+'</p>';
  html+='<div class="wcards">';
  for(const [p,label] of [[today,'Today'],[tonight,'Tonight']]){ if(!p.label)continue; html+='<div class="wcard"><h3>'+esc(p.label)+'</h3><div class="hl">'+esc(p.high?'High '+p.high:'')+esc(p.low?(p.high?' · ':'')+'Low '+p.low:'')+(p.uv?' · UV '+esc(p.uv):'')+'</div><p>'+esc((p.lines||[]).join(' '))+'</p></div>'; }
  html+='</div>';
  if(h.length){html+='<h2 class="w">Next 24 hours</h2><div class="wstrip">'+h.map((r,i)=>'<div class="whr'+(i===0?' now':'')+'"><div>'+hr(r.t)+'</div><div class="t">'+Math.round(r.temp)+'°</div><div class="r">'+(r.rain!=null?r.rain+'%':'')+'</div><div class="w">'+Math.round(r.wind)+' '+arrow(r.dir)+'</div></div>').join('')+'</div><p class="wsrc">Rain chance and wind in knots from the Open-Meteo model; the text above is the Bermuda Weather Service, which is the one to trust when they disagree.</p>';}
  const week=W.forecast.slice(2);
  if(week.length){html+='<h2 class="w">The week</h2><div class="wweek">'+week.map(p=>'<div class="wday"><span class="d">'+esc(p.label)+'</span><span class="tx">'+esc((p.lines||[])[0]||'')+'</span><span class="hl">'+esc(p.high?p.high.split(' / ')[0]:'')+(p.low?' / '+esc(p.low.split(' / ')[0]):'')+'</span></div>').join('')+'</div>';}
  if(W.marine&&W.marine.periods&&W.marine.periods.length){html+='<h2 class="w">On the water</h2>'+(W.marine.synopsis?'<p class="wsyn">'+esc(W.marine.synopsis)+'</p>':'')+'<div class="wcards">'+W.marine.periods.slice(0,3).map(p=>'<div class="wcard"><h3>'+esc(p.label)+'</h3><p>'+esc((p.lines||[]).join(' '))+'</p></div>').join('')+'</div>';}
  if(tides.length){html+='<h2 class="w">Tides at St George&#39;s</h2><div class="wtides">'+tides.map(d=>'<div class="wtide"><b>'+esc(d.day)+'</b>'+d.events.map(e=>'<div class="'+(e.kind==='High'?'hi':'')+'">'+esc(e.kind)+' '+esc(e.time)+' <span style="opacity:.6">'+esc(e.ft)+' ft</span></div>').join('')+'</div>').join('')+'</div>';}
  html+='<div id="wradar"></div>';
  if(W.radar&&W.radar.links)html+='<h2 class="w">Radar and satellite</h2><div class="wlinks">'+W.radar.links.map(l=>'<a href="'+esc(l.url)+'" target="_blank" rel="noopener">'+esc(l.name)+' ↗</a>').join('')+'</div>';
  html+='<p class="wsrc">Bermuda Weather Service forecast issued '+esc(W.issued)+(W.next_update?', next update '+esc(W.next_update):'')+'. Collected '+esc(W.asof)+'.</p>';
  el.innerHTML=html;
  // ---- Live radar and satellite, GitHub Pages copy only (the artifact viewer blocks outside images, so that copy
  // keeps the links). BWS names each frame by its UTC time and drops old ones, so the page works out the recent
  // names itself and keeps the ones that load. The buttons step outward: parish map, satellite, 100, 250, 500 km.
  const box=document.getElementById('wradar'), host=location.hostname;
  if(box&&(host.endsWith('github.io')||host==='localhost'||host==='127.0.0.1'||location.protocol==='file:')){
    const BASE='https://weather.bm/images/';
    const VIEWS=[
      {k:'parish',label:'Parishes',dir:'Radar/RadarParish/',suf:'_ParishRadar.png',step:6,ph:1,note:'Rainfall radar over the parishes'},
      {k:'sat',label:'Satellite',dir:'Satellite/LocalVisIRRadarSferic/',suf:'_SAT004.jpeg',step:5,ph:0,note:'Satellite cloud with radar and lightning'},
      {k:'r100',label:'100 km',dir:'Radar/CurrentRadarAnimation_100km_sri/',suf:'_100km_sri.png',step:6,ph:1,note:'Rainfall radar, 100 km'},
      {k:'r250',label:'250 km',dir:'Radar/CurrentRadarAnimation_250km_sri/',suf:'_250km_sri.png',step:6,ph:1,note:'Rainfall radar, 250 km'},
      {k:'r500',label:'500 km',dir:'Radar/CurrentRadarAnimation_500km_dBZ_0deg/',suf:'_500km_dBz_0deg.png',step:6,ph:0,note:'Radar reflectivity, 500 km'}];
    const stampAt=d=>{const s=d.toISOString();return s.slice(0,10)+'-'+s.slice(11,13)+s.slice(14,16)};
    const probe=u=>new Promise(res=>{const im=new Image();im.onload=()=>res(im.naturalWidth>1?u:null);im.onerror=()=>res(null);im.src=u});
    const clock=u=>{const n=u.slice(u.lastIndexOf('/')+1);const d=new Date(n.slice(0,10)+'T'+n.slice(11,13)+':'+n.slice(13,15)+':00Z');
      return d.toLocaleTimeString('en-US',{timeZone:'Atlantic/Bermuda',hour:'numeric',minute:'2-digit'}).toLowerCase()};
    let view=VIEWS[0], frames=[], i=0, playing=true, timer=null, started=false, token=0;
    try{const k=localStorage.getItem('hub-radar-view');view=VIEWS.find(v=>v.k===k)||view}catch(e){}
    async function find(v){
      const all=[];for(let k=0;k<75;k++){const d=new Date(Date.now()-k*60000);all.push({u:BASE+v.dir+stampAt(d)+v.suf,m:d.getUTCMinutes()});}
      let hits=(await Promise.all(all.filter(x=>x.m%v.step===v.ph).map(x=>probe(x.u)))).filter(Boolean);
      if(hits.length<2)hits=(await Promise.all(all.map(x=>probe(x.u)))).filter(Boolean);
      return Array.from(new Set(hits)).sort().slice(-10);
    }
    function show(){
      document.getElementById('wrimg').src=frames[i];
      document.getElementById('wrtime').textContent=clock(frames[i]);
      document.getElementById('wrn').textContent=(i+1)+' of '+frames.length;
    }
    function tick(){
      clearTimeout(timer); if(!playing||frames.length<2)return;
      i=(i+1)%frames.length; show();
      timer=setTimeout(tick,i===frames.length-1?1800:500);
    }
    function shell(){
      box.innerHTML='<h2 class="w">Live radar</h2><div class="wrseg" role="group">'+VIEWS.map(v=>'<button type="button" data-v="'+v.k+'">'+v.label+'</button>').join('')+'</div><div class="wradar"><img id="wrimg" alt=""><div class="wrbar"><button id="wrplay" type="button">Pause</button><span class="t" id="wrtime"></span><span class="n" id="wrn"></span></div></div><p class="wsrc" id="wrnote"></p>';
      box.querySelector('.wrseg').addEventListener('click',e=>{const b=e.target.closest('button[data-v]');if(!b)return;view=VIEWS.find(v=>v.k===b.dataset.v)||view;try{localStorage.setItem('hub-radar-view',view.k)}catch(x){}load()});
      document.getElementById('wrplay').addEventListener('click',e=>{playing=!playing;e.target.textContent=playing?'Pause':'Play';if(playing)tick();else clearTimeout(timer)});
    }
    async function load(){
      if(!document.getElementById('wrimg'))shell();
      const v=view, mine=++token;
      box.querySelectorAll('.wrseg button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.v===v.k?'true':'false'));
      document.getElementById('wrnote').textContent='Loading '+v.label+'...';
      const got=await find(v);
      if(mine!==token)return;
      clearTimeout(timer);
      if(!got.length){document.getElementById('wrnote').textContent='No '+v.label+' pictures from the Bermuda Weather Service in the last hour. Try another view or the links below.';return;}
      frames=got; i=frames.length-1; show();
      document.getElementById('wrimg').alt=v.note+', Bermuda Weather Service';
      document.getElementById('wrnote').textContent=v.note+' from the Bermuda Weather Service, last hour, newest picture held longest.';
      if(playing)timer=setTimeout(tick,1800);
    }
    const wait=setInterval(()=>{
      if(wxSec.hidden||started)return;
      started=true; clearInterval(wait); load();
      setInterval(()=>{if(!document.hidden&&!wxSec.hidden)load()},6*60000);
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
