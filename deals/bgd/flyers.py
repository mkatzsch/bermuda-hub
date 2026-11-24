"""Lindo's and Supermart flyers (images only) and Price Rite deals page.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.2
Last Updated: 2026-11-15

Change Log
  1.2  2026-11-15  Skip Lindo's sidebar brand adverts (monthly/advert in the file name).
  1.1  2026-11-15  Supermart heading is "Weekly Specials | 11/11 - 11/15"; read that form first.
  1.0  2026-11-15  First release.

The prices in these flyers live inside pictures, so this module only finds the newest flyer posts,
downloads the images into flyers/, and records which post or date range is current. A separate
weekly step (Claude) reads the images and writes data/flyers/lindos.json and supermart.json.
"""
import os, re
from bs4 import BeautifulSoup
from .util import get, log, download, FLYERS, slug


def lindos(max_posts=4):
    """Newest '<month>-<day>-<year>-specials' posts on lindos.bm with their images."""
    out = {"posts": []}
    try:
        r = get("https://lindos.bm/")
        links = re.findall(r'https?://lindos\.bm/([a-z]+-\d{1,2}-\d{4}-specials[^"\'\s]*)/?', r.text)
        seen = []
        for l in links:
            l = l.strip("/")
            if l not in seen:
                seen.append(l)
        for post in seen[:max_posts]:
            try:
                pr = get("https://lindos.bm/%s/" % post)
                soup = BeautifulSoup(pr.text, "html.parser")
                imgs = []
                for img in soup.select("article img, .entry-content img, main img, img"):
                    src = img.get("data-src") or img.get("src") or ""
                    if not re.search(r"\.(jpe?g|png|webp)(\?|$)", src, re.I) or re.search(r"logo|icon|\-\d+x\d+\.|monthly|advert", src, re.I):
                        continue
                    if src in imgs:
                        continue
                    imgs.append(src)
                files = []
                for src in imgs:
                    fn = os.path.join(FLYERS, "lindos", post, os.path.basename(src.split("?")[0]))
                    try:
                        new = download(src, fn)
                        files.append({"file": os.path.relpath(fn, os.path.dirname(FLYERS)), "url": src, "new": new})
                    except Exception as e:
                        log("Lindo's image failed %s: %s" % (src, e))
                text = soup.get_text(" ", strip=True)
                valid = re.search(r"(valid|prices?)[^.]{0,40}?(until|to|thru|through)\s+([A-Z][a-z]+\.? ?\d{1,2}(?:,? \d{4})?)", text)
                out["posts"].append({"post": post, "url": "https://lindos.bm/%s/" % post, "images": files, "valid": valid.group(3) if valid else ""})
            except Exception as e:
                log("Lindo's post %s failed: %s" % (post, e))
        log("Lindo's: %d posts, %d images" % (len(out["posts"]), sum(len(p["images"]) for p in out["posts"])))
    except Exception as e:
        log("Lindo's failed: %s" % e)
    return out


def supermart():
    out = {"range": "", "images": []}
    try:
        r = get("https://www.supermart.bm/weekly-specials")
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        m = re.search(r"Weekly Specials\s*\|\s*(\d{1,2}/\d{1,2}\s*-\s*\d{1,2}/\d{1,2})", text) or \
            re.search(r"([A-Z][a-z]+ \d{1,2}(?:st|nd|rd|th)?\s*(?:-|to|–)\s*(?:[A-Z][a-z]+ )?\d{1,2}(?:st|nd|rd|th)?(?:,? \d{4})?)", text)
        out["range"] = m.group(1).replace(" ", "") if m else ""
        srcs = re.findall(r'(https://static\.wixstatic\.com/media/[^"\'\s)]+~mv2\.(?:png|jpe?g|webp))', r.text)
        seen = []
        for s in srcs:
            base = re.sub(r"/v1/.*$", "", s)  # drop wix resize suffix to get the full image
            if base not in seen:
                seen.append(base)
        for s in seen[:4]:
            fn = os.path.join(FLYERS, "supermart", slug(out["range"] or "current") + "-" + os.path.basename(s))
            try:
                new = download(s, fn)
                out["images"].append({"file": os.path.relpath(fn, os.path.dirname(FLYERS)), "url": s, "new": new})
            except Exception as e:
                log("Supermart image failed %s: %s" % (s, e))
        log("Supermart: range '%s', %d images" % (out["range"], len(out["images"])))
    except Exception as e:
        log("Supermart failed: %s" % e)
    return out


def pricerite():
    out = {"text": ""}
    try:
        r = get("https://pricerite.bm/deals-2/")
        soup = BeautifulSoup(r.text, "html.parser")
        main = soup.find("main") or soup.body
        out["text"] = main.get_text("\n", strip=True)[:4000] if main else ""
        log("Price Rite: %d chars" % len(out["text"]))
    except Exception as e:
        log("Price Rite failed: %s" % e)
    return out
