"""Bermuda weather for the Hub: Bermuda Weather Service forecasts, warnings, tides, observations and radar, plus an hourly model.

Developed by AiTide Ltd. | www.AiTide.com
Version: 0.3
Last Updated: 2026-11-22

Change Log
  0.3  2026-11-22  Radar: the frame file names on the 100 km animation page are kept in weather.json (radar.dir and
                   radar.frames) so the GitHub Pages copy of the Hub can play the live animation.
  0.2  2026-11-21  Parsers written against the real BWS pages: div.periodElement blocks (h4 "Today -" then text) on
                   the public and marine forecasts, headline and synopsis, warnings and their validity, climate data
                   (sea surface, max, min, rain), the monthly tide table (time | m / ft, four a day), the airport
                   observations table, sunrise and sunset from the marine periods. Radar: the animation pages are
                   fetched and kept raw; the tab links to them live.
  0.1  2026-11-21  Discovery release.

Sources (all public, Bermuda Weather Service unless noted):
  https://weather.bm/ForecastpublicExtended.asp       public forecast, 5 days, headline, synopsis, UV, climate data
  https://weather.bm/forecastMarineExtended.asp       marine forecast, winds in knots, seas inside and outside the reef
  https://weather.bm/currentwarnings.asp              current watches and warnings
  https://weather.bm/observations.asp                 airport observations, hourly
  https://weather.bm/Tools/TideTimes.asp?Month=&Year= tide times, St George's, a month at a time
  https://weather.bm/radar.asp and /tools/graphics.asp?name=100KM SRI (CROPPED)  radar animation pages
  https://api.open-meteo.com/v1/forecast              hourly temperature, rain chance, wind, UV (free, no key)

Output: data/weather.json and meta "weather":
  {asof, issued, next_update, headline, synopsis, warnings: [{title, valid}], forecast: [{label, lines, high, low, uv}],
   marine: {synopsis, periods: [{label, lines, sunrise, sunset}]}, climate: {sea_surface, max, min, rain_yesterday,
   rain_month, sunshine}, now: {time, sky, wind, temp, rh, pressure}, tides: [{date, day, events: [{time, m, ft, kind}]}],
   radar: {page, links: [{name, url}], dir, frames: [file name]}, hourly: [{t, temp, rain, mm, wind, dir, uv}], days: [...], raw_pages: [...]}
Dependencies: requests, beautifulsoup4, lxml.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from ..util import UA, clean, get

BASE = "https://weather.bm/"
PAGES = {
    "home": BASE,
    "forecast": BASE + "ForecastpublicExtended.asp",
    "marine_extended": BASE + "forecastMarineExtended.asp",
    "warnings": BASE + "currentwarnings.asp",
    "warnings_detail": BASE + "forecastWarningsExtended.asp",
    "observations": BASE + "observations.asp",
    "radar": BASE + "radar.asp",
    "radar_100": BASE + "tools/graphics.asp?name=100KM%20SRI%20%28CROPPED%29&user=",
}
RADAR_LINKS = [
    {"name": "Radar, 100 km animation", "url": BASE + "tools/graphics.asp?name=100KM%20SRI%20%28CROPPED%29&user="},
    {"name": "Radar, 250 km animation", "url": BASE + "tools/graphics.asp?name=250KM%20SRI%20%28CROPPED%29&user="},
    {"name": "Satellite", "url": BASE + "tools/graphics.asp?name=LOCAL_SATELLITE&user="},
]
RAW_DIR = Path("data/weather_raw")
OPEN_METEO = ("https://api.open-meteo.com/v1/forecast?latitude=32.30&longitude=-64.78&timezone=Atlantic%2FBermuda"
              "&hourly=temperature_2m,precipitation_probability,precipitation,wind_speed_10m,wind_direction_10m,uv_index"
              "&daily=sunrise,sunset,temperature_2m_max,temperature_2m_min,precipitation_probability_max&forecast_days=5"
              "&wind_speed_unit=kn")


def _save(name: str, url: str, html: str) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / f"{name}.html").write_text(f"<!-- {url} -->\n" + html, encoding="utf-8")


def _lines(el) -> list[str]:
    return [clean(x) for x in el.get_text("\n").split("\n") if clean(x)]


def parse_forecast(html: str) -> dict:
    """The public and marine forecast pages share one layout."""
    soup = BeautifulSoup(html, "lxml")
    out = {"issued": "", "next_update": "", "headline": "", "synopsis": "", "warnings": [], "periods": [], "climate": {}}
    text = _lines(soup)
    for i, ln in enumerate(text):
        if ln.lower().startswith("issued at") and not out["issued"]:
            out["issued"] = ln.replace("Issued at", "").strip(" -")
        elif "next scheduled update" in ln.lower():
            m = re.search(r"issued at (.*)", ln, re.I)
            out["next_update"] = m.group(1).strip(". ") if m else ""
        elif re.search(r"warning|watch|advisory", ln, re.I) and len(ln) < 60 and i + 1 < len(text) and text[i + 1].lower().startswith("(valid"):
            out["warnings"].append({"title": ln, "valid": text[i + 1].strip("()").replace("Valid for", "").strip()})
        elif ln.lower().startswith("headline") and i + 1 < len(text):
            out["headline"] = text[i + 1]
        elif ln.lower().endswith("synopsis -") and i + 1 < len(text):
            out["synopsis"] = text[i + 1]
    for pe in soup.select("div.periodElement"):
        h = pe.find("h4")
        if not h:
            continue
        label = clean(h.get_text(" ")).rstrip(" -")
        h.extract()
        lines = [x.rstrip(".") + "." if not x.endswith((".", "!")) else x for x in _lines(pe)]
        p = {"label": label, "lines": [], "high": "", "low": "", "uv": "", "sunrise": "", "sunset": ""}
        for x in lines:
            m = re.search(r"High near (\d+)°C/(\d+)°F", x)
            if m:
                p["high"] = f"{m.group(1)}C / {m.group(2)}F"
            m = re.search(r"[Ll]ow near (\d+)°C/(\d+)°F", x)
            if m:
                p["low"] = f"{m.group(1)}C / {m.group(2)}F"
            m = re.search(r"UV Index forecast - (\d+)\s*or\s*(\w+)", x)
            if m:
                p["uv"] = f"{m.group(1)} ({m.group(2)})"
                continue
            m = re.search(r"Sunrise:\s*([\d:]+\s*[ap]m)", x)
            if m:
                p["sunrise"] = m.group(1)
            m = re.search(r"Sunset:\s*([\d:]+\s*[ap]m)", x)
            if m:
                p["sunset"] = m.group(1)
            if re.match(r"^(High|Low) near|^Sunrise|^Sunset|^Clear sky UV", x) or not re.search(r"[A-Za-z]{2}", x):
                continue
            p["lines"].append(x.replace("...", ".").replace("..", "."))
        out["periods"].append(p)
    joined = " ".join(text)
    cl = out["climate"]
    for key, pat in (("sea_surface", r"Sea Surface:\s*([\d.]+°C/[\d.]+°F)"), ("max", r"Maximum:\s*([\d.]+°C/[\d.]+°F)"),
                     ("min", r"Minimum:\s*([\d.]+°C/[\d.]+°F)"), ("rain_yesterday", r"Yesterday:\s*([\d.]+mm/[\d.]+\")"),
                     ("rain_month", r"to date:\s*([\d.]+mm/[\d.]+\")"), ("sunshine", r"Hours of sunshine:\s*([\d.]+)")):
        m = re.search(pat, joined)
        if m:
            cl[key] = m.group(1).replace("°", " ").replace("/", " / ")
    return out


def parse_observations(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    text = _lines(soup)
    out = {"time": "", "sky": "", "wind": "", "temp": "", "rh": "", "pressure": "", "rows": []}
    for i, ln in enumerate(text):
        if ln.lower().startswith("recorded at") and not out["time"]:
            out["time"] = ln.replace("Recorded at", "").strip()
            out["sky"] = text[i + 1] if i + 1 < len(text) else ""
        elif ln == "Temp.:" and i + 1 < len(text):
            out["temp"] = text[i + 1]
        elif ln == "Humidity:" and i + 1 < len(text):
            out["rh"] = text[i + 1]
        elif ln == "Wind:" and i + 1 < len(text):
            out["wind"] = text[i + 1] + (" " + text[i + 2] if i + 2 < len(text) and text[i + 2].startswith("or") else "")
    rows = []
    for tr in soup.find_all("tr"):
        cells = [clean(td.get_text(" ")) for td in tr.find_all("td")]
        if len(cells) >= 5 and re.match(r"^\d{2}:\d{2}$", cells[0]):
            rows.append({"time": cells[0], "sky": cells[1], "wind": cells[2], "temp": cells[3], "rh": cells[4], "pressure": cells[5] if len(cells) > 5 else ""})
    out["rows"] = rows[:12]
    return out


def parse_warnings(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    text = _lines(soup)
    out = []
    try:
        i = next(k for k, ln in enumerate(text) if "current watches" in ln.lower())
    except StopIteration:
        return out
    for ln in text[i + 1:]:
        if re.search(r"^(click here|for more detail)", ln, re.I):
            continue
        if re.search(r"warning|watch|advisory", ln, re.I) and len(ln) < 80 and not re.search(r"printable|view|list of", ln, re.I):
            out.append({"title": ln, "valid": ""})
        elif out and ln.lower().startswith("(valid"):
            out[-1]["valid"] = ln.strip("()").replace("Valid for", "").strip()
        elif re.search(r"none|no (watches|warnings)", ln, re.I):
            break
        if len(out) >= 6:
            break
    return out


def parse_tides(html: str, year: int, month: int) -> list[dict]:
    """Monthly table: each day cell reads '21 03:12 | 1.0 / 3.3 09:40 | 0.4 / 1.3 ...'."""
    soup = BeautifulSoup(html, "lxml")
    days: list[dict] = []
    for td in soup.find_all("td"):
        t = clean(td.get_text(" "))
        m = re.match(r"^(\d{1,2})\s+(\d{2}:\d{2}\s*\|.*)$", t)
        if not m:
            continue
        d = int(m.group(1))
        evs = []
        for tm, metres, feet in re.findall(r"(\d{2}:\d{2})\s*\|\s*([\d.]+)\s*/\s*([\d.]+)", m.group(2)):
            evs.append({"time": tm, "m": float(metres), "ft": float(feet), "kind": ""})
        if not evs:
            continue
        # high or low: compare each with its neighbours
        for i, e in enumerate(evs):
            prev_h = evs[i - 1]["m"] if i > 0 else None
            next_h = evs[i + 1]["m"] if i + 1 < len(evs) else None
            ref = next_h if prev_h is None else prev_h
            e["kind"] = "High" if ref is not None and e["m"] > ref else "Low"
        try:
            dt = date(year, month, d)
        except ValueError:
            continue
        days.append({"date": dt.isoformat(), "day": dt.strftime("%a %d %b").replace(" 0", " "), "events": evs})
    return days


RADAR_DIR = "images/Radar/CurrentRadarAnimation_100km_sri_cropped/"


def parse_radar_frames(html: str) -> list[str]:
    """File names of the radar frames on the 100 km animation page, oldest first (100km_sri-radar-2026-11-22-0601L.jpg)."""
    names = re.findall(re.escape("/" + RADAR_DIR) + r"([\w.-]+\.jpe?g)", html, flags=re.I)
    return sorted(set(names))


def hourly() -> dict:
    r = requests.get(OPEN_METEO, headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    j = r.json()
    h = j.get("hourly", {})
    rows = [{"t": t, "temp": h["temperature_2m"][i], "rain": h["precipitation_probability"][i], "mm": h["precipitation"][i],
             "wind": h["wind_speed_10m"][i], "dir": h["wind_direction_10m"][i], "uv": h["uv_index"][i]} for i, t in enumerate(h.get("time", []))]
    d = j.get("daily", {})
    days = [{"date": d["time"][i], "sunrise": d["sunrise"][i][-5:], "sunset": d["sunset"][i][-5:], "max": d["temperature_2m_max"][i],
             "min": d["temperature_2m_min"][i], "rain": d["precipitation_probability_max"][i]} for i in range(len(d.get("time", [])))]
    return {"hourly": rows, "days": days}


def build(pages: dict[str, str], today: date | None = None) -> dict:
    """Everything the tab needs, from already fetched HTML (so it can be tested offline)."""
    today = today or date.today()
    out = {"asof": datetime.now().strftime("%Y-%m-%d %H:%M"), "issued": "", "next_update": "", "headline": "", "synopsis": "",
           "warnings": [], "forecast": [], "marine": {"synopsis": "", "periods": []}, "climate": {}, "now": {}, "tides": [],
           "radar": {"page": PAGES["radar"], "links": RADAR_LINKS}, "hourly": [], "days": [], "raw_pages": []}
    if "forecast" in pages:
        f = parse_forecast(pages["forecast"])
        out.update({k: f[k] for k in ("issued", "next_update", "headline", "synopsis", "climate")})
        out["forecast"] = f["periods"]
        out["warnings"] = f["warnings"]
    if "marine_extended" in pages:
        mf = parse_forecast(pages["marine_extended"])
        out["marine"] = {"synopsis": mf["synopsis"], "periods": mf["periods"]}
        if not out["warnings"]:
            out["warnings"] = mf["warnings"]
    if "warnings" in pages:
        w = parse_warnings(pages["warnings"])
        if w:  # the warnings page is the authority on which are active; the forecast page carries the validity text
            valid = {x["title"].lower(): x["valid"] for x in out["warnings"] if x.get("valid")}
            out["warnings"] = [{"title": x["title"], "valid": x["valid"] or valid.get(x["title"].lower(), "")} for x in w]
    if "observations" in pages:
        out["now"] = parse_observations(pages["observations"])
    tides = []
    for key in ("tides", "tides_next"):
        if key in pages:
            y, m = pages[key + "_ym"]
            tides.extend(parse_tides(pages[key], y, m))
    if "radar_100" in pages:
        out["radar"] = dict(out["radar"], dir=BASE + RADAR_DIR, frames=parse_radar_frames(pages["radar_100"]))
    out["tides"] = [d for d in tides if date.fromisoformat(d["date"]) >= today - timedelta(days=1)][:8]
    return out


def fetch(cfg: dict | None = None) -> dict:
    today = date.today()
    pages: dict = {}
    raw = []
    urls = dict(PAGES)
    urls["tides"] = BASE + f"Tools/TideTimes.asp?Month={today.month}&Year={today.year}"
    nxt = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    urls["tides_next"] = BASE + f"Tools/TideTimes.asp?Month={nxt.month}&Year={nxt.year}"
    for name, url in urls.items():
        try:
            html = get(url, ttl_hours=1)
            pages[name] = html
            _save(name, url, html)
            raw.append({"name": name, "url": url, "ok": True, "chars": len(html)})
        except Exception as e:
            raw.append({"name": name, "url": url, "ok": False, "chars": 0, "error": str(e)[:120]})
    pages["tides_ym"] = (today.year, today.month)
    pages["tides_next_ym"] = (nxt.year, nxt.month)
    out = build(pages, today)
    out["raw_pages"] = raw
    try:
        out.update(hourly())
    except Exception as e:
        print(f"[weather] open-meteo: {e}")
    Path("data").mkdir(exist_ok=True)
    Path("data/weather.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for p in raw if p["ok"])
    print(f"[weather] {ok} of {len(raw)} BWS pages, {len(out['forecast'])} forecast periods, {len(out['marine']['periods'])} marine, "
          f"{len(out['warnings'])} warnings, {len(out['tides'])} tide days, now {out['now'].get('temp', '?')} at {out['now'].get('time', '?')}, "
          f"{len(out['hourly'])} hourly rows")
    return out
