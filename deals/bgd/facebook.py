"""Facebook page sweep: reads the newest public post of every store, farm, shop and restaurant page signed out
and writes data/<date>/facebook.json, so the weekly model step only summarises text instead of browsing.

Developed by AiTide Ltd. | www.AiTide.com
Version: 1.0
Last Updated: 2026-11-17

Change Log
  1.0  2026-11-17  First release. Playwright Chromium, signed out, one tab reused for every page. Reads the Posts
                   section text, expands "See more", records the post date, flags login walls and missing pages,
                   screenshots image-only posts into flyers/facebook/. Tiers (weekly, monthly, parked) decide
                   which pages are read on a given day.

Dependencies: playwright (pip install playwright, then: playwright install chromium). The page list lives in
config.json under "facebook" (see config_pages() for the shape). Writes data/<date>/facebook.json and
data/facebook_latest.json; screenshots go to flyers/facebook/<slug>.png.

Scheduling: weekly pages are read on Mondays and whenever collect.py is run with --facebook; monthly pages on the
first Monday of the month; parked pages on the first Monday of January, April, July and October. A page whose
"when" the weekly step moves between tiers only needs its "tier" changed in config.json.
"""
import os, re, json, datetime as dt
from .util import log, FLYERS, DATA, slug, save_json, load_json

# Lines Facebook adds around a post that carry no information
NOISE = ("Like", "Comment", "Share", "Privacy", "Terms", "Advertising", "Ad Choices", "Cookies", "More", "Meta",
         "See more from", "Email or phone number", "Password", "Log In", "Forgot password?", "or", "Create new account",
         "All reactions:", "View more comments", "See all photos", "Photos", "Intro", "About", "Reels", "Posts")
DATE_RX = re.compile(r"^(?:(?:Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day, )?(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}(?:, \d{4})?(?: at \d{1,2}:\d{2} [AP]M)?$|^\d+ (?:minute|hour|day|week)s? ago$|^\d+[hdw]$|^Yesterday")
MONTHS = {m: i for i, m in enumerate(("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"), 1)}


def due_tiers(d):
    """Which tiers are read on date d: weekly on Mondays, monthly on the first Monday, parked on the first Monday of a quarter."""
    tiers = set()
    if d.weekday() == 0:
        tiers.add("weekly")
        if d.day <= 7:
            tiers.add("monthly")
            if d.month in (1, 4, 7, 10):
                tiers.add("parked")
    return tiers


def parse_posted(line, d):
    """Turn a Facebook date line into an ISO date where possible."""
    m = re.match(r"^(\d+)\s*(minute|hour|day|week|m|h|d|w)", line)
    if m:
        n, u = int(m.group(1)), m.group(2)[0]
        days = {"m": 0, "h": 0, "d": n, "w": n * 7}[u]
        return (d - dt.timedelta(days=days)).isoformat()
    if line.startswith("Yesterday"):
        return (d - dt.timedelta(days=1)).isoformat()
    m = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2})(?:, (\d{4}))?", line)
    if m:
        y = int(m.group(3)) if m.group(3) else d.year
        try:
            p = dt.date(y, MONTHS[m.group(1)], int(m.group(2)))
        except ValueError:
            return None
        if not m.group(3) and p > d:
            p = p.replace(year=y - 1)
        return p.isoformat()
    return None


def clean(text):
    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        if not s or s in NOISE or s == "·" or s.startswith("See more from"):
            continue
        out.append(s)
    return out


def parse_body(body, d):
    """Split the signed-out page text into (status, posted ISO date, post lines)."""
    i = body.find("\nPosts\n")
    if i < 0:
        return "empty", None, [body[:300]]
    chunk = body[i:i + 4000]
    for marker in ("\nEmail or phone number", "\nSee more from ", "\nAll reactions:", "\nView more comments"):
        j = chunk.find(marker)
        if j > 0:
            chunk = chunk[:j]
    lines = clean(chunk)
    posted = None
    for k, ln in enumerate(lines):
        if DATE_RX.match(ln):
            # the first date line opens the newest post; an absolute date on the next line or two beats a relative one
            cand = [x for x in lines[k:k + 3] if DATE_RX.match(x)]
            absd = [x for x in cand if re.search(r"[A-Z][a-z]+ \d", x)]
            posted = parse_posted((absd or cand)[0], d)
            lines = lines[k + 1:]
            break
    lines = [ln for ln in lines if not DATE_RX.match(ln) and not re.match(r"^\d+$", ln)]
    return "ok", posted, lines


