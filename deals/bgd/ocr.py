"""OCR: read prices out of flyer images with free, local readers before spending any model tokens.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.1
Last Updated: 2026-11-16

Change Log
  1.1  2026-11-16  Rebuilt the flyer half against real Lindo's flyers. Prices are display type ("$6" with a raised
                   "69") and come back as "5669" or "s660": each price box is now re-read three ways (as read,
                   whole box enlarged with digits only, dollars and cents windows) and voted; a disagreement
                   marks the line for the weekly check (conf 0.4). Names are the stack of lines directly above
                   the price in its column, pack circles ("6" over "PACK") are merged, sizes and "each" lines
                   attach to their price, brand logos read as gibberish are dropped. Small images are upscaled
                   before reading. 23 of 29 known prices exact on the 10 Nov flyers, 5 of the 6 misses flagged.
                   Generic half: tie break is now a `prefer` pattern (default: a money amount) so the top half
                   can be copied alone; reread_boxes() and _light() added for any digits-only second look.
  1.0  2026-11-16  First release. Reader chain EasyOCR -> Tesseract -> (optional) vision model, per line
                   confidence gate, price and unit parsing, section headings, and writers for the
                   data/flyers/lindos.json and supermart.json files that build.py already reads.

The file has two halves. The top half (READERS, read_image) knows nothing about groceries and can be
copied as is into any other project: give it an image path, get back
a list of lines, each with its text, a 0 to 1 confidence and a box. The bottom half turns those lines
into flyer items.

Readers, tried in this order, each one only on what the previous one was unsure about:
  1. EasyOCR      pip install easyocr        best on coloured, rotated, text over photo (flyers). Downloads
                                             its model (about 100 MB) the first time it runs. CPU only is fine.
  2. Tesseract    pip install pytesseract    plus the Tesseract program (already at C:\\Program Files\\Tesseract-OCR).
                                             Better on clean typed text; used as the second opinion on low
                                             confidence lines, and as the only reader when EasyOCR is absent.
  3. PaddleOCR    pip install paddleocr      optional upgrade for dense layouts; picked up automatically if installed.
  4. Vision model off by default (config.json "ocr": {"vision": true} and ANTHROPIC_API_KEY). Only the lines
                                             the local readers disagreed on are sent, as one cropped strip each.

Dependencies: Pillow (ships with Anaconda). config.json keys, all optional:
  "ocr": {"min_conf": 0.45, "tesseract": "C:\\\\Program Files\\\\Tesseract-OCR\\\\tesseract.exe", "vision": false}
Output: data/flyers/<store>_ocr.json every run (for review), and data/flyers/<store>.json whenever the
flyer is newer than the one already transcribed there, so a hand checked transcription of the current
flyer is never overwritten by the machine read of the same flyer.
"""
import os, re, json, datetime as dt

# ----------------------------------------------------------------------------------------------------
# Generic half: readers and read_image. No project specific code above the next banner.
# ----------------------------------------------------------------------------------------------------

DEFAULT_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
_easy = None
_paddle = None


def _easyocr():
    global _easy
    if _easy is None:
        try:
            import easyocr  # type: ignore
            _easy = easyocr.Reader(["en"], gpu=False, verbose=False)
        except Exception as e:  # not installed, or model download failed
            _easy = False
            print("[ocr] EasyOCR unavailable: %s" % e)
    return _easy or None


def _paddleocr():
    global _paddle
    if _paddle is None:
        try:
            from paddleocr import PaddleOCR  # type: ignore
            _paddle = PaddleOCR(lang="en", show_log=False)
        except Exception:
            _paddle = False
    return _paddle or None


def _tesseract_ok(path):
    try:
        import pytesseract  # type: ignore
    except ImportError:
        return None
    exe = path or DEFAULT_TESSERACT
    if os.path.exists(exe):
        pytesseract.pytesseract.tesseract_cmd = exe
    try:
        pytesseract.get_tesseract_version()
        return pytesseract
    except Exception:
        return None


def _box(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]


def _load(path, cfg):
    """The image as a PIL image, upscaled when it is small (readers want glyphs of 20 px or more). Returns (img, scale)."""
    from PIL import Image
    img = Image.open(path).convert("RGB")
    target = int((cfg or {}).get("min_width", 1800))
    scale = 1.0
    if img.width < target:
        scale = min(3.0, target / float(img.width))
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    return img, scale


def _unscale(lines, scale):
    if scale != 1.0:
        for L in lines:
            L["box"] = [int(v / scale) for v in L["box"]]
    return lines


def read_easy(reader, image, allowlist=None):
    import numpy as np
    arr = np.array(image) if not isinstance(image, str) else image
    out = []
    for pts, text, conf in reader.readtext(arr, paragraph=False, allowlist=allowlist):
        if text.strip():
            out.append({"text": text.strip(), "conf": float(conf), "box": _box(pts), "reader": "easyocr"})
    return out


