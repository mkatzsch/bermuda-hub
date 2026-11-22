"""Source scrapers. Each exposes fetch(cfg) -> list[Listing].

Developed by AiTide Ltd. | www.AiTide.com
Version: 0.2
Last Updated: 2026-11-21

A Listing is a plain dict with:
  date (datetime.date), end (date or None), name, time (short like '7pm'), time_text, venue, cost,
  ages, note, link, source, source_key, raw (the text the parser saw, kept for debugging and for
  the optional model classifier)
Scrapers never decide the view or category; classify.py does that from the text.
"""
from . import ptix, gotobermuda, cinema, runsignup, sky, gpass  # noqa: F401

REGISTRY = {
    "ptix": ptix.fetch,
    "gotobermuda": gotobermuda.fetch,
    "runsignup": runsignup.fetch,
    "gpass": gpass.fetch,
}