def read_page(page, url, d, shots_dir, name):
    """Read one page signed out. Returns a dict with status ok | login | notfound | empty | error."""
    rec = {"name": name, "url": url, "status": "error", "posted": None, "text": "", "lines": [], "shot": None}
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(5000)
        cur = page.url
        body = page.evaluate("document.body.innerText") or ""
        if "/login" in cur or body.lstrip().startswith("Log into Facebook") or "You must log in to continue" in body[:400]:
            rec["status"] = "login"; return rec
        if "This content isn't available" in body[:1500] or "This page isn't available" in body[:1500]:
            rec["status"] = "notfound"; return rec
        # expand the newest post
        try:
            page.evaluate("""[...document.querySelectorAll('div[role="button"]')].filter(e=>e.innerText.trim()==='See more').slice(0,3).forEach(e=>e.click())""")
            page.wait_for_timeout(1500)
            body = page.evaluate("document.body.innerText") or ""
        except Exception:
            pass
        status, posted, lines = parse_body(body, d)
        rec.update({"status": status, "posted": posted, "lines": lines[:40], "text": " ".join(lines[:40])[:1500]})
        if status != "ok":
            return rec
        if len(rec["text"]) < 60:
            # image-only post: keep a picture for the weekly read
            os.makedirs(shots_dir, exist_ok=True)
            f = os.path.join(shots_dir, slug(name) + ".png")
            page.screenshot(path=f, clip={"x": 0, "y": 0, "width": 1100, "height": 1600})
            rec["shot"] = os.path.relpath(f, os.path.dirname(DATA)).replace("/", "\\")
    except Exception as e:
        rec["status"] = "error"; rec["text"] = str(e)[:200]
    return rec


def run(cfg, d, force=False, only=None):
    """cfg is config.json["facebook"]: {"pages": [{"name", "url", "group", "tier"}]}. Returns the record written."""
    pages = (cfg or {}).get("pages") or []
    tiers = {"weekly", "monthly", "parked"} if force == "all" else (due_tiers(d) | ({"weekly"} if force else set()))
    todo = [p for p in pages if p.get("url") and (p.get("tier", "weekly") in tiers) and (not only or only.lower() in p["name"].lower())]
    skipped = [p["name"] for p in pages if not p.get("url")]
    out = {"read": d.isoformat(), "tiers": sorted(tiers), "pages": [], "no_url": skipped}
    if not todo:
        log("Facebook: nothing due today (tiers %s)" % (sorted(tiers) or "none"))
        return out
    from playwright.sync_api import sync_playwright
    shots = os.path.join(FLYERS, "facebook")
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        ctx = br.new_context(viewport={"width": 1100, "height": 1600}, locale="en-US",
                             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36")
        page = ctx.new_page()
        for p in todo:
            rec = read_page(page, p["url"], d, shots, p["name"])
            rec.update({"group": p.get("group", ""), "tier": p.get("tier", "weekly")})
            out["pages"].append(rec)
            log("Facebook %-40s %-8s %s" % (p["name"][:40], rec["status"], (rec["posted"] or "")))
        br.close()
    n_ok = sum(1 for r in out["pages"] if r["status"] == "ok")
    log("Facebook: %d of %d pages read (%d login walls, %d not found)" % (
        n_ok, len(todo), sum(1 for r in out["pages"] if r["status"] == "login"), sum(1 for r in out["pages"] if r["status"] == "notfound")))
    save_json(os.path.join(DATA, d.isoformat(), "facebook.json"), out)
    save_json(os.path.join(DATA, "facebook_latest.json"), out)
    return out
