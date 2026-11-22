"""Hamilton retail web stores: Red Laser sale items, Gosling's sale collection, Masters and Phoenix promotion images.

Developed by AiTide Ltd. | www.AiTide.com
Version: 1.1
Last Updated: 2026-11-15

Change Log
  1.1  2026-11-15  Cap promotion image downloads at 8 per page (P-Tech lists its whole catalogue).
  1.0  2026-11-15  First release.
"""
import os, re
from bs4 import BeautifulSoup
from .util import get, log, download, FLYERS, slug


def redlaser():
    out = []
    try:
        r = get("https://redlaser.bm/")
        soup = BeautifulSoup(r.text, "html.parser")
        for li in soup.select(".product-item"):
            name = li.select_one(".product-item-link")
            old = li.select_one(".old-price .price")
            sp = li.select_one(".special-price .price")
            if name and sp:
                out.append({"item": name.get_text(strip=True), "regular": _num(old.get_text() if old else ""), "price": _num(sp.get_text())})
        log("Red Laser: %d sale items" % len(out))
    except Exception as e:
        log("Red Laser failed: %s" % e)
    return out


def goslings():
    out = []
    try:
        page = 1
        while page < 10:
            j = get("https://goslingslimited.com/collections/sale-items/products.json?limit=250&page=%d" % page).json()
            prods = j.get("products") or []
            for p in prods:
                for v in p.get("variants") or []:
                    price = _num(v.get("price"))
                    cmp = _num(v.get("compare_at_price"))
                    out.append({"item": p.get("title"), "variant": v.get("title"), "price": price,
                                "regular": cmp if cmp and cmp > (price or 0) else None, "available": bool(v.get("available"))})
            if len(prods) < 250:
                break
            page += 1
        log("Gosling's: %d sale variants" % len(out))
    except Exception as e:
        log("Gosling's failed: %s" % e)
    return out


def promo_images(name, url, pattern=r"\.(jpe?g|png|webp)", cap=8):
    """Download any new promotion images from a page into flyers/<name>/. Returns the list of local files found this run."""
    files = []
    try:
        r = get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        seen = set()
        for img in soup.find_all("img"):
            src = img.get("data-src") or img.get("src") or ""
            if not re.search(pattern, src, re.I) or src in seen:
                continue
            if re.search(r"logo|icon|avatar|placeholder|\.svg", src, re.I):
                continue
            seen.add(src)
            if len(seen) > cap:
                break
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = re.match(r"https?://[^/]+", url).group(0) + src
            fn = os.path.join(FLYERS, name, slug(os.path.basename(src.split("?")[0]))[:120] + os.path.splitext(src.split("?")[0])[1].lower())
            try:
                new = download(src, fn)
                files.append({"file": os.path.relpath(fn, os.path.dirname(FLYERS)), "url": src, "new": new})
            except Exception as e:
                log("%s image failed %s: %s" % (name, src, e))
        log("%s: %d promo images, %d new" % (name, len(files), sum(1 for f in files if f["new"])))
    except Exception as e:
        log("%s promotions page failed: %s" % (name, e))
    return files


def _num(s):
    m = re.search(r"[\d,]+\.?\d*", str(s or ""))
    return float(m.group(0).replace(",", "")) if m else None
