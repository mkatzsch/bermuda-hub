"""Daily price history (history.csv) and the price-move summaries built from it.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.0
Last Updated: 2026-11-15

history.csv columns: date, store, key, price, note. One row per staple per store per day,
plus one row per sale item on the MarketPlace ad (key sale:<slug>) so repeats can be spotted.
"""
import csv, os, datetime as dt
from .util import ROOT

PATH = os.path.join(ROOT, "history.csv")


def append(rows):
    new = not os.path.exists(PATH)
    with open(PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "store", "key", "price", "note"])
        for r in rows:
            w.writerow(r)


def load():
    out = []
    if not os.path.exists(PATH):
        return out
    with open(PATH, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                r["price"] = float(r["price"])
                r["d"] = dt.date.fromisoformat(r["date"])
                out.append(r)
            except (ValueError, KeyError):
                pass
    return out


def moves(today, staple_rules, store_names, window=90):
    """Price changes vs the previous recorded day, and 90-day lows, for every staple and store."""
    hist = [h for h in load() if not h["key"].startswith("sale:")]
    by = {}
    for h in hist:
        by.setdefault((h["store"], h["key"]), []).append(h)
    names = {r["key"]: r["item"] + " " + r["size"] for r in staple_rules}
    changes, lows = [], []
    cutoff = today - dt.timedelta(days=window)
    for (store, key), rows in by.items():
        rows.sort(key=lambda r: r["d"])
        if rows[-1]["d"] != today:
            continue
        cur = rows[-1]["price"]
        prev = [r for r in rows if r["d"] < today]
        if prev and abs(prev[-1]["price"] - cur) >= 0.01:
            p = prev[-1]["price"]
            changes.append({"n": names.get(key, key), "when": "%s, %s to %s" % (store_names.get(store, store), prev[-1]["d"].strftime("%d %b"), today.strftime("%d %b")),
                            "t": ("Down" if cur < p else "Up") + " from $%.2f to $%.2f (%+.0f%%)." % (p, cur, (cur - p) / p * 100), "delta": cur - p})
        recent = [r["price"] for r in rows if r["d"] >= cutoff]
        if len(recent) >= 7 and cur <= min(recent) and len(set(recent)) > 1:
            lows.append({"n": names.get(key, key), "when": "%s, lowest in %d days" % (store_names.get(store, store), window),
                         "t": "$%.2f today; it has been as high as $%.2f in that window." % (cur, max(recent))})
    changes.sort(key=lambda c: c["delta"])
    return changes + lows
