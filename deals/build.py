"""Build report.html from the latest collected data, the flyer transcriptions and editorial.json. Works offline.

Developed by AiTide Ltd. | www.AiTide.com
Version: 1.0
Last Updated: 2026-11-15

Change Log
  1.0  2026-11-15  First release.

Inputs (all inside this folder):
  template.html                   the page with {{PLACEHOLDERS}}; do not hand edit the data block
  config.json                     staples basket
  data/latest.json                which day folder is current
  data/<date>/*.json              collector output for that day
  data/menus.json, menus_meta.json  Sargasso menus
  data/flyers/lindos.json         Lindo's flyer transcription (weekly Claude step): {source, valid, note, items:[{section,item,unit,price,regular}]}
  data/flyers/supermart.json      same for Supermart
  editorial.json                  Claude-written cards and prose: best, vs, farms, others, rdeals, rstanding, rshops,
                                  edeals, estanding, eplaces, all_extra, prose{...}, asof (ISO date)
Output: report.html
"""
import os, sys, json, re, html, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bgd.util import ROOT, DATA, load_json, log, today
from bgd import staples as st, history

STORE_NAMES = {"mp": "MarketPlace", "ml": "Miles Market", "pr": "Pronto", "ld": "Lindo's", "sm": "Supermart", "prc": "Price Rite", "fm": "Farms"}
FRESH_DAYS = 12


def dlong(d):
    return d.strftime("%A %-d %B %Y") if os.name != "nt" else d.strftime("%A %#d %B %Y")


def dshort(d):
    return d.strftime("%-d %b") if os.name != "nt" else d.strftime("%#d %b")


def pdate(s):
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except (ValueError, TypeError):
        return None


def fresh(ed, d):
    a = pdate(ed.get("asof"))
    return a is not None and (d - a).days <= FRESH_DAYS


def auto_best(ad, sp, rules, d):
    out = []
    if ad:
        fin = pdate(ad.get("finish"))
        items = [i for i in ad["items"] if i.get("regular") and float(i["regular"]) > float(i["price"])]
        items.sort(key=lambda i: (float(i["price"]) - float(i["regular"])) / float(i["regular"]))
        for i in items[:10]:
            pct = (1 - float(i["price"]) / float(i["regular"])) * 100
            out.append({"s": "mp", "p": "%.2f" % float(i["price"]), "u": ("/" + i["size"]) if i.get("size") else "",
                        "n": i["item"], "w": "MarketPlace ad%s, reg $%.2f, %.0f%% off. 5%% off on Tuesdays and Wednesdays on top." % ((" to " + dshort(fin)) if fin else "", float(i["regular"]), pct)})
    # cheapest-store wins across the basket, biggest spread first
    spreads = []
    for r in rules:
        hits = {c: h for c, h in (sp.get(r["key"]) or {}).items() if h and h.get("price") is not None and not h.get("oos")}
        if len(hits) >= 2:
            lo = min(hits, key=lambda c: hits[c]["price"]); hi = max(hits, key=lambda c: hits[c]["price"])
            if hits[hi]["price"] > hits[lo]["price"] * 1.15:
                spreads.append((hits[hi]["price"] - hits[lo]["price"], r, lo, hi, hits))
    spreads.sort(key=lambda x: -x[0])
    for gap, r, lo, hi, hits in spreads[:6]:
        out.append({"s": lo, "p": "%.2f" % hits[lo]["price"], "u": "/" + r["size"], "n": r["item"] + " (" + hits[lo]["name"] + ")",
                    "w": "Cheapest of the three online shelves today: %s $%.2f against %s $%.2f%s." % (STORE_NAMES[lo], hits[lo]["price"], STORE_NAMES[hi], hits[hi]["price"], (", %s $%.2f" % (STORE_NAMES[[c for c in hits if c not in (lo, hi)][0]], hits[[c for c in hits if c not in (lo, hi)][0]]["price"])) if len(hits) == 3 else "")})
    return out


