"""On this day miner: finds dated sentences about Bermuda in Wikipedia articles, for a person to check.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.0
Last Updated: 2026-11-24

Change Log
  1.0 2026-11-24  First release. Reads the plain text of each article in TITLES, keeps every sentence that
                  carries a full date (day, month and year), and writes them to
                  events/data/onthisday_candidates.json. Nothing here reaches the Hub by itself: each
                  candidate is checked and rewritten by hand before it goes into onthisday.json.

Depends on: Python 3.9 or later (standard library only) and the internet (en.wikipedia.org). Run it with
otd_mine.bat. Dates already in events/data/onthisday.json are marked "have": true so they can be skipped.
"""
import datetime as dt
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "events", "data")
OUT = os.path.join(DATA, "onthisday_candidates.json")
HAVE = os.path.join(DATA, "onthisday.json")
UA = "BermudaHub/1.0 (+https://github.com/mkatzsch/bermuda-hub)"

# Articles to read. Add a title here (exactly as Wikipedia spells it) and run again.
TITLES = [
    "History of Bermuda", "Bermuda", "St. George's, Bermuda", "Hamilton, Bermuda", "Sea Venture",
    "Somers Isles Company", "Cup Match", "Theatre Boycott (Bermuda)", "Bermuda Triangle", "Flight 19",
    "Star Tiger", "Star Ariel", "USS Cyclops (AC-4)", "Mary Celestia", "Cristóbal Colón (1923)",
    "Progressive Labour Party (Bermuda)", "United Bermuda Party", "One Bermuda Alliance",
    "1995 Bermudian independence referendum", "Governor of Bermuda", "Premier of Bermuda",
    "Parliament of Bermuda", "2017 America's Cup", "Newport Bermuda Race", "Bermuda at the Olympics",
    "Clarence Hill (boxer)", "Flora Duffy", "Shaun Goater", "Bermuda national football team",
    "Bermuda national cricket team", "Kindley Air Force Base", "Naval Air Station Bermuda",
    "Naval Air Station Bermuda Annex", "Darrell's Island, Bermuda", "RAF Darrell's Island",
    "Royal Naval Dockyard, Bermuda", "Bermuda Garrison", "Royal Bermuda Regiment",
    "Bermuda Volunteer Rifle Corps", "Bermuda Militia Artillery", "Bermuda Railway",
    "L.F. Wade International Airport", "Gibbs Hill Lighthouse", "St. David's Lighthouse",
    "St. Peter's Church, St. George's", "Cathedral of the Most Holy Trinity, Bermuda", "Sessions House, Bermuda",
    "Unfinished Church", "Fort St. Catherine", "Bermuda Institute of Ocean Sciences", "Bathysphere",
    "William Beebe", "Bermuda petrel", "Nonsuch Island, Bermuda", "David B. Wingate",
    "Bermuda Aquarium, Museum and Zoo", "Mary Prince", "Sally Bassett", "Joseph Rainey", "E. F. Gordon",
    "Lois Browne-Evans", "Henry Tucker (Bermudian politician)", "Richard Sharples", "Ewart Brown",
    "Bermuda sloop", "Bermuda rig", "Bermuda Gunpowder Plot", "Bermuda Hundred", "Bermuda Conference",
    "Bermuda Conference (1953)", "Bermuda II Agreement", "Bermuda Agreement", "Bermuda Monetary Authority",
    "Bermudian dollar", "Bank of N. T. Butterfield & Son", "The Royal Gazette (Bermuda)",
    "Bermuda Broadcasting Company", "Masterworks Museum of Bermuda Art", "Bermuda National Trust",
    "Bermuda Day", "Gombey", "Bermuda onion", "Hurricane Fabian", "Hurricane Gonzalo", "Hurricane Emily (1987)",
    "1926 Havana–Bermuda hurricane", "HMS Valerian (1916)", "Deliverance (1609)", "Patience (1609)",
]

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
MON = "|".join(MONTHS)
DMY = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)? (%s),? (1[5-9]\d\d|20\d\d)\b" % MON)
MDY = re.compile(r"\b(%s) (\d{1,2})(?:st|nd|rd|th)?, (1[5-9]\d\d|20\d\d)\b" % MON)


def article(title: str) -> str:
    """The plain text of one Wikipedia article, or "" when it does not exist."""
    q = urllib.parse.urlencode({"action": "query", "prop": "extracts", "explaintext": 1, "redirects": 1,
                                "format": "json", "titles": title})
    req = urllib.request.Request("https://en.wikipedia.org/w/api.php?" + q, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        pages = json.load(r).get("query", {}).get("pages", {})
    return "".join(p.get("extract") or "" for p in pages.values())


def dated(text: str) -> list:
    """[(mm-dd, year, sentence)] for every sentence in text that carries a full date."""
    out = []
    for sent in re.split(r"(?<=[.!?])\s+(?=[A-Z\"(])|\n+", text):
        sent = sent.strip()
        if not 40 <= len(sent) <= 400 or sent.startswith("="):
            continue
        hits = [(int(m.group(1)), m.group(2), int(m.group(3))) for m in DMY.finditer(sent)]
        hits += [(int(m.group(2)), m.group(1), int(m.group(3))) for m in MDY.finditer(sent)]
        for day, mon, year in hits:
            try:
                dt.date(2000, MONTHS.index(mon) + 1, day)  # 2000 is a leap year, so 29 February passes
            except ValueError:
                continue
            out.append(("%02d-%02d" % (MONTHS.index(mon) + 1, day), year, sent))
    return out


def main() -> None:
    have = set()
    if os.path.exists(HAVE):
        with open(HAVE, encoding="utf-8") as f:
            have = {(e["d"], e["y"]) for e in json.load(f).get("events", [])}
    found, said = [], []
    for title in TITLES:
        try:
            text = article(title)
        except Exception as e:
            said.append("%s: failed (%s)" % (title, str(e)[:60]))
            continue
        rows = dated(text) if text else []
        said.append("%s: %s" % (title, ("%d dated sentences" % len(rows)) if text else "no such article"))
        for d, y, sent in rows:
            found.append({"d": d, "y": y, "from": title, "text": sent, "have": (d, y) in have})
        time.sleep(0.5)  # be polite to Wikipedia
    seen, keep = set(), []
    for row in sorted(found, key=lambda r: (r["d"], r["y"], r["from"])):
        key = (row["d"], row["y"], row["text"][:80])
        if key not in seen:
            seen.add(key)
            keep.append(row)
    os.makedirs(DATA, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"read": dt.datetime.now().isoformat(timespec="seconds"), "articles": said, "candidates": keep},
                  f, ensure_ascii=False, indent=1)
    print("\n".join(said))
    print("%d candidates written to %s, %d of them on dates not yet in the Hub" % (len(keep), OUT, sum(1 for r in keep if not r["have"])))


if __name__ == "__main__":
    main()
