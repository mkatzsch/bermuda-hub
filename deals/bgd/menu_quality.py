"""Decide which machine read restaurant menus are clean enough to show, and tidy the ones that are.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.0
Last Updated: 2026-11-22

Change Log
  1.0  2026-11-22  First release. The website reader (bgd/menus_own.py) gets prices from many sites, but some of what
                   it reads is not a menu: review dates, half sentences of description, and garbled text from
                   pictures. good_name() says whether a line reads like a dish; tidy() keeps the good lines of one
                   restaurant and says whether enough survive for the menu to be shown on the page.

Depends on: nothing outside the standard library, so build.py can use it offline.
Used by: build.py (to choose what reaches the Eats page).
"""
import re

MONTH = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
BAD = re.compile(r"\d{1,2}:\d{2}|[\u2013\u2014]{2,}|\b" + MONTH + r"\b\s*\d|\d\s*\b" + MONTH + r"\b|\s{3,}|[|_{}<>=~^]|https?:|www\.|@|\bcopyright\b|\ball rights\b", re.I)
FRAGMENT = re.compile(r"^(with|served|add|and|or|choice|choose|your|topped|in|on|for|per|plus|extra|each|all|our|includes?|please|ask|available)\b", re.I)
SIZE_ONLY = {"half", "whole", "small", "medium", "large", "regular", "single", "double", "glass", "bottle", "lunch", "dinner",
             "cup", "bowl", "pint", "side", "menu", "price", "prices", "each", "kids", "adult", "adults"}


DESCRIBES = re.compile(r"\b(served|topped|drizzled|marinated|tossed|garnished|sprinkled)\b", re.I)
TAIL = re.compile(r"[\s.:,_\-\u2013\u2014]+$")


def clean_name(name):
    """The line without the row of dashes or dots that led to its price."""
    return TAIL.sub("", re.sub(r"\s+", " ", name or "")).strip(" .:-,")


def good_name(name, from_picture=False):
    """True when a line reads like the name of a dish or a drink."""
    n = clean_name(name)
    if not 3 <= len(n) <= 60 or BAD.search(TAIL.sub("", name or "")) or DESCRIBES.search(n):
        return False
    if sum(c.isalpha() or c in " ()&'/" for c in n) / len(n) < 0.8 or len(re.findall(r"\d", n)) > 3:
        return False
    words = n.split()
    if len(words) > 8 or FRAGMENT.match(n) or n.lower() in SIZE_ONLY:
        return False
    if from_picture and len(words) >= 4 and sum(1 for w in words if len(w) <= 2) / len(words) > 0.4:
        return False  # picture text read badly comes out as a run of one and two letter scraps
    if len(set(w.lower() for w in words)) < len(words) * 0.7:
        return False  # the same word over and over: two columns of a picture read as one line
    return True


def tidy(entry):
    """Return (cats, good, total, ok) for one restaurant: its dish lines, how many there are, and whether to show it."""
    cats, good, total, seen = [], 0, 0, set()
    pic = "image" in (entry.get("kind") or "")
    for cat, items in entry.get("cats") or []:
        keep = []
        for it in items:
            total += 1
            name = clean_name(str(it[0]))
            key = (name.lower(), it[1])
            if good_name(str(it[0]), pic) and 1 <= float(it[1]) <= 250 and key not in seen:
                seen.add(key)
                keep.append([name, it[1]])
        if keep:
            label = cat if good_name(cat) and cat not in ("Menu", "More") else "Menu"
            if cats and cats[-1][0] == label:
                cats[-1][1].extend(keep)
            else:
                cats.append([label, keep])
            good += len(keep)
    need = 0.8 if pic else 0.7
    ok = good >= 8 and total and good / total >= need
    return cats, good, total, bool(ok)
