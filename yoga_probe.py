"""Bermuda Hub yoga probe: saves the public schedule pages of the two studios whose timetables sit in a booking app.

Developed by AiTide Ltd. | www.AiTide.com
Version: 1.0
Last Updated: 2026-11-22

Change Log
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
    with open(os.path.join(OUT, "index.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("Saved %d pages to %s" % (len(PAGES) + len(extra), OUT))


if __name__ == "__main__":
    main()
