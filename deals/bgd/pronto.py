"""Pronto (pronto.bm, Eddress platform) product search.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.0
Last Updated: 2026-11-15

Source: prod-api.eddress.co public search endpoint, no login needed.
"""
from .util import post_json

URL = "https://prod-api.eddress.co/v1/api/searchengine/public/WLxcLSplRaS7A9DKkDDHMQ/search"
STORE = "62bc5c3f5e1f9a0685630dbf"
TENANT = "WLxcLSplRaS7A9DKkDDHMQ"


def search(term, limit=14):
    j = post_json(URL, {"query": term, "page": 0, "storeId": STORE, "tenantUid": TENANT})
    out = []
    for it in (j.get("items") or [])[:limit]:
        price = it.get("price")
        struck = it.get("strikedPrice") or None
        out.append({
            "name": it.get("label") or it.get("productName") or "",
            "size": it.get("size") or "",
            "price": price,
            "regular": struck if struck and struck > (price or 0) else price,
            "sale": bool(struck and price and struck > price),
            "oos": bool(it.get("outOfStock")),
            "promo": it.get("promoTag") or it.get("discountLabel") or "",
        })
    return out
