"""Restaurant menus from each place's own website (HTML, PDF or image, via the OCR module) and the Sargasso markup.

Developed by AiTide Ltd. | www.AiTide.com
Version: 1.2
Last Updated: 2026-11-22

Change Log
  1.2  2026-11-22  Menu links are now looked for in the whole page. Before, the navigation bar, header and footer
                   were thrown away first to get clean text, and that is exactly where most sites keep their
                   Menu link, so sites such as KFC and Mr. Chicken reported that they had no menu link at all.
                   The browser is also tried when a home page gives no prices and no menu link.
  1.1  2026-11-22  The first run got prices from only 3 of 30 sites, so the reader looks much harder. It now tries
                   the https and www forms of an address when one fails; follows menu links two levels deep and up
                   to ten pages a site, including PDFs and menu images kept on another host (Squarespace, Wix and
                   the like), PDF addresses buried in page scripts, and menu frames; adds up the items from every
                   menu it finds instead of keeping only the best page; reads prices written as bare numbers
                   ("Fish sandwich 18") when a page has several of them; and, when a page is built by scripts and
                   has no text of its own, opens it in a real browser (Playwright, already used for Facebook).
                   Every site also gets a "diag" entry in menus_own.json saying what was tried and why it came up
                   short, so the fix list explains itself.
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


MENU_LINK = re.compile(r"menu|food|\beat\b|\bdine|dining|lunch|dinner|breakfast|brunch|take-?out|take ?away|order|pizza|sushi|drinks|specials|carte|kitchen", re.I)
NOT_MENU = re.compile(r"facebook\.com|instagram\.com|twitter\.com|x\.com/|tiktok|youtube|linkedin|mailto:|tel:|javascript:|whatsapp|maps\.google|goo\.gl|#$|/cart|/account|/login|privacy|terms|career|gift", re.I)
FILE_HOSTS = re.compile(r"squarespace|wixstatic|usrfiles|filesusr|wix\.com|cloudfront|amazonaws|shopify|wp\.com|googleusercontent|cloudinary|webflow|godaddy|wsimg", re.I)
PDF_IN_HTML = re.compile(r"https?:[\\/]+[^\"'<>\s)]+?\.pdf", re.I)
LOOSE = re.compile(r"^(?P<name>.*[A-Za-z]{3}.*?)[\s.]+\$?(?P<p>\d{1,3})(?:\s*/\s*\$?\d{1,3})?$")
LOOSE_BAD = re.compile(r"\b(oz|pcs?|pieces?|inch|in|cm|ml|lb|lbs|people|persons?|guests?|years?|est|since|floor|suite|ext|box|street|st|road|rd|lane|hm|\d{4})$", re.I)
PLATFORMS = [("wix", "Wix"), ("squarespace", "Squarespace"), ("wp-content", "WordPress"), ("shopify", "Shopify"), ("toasttab", "Toast"),
             ("chownow", "ChowNow"), ("gloriafood", "GloriaFood"), ("popmenu", "Popmenu"), ("getbento", "BentoBox"), ("sargassosea", "Sargasso"),
             ("godaddy", "GoDaddy"), ("webflow", "Webflow"), ("weebly", "Weebly"), ("opentable", "OpenTable")]


def loose_items(text):
    """Prices written as bare whole numbers at the end of a line ('Fish sandwich 18')."""
    items = []
    for raw in text.split("\n"):
        ln = re.sub(r"[.…_\-]{3,}", " ", raw).strip()
        m = LOOSE.match(ln)
        if not m or PRICE.search(ln):
            continue
        name, price = m.group("name").strip(" .:-"), float(m.group("p"))
        if 4 <= price <= 250 and 2 < len(name) < 80 and not SKIP_LINE.search(name) and not LOOSE_BAD.search(name) and not re.search(r"\d{3}", name):
            items.append([name, price])
    return items


def loose_pairs(text):
    """Bare number prices are only trusted on their own when a page has several of them."""
    items = loose_items(text)
    return [["Menu", items]] if len(items) >= 6 else []


def count(cats):
    return sum(len(c[1]) for c in cats)


def text_to_cats(text):
    cats = pairs_from_text(text)
    if count(cats) >= 4:  # clearly a menu: bare number lines on the same page are prices too
        have = {nkey(it[0]) for c in cats for it in c[1]}
        extra = [it for it in loose_items(text) if nkey(it[0]) not in have]
        return cats + ([["More", extra]] if extra else [])
    loose = loose_pairs(text)
    return loose if count(loose) > count(cats) else cats


def fetch(url):
    """GET, trying the https and www forms of the address when the one given does not answer."""
    u = urlparse(url)
    host = u.netloc
    alts = [url]
    for scheme in ("https", "http"):
        for h in (host, host[4:] if host.startswith("www.") else "www." + host):
            cand = u._replace(scheme=scheme, netloc=h).geturl()
            if cand not in alts:
                alts.append(cand)
    last = None
    for cand in alts:
        try:
            r = get(cand, retries=1, timeout=25)
            if r.status_code < 400:
                return r
            last = RuntimeError("HTTP %s" % r.status_code)
        except Exception as e:
            last = e
    raise last


class Renderer:
    """A real browser for pages that are built by scripts. Started only if a site needs it; one browser for the whole run."""
    def __init__(self):
        self.pw = self.br = None
        self.dead = False

    def page(self, url):
        if self.dead:
            return None
        try:
            if not self.br:
                from playwright.sync_api import sync_playwright
                self.pw = sync_playwright().start()
                self.br = self.pw.chromium.launch(headless=True)
            pg = self.br.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36")
            try:
                pg.goto(url, wait_until="domcontentloaded", timeout=30000)
                pg.wait_for_timeout(3500)
                text = pg.evaluate("document.body ? document.body.innerText : ''")
                html = pg.content()
            finally:
                pg.close()
            return text, html
        except ImportError:
            self.dead = True
            log("  Playwright is not installed, so script built pages are skipped")
        except Exception as e:
            log("  browser could not open %s: %s" % (url[:60], str(e)[:80]))
        return None

    def close(self):
        try:
            if self.br:
                self.br.close()
            if self.pw:
                self.pw.stop()
        except Exception:
            pass


def whole(html):
    """The page with nothing removed, for finding links (html_text drops the navigation, where menu links usually live)."""
    from bs4 import BeautifulSoup
    return BeautifulSoup(html or "", "html.parser")


def links_from(html, soup, base, deep):
    """Menu candidates on a page, best first: PDFs, then menu pages, then menu images. deep is True on a page that is itself a menu page."""
    root = ".".join(urlparse(base).netloc.split(".")[-2:])
    pdfs, pages, imgs = [], [], []
    def same(h):
        return urlparse(h).netloc.endswith(root)
    for a in soup.find_all("a", href=True):
        h = urljoin(base, a["href"]).split("#")[0]
        t = a.get_text(" ", strip=True) + " " + h
        if not h.startswith("http") or NOT_MENU.search(h):
            continue
        low = h.lower().split("?")[0]
        if low.endswith(".pdf"):
            (pdfs.insert(0, h) if MENU_LINK.search(t) else pdfs.append(h)) if (same(h) or FILE_HOSTS.search(h)) else None
        elif re.search(r"\.(jpe?g|png|webp)$", low):
            if MENU_LINK.search(t) and (same(h) or FILE_HOSTS.search(h)):
                imgs.append(h)
        elif MENU_LINK.search(t) and same(h) and h.rstrip("/") != base.rstrip("/"):
            pages.append(h)
    for m in PDF_IN_HTML.findall(html or ""):
        h = m.replace("\\/", "/")
        if h not in pdfs and (same(h) or FILE_HOSTS.search(h)):
            pdfs.append(h)
    for tag, attr in (("iframe", "src"), ("embed", "src"), ("object", "data")):
        for el in soup.find_all(tag):
            h = urljoin(base, el.get(attr) or "")
            if h.startswith("http") and not NOT_MENU.search(h) and (h.lower().split("?")[0].endswith(".pdf") or MENU_LINK.search(h)):
                (pdfs if ".pdf" in h.lower() else pages).append(h)
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or (img.get("srcset") or "").split(" ")[0]
        if not src:
            continue
        h = urljoin(base, src)
        if not re.search(r"\.(jpe?g|png|webp)", h.lower()) or re.search(r"logo|icon|sprite|avatar|banner|favicon", h, re.I):
            continue
        if MENU_LINK.search(h + " " + (img.get("alt") or "")) or deep:
            imgs.append(h)
    seen, out = set(), []
    for kind, lst in (("pdf", pdfs), ("page", pages), ("image", imgs[:6])):
        for h in lst:
            if h not in seen:
                seen.add(h); out.append((kind, h))
    return out


def read_site(url, name, cfg, renderer=None, budget=150):
    """Return (cats, kind, source, diag). Walks the site for its menus and adds up what every menu page, PDF and image gives."""
    import time
    t0 = time.time()
    diag = {"tried": [], "rendered": False, "platform": "", "note": ""}
    merged, sources, kinds, seen_items = [], [], set(), set()
    queue, done, images_read = [("page", url, 0)], set(), 0

    def add(cats, src, kind):
        new = []
        for cat, items in cats:
            keep = [it for it in items if (nkey(it[0]), it[1]) not in seen_items and not seen_items.add((nkey(it[0]), it[1]))]
            if keep:
                new.append([cat, keep])
        if count(new):
            merged.extend(new); sources.append(src); kinds.add(kind)

    while queue and len(done) < 10 and time.time() - t0 < budget and count(merged) < 400:
        kind, u, depth = queue.pop(0)
        if u in done:
            continue
        done.add(u)
        try:
            r = fetch(u)
        except Exception as e:
            diag["tried"].append([u[:120], "error", str(e)[:60]])
            if depth == 0:
                raise
            continue
        ctype = (r.headers.get("content-type") or "").lower()
        low = u.lower().split("?")[0]
        if "pdf" in ctype or low.endswith(".pdf"):
            try:
                cats = text_to_cats(pdf_text(r.content))
            except Exception as e:
                diag["tried"].append([u[:120], "pdf", "unreadable: " + str(e)[:40]]); continue
            diag["tried"].append([u[:120], "pdf", count(cats)]); add(cats, u, "pdf"); continue
        if ctype.startswith("image/") or re.search(r"\.(jpe?g|png|webp)$", low):
            if images_read >= 6 or len(r.content) < 25000:
                continue
            images_read += 1
            try:
                text, _ = image_text(r.content, u, cfg)
                cats = text_to_cats(text)
            except Exception as e:
                diag["tried"].append([u[:120], "image", "unreadable: " + str(e)[:40]]); continue
            diag["tried"].append([u[:120], "image", count(cats)]); add(cats, u, "image"); continue
        html = r.text
        text, soup = html_text(html)
        if depth == 0:
            diag["chars"] = len(text.strip())
            diag["title"] = (soup.title.get_text(strip=True)[:80] if soup.title else "")
            diag["platform"] = next((label for key, label in PLATFORMS if key in html.lower()), "")
        cats = text_to_cats(text)
        rendered = False
        soup = whole(html)
        found = links_from(html, soup, r.url, deep=depth >= 1 and bool(MENU_LINK.search(u)))
        if count(cats) < 5 and renderer and (len(text.strip()) < 700 or depth >= 1 or not found):
            got = renderer.page(r.url)
            if got:
                rendered = diag["rendered"] = True
                text2, html2 = got
                c2 = text_to_cats(text2)
                if count(c2) > count(cats):
                    cats = c2
                html = html2
                soup = whole(html2)
                found = links_from(html, soup, r.url, deep=depth >= 1 and bool(MENU_LINK.search(u)))
        diag["tried"].append([u[:120], "page+browser" if rendered else "page", count(cats)])
        add(cats, u, "html")
        if depth < 2:
            for k2, h in found:
                if h not in done:
                    queue.append((k2, h, depth + 1))
            queue.sort(key=lambda q: (q[2], {"pdf": 0, "page": 1, "image": 2}[q[0]]))
    n = count(merged)
    if not n:
        tried = diag["tried"]
        if diag.get("chars", 0) < 200 and not diag["rendered"]:
            diag["note"] = "The page has almost no text of its own (built by scripts) and no browser was available."
        elif len(tried) <= 1:
            diag["note"] = "No link to a menu was found on the home page."
        elif any(t[1] == "image" for t in tried):
            diag["note"] = "The menu is a picture and the reader could not make out priced lines."
        elif any(t[1] == "pdf" for t in tried):
            diag["note"] = "A PDF menu was found but no priced lines could be read from it (it may be a scan)."
        else:
            diag["note"] = "Menu pages were found but they show no prices."
    kind = "+".join(sorted(kinds)) or "html"
    return merged, kind, (sources[0] if sources else url), diag


def read_url(url, name, cfg, depth=0):
    """Kept for callers of the 1.0 name."""
    cats, kind, src, _ = read_site(url, name, cfg)
    return cats, kind, src


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
    renderer = Renderer()
    try:
        for i, r in enumerate(todo):
            sl = slug(r["name"])
            try:
                cats, kind, src, diag = read_site(r["url"], r["name"], ocr_cfg, renderer)
                n = count(cats)
                out[sl] = {"n": r["name"], "src": src, "kind": kind, "read": d.isoformat(), "sargasso_id": r.get("sargasso_id"), "cats": cats, "items": n, "diag": diag}
                ok += 1 if n else 0
                log("Menu %2d/%d %-30s %-10s %3d items  %s" % (i + 1, len(todo), r["name"][:30], kind, n, (src if n else diag.get("note", ""))[:70]))
            except Exception as e:
                out[sl] = {"n": r["name"], "src": r["url"], "kind": "error", "read": d.isoformat(), "sargasso_id": r.get("sargasso_id"), "cats": [], "items": 0, "error": str(e)[:160],
                           "diag": {"note": "The site did not answer on any form of its address."}}
                log("Menu %2d/%d %-30s error  %s" % (i + 1, len(todo), r["name"][:30], str(e)[:80]))
            if (i + 1) % 10 == 0:
                save_json(os.path.join(DATA, "menus_own.json"), out)  # keep what has been read so far
    finally:
        renderer.close()
    save_json(os.path.join(DATA, "menus_own.json"), out)
    log("Own menus: %d of %d sites gave priced items; %d with nothing (fix list in data/menus_own.json)" % (ok, len(todo), len(todo) - ok))
    mk = compare(out, sarg or load_json(os.path.join(DATA, "menus.json"), {}))
    save_json(os.path.join(DATA, "markup.json"), {"read": d.isoformat(), "restaurants": mk})
    if mk:
        meds = sorted(v["median_markup_pct"] for v in mk.values())
        log("Markup: %d restaurants matched, median Sargasso markup %.0f%% (range %.0f%% to %.0f%%)" % (len(mk), meds[len(meds) // 2], meds[0], meds[-1]))
    return out, mk
