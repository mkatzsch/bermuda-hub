"""MarketPlace and Miles Market (both run on the Freshop platform).

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.2
Last Updated: 2026-11-15

Change Log
  1.2  2026-11-15  Two seconds between calls and a 30 second back-off on 400 (per-minute limit confirmed on the second run).
  1.1  2026-11-15  Pace API calls and re-mint the session token on a 400.
  1.0  2026-11-15  First release.

Sources: api.freshop.ncrcloud.com. MarketPlace is app_key the_marketplace, store 2883 (Hamilton).
Miles Market is app_key miles_market, store 7269. A session token is minted with a plain GET.
"""
import time
from .util import get, log

API = "https://api.freshop.ncrcloud.com"
FIELDS = "name,brand,size,base_price,offer_sale_price,sale_start_date,sale_finish_date,department_name,sell_by"


def _name(p):
    """Brand plus name, without repeating a brand the name already starts with."""
    b = (p.get("brand") or "").strip()
    n = (p.get("name") or "").strip()
    if b and not n.lower().startswith(b.lower()[:6]):
        n = b + " " + n
    return " ".join(n.split()).title() if n.isupper() else " ".join(n.split())


class Freshop:
    def __init__(self, app_key, store_id):
        self.app_key = app_key
        self.store_id = str(store_id)
        self._session()

    def _session(self):
        r = get("%s/1/sessions?app_key=%s" % (API, self.app_key))
        r.raise_for_status()
        self.token = r.json()["token"]

    def _q(self, path, **params):
        """One API call. Freshop answers 400 after about 20 calls in a minute, so pace calls and back off on a 400."""
        for attempt in range(4):
            params.update(app_key=self.app_key, token=self.token)
            r = get("%s/%s" % (API, path), params=params, timeout=60)
            if r.status_code == 400 and attempt < 3:
                log("Freshop 400 on %s, waiting %ds" % (path, 30 * (attempt + 1)))
                time.sleep(30 * (attempt + 1))
                self._session()
                continue
            r.raise_for_status()
            time.sleep(2.0)
            return r.json()

    def circular(self):
        """The current bi-weekly ad: id, dates and every product on it with regular and sale price."""
        c = self._q("1/circulars", store_id=self.store_id)
        items = c.get("items") or []
        if not items:
            return None
        circ = items[0]
        cid = circ["id"]
        pages = self._q("1/circular_pages", circular_id=cid, include_spots="false", store_id=self.store_id).get("items") or []
        pids = []
        for p in pages:
            spots = self._q("2/circular_spots", circular_page_id=p["id"]).get("items") or []
            for s in spots:
                for pid in (s.get("product_ids") or ([s["product_id"]] if s.get("product_id") else [])):
                    if pid not in pids:
                        pids.append(pid)
        products = []
        for i in range(0, len(pids), 50):
            batch = ",".join(str(x) for x in pids[i:i + 50])
            got = self._q("1/products", id=batch, store_id=self.store_id, limit=50, fields=FIELDS).get("items") or []
            products.extend(got)
        out = []
        for p in products:
            sale = p.get("offer_sale_price")
            reg = p.get("base_price")
            if sale is None:
                continue
            out.append({
                "item": _name(p),
                "size": p.get("size") or "",
                "section": p.get("department_name") or "",
                "regular": reg,
                "price": sale,
                "start": p.get("sale_start_date"),
                "finish": p.get("sale_finish_date"),
            })
        log("Freshop %s circular %s: %d pages, %d products, %d on sale" % (self.app_key, cid, len(pages), len(products), len(out)))
        return {"id": cid, "name": circ.get("name"), "start": circ.get("start_date"), "finish": circ.get("finish_date"), "items": out}

    def search(self, term, limit=16):
        got = self._q("1/products", store_id=self.store_id, q=term, limit=limit, fields=FIELDS).get("items") or []
        out = []
        for p in got:
            out.append({
                "name": _name(p),
                "size": p.get("size") or "",
                "price": p.get("offer_sale_price") if p.get("offer_sale_price") is not None else p.get("base_price"),
                "regular": p.get("base_price"),
                "sale": p.get("offer_sale_price") is not None,
                "finish": p.get("sale_finish_date"),
                "oos": False,
            })
        return out
