"""Bermuda Hub Atlantic Explorer probe: saves the BIOS cruise schedule and what Python can read from it.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.0
Last Updated: 2026-11-23

Change Log
  1.0 2026-11-23  First release. A one off test, so the right schedule reader can be written for run.py.

What it does
  Opens the BIOS cruise schedule page, finds the schedule files it links to (one PDF per year), downloads the
  newest two, and saves every word on each page with its position, plus every coloured box with its colour.
  The schedule is a calendar grid (days down the side, months across the top), so positions are what a reader
  needs to tell which day and month each entry belongs to.

Depends on
  The internet. pdfplumber (installed earlier by install_pdf_and_read_menus.bat). Python's standard library.

Writes
  .cache/ae_probe/  page.html, the PDF files, and for each PDF a words file and a boxes file (tab separated),
  plus index.txt saying what was found. The .cache folder is ignored by git.

Run
  In the terminal: .\\ae_probe.bat
"""
import os
import re
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, ".cache", "ae_probe")
PAGE = "https://bios.asu.edu/ship-ops/cruise-schedule"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


def fetch(url):
    """Returns the bytes at a web address."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    os.makedirs(OUT, exist_ok=True)
    notes = []
    try:
        html = fetch(PAGE)
    except Exception as e:  # the probe reports the failure and stops
        notes.append("page: could not be fetched: %r" % (e,))
        open(os.path.join(OUT, "index.txt"), "w", encoding="utf-8").write("\n".join(notes) + "\n")
        print(notes[-1])
        return
    open(os.path.join(OUT, "page.html"), "wb").write(html)
    text = html.decode("utf-8", "replace")
    links = []
    for m in re.finditer(r'<a[^>]+href="([^"]+\.pdf)"[^>]*>(.*?)</a>', text, flags=re.I | re.S):
        label = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if "schedule" in label.lower() or "schedule" in m.group(1).lower() or "AE_" in m.group(1):
            links.append((label, urllib.parse.urljoin(PAGE, m.group(1))))
    notes.append("page: %d bytes, %d schedule links" % (len(html), len(links)))
    for label, url in links:
        notes.append("link: %s | %s" % (label, url))
    try:
        import pdfplumber
    except Exception as e:
        notes.append("pdfplumber is not installed: %r" % (e,))
        pdfplumber = None
    for n, (label, url) in enumerate(links[:2]):
        name = "schedule_%d" % n
        try:
            data = fetch(url)
        except Exception as e:
            notes.append("%s: could not be fetched: %r" % (name, e))
            continue
        path = os.path.join(OUT, name + ".pdf")
        open(path, "wb").write(data)
        notes.append("%s: %s, %d bytes" % (name, label, len(data)))
        if not pdfplumber:
            continue
        try:
            with pdfplumber.open(path) as pdf:
                words, boxes = [], []
                for pn, page in enumerate(pdf.pages):
                    notes.append("%s page %d: %.0f wide, %.0f high" % (name, pn, page.width, page.height))
                    for w in page.extract_words(keep_blank_chars=False, use_text_flow=False):
                        words.append("%d\t%.1f\t%.1f\t%.1f\t%.1f\t%s" % (pn, w["x0"], w["top"], w["x1"], w["bottom"], w["text"]))
                    for r in page.rects:
                        boxes.append("%d\t%.1f\t%.1f\t%.1f\t%.1f\t%s" % (pn, r["x0"], r["top"], r["x1"], r["bottom"], r.get("non_stroking_color")))
                open(os.path.join(OUT, name + "_words.tsv"), "w", encoding="utf-8").write("\n".join(words) + "\n")
                open(os.path.join(OUT, name + "_boxes.tsv"), "w", encoding="utf-8").write("\n".join(boxes) + "\n")
                notes.append("%s: %d words, %d boxes" % (name, len(words), len(boxes)))
        except Exception as e:
            notes.append("%s: could not be read: %r" % (name, e))
    open(os.path.join(OUT, "index.txt"), "w", encoding="utf-8").write("\n".join(notes) + "\n")
    print("\n".join(notes))


if __name__ == "__main__":
    main()
