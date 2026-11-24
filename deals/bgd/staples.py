"""Pick the matching product for each staple from loose search results.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.1
Last Updated: 2026-11-15

Change Log
  1.1  2026-11-15  Require a size hit when the rule lists sizes; out of stock listings rank below in-stock ones.
  1.0  2026-11-15  First release.

Rules per staple in config.json: every word in "must" has to appear in the product name plus size,
no word in "not" may appear, and a hit on "any" ranks a candidate above one without. Among the
survivors the lowest price wins, with the next few kept as candidates for a human check.
"""
import re


def _text(c):
    return ("%s %s" % (c.get("name", ""), c.get("size", ""))).lower()


def _hit(t, w):
    w = w.lower()
    if re.search(r"\d", w):  # numeric sizes: match as substring
        return w in t
    return re.search(r"\b" + re.escape(w), t) is not None


def pick(rule, cands):
    scored = []
    for c in cands:
        if c.get("price") in (None, 0):
            continue
        t = _text(c)
        if not all(_hit(t, w) for w in rule.get("must", [])):
            continue
        if any(_hit(t, w) for w in rule.get("not", [])):
            continue
        anyhit = 1 if (not rule.get("any") or any(_hit(t, w) for w in rule["any"])) else 0
        scored.append((-anyhit, 1 if c.get("oos") else 0, float(c["price"]), c))
    scored.sort(key=lambda x: (x[0], x[1], x[2]))
    if not scored:
        return None
    if rule.get("any") and scored[0][0] == 0:
        # nothing in the right size: report the closest listing instead of a wrong price
        c = scored[0][3]
        return {"price": None, "closest": "%s %s $%.2f" % (c.get("name", ""), c.get("size", ""), float(c["price"])), "cands": []}
    best = scored[0][3]
    return {
        "price": float(best["price"]), "name": best.get("name", ""), "size": best.get("size", ""),
        "oos": bool(best.get("oos")), "sale": bool(best.get("sale")), "regular": best.get("regular"),
        "weak": scored[0][0] == 0,
        "cands": [{"name": s[3].get("name", ""), "size": s[3].get("size", ""), "price": float(s[3]["price"]), "oos": bool(s[3].get("oos"))} for s in scored[1:5]],
    }


def cell(hit):
    """Render one staple price cell the way the page expects: a leading number, then a note."""
    if not hit:
        return "not listed"
    if hit.get("price") is None:
        return "no match in this size (closest: %s)" % hit.get("closest", "")
    s = "%.2f" % hit["price"]
    note = []
    nm = hit["name"]
    if hit.get("size") and hit["size"].lower() not in nm.lower():
        nm += " " + hit["size"]
    note.append(nm)
    if hit.get("sale") and hit.get("regular"):
        note.append("on sale, reg %.2f" % float(hit["regular"]))
    if hit.get("weak"):
        note.append("size unconfirmed")
    s += " (" + "; ".join(note) + ")"
    if hit.get("oos"):
        s += " OOS"
    return s