def reread_boxes(path, lines, allowlist="0123456789$.", pad=0.25, zoom=3, cfg=None):
    """Second look at chosen boxes: each one cropped, enlarged and read again with both readers limited to
    `allowlist` characters. Sets L["alt_num"] = [readings...] on each line; the caller decides what to keep.
    Project neutral: use it for amounts, dates, reference numbers, anything where the character set is known."""
    from PIL import Image
    img = Image.open(path).convert("L")
    ez = _easyocr()
    pt = _tesseract_ok((cfg or {}).get("tesseract"))
    W, H = img.size
    for L in lines:
        l, t, r, b = L["box"]
        px, py = int((r - l) * pad), int((b - t) * pad)
        crop = img.crop((max(0, l - px), max(0, t - py), min(W, r + px), min(H, b + py)))
        if crop.width < 6 or crop.height < 6:
            continue
        crop = _light(crop).resize((crop.width * zoom, crop.height * zoom), Image.LANCZOS)
        reads = []
        if ez:
            try:
                reads += [(x["text"], x["conf"], "easyocr") for x in read_easy(ez, crop.convert("RGB"), allowlist=allowlist)]
            except Exception as e:
                print("[ocr] reread easyocr: %s" % e)
        if pt:
            try:
                wl = "-c tessedit_char_whitelist=%s" % allowlist if allowlist else ""
                for psm in (7, 6):
                    txt = pt.image_to_string(crop, config="--psm %d %s" % (psm, wl)).strip()
                    if txt:
                        reads.append((txt, 0.6, "tesseract-%d" % psm))
            except Exception as e:
                print("[ocr] reread tesseract: %s" % e)
        L["alt_num"] = reads
    return lines


def read_paddle(reader, path):
    out = []
    res = reader.ocr(path, cls=True) or []
    for page in res:
        for pts, (text, conf) in page or []:
            if text.strip():
                out.append({"text": text.strip(), "conf": float(conf), "box": _box(pts), "reader": "paddle"})
    return out


def read_tesseract(pt, image, psm=11):
    """Lines (not words) from Tesseract, with the mean word confidence of each line scaled to 0..1."""
    from PIL import Image
    img = image if not isinstance(image, str) else Image.open(image)
    d = pt.image_to_data(img, config="--psm %d" % psm, output_type=pt.Output.DICT)
    lines = {}
    for i, txt in enumerate(d["text"]):
        if not txt.strip() or int(d["conf"][i]) < 0:
            continue
        key = (d["block_num"][i], d["par_num"][i], d["line_num"][i])
        L = lines.setdefault(key, {"words": [], "confs": [], "l": 10**9, "t": 10**9, "r": 0, "b": 0})
        L["words"].append(txt)
        L["confs"].append(int(d["conf"][i]))
        L["l"] = min(L["l"], d["left"][i]); L["t"] = min(L["t"], d["top"][i])
        L["r"] = max(L["r"], d["left"][i] + d["width"][i]); L["b"] = max(L["b"], d["top"][i] + d["height"][i])
    return [{"text": " ".join(L["words"]), "conf": sum(L["confs"]) / len(L["confs"]) / 100.0,
             "box": [L["l"], L["t"], L["r"], L["b"]], "reader": "tesseract"} for L in lines.values()]


MONEY = re.compile(r"\$?\s?\d{1,3}(?:,\d{3})*[.,]\d{2}\b")  # default tie break: the reading that contains an amount wins


