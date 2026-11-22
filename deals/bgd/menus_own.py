"""Restaurant menus from each place's own website (HTML, PDF or image, via the OCR module) and the Sargasso markup.

Developed by AiTide Ltd. | www.AiTide.com
Version: 1.0
Last Updated: 2026-11-17

Change Log
  1.0  2026-11-17  First release. For every entry in config.json "restaurants" (or every place in data/places.json
                   with a website): fetch the page, follow one "menu" link when the page itself has no prices,
                   pull item and price pairs from HTML text, from PDF text (pdfplumber, pypdf fallback) and from
                   menu images through bgd/ocr.read_image (EasyOCR plus Tesseract, boxes grouped into rows).
                   Writes data/menus_own.json in the same shape as the Sargasso menus.json, then matches each
                   item to the Sargasso menu of the same place and writes data/markup.json (per item and per
                   restaurant markup). collect.py runs it with --own-menus or on the 28 day menu cycle.

Dependencies: requests, beautifulsoup4 (Anaconda); pdfplumber or pypdf for PDF menus (pip install pdfplumber);
easyocr and pytesseract through bgd/ocr.py for image menus. config.json "restaurants" is a list of
{"name", "url", "kind": "auto" | "html" | "pdf" | "image" | "skip", "sargasso_id": optional}; places.json fills
in any website the list does not name. Output shape: {slug: {"n", "src", "kind", "read", "cats": [[category,
[[item, price], ...]], ...]}}.
"""
import os, re, io, json, difflib, datetime as dt
from urllib.parse import urljoin, urlparse
from .util import log, get, DATA, FLYERS, save_json, load_json, slug
from . import ocr

PRICE = re.compile(r"\$\s?(\d{1,3}(?:\.\d{2})?)\b|(?<![\d.])(\d{1,3}\.\d{2})(?![\d%])")
SKIP_LINE = re.compile(r"(gratuit|service charge|tax|minimum|per person|subject to|allerg|copyright|©|reserved|\bpm\b|\bam\b|open|hours|call|phone|\d{3}-\d{4})", re.I)
MENU_WORD = re.compile(r"menu|food|dinner|lunch|breakfast|takeout|take-out|pizza|sushi|specials", re.I)
HEAD = re.compile(r"^[A-Z][A-Z &'/\-]{2,40}$")


# ---------------------------------------------------------------- text -> items
def pairs_from_text(text):
    """Item and price pairs from plain text. Handles 'Name $12', 'Name ..... 12.50', '12.50' on the next line, and headings."""
    cats, cur, items, carry = [], "Menu", [], None
    for raw in text.split("\n"):
        ln = re.sub(r"[.…_\-]{3,}", " ", raw).strip()
        if not ln:
            continue
        prices = [float(a or b) for a, b in PRICE.findall(ln)]
        words = re.sub(PRICE, " ", ln).strip(" .:$-")
        if prices and not SKIP_LINE.search(words) and 0.5 < prices[0] < 500:
            name = words if len(words) > 2 else (carry or "")
            if name and len(name) < 90:
                items.append([name[:80], prices[0]])
            carry = None
            continue
        if not prices and HEAD.match(ln) and len(items) >= 0:
            if items:
                cats.append([cur, items]); items = []
            cur = ln.title(); carry = None
            continue
        if not prices and 2 < len(ln) < 70 and not SKIP_LINE.search(ln):
            carry = ln
    if items:
        cats.append([cur, items])
    return cats


def rows_from_ocr(lines, h0=None):
    """Group OCR line boxes into rows by vertical overlap, then join each row's text left to right."""
    L = [l for l in lines if l.get("text", "").strip()]
    L.sort(key=lambda l: (l["box"][1], l["box"][0]))
    rows, cur = [], []
    for l in L:
        if cur and min(cur[-1]["box"][3], l["box"][3]) - max(cur[-1]["box"][1], l["box"][1]) < 0.4 * (l["box"][3] - l["box"][1]):
            rows.append(cur); cur = []
        cur.append(l)
    if cur:
        rows.append(cur)
    out = []
    for r in rows:
        r.sort(key=lambda l: l["box"][0])
        out.append(" ".join(l["text"] for l in r))
    return "\n".join(out)


# ---------------------------------------------------------------- fetchers
def html_text(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        t.decompose()
    return soup.get_text("\n"), soup


def pdf_text(data):
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return "\n".join((p.extract_text() or "") for p in pdf.pages)
    except ImportError:
        from pypdf import PdfReader
        return "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(data)).pages)


def image_text(data, name, cfg):
    d = os.path.join(FLYERS, "menus")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, slug(name)[:60] + os.path.splitext(urlparse(name).path)[1].lower() or ".jpg")
    with open(path, "wb") as f:
        f.write(data)
    res = ocr.read_image(path, cfg)
    return rows_from_ocr(res["lines"]), path


