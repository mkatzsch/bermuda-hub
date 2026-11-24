"""Bermuda Hub yoga probe: saves the public schedule pages of the two studios whose timetables sit in a booking app.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.1
Last Updated: 2026-11-22

Change Log
  1.1 2026-11-22  The first run showed both studios' TeamUp pages are empty shells that ask TeamUp's own data
                  service for the timetable. This run reads the page's program file to list the data addresses
                  it uses, then tries the events address for each studio and saves what comes back.
  1.0 2026-11-22  First release. A one off test, so the right reader can be written for run.py.

What it does
  Fetches a handful of web addresses for Shamana Circle and Salt Yoga (their own schedule pages and the TeamUp
  booking pages behind them) and saves exactly what comes back, so it can be checked whether Python can read the
  timetables without a browser.

Depends on
  The internet. Python's standard library only.

Writes
  .cache/yoga_probe/  one file per address, plus index.txt listing each address, its status and size.
  The .cache folder is ignored by git.

Run
  In the terminal: .\\yoga_probe.bat
"""
import os
import re
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, ".cache", "yoga_probe")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
PAGES = [
    ("salt_home", "https://www.salt-yoga.bm/"),
    ("salt_schedule", "https://www.salt-yoga.bm/class-schedule"),
    ("salt_teamup", "https://goteamup.com/p/7577870-salt-yoga-bermuda/"),
    ("salt_teamup_events", "https://goteamup.com/p/7577870-salt-yoga-bermuda/e/schedule/"),
    ("shamana_schedule", "https://shamanacirclestudio.com/pages/schedule"),
    ("shamana_home", "https://shamanacirclestudio.com/"),
]


def get(url: str) -> tuple:
    """(status, final address, body) for one page. Never raises: a failure comes back as status 0 and the reason."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.geturl(), r.read()
    except Exception as e:
        return 0, url, ("%s: %s" % (type(e).__name__, e)).encode("utf-8")


STUDIOS = {"salt": "7577870", "shamana": "7167098"}  # the provider numbers in each studio's TeamUp address


def get_json(url: str, provider: str) -> tuple:
    """(status, body) from TeamUp's data service, asked the way the public customer page asks. Never raises."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json", "TeamUp-Provider-ID": provider,
                                                   "TeamUp-Request-Mode": "customer", "Referer": "https://goteamup.com/"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:2000]
    except Exception as e:
        return 0, ("%s: %s" % (type(e).__name__, e)).encode("utf-8")


def probe_api(lines: list) -> None:
    """List the data addresses named in TeamUp's page program, then try the events address for each studio."""
    import datetime as dt
    shell = ""
    p = os.path.join(OUT, "salt_teamup.html")
    if os.path.exists(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            shell = f.read()
    m = re.search(r"https://teamupstatic\.com/static/js/dist/[^\"']+consumer[^\"']+\.js", shell)
    if m:
        status, final, body = get(m.group(0))
        js = body.decode("utf-8", "replace")
        paths = sorted(set(re.findall(r"[\"'`](/?api/v[0-9]/[A-Za-z0-9_\-/${}.]*)", js)))
        heads = sorted(set(re.findall(r"TeamUp-[A-Za-z\-]+", js)))
        with open(os.path.join(OUT, "api_paths.txt"), "w", encoding="utf-8") as f:
            f.write("program file: %s, status %s, %d bytes\n\nheaders named:\n%s\n\ndata addresses named:\n%s\n" % (m.group(0), status, len(body), "\n".join(heads), "\n".join(paths)))
        lines.append("program file read: %d data addresses and %d header names listed in api_paths.txt" % (len(paths), len(heads)))
    today = dt.date.today()
    a, b = today.isoformat(), (today + dt.timedelta(days=7)).isoformat()
    tries = [("events_a", "https://goteamup.com/api/v2/events?starts_after=%sT00:00:00&starts_before=%sT23:59:59&page_size=200&expand=instructors,venue,offering_type,category" % (a, b)),
             ("events_b", "https://goteamup.com/api/v2/events?starts_at_after=%s&starts_at_before=%s&page_size=200" % (a, b)),
             ("events_c", "https://goteamup.com/api/v2/events?page_size=50")]
    for studio, pid in STUDIOS.items():
        for name, url in tries:
            status, body = get_json(url, pid)
            with open(os.path.join(OUT, "%s_%s.json" % (studio, name)), "wb") as f:
                f.write(body)
            lines.append("%s %s | status %s | %d bytes | %s" % (studio, name, status, len(body), url))
            print(lines[-1][:150])


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    lines, extra = [], []
    for name, url in PAGES:
        status, final, body = get(url)
        with open(os.path.join(OUT, name + ".html"), "wb") as f:
            f.write(body)
        text = body.decode("utf-8", "replace")
        found = sorted(set(re.findall(r"https://goteamup\.com/[^\"'<> )]+", text)))
        lines.append("%s | %s | status %s | %d bytes | ended at %s" % (name, url, status, len(body), final))
        for u in found[:12]:
            lines.append("    mentions %s" % u)
            if "/p/" in u and all(u != x[1] for x in PAGES + extra) and len(extra) < 4 and "shamana" in name:
                extra.append(("shamana_teamup_%d" % (len(extra) + 1), u))
        print(lines[-1 - min(len(found), 12)])
    for name, url in extra:  # follow the TeamUp addresses the Shamana pages point to
        status, final, body = get(url)
        with open(os.path.join(OUT, name + ".html"), "wb") as f:
            f.write(body)
        lines.append("%s | %s | status %s | %d bytes | ended at %s" % (name, url, status, len(body), final))
        print(lines[-1])
    probe_api(lines)
    with open(os.path.join(OUT, "index.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("Saved %d pages to %s" % (len(PAGES) + len(extra), OUT))


if __name__ == "__main__":
    main()
