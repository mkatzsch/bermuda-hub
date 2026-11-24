"""Sky layer: moon phases, glow worm nights, meteor showers, best stargazing nights.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 0.2
Last Updated: 2026-11-16

Computed with PyEphem for Bermuda (32.3N, 64.78W). Glow worms (Odontosyllis) rise on the 2nd and
3rd nights after the full moon, about 56 minutes after sunset. Meteor shower peaks are a fixed
table from the American Meteor Society calendar; update it once a year. Best stargazing is the
three nights around each new moon.

Shared by the kids and adults views (category "sky").
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import ephem

from ..util import fmt_time

TZ = ZoneInfo("Atlantic/Bermuda")
LAT, LON = "32.3", "-64.78"

# (month, day, name, note). Peak nights, AMS calendar.
SHOWERS = [
    (1, 3, "Quadrantids peak", "Short sharp peak before dawn on the 4th. Look north east after midnight."),
    (4, 22, "Lyrids peak", "Up to 18 an hour after midnight."),
    (5, 6, "Eta Aquariids peak", "Halley's Comet debris, best in the hour before dawn."),
    (8, 12, "Perseids peak", "The big summer shower, best after 11pm with the moon out of the way."),
    (10, 21, "Orionids peak", "Fast meteors from Halley's Comet, after midnight."),
    (11, 17, "Leonids peak", "Usually modest, occasionally a storm."),
    (12, 13, "Geminids peak", "The best shower of the year, from 9pm onwards, often 100 an hour."),
    (12, 22, "Ursids peak", "Minor shower near the pole star."),
]


def _local(e) -> datetime:
    return ephem.Date(e).datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(TZ)


def sunset(d: date) -> datetime:
    obs = ephem.Observer()
    obs.lat, obs.lon = LAT, LON
    obs.date = datetime(d.year, d.month, d.day, 16, 0, tzinfo=TZ).astimezone(ZoneInfo("UTC"))
    return _local(obs.next_setting(ephem.Sun()))


def phases(start: date, end: date) -> list[tuple[str, datetime]]:
    out = []
    cursor = ephem.Date(datetime(start.year, start.month, start.day))
    funcs = [("New moon", ephem.next_new_moon), ("First quarter", ephem.next_first_quarter_moon),
             ("Full moon", ephem.next_full_moon), ("Last quarter", ephem.next_last_quarter_moon)]
    for name, fn in funcs:
        t = fn(cursor)
        while _local(t).date() <= end:
            out.append((name, _local(t)))
            t = fn(t)
    return sorted(out, key=lambda x: x[1])


def build(months: list[tuple[int, int]]) -> list[dict]:
    """Events in the page schema for the given (year, month) window."""
    start = date(months[0][0], months[0][1], 1)
    last_y, last_m = months[-1]
    end = (date(last_y + (last_m == 12), (last_m % 12) + 1, 1) - timedelta(days=1))
    out: list[dict] = []
    for name, when in phases(start - timedelta(days=3), end):
        d = when.date()
        if start <= d <= end:
            out.append({"m": d.month, "d": d.day, "cat": "sky", "t": "", "name": name, "time": fmt_time(when),
                        "venue": "Anywhere with a dark sky", "ages": "All ages", "cost": "Free", "status": "ok",
                        "note": {"New moon": "Darkest skies of the month; the best stargazing is tonight and the two nights either side.",
                                 "Full moon": "Moonrise around sunset. Glow worms follow on the 2nd and 3rd nights after.",
                                 "First quarter": "Half moon high at sunset, sets around midnight.",
                                 "Last quarter": "Moon rises around midnight, so evenings are dark."}[name],
                        "link": "https://in-the-sky.org/"})
        if name == "Full moon":
            for k in (2, 3):
                g = d + timedelta(days=k)
                if start <= g <= end:
                    ss = sunset(g)
                    show = ss + timedelta(minutes=56)
                    out.append({"m": g.month, "d": g.day, "cat": "sky", "t": fmt_time(show), "name": "Glow worms",
                                "time": f"About {fmt_time(show)} (56 minutes after the {fmt_time(ss)} sunset), lasts 15 to 20 minutes",
                                "venue": "A dock on a calm bay: Ferry Reach, Flatts Inlet or Somerset", "ages": "All ages, bring a torch", "cost": "Free", "status": "ok",
                                "note": f"{'Second' if k == 2 else 'Third'} night after the full moon. Green pinpricks of light in the water as the worms spawn. Calm, dark water is best.",
                                "link": "https://www.gotobermuda.com/inspiration/article/bermudas-glow-worms"})
        if name == "New moon":
            for k in (-1, 1):
                g = d + timedelta(days=k)
                if start <= g <= end:
                    out.append({"m": g.month, "d": g.day, "cat": "sky", "t": "", "name": "Best stargazing night", "time": "After 9pm",
                                "venue": "South Shore beaches, Spittal Pond or Cooper's Island", "ages": "All ages", "cost": "Free", "status": "check",
                                "note": "No moon, so the Milky Way shows if the sky is clear. Check the forecast.", "link": "https://in-the-sky.org/"})
    for (m, d, name, note) in SHOWERS:
        for y, mm in months:
            if mm == m:
                out.append({"m": m, "d": d, "cat": "sky", "t": "", "name": name, "time": "Late evening to dawn", "venue": "Dark beach, lie back and look up",
                            "ages": "All ages", "cost": "Free", "status": "ok", "note": note, "link": "https://www.amsmeteors.org/meteor-showers/meteor-shower-calendar/"})
    return out