def read_url(url, name, cfg, depth=0):
    """Return (cats, kind, source url). Follows one menu link or PDF/image link when the page itself has no prices."""
    r = get(url, timeout=60)
    ctype = (r.headers.get("content-type") or "").lower()
    if "pdf" in ctype or url.lower().endswith(".pdf"):
        return pairs_from_text(pdf_text(r.content)), "pdf", url
    if ctype.startswith("image/") or re.search(r"\.(jpe?g|png|webp)(\?|$)", url.lower()):
        text, _ = image_text(r.content, url, cfg)
        return pairs_from_text(text), "image", url
    text, soup = html_text(r.text)
    cats = pairs_from_text(text)
    n = sum(len(c[1]) for c in cats)
    if n >= 8 or depth >= 1:
        return cats, "html", url
    # no priced lines on this page: look for a menu link, a PDF or a menu image
    links = []
    for a in soup.find_all("a", href=True):
        h = urljoin(url, a["href"]); t = (a.get_text(" ", strip=True) + " " + h)
        if urlparse(h).netloc != urlparse(url).netloc and not h.lower().endswith(".pdf"):
            continue
        if h.lower().endswith(".pdf") and MENU_WORD.search(t):
            links.insert(0, h)
        elif MENU_WORD.search(t) and h.rstrip("/") != url.rstrip("/"):
            links.append(h)
    for img in soup.find_all("img", src=True):
        s = urljoin(url, img["src"])
        if MENU_WORD.search(s + " " + (img.get("alt") or "")) and re.search(r"\.(jpe?g|png|webp)", s.lower()):
            links.append(s)
    best, bkind, bsrc = cats, "html", url
    for h in links[:4]:
        try:
            c2, k2, s2 = read_url(h, name, cfg, depth + 1)
        except Exception as e:
            log("  %s: %s failed: %s" % (name, h, e)); continue
        if sum(len(c[1]) for c in c2) > sum(len(c[1]) for c in best):
            best, bkind, bsrc = c2, k2, s2
        if sum(len(c[1]) for c in best) >= 15:
            break
    return best, bkind, bsrc


# ---------------------------------------------------------------- markup against Sargasso
def nkey(s):
    s = re.sub(r"\(.*?\)", " ", (s or "").lower())
    s = re.sub(r"\b(the|with|and|&|a|of|w/)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def compare(own, sarg):
    """Match each own-menu item to the Sargasso item of the same restaurant. Returns {slug: {n, matched, rows, median}}."""
    sarg_by_name = {nkey(v["n"]): k for k, v in (sarg or {}).items()}
    out = {}
    for sl, m in own.items():
        sid = m.get("sargasso_id")
        if not sid or str(sid) not in sarg:
            mm = difflib.get_close_matches(nkey(m["n"]), list(sarg_by_name), n=1, cutoff=0.85)
            sid = sarg_by_name[mm[0]] if mm else None
        if not sid or str(sid) not in sarg:
            continue
        sitems = {}
        for cat, items in sarg[str(sid)]["cats"]:
            for it in items:
                if it[1]:
                    sitems.setdefault(nkey(it[0]), float(it[1]))
        keys = list(sitems)
        rows = []
        for cat, items in m["cats"]:
            for name, price in items:
                k = nkey(name)
                hit = k if k in sitems else (difflib.get_close_matches(k, keys, n=1, cutoff=0.8) or [None])[0]
                if hit and price:
                    sp = sitems[hit]
                    rows.append([name, round(price, 2), round(sp, 2), round((sp / price - 1) * 100, 1)])
        if rows:
            ups = sorted(r[3] for r in rows)
            out[sl] = {"n": m["n"], "sargasso_id": str(sid), "matched": len(rows), "median_markup_pct": ups[len(ups) // 2], "rows": rows}
    return out


# ---------------------------------------------------------------- entry point
def run(cfg_list, d, places=None, sarg=None, ocr_cfg=None, only=None):
    todo = []
    seen = set()
    for r in cfg_list or []:
        if r.get("kind") == "skip" or not r.get("url"):
            continue
        todo.append(r); seen.add(nkey(r["name"]))
    for p in (places or {}).get("places") or []:
        if p.get("website") and nkey(p["name"]) not in seen and "sargassosea" not in p["website"]:
            todo.append({"name": p["name"], "url": p["website"], "kind": "auto", "sargasso_id": p.get("sargasso_id")}); seen.add(nkey(p["name"]))
    if only:
        todo = [t for t in todo if only.lower() in t["name"].lower()]
    out = load_json(os.path.join(DATA, "menus_own.json"), {}) if only else {}
    ok = 0
    for r in todo:
        sl = slug(r["name"])
        try:
            cats, kind, src = read_url(r["url"], r["name"], ocr_cfg)
            n = sum(len(c[1]) for c in cats)
            out[sl] = {"n": r["name"], "src": src, "kind": kind, "read": d.isoformat(), "sargasso_id": r.get("sargasso_id"), "cats": cats, "items": n}
            ok += 1 if n else 0
            log("Menu %-34s %-5s %3d items  %s" % (r["name"][:34], kind, n, src[:70]))
        except Exception as e:
            out[sl] = {"n": r["name"], "src": r["url"], "kind": "error", "read": d.isoformat(), "sargasso_id": r.get("sargasso_id"), "cats": [], "items": 0, "error": str(e)[:160]}
            log("Menu %-34s error  %s" % (r["name"][:34], str(e)[:80]))
    save_json(os.path.join(DATA, "menus_own.json"), out)
    log("Own menus: %d of %d sites gave priced items; %d with nothing (fix list in data/menus_own.json)" % (ok, len(todo), len(todo) - ok))
    mk = compare(out, sarg or load_json(os.path.join(DATA, "menus.json"), {}))
    save_json(os.path.join(DATA, "markup.json"), {"read": d.isoformat(), "restaurants": mk})
    if mk:
        meds = sorted(v["median_markup_pct"] for v in mk.values())
        log("Markup: %d restaurants matched, median Sargasso markup %.0f%% (range %.0f%% to %.0f%%)" % (len(mk), meds[len(meds) // 2], meds[0], meds[-1]))
    return out, mk