def read_image(path, cfg=None):
    """Read one image with the best available reader chain.
    Returns {"lines": [{text, conf, box:[l,t,r,b], reader}], "readers": [...], "low": n_low_conf}.
    cfg["prefer"] may be a compiled regex: when the two readers disagree on a doubtful line, the reading
    that matches it wins (default: a money amount). Everything above the flyer banner is project neutral."""
    cfg = cfg or {}
    min_conf = float(cfg.get("min_conf", 0.45))
    prefer = cfg.get("prefer") or MONEY
    pt = _tesseract_ok(cfg.get("tesseract"))
    primary = _paddleocr() if cfg.get("prefer_paddle") else None
    img, scale = _load(path, cfg)
    lines, used = [], []
    if primary:
        import numpy as np
        lines = read_paddle(primary, np.array(img)); used.append("paddle")
    else:
        ez = _easyocr()
        if ez:
            lines = read_easy(ez, img); used.append("easyocr")
    if not lines and pt:  # no neural reader installed: Tesseract on the whole page
        lines = _unscale(read_tesseract(pt, img), scale); used.append("tesseract")
        return {"lines": lines, "readers": used, "low": sum(1 for L in lines if L["conf"] < min_conf)}
    _unscale(lines, scale)

    low = [L for L in lines if L["conf"] < min_conf]
    if low and pt:  # second opinion from Tesseract on each doubtful strip
        from PIL import Image
        img = Image.open(path).convert("L")
        W, H = img.size
        for L in low:
            l, t, r, b = L["box"]
            pad = max(4, (b - t) // 3)
            crop = img.crop((max(0, l - pad), max(0, t - pad), min(W, r + pad), min(H, b + pad)))
            if crop.width < 8 or crop.height < 8:
                continue
            crop = crop.resize((crop.width * 2, crop.height * 2))  # Tesseract likes bigger glyphs
            alt = read_tesseract(pt, crop, psm=7)
            if not alt:
                continue
            best = max(alt, key=lambda a: a["conf"])
            L["alt"] = {"text": best["text"], "conf": best["conf"]}
            # prefer the reading that contains a price, then the higher confidence
            if (prefer.search(best["text"]) and not prefer.search(L["text"])) or best["conf"] > L["conf"] + 0.15:
                L["text"], L["conf"], L["reader"] = best["text"], best["conf"], "tesseract"
        if "tesseract" not in used:
            used.append("tesseract")

    still = [L for L in lines if L["conf"] < min_conf]
    if still and cfg.get("vision") and os.environ.get("ANTHROPIC_API_KEY"):
        try:
            _vision_fix(path, still)
            used.append("vision")
        except Exception as e:
            print("[ocr] vision step skipped: %s" % e)
    return {"lines": lines, "readers": used, "low": sum(1 for L in lines if L["conf"] < min_conf)}


def _vision_fix(path, lines, model="claude-haiku-4-5"):
    """Send only the doubtful strips, as one tall image, to a small vision model. Keeps tokens tiny."""
    import base64, io
    from PIL import Image
    import anthropic  # type: ignore
    img = Image.open(path).convert("RGB")
    strips = []
    for L in lines:
        l, t, r, b = L["box"]
        strips.append(img.crop((max(0, l - 6), max(0, t - 6), min(img.width, r + 6), min(img.height, b + 6))))
    w = max(s.width for s in strips)
    h = sum(s.height + 8 for s in strips)
    sheet = Image.new("RGB", (w, h), "white")
    y = 0
    for s in strips:
        sheet.paste(s, (0, y)); y += s.height + 8
    buf = io.BytesIO(); sheet.save(buf, "PNG")
    client = anthropic.Anthropic()
    msg = client.messages.create(model=model, max_tokens=800, messages=[{"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64.b64encode(buf.getvalue()).decode()}},
        {"type": "text", "text": "This image is %d text strips stacked top to bottom. Transcribe each strip exactly, one per line, in order. Output only the lines." % len(strips)}]}])
    got = [s for s in msg.content[0].text.splitlines() if s.strip()]
    for L, txt in zip(lines, got):
        L["text"], L["conf"], L["reader"] = txt.strip(), 0.9, "vision"


# ----------------------------------------------------------------------------------------------------
# Flyer half: turn lines into {section, item, unit, price, regular} rows for build.py.
# ----------------------------------------------------------------------------------------------------

_PRICE = re.compile(r"(?<![\d.])(?:\$\s?)?(\d{1,3})\s?[.,]\s?(\d{2})(?!\d)|(\d{1,2})\s*/\s*\$?\s?(\d{1,3})(?:[.,](\d{2}))?|(\d{2})\s?[¢c](?![a-z])", re.I)
_UNIT = re.compile(r"\b(\d+(?:\.\d+)?)\s?(oz|fl\.? ?oz|lb|lbs|g|kg|ml|l|ltr|litre|ct|pk|pack|each|ea|dozen|doz|bunch|pt|qt|gal)\b|\b(per|/)\s?(lb|each|ea|kg|pk|bag|bunch)\b", re.I)
_SIZE = re.compile(r"\b\d+(?:\.\d+)?\s?(fl\.? ?oz|oz|g|kg|ml|l|ltr|litre|ct|pk|pack|dozen|doz|pt|qt|gal)\b", re.I)  # package sizes, never prices
_REG = re.compile(r"(?:reg(?:ular)?|was|everyday)\.?\s*\$?\s?(\d{1,3})[.,](\d{2})", re.I)
SECTIONS = ["Butcher's Block", "Butcher", "Meat", "Seafood", "Fish", "Produce", "Fruit", "Vegetables", "Deli", "Dairy", "Frozen",
            "Bakery", "Grocery", "Beverages", "Drinks", "Snacks", "Health & Beauty", "Health and Beauty", "Household", "Pet",
            "Baby", "Pharmacy", "Wine", "Beer", "Spirits", "Waitrose", "Organic"]
_SECTION = re.compile(r"^\s*(%s)\s*$" % "|".join(re.escape(s) for s in SECTIONS), re.I)
_NOISE = re.compile(r"^(sale|special|specials|save|offer|only|price|each|new|while supplies last|limit.*|valid.*|lindo'?s|supermart|weekly specials?)$", re.I)


