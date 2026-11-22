"""Sargasso Sea delivery app: restaurant list and full menus.

Developed by AiTide Ltd. | www.AiTide.com
Version: 1.0
Last Updated: 2026-11-15

Source: sargassosea.app marketplace API (Yelo platform). No login needed.
"""
import datetime as dt
from concurrent.futures import ThreadPoolExecutor
from .util import get, post_json, log

HOST = "https://sargassosea.app/api/"
REF = "3a91f3acbffd75fdc13fb295824358a4"
MKT = 58603
LAT, LNG = 32.289431, -64.790653


def _base(store_id=None):
    b = {"marketplace_reference_id": REF, "marketplace_user_id": MKT, "domain_name": "sargassosea.app",
         "dual_user_key": 0, "language": "en", "date_time": dt.datetime.utcnow().isoformat() + "Z"}
    if store_id is not None:
        b["user_id"] = store_id
    return b


def stores():
    """Every storefront Sargasso lists for Hamilton, with address, phone, category and closed flag."""
    out = []
    skip = 0
    while True:
        url = (HOST + "marketplace/marketplace_get_city_storefronts_v3?domain_name=sargassosea.app&post_to_get=1"
               "&marketplace_reference_id=%s&marketplace_user_id=%s&latitude=%s&longitude=%s"
               "&search_text=Hamilton%%20Bermuda%%2C%%20Bermuda%%2C%%20Bermuda&skip=%d&limit=25&home_delivery=1&source=0&dual_user_key=0&language=en"
               % (REF, MKT, LAT, LNG, skip))
        j = get(url).json()
        arr = j.get("data") or []
        if not isinstance(arr, list) or not arr:
            break
        for s in arr:
            out.append({
                "id": s.get("user_id"), "n": (s.get("store_name") or "").strip(), "addr": s.get("display_address") or s.get("address") or "",
                "ph": s.get("phone") or "", "cat": s.get("business_categories_name") or "", "slug": s.get("storepage_slug") or "",
                "closed": int(s.get("is_closed") or 0), "desc": (s.get("description") or "")[:120], "rating": s.get("store_rating"),
                "min": s.get("merchantMinimumOrder"),
            })
        skip += 25
        if len(arr) < 25:
            break
    log("Sargasso: %d storefronts" % len(out))
    return out


def menu(store_id):
    """[[categoryPath, [[item, price, specialOrOmitted], ...]], ...] for one store."""
    c = post_json(HOST + "catalogue/get", dict(_base(store_id), show_all_sub_categories=1))
    leaves = []

    def walk(arr, path):
        for x in arr or []:
            nm = (x.get("name") or "").strip()
            p = (path + " / " + nm) if path else nm
            if x.get("has_products"):
                leaves.append((x.get("catalogue_id"), p))
            if x.get("sub_categories"):
                walk(x["sub_categories"], p)

    walk((c.get("data") or {}).get("result"), "")
    cats = []
    for cid, cname in leaves:
        items = []
        page = 1
        while page < 20:
            r = post_json(HOST + "get_products_for_category", dict(_base(store_id), parent_category_id=cid, page_no=page, offset=(page - 1) * 25, limit=25))
            d = r.get("data") or []
            if not isinstance(d, list):
                d = d.get("result") or []
            for it in d:
                if it.get("is_enabled") == 0:
                    continue
                row = [(it.get("name") or "").strip(), it.get("price")]
                if it.get("special_price"):
                    row.append(it.get("special_price"))
                items.append(row)
            if len(d) < 25:
                break
            page += 1
        if items:
            cats.append([cname, items])
    return cats


def food_stores(all_stores):
    skip = {1113512, 1357919, 1466482, 3532330}  # Pronto HQ, catering, merch, PHCMDC
    return [s for s in all_stores if s["id"] not in skip and ("Restaurants" in s["cat"] or "Pantry" in s["cat"])]


def crawl(all_stores, workers=5):
    """Menus for every food store. Returns {id: {n, cats}}."""
    todo = food_stores(all_stores)
    out = {}

    def one(s):
        try:
            cats = menu(s["id"])
        except Exception as e:  # keep going; one bad store should not stop the crawl
            log("Sargasso menu failed for %s: %s" % (s["n"], e))
            return
        if cats:
            out[str(s["id"])] = {"n": s["n"], "cats": cats}

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(one, todo))
    n = sum(len(c[1]) for v in out.values() for c in v["cats"])
    log("Sargasso: %d menus, %d items" % (len(out), n))
    return out
