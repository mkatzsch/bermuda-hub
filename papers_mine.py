"""Papers miner: lists research papers about Bermuda and the Sargasso Sea, for a person to check.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.0
Last Updated: 2026-11-24

Change Log
  1.0 2026-11-24  First release. Asks Crossref (free, no key) for three lists: papers from the Bermuda
                  Institute of Ocean Sciences in the last two years, recent papers with Bermuda or Sargasso
                  in the title, and the most cited Bermuda papers of all time. When OPENALEX_API_KEY is in
                  .env it also asks OpenAlex for recent papers that mention Bermuda in the title or summary.
                  Writes everything to events/data/papers_candidates.json. Nothing here reaches the Hub by
                  itself: a paper is read and described in our own words before it goes on a card.
                  Written without a live test (the laptop was locked): check the first run's log.

Depends on: Python 3.9 or later (standard library only) and the internet (api.crossref.org, and
api.openalex.org when a key is set). Run it with papers_mine.bat. The OpenAlex key is free: make an account
at openalex.org, copy the key from its settings page and add the line OPENALEX_API_KEY=... to .env.
"""
import datetime as dt
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "events", "data", "papers_candidates.json")
ENV = os.path.join(ROOT, ".env")
UA = "BermudaHub/1.0 (+https://github.com/mkatzsch/bermuda-hub)"
WORDS = ("bermuda", "sargasso")  # a title must carry one of these to be kept by the title searches
SKIP = ("bermudagrass", "bermuda grass", "bermuda-grass", "cynodon")  # the lawn grass, not the island
YEARS_BACK = 2
CROSSREF = "https://api.crossref.org/works"
OPENALEX = "https://api.openalex.org/works"
FIELDS = "DOI,title,container-title,issued,author,is-referenced-by-count,type"


def env_key(name):
    """One value from .env (lines of NAME=value), or an empty string. The value is never printed."""
    if not os.path.exists(ENV):
        return ""
    with open(ENV, encoding="utf-8") as f:
        for line in f:
            k, sep, v = line.strip().partition("=")
            if sep and k.strip() == name:
                return v.strip().strip('"').strip("'")
    return ""


def get(url, params):
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def tidy(text):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", str(text or ""))).strip()


def crossref_row(it, found):
    parts = ((it.get("issued") or {}).get("date-parts") or [[None]])[0]
    date = "-".join("%02d" % p if i else "%04d" % p for i, p in enumerate(parts) if p)
    authors = [tidy("%s %s" % (a.get("given", ""), a.get("family", ""))) for a in (it.get("author") or [])]
    return {"doi": it.get("DOI", ""), "title": tidy((it.get("title") or [""])[0]),
            "journal": tidy((it.get("container-title") or [""])[0]), "date": date,
            "authors": [a for a in authors if a][:6], "cited": it.get("is-referenced-by-count", 0),
            "type": it.get("type", ""), "found": found,
            "link": "https://doi.org/" + it["DOI"] if it.get("DOI") else ""}


def crossref(found, params, title_words=True):
    params = dict(params, select=FIELDS, rows=200, mailto="hub@users.noreply.github.com")
    items = (get(CROSSREF, params).get("message") or {}).get("items") or []
    rows = [crossref_row(it, found) for it in items]
    if title_words:
        rows = [r for r in rows if any(w in r["title"].lower() for w in WORDS)]
    rows = [r for r in rows if not any(w in r["title"].lower() for w in SKIP)]
    print("%s: %d kept of %d" % (found, len(rows), len(items)))
    return rows


def openalex(key, since):
    data = get(OPENALEX, {"filter": "title_and_abstract.search:bermuda,from_publication_date:" + since,
                          "sort": "publication_date:desc", "per-page": 100, "api_key": key,
                          "select": "doi,title,publication_date,primary_location,authorships,cited_by_count,type"})
    rows = []
    for w in data.get("results") or []:
        doi = str(w.get("doi") or "").replace("https://doi.org/", "")
        src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name", "")
        names = [tidy(((a.get("author") or {}).get("display_name"))) for a in (w.get("authorships") or [])]
        rows.append({"doi": doi, "title": tidy(w.get("title")), "journal": tidy(src), "date": w.get("publication_date") or "",
                     "authors": [n for n in names if n][:6], "cited": w.get("cited_by_count", 0), "type": w.get("type", ""),
                     "found": "openalex recent", "link": "https://doi.org/" + doi if doi else ""})
    print("openalex recent: %d" % len(rows))
    return rows


def main():
    since = (dt.date.today() - dt.timedelta(days=365 * YEARS_BACK)).isoformat()
    jobs = [("bios recent", {"query.affiliation": "Bermuda Institute of Ocean Sciences", "filter": "from-pub-date:" + since,
                             "sort": "issued", "order": "desc"}, False),
            ("title recent", {"query.bibliographic": "Bermuda Sargasso", "filter": "from-pub-date:" + since + ",type:journal-article",
                              "sort": "issued", "order": "desc"}, True),
            ("most cited", {"query.bibliographic": "Bermuda", "filter": "type:journal-article",
                            "sort": "is-referenced-by-count", "order": "desc"}, True)]
    rows = []
    for found, params, title_words in jobs:
        try:
            rows += crossref(found, params, title_words)
        except Exception as e:  # one list failing must not lose the others
            print("%s: failed (%s)" % (found, str(e)[:160]))
        time.sleep(1)
    key = env_key("OPENALEX_API_KEY")
    if key:
        try:
            rows += openalex(key, since)
        except Exception as e:
            print("openalex recent: failed (%s)" % str(e)[:160].replace(key, "***"))
    else:
        print("openalex: skipped, no OPENALEX_API_KEY in .env")
    seen, out = set(), []
    for r in rows:  # the same paper can turn up in more than one list: keep the first
        k = r["doi"].lower() or r["title"].lower()
        if k and k not in seen and r["title"]:
            seen.add(k)
            out.append(r)
    doc = {"read": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "since": since,
           "how": "Lists from Crossref and OpenAlex. Candidates only: read the paper's summary and write the card in our own words.",
           "papers": out}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print("%d papers written to %s" % (len(out), OUT))


if __name__ == "__main__":
    main()