def _fix(t):
    """Common OCR slips: 'per Ib' -> 'per lb', '7.25 0z' -> '7.25 oz', 'S2.99' -> '$2.99'."""
    t = t.strip()
    t = re.sub(r"\b(per\s*)?[Il1]b\b", lambda m: (m.group(1) or "") + "lb", t)
    t = re.sub(r"(\d)\s?0z\b", r"\1 oz", t)
    t = re.sub(r"(?<![A-Za-z])S(\d{1,3}[.,]\d{2})", r"$\1", t)
    return t


def parse_price(text):
    """Return (price, is_multi) or (None, False). '2/$5' -> 2.50 each. Numbers bound to a size ('7.25 oz') are not prices."""
    m = _PRICE.search(_SIZE.sub(" ", text))
    if not m:
        return None, False
    if m.group(1):
        return float("%s.%s" % (m.group(1), m.group(2))), False
    if m.group(3):
        n = int(m.group(3)); dollars = int(m.group(4)); cents = int(m.group(5) or 0)
        return round((dollars + cents / 100.0) / n, 2), True
    return int(m.group(6)) / 100.0, False


def _centre(b):
    return ((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0)


_BIGPRICE = re.compile(r"^[\$5sS§]\s?(\d{1,5})\b")       # "$23 25" set in display type comes back as "52325", "s1389", "S910"
_DIGITS = re.compile(r"^\d{1,3}$")
_PACK = re.compile(r"^(\d{1,3})\s*(pack|pk|ct)\.?$|^(pack|pk)\.?$", re.I)
_EACH = re.compile(r"^(ea|each|lb|/lb|per lb)[.:]?$", re.I)
_SIZELINE = re.compile(r"^\s*(\d+(?:[.,]\d+)?\s?\"?\s?(x\s?\d+\s?)?(fl\.? ?oz|oz|0z|lb|lbs|ib|g|gm|kg|ml|l|ltr|litre|liter|ct|pk|pack|cl|ft|f\.)\.?[\s_:]*(bottles?|cans?|pkgs?|bags?|boxe?s?|jars?|pouch|tubs?|pack|pkg)?|bottles?|cans?|pkgs?|bags?|boxe?s?|jars?|pouch|tubs?)\s*[.:_]*$", re.I)
_FOOTER = re.compile(r"(valid|store hours|tel[:.]|ext[.:]|road|street|devonshire|hamilton|paget|warwick|st\.? ?george|stack up|while stocks|next level|weekly|deals at|lindo|supermart|facebook|www\.|\.bm|\.com|am to|pm$)", re.I)


def _norm_lines(lines):
    """Clean copies of the lines: fixed text, dropped gibberish, plus the page's typical line height."""
    out = []
    for L in lines:
        t = _fix(L["text"]).strip(" _~`'\"|")
        if not t:
            continue
        if L["conf"] < 0.3 and not re.search(r"\d", t):  # unreadable brand logos and the like
            continue
        if len(re.findall(r"[A-Za-z0-9]", t)) < 2 and not t.isdigit():
            continue
        if _FOOTER.search(t) and not _BIGPRICE.match(t):
            continue
        out.append(dict(L, text=t, h=max(1, L["box"][3] - L["box"][1]), w=max(1, L["box"][2] - L["box"][0])))
    hs = sorted(L["h"] for L in out if re.search(r"[A-Za-z]{3}", L["text"]))
    h0 = hs[len(hs) // 2] if hs else 24
    return out, h0


def _overlap_y(a, b):
    return min(a[3], b[3]) - max(a[1], b[1])


def _find_prices(lines, h0):
    """Price boxes. Display type prices (tall box, dollar-like lead) and ordinary "$1.99" / "2/$5" lines."""
    prices, used = [], set()
    tall = [L for L in lines if L["h"] >= 1.35 * h0]
    for L in tall:
        m = _BIGPRICE.match(L["text"])
        if not m or id(L) in used:
            continue
        digits = m.group(1)
        box = list(L["box"])
        if len(digits) <= 2:  # cents may sit in their own box to the right ("s1" + "709", "586" + "65")
            for R in lines:
                if R["h"] < 0.8 * h0:
                    continue
                if R is L or id(R) in used or not _DIGITS.match(R["text"]):
                    continue
                gap = R["box"][0] - L["box"][2]
                if -0.3 * L["w"] < gap < 1.2 * L["h"] and _overlap_y(L["box"], R["box"]) > 0.3 * min(L["h"], R["h"]):
                    digits += R["text"]; used.add(id(R)); box[2] = max(box[2], R["box"][2]); box[1] = min(box[1], R["box"][1]); box[3] = max(box[3], R["box"][3])
                    break
        if len(digits) < 3 or len(digits) > 5:
            continue
        val = int(digits[:-2]) + int(digits[-2:]) / 100.0
        if val <= 0 or val > 500:
            continue
        used.add(id(L))
        prices.append({"val": val, "multi": False, "box": box, "conf": L["conf"], "line": L})
    for L in lines:
        if id(L) in used or L in tall and _BIGPRICE.match(L["text"]):
            continue
        t = L["text"]
        if _FOOTER.search(t) or re.search(r"\d\s*[/:]\s*\d{4}|am|pm", t, re.I):
            continue
        p, multi = parse_price(t)
        rest = _PRICE.sub(" ", _SIZE.sub(" ", t)).strip(" $-|,")
        if p is None or (len(rest) >= 4 and not _EACH.match(rest)):
            continue
        if multi and (int(_PRICE.search(t).group(3) or 0) > 12 or p > 100):
            continue
        used.add(id(L))
        prices.append({"val": p, "multi": multi, "box": list(L["box"]), "conf": L["conf"], "line": L})
    return prices, used


def _owner(L, prices):
    """The price a text line most plausibly belongs to: nearest column centre among prices below or beside it."""
    cx = (L["box"][0] + L["box"][2]) / 2.0
    best, bd = None, None
    for P in prices:
        l, t, r, b = P["box"]
        pcx = (l + r) / 2.0
        above = t - L["box"][3]
        if above < -0.6 * L["h"] and _overlap_y(P["box"], L["box"]) <= 0:
            continue
        if above > 7.5 * max(12, b - t) * 0.6 + 60:
            continue
        d = abs(cx - pcx) + max(0, above) * 0.25
        if _overlap_y(P["box"], L["box"]) > 0.3 * L["h"]:
            d *= 0.5  # a pack circle or size sitting beside the price belongs to it
        if bd is None or d < bd:
            best, bd = P, d
    return best


def _merge_packs(lines, h0):
    """'6' sitting on top of 'PACK' in a circle becomes one line '6 PACK'."""
    packs = [L for L in lines if re.fullmatch(r"(pack|pk)\.?", L["text"], re.I)]
    nums = [L for L in lines if _DIGITS.match(L["text"])]
    drop = set()
    for Pk in packs:
        for N in nums:
            if id(N) in drop:
                continue
            ox = min(N["box"][2], Pk["box"][2]) - max(N["box"][0], Pk["box"][0])
            gap = Pk["box"][1] - N["box"][3]
            if ox > 0 and -0.8 * h0 < gap < 1.2 * h0:
                Pk["text"] = "%s PACK" % N["text"]; Pk["h"] = max(Pk["h"], N["h"])
                Pk["box"] = [min(N["box"][0], Pk["box"][0]), N["box"][1], max(N["box"][2], Pk["box"][2]), Pk["box"][3]]
                drop.add(id(N)); break
    return [L for L in lines if id(L) not in drop]


def _best_numeric(L):
    """Settle a price box from its readings: the value most of them agree on, display style ('$2325') or plain."""
    votes = {}
    for txt, conf, who in [(L["text"], L["conf"], L["reader"])] + list(L.get("alt_num", [])):
        t = txt.strip().replace(",", ".").replace("O", "0").replace("o", "0")
        m = re.search(r"(\d{1,3})\.(\d{2})\b", t)
        if m:
            val = int(m.group(1)) + int(m.group(2)) / 100.0
        else:
            d = re.sub(r"\D", "", t)
            if t[:1] in "58" and len(d) in (4, 5):
                d = d[1:]  # the dollar sign came back as a 5 or an 8
            if len(d) < 3 or len(d) > 5:
                continue
            val = int(d[:-2]) + int(d[-2:]) / 100.0
        if 0 < val <= 500:
            votes.setdefault(val, []).append(conf + (0.2 if who.startswith("easyocr") else 0))
    if not votes:
        return None
    val = max(votes, key=lambda v: (len(votes[v]), sum(votes[v])))
    return val


def _vote(reads):
    """reads: [(text, weight)] -> the digit string with the most weight, or ''."""
    tally = {}
    for txt, wgt in reads:
        d = re.sub(r"\D", "", txt or "")
        if d:
            tally[d] = tally.get(d, 0) + wgt
    return max(tally, key=tally.get) if tally else ""


def _light(crop):
    """Dark text on a light ground, whatever the original: white on red comes out black on white."""
    import numpy as np
    from PIL import ImageOps
    a = np.asarray(crop)
    if a.mean() < 128:
        crop = ImageOps.invert(crop)
    return ImageOps.autocontrast(crop)


def _read_digits(img, box, ez, pt, zoom=4):
    """Digits in one crop, from every reader available: [(text, weight)]."""
    from PIL import Image
    l, t, r, b = [int(v) for v in box]
    l, t = max(0, l), max(0, t)
    r, b = min(img.width, r), min(img.height, b)
    if r - l < 4 or b - t < 4:
        return []
    crop = _light(img.crop((l, t, r, b)))
    crop = crop.resize((crop.width * zoom, crop.height * zoom), Image.LANCZOS)
    reads = []
    if ez:
        try:
            rs = read_easy(ez, crop.convert("RGB"), allowlist="0123456789")
            if rs:  # the biggest box is the figure; small ones are bleed from neighbours
                big = max(rs, key=lambda x: (x["box"][2] - x["box"][0]) * (x["box"][3] - x["box"][1]))
                reads.append((big["text"], 1.0 + big["conf"]))
        except Exception as e:
            print("[ocr] digits easyocr: %s" % e)
    if pt:
        for psm in (7, 8):
            try:
                txt = pt.image_to_string(crop, config="--psm %d -c tessedit_char_whitelist=0123456789" % psm).strip()
                if txt:
                    reads.append((txt, 0.5))
            except Exception as e:
                print("[ocr] digits tesseract: %s" % e)
    return reads


def _split_price_box(img, box):
    """Where the dollars and the cents sit inside a display price box, from the ink itself: the dollar sign
    and the cents are raised, so only the dollar digits put ink in the bottom third of the box.
    Returns (dollars_box, cents_box) in image pixels, or None."""
    import numpy as np
    l, t, r, b = [int(v) for v in box]
    l, t, r, b = max(0, l), max(0, t), min(img.width, r), min(img.height, b)
    if r - l < 8 or b - t < 8:
        return None
    a = np.asarray(img.crop((l, t, r, b)), dtype=np.float32)
    thr = a.mean()
    dark = (a < thr)
    ink = (dark if dark.mean() < 0.5 else ~dark).astype(np.float32)  # the minority shade is the text
    H, W = ink.shape
    bottom = ink[int(H * 0.70):, :].mean(axis=0)
    anyink = ink.mean(axis=0)
    cols = np.where(bottom > 0.04)[0]
    if len(cols) == 0:
        return None
    # the dollars span: the widest run of bottom ink columns, allowing small gaps between digits
    runs, start = [], cols[0]
    for i in range(1, len(cols)):
        if cols[i] - cols[i - 1] > max(3, H * 0.25):
            runs.append((start, cols[i - 1])); start = cols[i]
    runs.append((start, cols[-1]))
    d0, d1 = max(runs, key=lambda x: x[1] - x[0])
    # cents: any ink to the right of the dollars
    right = np.where(anyink[d1 + 1:] > 0.03)[0]
    cents = None
    if len(right):
        c0 = d1 + 1 + right[0]; c1 = d1 + 1 + right[-1]
        if c1 - c0 >= H * 0.15:
            cents = (l + c0 - 2, t - 2, l + c1 + 3, t + int(H * 0.68))
    m = max(2, int(H * 0.06))
    return (l + d0 - m, t, l + d1 + m + 1, b), cents


def price_readings(img, path, L, ez, pt, cfg=None):
    """Three independent readings of one display price box: whole box, fixed windows, ink split.
    Returns {"whole": v, "windows": v, "ink": v} with None where a method gave nothing."""
    l, t, r, b = L["box"]
    w, h = r - l, b - t
    out = {"raw": None, "whole": None, "windows": None, "ink": None}
    out["raw"] = _best_numeric(dict(L, alt_num=[]))  # the page read as it came
    reread_boxes(path, [L], allowlist="0123456789$", pad=0.08, cfg=cfg)
    out["whole"] = _best_numeric(dict(L, text="", conf=0, alt_num=L.get("alt_num", [])))
    has_sign = L["text"][:1] in "$5sS§8"
    dwin = (0.26, 0.60) if has_sign else (0.0, 0.58)
    d = _vote(_read_digits(img, (l + dwin[0] * w, t, l + dwin[1] * w, b), ez, pt))
    c = _vote(_read_digits(img, (l + 0.58 * w, t - 0.08 * h, r + 0.04 * w, t + 0.62 * h), ez, pt))
    if d and len(d) <= 3 and len(c) >= 2:
        out["windows"] = int(d) + int(c[:2]) / 100.0
    if cfg and cfg.get("ink_split"):  # experimental: off by default, the windows read scores the same
        parts = _split_price_box(img, L["box"])
        if parts:
            dbox, cbox = parts
            d = _vote(_read_digits(img, dbox, ez, pt))
            c = _vote(_read_digits(img, cbox, ez, pt)) if cbox else ""
            if d and len(d) <= 3 and len(c) >= 2:
                out["ink"] = int(d) + int(c[:2]) / 100.0
    return out


def settle_price(reads):
    """Pick one value from the three readings: majority first, then the pairing of dollars and cents that
    most readings support, then the whole box reading."""
    vals = [v for v in reads.values() if v is not None]
    if not vals:
        return None
    for v in vals:
        if vals.count(v) >= 2:
            return v
    dollars = [int(v) for v in vals]
    cents = [round((v - int(v)) * 100) for v in vals]
    dol = max(set(dollars), key=dollars.count)
    if dollars.count(dol) >= 2:
        cen = [cents[i] for i in range(len(vals)) if dollars[i] == dol]
        c = max(set(cen), key=cen.count)
        return dol + c / 100.0
    for k in ("raw", "whole", "windows"):
        if reads.get(k) is not None:
            return reads[k]
    return vals[0]


def reread_prices(path, lines, h0, cfg=None):
    """Display type prices ("$6" with a raised "69") get three independent re-reads and a vote."""
    from PIL import Image
    cands = [L for L in lines if L["h"] >= 1.35 * h0 and re.search(r"\d", L["text"]) and len(L["text"]) <= 8
             and not _SIZELINE.match(L["text"]) and not _PACK.match(L["text"])]
    if not cands:
        return
    img = Image.open(path).convert("L")
    ez = _easyocr()
    pt = _tesseract_ok((cfg or {}).get("tesseract"))
    for L in cands:
        l, t, r, b = L["box"]
        if r - l < 1.2 * (b - t):  # a lone digit box (pack count, or cents split off); leave it
            continue
        reads = price_readings(img, path, L, ez, pt, cfg)
        val = settle_price(reads)
        L["price_reads"] = reads
        if val is not None and 0 < val <= 500:
            L["text"] = "$%d%02d" % (int(val), round((val - int(val)) * 100))
            agree = len({v for v in reads.values() if v is not None}) == 1
            L["conf"] = 0.85 if agree else 0.4  # a disagreement between the two reads is what the weekly check looks at


def lines_to_items(lines, default_section="Grocery", path=None, cfg=None):
    """Pair every price with the stack of name lines directly above it (brand, product, size)."""
    lines, h0 = _norm_lines(lines)
    if path:
        reread_prices(path, lines, h0, cfg)
    prices, used = _find_prices(lines, h0)
    prices.sort(key=lambda P: (P["box"][1], P["box"][0]))
    lines = _merge_packs(lines, h0)
    text_lines = [L for L in lines if id(L) not in used and not _BIGPRICE.match(L["text"]) and not _DIGITS.match(L["text"])
                  and not _EACH.match(L["text"]) and (L["h"] < 1.6 * h0 or (L["h"] < 2.8 * h0 and re.search(r"[A-Za-z]{3}", L["text"])))]
    sections = [L for L in text_lines if _SECTION.match(L["text"]) and L["h"] >= 1.3 * h0]
    taken = set()
    items = []
    for P in prices:
        l, t, r, b = P["box"]
        w = r - l
        col = (l - 0.6 * w, r + 0.4 * w)  # the column this price belongs to
        cands = []
        for L in text_lines:
            if id(L) in taken or L in sections:
                continue
            cx = (L["box"][0] + L["box"][2]) / 2.0
            ox = min(L["box"][2], col[1]) - max(L["box"][0], col[0])  # horizontal overlap with the column
            above = t - L["box"][3]
            beside = _overlap_y(P["box"], L["box"]) > 0.4 * L["h"] and (
                (L["box"][2] <= l + 0.2 * w and l - L["box"][2] < 0.6 * w) or (L["box"][0] >= r - 0.2 * w and L["box"][0] - r < 0.8 * w))
            if (ox > 0.6 * L["w"] or col[0] <= cx <= col[1]) and (-0.5 * L["h"] <= above <= 7.5 * h0 or beside):
                if _owner(L, prices) is P:
                    cands.append(L)
        cands.sort(key=lambda L: (-L["box"][3]))  # nearest the price first, walking upward
        stack = []
        last_top = t
        for L in cands:
            gap = last_top - L["box"][3]
            if gap > 2.2 * h0 and stack:
                break
            stack.append(L)
            last_top = min(last_top, L["box"][1])
            if len(stack) >= 6:
                break
        if not stack:
            continue
        stack.sort(key=lambda L: (int(((L["box"][1] + L["box"][3]) / 2) // (0.7 * h0)), L["box"][0]))  # by row, then left to right
        for L in stack:
            taken.add(id(L))
        packs = [L for L in stack if _PACK.match(L["text"])]
        sizes = [L["text"] for L in stack if _SIZELINE.match(L["text"]) and L not in packs]
        names = [L["text"] for L in stack if L["text"] not in sizes and L not in packs and not _gibberish(L)]
        name = clean_name(" ".join(names))
        unit = " ".join(re.sub(r"[\s_:.]+$", "", x) for x in sizes)
        pack = next((m.group(1) for m in (_PACK.match(L["text"]) for L in packs) if m and m.group(1)), "")
        if pack:
            unit = ("%s pack" % pack + (", " + unit if unit else ""))
        if P["multi"]:
            unit = (unit + " " if unit else "") + "(multi-buy, price each)"
        reg = next((_REG.search(L["text"]) for L in stack if _REG.search(L["text"])), None)
        regular = float("%s.%s" % (reg.group(1), reg.group(2))) if reg else None
        sec = default_section
        for S in sorted(sections, key=lambda S: S["box"][1]):
            if S["box"][1] <= t:
                sec = S["text"].title().replace("'S", "'s")
        if len(name) < 3:
            continue
        items.append({"section": sec, "item": name[:90], "unit": unit, "regular": regular, "price": P["val"],
                      "conf": round(min([P["conf"]] + [L["conf"] for L in stack]), 2)})
    seen, out = set(), []
    for it in items:
        k = (it["item"].lower(), it["price"])
        if k not in seen:
            seen.add(k); out.append(it)
    return out


def _gibberish(L):
    """Brand logos come back as 'FTTvHv8' or 'GampGelli': low confidence, or letters mixed with digits."""
    t = L["text"]
    if re.search(r"[A-Za-z]\d|\d[A-Za-z]", t) and not _SIZELINE.match(t):
        return True
    if L["conf"] < 0.5 and (" " not in t.strip() or re.search(r"[a-z][A-Z]", t)):
        return True
    return False


def clean_name(s):
    s = re.sub(r"\b(ea|each)[.:]?\b", " ", s, flags=re.I)
    s = re.sub(r"[_~`|]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" ,-.:")
    # ALL CAPS brand lines read better in title case
    return " ".join(w.title() if (w.isupper() and len(w) > 3) else w for w in s.split())


def read_flyer(image_paths, cfg=None, default_section="Grocery"):
    all_items, meta = [], {"images": [], "readers": set()}
    for p in image_paths:
        if not os.path.exists(p):
            continue
        r = read_image(p, cfg)
        items = lines_to_items(r["lines"], default_section, path=p, cfg=cfg)
        meta["images"].append({"file": os.path.basename(p), "lines": len(r["lines"]), "low": r["low"], "items": len(items)})
        meta["readers"].update(r["readers"])
        all_items.extend(items)
    meta["readers"] = sorted(meta["readers"])
    return all_items, meta


def write_store(store, source, valid, items, meta, data_dir, log=print):
    """Always write <store>_ocr.json; replace <store>.json only when it is for an older flyer or empty."""
    fdir = os.path.join(data_dir, "flyers")
    os.makedirs(fdir, exist_ok=True)
    today = dt.date.today().isoformat()
    doc = {"source": source, "valid": valid, "read": today, "by": "ocr", "items": items, "ocr": meta}
    with open(os.path.join(fdir, "%s_ocr.json" % store), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    cur_path = os.path.join(fdir, "%s.json" % store)
    cur = {}
    if os.path.exists(cur_path):
        try:
            cur = json.load(open(cur_path, encoding="utf-8"))
        except Exception:
            cur = {}
    newest = (source or "").split()[0] if source else ""
    same_flyer = bool(newest) and newest in (cur.get("source") or "")
    hand_read = cur.get("items") and cur.get("by") != "ocr"
    enough = len(items) >= max(15, int(0.5 * len(cur.get("items") or [])))  # a thin read never replaces a full one
    if items and (not cur.get("items") or (not same_flyer and enough and not (hand_read and not enough))):
        with open(cur_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        log("OCR %s: %d items from %d images (%s), written to %s.json" % (store, len(items), len(meta["images"]), "+".join(meta["readers"]), store))
    else:
        log("OCR %s: %d items from %d images (%s); %s.json kept (%s)" % (store, len(items), len(meta["images"]), "+".join(meta["readers"]), store,
                                                                       "same flyer already transcribed" if same_flyer else "no items read"))


def run(lindos_posts, supermart_flyer, root, cfg=None, log=print):
    """Called by collect.py after the flyer images are downloaded."""
    cfg = cfg or {}
    data_dir = os.path.join(root, "data")
    if lindos_posts and lindos_posts.get("posts"):
        posts = lindos_posts["posts"]
        paths = [os.path.join(root, im["file"]) for p in posts for im in p.get("images", [])]
        items, meta = read_flyer(paths, cfg)
        write_store("lindos", " ".join(p["post"] for p in posts), posts[0].get("valid") or "", items, meta, data_dir, log)
    if supermart_flyer and supermart_flyer.get("images"):
        paths = [os.path.join(root, im["file"]) for im in supermart_flyer["images"]]
        items, meta = read_flyer(paths, cfg)
        write_store("supermart", supermart_flyer.get("range") or "", supermart_flyer.get("range") or "", items, meta, data_dir, log)


if __name__ == "__main__":  # python -m bgd.ocr <image> ... : print what the readers see, for checking a flyer by hand
    import sys
    for p in sys.argv[1:]:
        r = read_image(p)
        print("== %s: %d lines, %d low confidence, readers %s" % (p, len(r["lines"]), r["low"], r["readers"]))
        for L in sorted(r["lines"], key=lambda L: (L["box"][1], L["box"][0])):
            print("  %.2f %-10s %s" % (L["conf"], L["reader"], L["text"]))
        print("-- items:")
        for it in lines_to_items(r["lines"], path=p):
            print("  %-16s %-50s %-10s %7.2f %s" % (it["section"], it["item"], it["unit"], it["price"], it["conf"]))
