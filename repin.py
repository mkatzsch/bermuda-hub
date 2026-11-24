"""Bermuda Hub map check: looks up every Explore place still marked approximate on OpenStreetMap.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.0
Last Updated: 2026-11-22

Change Log
  1.0 2026-11-22  First release.

What it does: reads events/data/explore.json, takes each place with "approx": true (wrecks and street art
are skipped, since they are not on any map), and asks the OpenStreetMap search service for a place of that
name in Bermuda. It writes what it finds to events/data/repin_report.json. It changes nothing else: the
report is reviewed before any pin is moved.

Dependencies: Python standard library only. Needs the internet (nominatim.openstreetmap.org, one request
a second as their rules ask). Reads events/data/explore.json. Run it with repin.bat.
"""
import json, math, os, re, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "events", "data", "explore.json")
OUT = os.path.join(ROOT, "events", "data", "repin_report.json")
URL = "https://nominatim.openstreetmap.org/search?"
SKIP = {"wreck", "art"}


def metres(a, b, c, d):
    return int(math.hypot((a - c) * 111000, (b - d) * 94000))


def ask(q):
    url = URL + urllib.parse.urlencode({"q": q, "format": "jsonv2", "limit": 3, "countrycodes": "bm"})
    req = urllib.request.Request(url, headers={"User-Agent": "BermudaHub/1.0 (+https://github.com/mkatzsch/bermuda-hub)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def names(n):
    """The name as written, then shorter forms: before a comma, without brackets, without a leading 'The'."""
    out = [n]
    for v in (re.sub(r"\s*\(.*?\)", "", n), n.split(",")[0], re.sub(r"\s*\(.*?\)", "", n.split(",")[0])):
        v = re.sub(r"^The\s+", "", v.strip())
        if v and v not in out:
            out.append(v)
    return out


def main():
    with open(SRC, encoding="utf-8") as f:
        sites = json.load(f)["sites"]
    todo = [s for s in sites if s.get("approx") and s.get("kind") not in SKIP]
    print("Checking %d places. About %d minutes." % (len(todo), len(todo) * 2 // 60 + 1))
    rows = []
    for i, s in enumerate(todo, 1):
        row = {"id": s["id"], "name": s["name"], "lat": s["lat"], "lon": s["lon"], "found": []}
        for q in names(s["name"]):
            try:
                hits = ask(q)
            except Exception as e:
                row["error"] = str(e)[:80]
                hits = []
            time.sleep(1.1)
            for h in hits:
                la, lo = float(h["lat"]), float(h["lon"])
                row["found"].append({"q": q, "n": h.get("display_name", "")[:70], "t": "%s/%s" % (h.get("category"), h.get("type")),
                                     "lat": round(la, 5), "lon": round(lo, 5), "m": metres(s["lat"], s["lon"], la, lo)})
            if hits:
                break
        rows.append(row)
        print("%3d/%d %s: %s" % (i, len(todo), s["name"], "found" if row["found"] else "nothing"))
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"made": time.strftime("%Y-%m-%d %H:%M"), "rows": rows}, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, OUT)
    print("Done. %d of %d found. Report: %s" % (sum(1 for r in rows if r["found"]), len(rows), OUT))


if __name__ == "__main__":
    sys.exit(main())
