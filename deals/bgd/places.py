"""Island restaurant directory: every place that serves food, from OpenStreetMap, merged with the Sargasso Sea list.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.0
Last Updated: 2026-11-17

Change Log
  1.0  2026-11-17  First release. One Overpass query for amenity=restaurant, fast_food, cafe, bar, pub, food_court,
                   ice_cream inside Bermuda (name, cuisine, website, Facebook, phone, address, coordinates), merged
                   by name with the Sargasso Sea storefront list so each place carries its Sargasso id when it has
                   one. Writes data/places.json; collect.py refreshes it with --places or every 28 days.

Dependencies: requests (ships with Anaconda). No key needed; Overpass asks for one query at a time, so this is
never run more often than monthly. Reads data/<date>/sargasso_stores.json when it exists.
"""
import os, re, json, difflib, datetime as dt
from .util import log, get, DATA, save_json, load_json

OVERPASS = ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter")
QUERY = """[out:json][timeout:90];
area["name"="Bermuda"]["admin_level"="2"]->.a;
( node["amenity"~"^(restaurant|fast_food|cafe|bar|pub|food_court|ice_cream)$"](area.a);
  way["amenity"~"^(restaurant|fast_food|cafe|bar|pub|food_court|ice_cream)$"](area.a); );
out center tags;"""


def norm(s):
    s = (s or "").lower()
    s = re.sub(r"\b(the|restaurant|bar|grill|grille|cafe|café|bistro|and|&|ltd|bermuda|bda)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def osm():
    last = None
    for url in OVERPASS:
        try:
            r = get(url, timeout=120, params={"data": QUERY})
            r.raise_for_status()
            els = r.json()["elements"]
            break
        except Exception as e:
            last = e; els = None
    if els is None:
        raise RuntimeError("Overpass failed: %s" % last)
    out = []
    for e in els:
        t = e.get("tags") or {}
        if not t.get("name"):
            continue
        c = e.get("center") or {}
        fb = t.get("contact:facebook") or ""
        if fb and not fb.startswith("http"):
            fb = "https://www.facebook.com/" + fb.strip("/")
        out.append({"osm": "%s/%s" % (e["type"], e["id"]), "name": t["name"], "type": t.get("amenity"), "cuisine": t.get("cuisine") or "",
                    "website": t.get("website") or t.get("contact:website") or "", "facebook": fb,
                    "instagram": t.get("contact:instagram") or "", "phone": t.get("phone") or t.get("contact:phone") or "",
                    "street": t.get("addr:street") or "", "city": t.get("addr:city") or "", "hours": t.get("opening_hours") or "",
                    "lat": e.get("lat") or c.get("lat"), "lon": e.get("lon") or c.get("lon"), "sargasso_id": None, "sargasso_name": ""})
    log("OSM: %d food places in Bermuda" % len(out))
    return out


def merge(places, stores):
    """Attach Sargasso ids by name; add Sargasso-only places so the directory is the union."""
    byn = {norm(p["name"]): p for p in places}
    keys = list(byn)
    added = 0
    for s in stores or []:
        if "Restaurants" not in (s.get("cat") or "") and "Pantry" not in (s.get("cat") or ""):
            continue
        k = norm(s["n"])
        hit = byn.get(k)
        if not hit:
            m = difflib.get_close_matches(k, keys, n=1, cutoff=0.82)
            hit = byn[m[0]] if m else None
        if hit:
            hit["sargasso_id"], hit["sargasso_name"] = s["id"], s["n"]
        else:
            p = {"osm": "", "name": s["n"], "type": "sargasso", "cuisine": s.get("cat") or "", "website": "", "facebook": "", "instagram": "",
                 "phone": s.get("ph") or "", "street": s.get("addr") or "", "city": "", "hours": "", "lat": None, "lon": None,
                 "sargasso_id": s["id"], "sargasso_name": s["n"]}
            places.append(p); byn[k] = p; keys.append(k); added += 1
    log("Places: %d with a Sargasso id, %d Sargasso-only places added" % (sum(1 for p in places if p["sargasso_id"]), added))
    return places


def run(d, stores=None):
    places = merge(osm(), stores)
    places.sort(key=lambda p: p["name"].lower())
    out = {"read": d.isoformat(), "count": len(places), "places": places}
    save_json(os.path.join(DATA, "places.json"), out)
    log("Places: %d written to data/places.json (%d with a website, %d with Facebook)" % (
        len(places), sum(1 for p in places if p["website"]), sum(1 for p in places if p["facebook"])))
    return out