def auto_vs(sp, rules):
    out = []
    for r in rules:
        hits = {c: h for c, h in (sp.get(r["key"]) or {}).items() if h and h.get("price") is not None and not h.get("oos")}
        if len(hits) < 2:
            continue
        order = sorted(hits, key=lambda c: hits[c]["price"])
        a, b = order[0], order[1]
        out.append([r["item"] + ", " + r["size"], a, "%.2f (%s)" % (hits[a]["price"], hits[a]["name"][:40]), b, "%.2f (%s)" % (hits[b]["price"], hits[b]["name"][:40]), a if hits[a]["price"] < hits[b]["price"] else "tie"])
    return out


def main():
    d = today()
    latest = load_json(os.path.join(DATA, "latest.json"), {}).get("date")
    ddir = os.path.join(DATA, latest) if latest else None
    if not ddir or not os.path.isdir(ddir):
        log("build: no collected data yet"); return
    ld_ = lambda n, default=None: load_json(os.path.join(ddir, n), default)
    cfg = load_json(os.path.join(ROOT, "config.json"), {})
    rules = cfg.get("staples", [])
    ed = load_json(os.path.join(ROOT, "editorial.json"), {})
    edfresh = fresh(ed, d)
    prose = ed.get("prose", {})
    ad = ld_("marketplace_ad.json")
    sp = ld_("staples.json", {})
    lposts = ld_("lindos_posts.json", {"posts": []})
    sflyer = ld_("supermart_flyer.json", {})
    rl = ld_("redlaser.json", []) or []
    gs = ld_("goslings.json", []) or []
    lfl = load_json(os.path.join(DATA, "flyers", "lindos.json"), {})
    sfl = load_json(os.path.join(DATA, "flyers", "supermart.json"), {})
    menus = load_json(os.path.join(DATA, "menus.json"), {})
    mmeta = load_json(os.path.join(DATA, "menus_meta.json"), {"src": "Sargasso Sea app", "read": ""})
    cdate = pdate(latest) or d

    # ---- all specials
    allrows = []
    if ad:
        s0, f0 = pdate(ad.get("start")), pdate(ad.get("finish"))
        lab = "Bi-weekly ad (%s to %s)" % (dshort(s0), dshort(f0)) if s0 and f0 else "Bi-weekly ad"
        for i in ad["items"]:
            allrows.append(["mp", lab + (": " + i["section"] if i.get("section") else ""), i["item"], i.get("size") or "", i.get("regular"), float(i["price"])])
    newest_post = lposts["posts"][0]["post"] if lposts.get("posts") else ""
    ld_current = bool(lfl.get("items")) and (not newest_post or newest_post in (lfl.get("source") or ""))
    for i in lfl.get("items") or []:
        allrows.append(["ld", "%s (Flyer%s%s)" % (i.get("section", "Grocery"), (" to " + lfl["valid"]) if lfl.get("valid") else "", "" if ld_current else ", older post"), i["item"], i.get("unit", ""), i.get("regular"), float(i["price"])])
    sm_current = bool(sfl.get("items")) and (not sflyer.get("range") or sflyer["range"] == sfl.get("source"))
    for i in sfl.get("items") or []:
        allrows.append(["sm", "%s (%s%s)" % (i.get("section", "Grocery"), sfl.get("valid") or "flyer", "" if sm_current else ", last week's flyer"), i["item"], i.get("unit", ""), i.get("regular"), float(i["price"])])
    if edfresh:
        allrows.extend(ed.get("all_extra") or [])

    # ---- staples table
    staple_rows = []
    for r in rules:
        h = sp.get(r["key"]) or {}
        staple_rows.append([r["item"], r["size"], st.cell(h.get("mp")), st.cell(h.get("ml")), st.cell(h.get("pr"))])
    wins = {"mp": 0, "ml": 0, "pr": 0}
    for r in rules:
        h = {c: x for c, x in (sp.get(r["key"]) or {}).items() if x and x.get("price") is not None and not x.get("oos")}
        if h:
            wins[min(h, key=lambda c: h[c]["price"])] += 1

    best = (ed.get("best") or [] if edfresh else []) + auto_best(ad, sp, rules, d)
    vs = auto_vs(sp, rules) + (ed.get("vs") or [] if edfresh else [])
    changes = history.moves(cdate, rules, STORE_NAMES)

    # ---- retail auto cards
    rdeals = list(ed.get("rdeals") or []) if edfresh else []
    rl_sorted = sorted([x for x in rl if x.get("regular") and x.get("price")], key=lambda x: x["price"] / x["regular"])
    for x in rl_sorted[:6]:
        rdeals.append({"shop": "Red Laser", "cat": "Electronics", "what": "%s $%.2f (reg $%.2f, %.0f%% off)" % (x["item"], x["price"], x["regular"], (1 - x["price"] / x["regular"]) * 100), "meta": "redlaser.bm, read %s" % dshort(cdate)})
    if gs:
        marked = [x for x in gs if x.get("regular")]
        rdeals.append({"shop": "Gosling's", "cat": "Liquor / wine", "what": "%d items in the online sale collection%s. Free delivery over $100." % (len(gs), (", %d with a marked-down price" % len(marked)) if marked else ""), "meta": "goslingslimited.com/collections/sale-items, read %s" % dshort(cdate)})

    # ---- header notes
    notes = []
    if ad:
        s0, f0 = pdate(ad.get("start")), pdate(ad.get("finish"))
        top = sorted([i for i in ad["items"] if i.get("regular")], key=lambda i: float(i["price"]) / float(i["regular"]))[:5]
        notes.append(("mp", "MarketPlace", "Bi-weekly ad%s, %d sale lines read from the Hamilton store listing on %s (circular %s). Deepest cuts: %s. Everyday shelf prices in the staples table were re-read the same day. 5%% off on Tuesdays and Wednesdays, including online pick-up orders." % (
            (" runs %s to %s" % (dlong(s0), dlong(f0))) if s0 and f0 else "", len(ad["items"]), dshort(cdate), ad["id"],
            "; ".join("%s $%.2f (reg $%.2f)" % (i["item"], float(i["price"]), float(i["regular"])) for i in top) or "none with a regular price")))
    else:
        notes.append(("mp", "MarketPlace", "The ad could not be read on %s; the staples table still has the shelf prices. 5%% off on Tuesdays and Wednesdays." % dshort(cdate)))
    ldn = prose.get("ld_note") if (edfresh and ld_current) else ""
    if not ldn:
        ldn = "Newest flyer post%s: %s. %s 5%% off on Tuesdays and Wednesdays through 2026 (excludes alcohol, pharmacy, general merchandise, seasonal)." % (
            "s" if len(lposts.get("posts", [])) > 1 else "", ", ".join(p["post"] for p in lposts.get("posts", [])[:3]) or "none found",
            ("%d flyer lines are in the table below (valid %s)." % (len(lfl.get("items", [])), lfl.get("valid", ""))) if lfl.get("items") else "The flyer images are downloaded and waiting for the weekly read.")
    notes.append(("ld", "Lindo's", ldn))
    smn = prose.get("sm_note") if (edfresh and sm_current) else ""
    if not smn:
        smn = "Flyer for %s. %s Waitrose range is exclusive to Supermart." % (sflyer.get("range") or "the current week", ("%d lines in the table below." % len(sfl.get("items", []))) if sm_current else ("%d lines from the previous flyer below; the new one is downloaded and waiting for the weekly read." % len(sfl.get("items", [])) if sfl.get("items") else "The flyer image is downloaded and waiting for the weekly read."))
    notes.append(("sm", "Supermart", smn))
    notes.append(("ml", "Miles Market", "No weekly ad. Everyday prices from shop.miles.bm, re-read %s. Cheapest on %d of the %d staples today." % (dshort(cdate), wins["ml"], len(rules))))
    notes.append(("pr", "Pronto", "Online grocery with a Hamilton shop (Pronto City Market). Everyday prices from pronto.bm, re-read %s; cheapest on %d of the %d staples. $5 delivery on orders over $100." % (dshort(cdate), wins["pr"], len(rules))))
    notes_html = "".join('<div class="note"><b><span class="store %s">%s</span></b>%s</div>' % (c, html.escape(n), html.escape(t)) for c, n, t in notes)

    D = {
        "best": best, "vs": vs, "staples": staple_rows,
        "farms": ed.get("farms") or [], "others": ed.get("others") or [], "all": allrows,
        "rdeals": rdeals, "rstanding": ed.get("rstanding") or [], "rshops": ed.get("rshops") or [],
        "eplaces": ed.get("eplaces") or [], "edeals": (ed.get("edeals") or []) if edfresh else [], "estanding": ed.get("estanding") or [],
        "menus": menus, "menus_meta": mmeta, "changes": changes,
    }
    asof = pdate(ed.get("asof"))
    asof_s = dshort(asof) if asof else "not yet"
    fills = {
        "EYEBROW_GROC": "Prices collected %s · flyers and Facebook read %s" % (dlong(cdate), asof_s),
        "NOTES": notes_html,
        "STAPLES_SUB": "Regular shelf prices from the three stores that publish them online, re-read by the daily collector on %s. The cheapest store is in green on each row. Lindo's and Supermart publish flyers only, so their everyday prices need an in-store check. A product name in brackets is the listing that was matched; \"size unconfirmed\" means the closest listing did not state the size. \"OOS\" means out of stock online that day." % dshort(cdate),
        "STAPLES_OVERALL": prose.get("staples_overall") if edfresh and prose.get("staples_overall") else "Today MarketPlace is cheapest on %d of the %d rows, Pronto on %d and Miles on %d." % (wins["mp"], len(rules), wins["pr"], wins["ml"]),
        "FARMS_SUB": prose.get("farms_sub") or "Newest public Facebook post from each farm, read %s. Farms post what is in season rather than prices." % asof_s,
        "OTHERS_SUB": prose.get("others_sub") or "Newest public Facebook post from each, read %s, plus standing discounts." % asof_s,
        "EYEBROW_RETAIL": "Web stores read %s · Facebook pages read %s" % (dlong(cdate), asof_s),
        "RSHOPS_SUB": prose.get("rshops_sub") or "Newest post from each shop in the weekly sweep, grouped by category, with each shop's tier at the end of its line.",
        "EYEBROW_EATS": "Directory built Saturday 11 October 2026 · menus refreshed %s · deals read %s" % (mmeta.get("read") or "not yet", asof_s),
        "EATS_SUB": prose.get("eats_sub") or "Quick food across the island with hours, phone, delivery and menu links. Deals and notices come from each place's newest public Facebook post, website specials page and Sargasso Sea listing. Hours are from listings and can drift, so a call before a long ride is worth it.",
        "FOOTER": 'Sources: <a href="https://www.marketplace.bm/weekly-ad">MarketPlace bi-weekly ad</a> and MarketPlace online shelf prices for the Hamilton store, <a href="https://shop.miles.bm/">Miles Market online shop</a>, <a href="https://pronto.bm/">Pronto online shop</a>, <a href="https://lindos.bm/">Lindo\'s specials posts</a>, <a href="https://www.supermart.bm/weekly-specials">Supermart weekly specials</a>, <a href="https://redlaser.bm/">Red Laser</a>, <a href="https://goslingslimited.com/collections/sale-items">Gosling\'s sale collection</a>, <a href="https://masters.bm/special-promotions/">Masters promotions</a>, <a href="https://sargassosea.app/en/list">Sargasso Sea</a>, and the public Facebook pages of the stores, farms and shops named above. Shelf prices and menus are collected daily by a script on Matt\'s computer (last run %s); Lindo\'s, Supermart and Masters prices are transcribed from the published images once a week, so check the shelf tag if a number looks off.' % dlong(cdate),
        "DATA": json.dumps(D, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
    }
    tpl = open(os.path.join(ROOT, "template.html"), encoding="utf-8").read()
    for k, v in fills.items():
        tpl = tpl.replace("{{%s}}" % k, v)
    missing = re.findall(r"\{\{[A-Z_]+\}\}", tpl)
    if missing:
        log("build: unfilled placeholders %s" % missing)
    out = os.path.join(ROOT, "report.html")
    open(out, "w", encoding="utf-8").write(tpl)
    log("build: report.html written, %d KB, %d specials, %d staples, %d menus, %d moves" % (len(tpl) // 1024, len(allrows), len(staple_rows), len(menus), len(changes)))


if __name__ == "__main__":
    main()
