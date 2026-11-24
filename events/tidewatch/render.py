"""Render the planner page from the store.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 0.5
Last Updated: 2026-11-24

Change Log
  0.5  2026-11-24  A note that ends in the front half of an email address (cut by a length limit when it was
                   collected) has that fragment dropped as the page is written, so rows already saved in the
                   store are fixed too. Whole addresses, such as a booking contact, are left alone.
  0.4  2026-11-22  Every text field of every event is passed through clean() as the page is written, so HTML tags
                   and entities already saved in the store no longer show up as raw code in a description.
  0.3  2026-11-20  A category the page has no colour for gets a neutral fallback entry in CATS, so one stray
                   event cannot stop the grid from drawing (the 20 Nov build showed an empty planner because
                   three events still carried the retired "hallow" key).
  0.2  2026-11-16  Windows safe date formatting.
  0.1  2026-11-15  First release.

template/planner.html is the live page with its data region replaced by {{DATA}}. This module
emits that region as JavaScript constants in exactly the shape the page's own code expects
(CATS_K, EVENTS_K, ... FILMS, SCREENINGS_V, LEAGUES, TODAY_M, TODAY, ORD, MONTHS, MONTH), then
fixes the month buttons and the footer sentence. Nothing in the page's CSS or behaviour changes.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from .store import BLOCK_KINDS, SUFFIX, VIEWS, Store
from .util import clean, drop_cut_email, first_weekday_sunday0, fmt_date_long, window

MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
NO_DASH = re.compile("[–—]")  # en and em dashes never appear in the page


def js(value) -> str:
    return NO_DASH.sub(", ", json.dumps(value, ensure_ascii=False))


def months_table(months: list[tuple[int, int]], breaks: dict) -> dict:
    out = {}
    for y, m in months:
        days = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
        b = breaks.get(f"{y}-{m:02d}", {})
        out[m] = {"name": MONTH_NAMES[m], "short": MONTH_NAMES[m][:3], "first": first_weekday_sunday0(y, m), "days": days,
                  "breaks": b.get("days", []), "breakLabel": b.get("label", ""), "year": y}
    return out


def data_block(store: Store, today: date, months: list[tuple[int, int]], breaks: dict) -> str:
    parts = []
    for view in VIEWS:
        sfx = SUFFIX[view]
        events = store.events_for(view, months)
        for ev in events:  # plain text only: no tags or entities left over from the source sites
            for k, v in ev.items():
                if isinstance(v, str) and k != "link" and ("<" in v or "&" in v):
                    ev[k] = clean(v)
            if "@" in (ev.get("note") or ""):
                ev["note"] = drop_cut_email(ev["note"])
        for kind in BLOCK_KINDS:
            block = store.get_block(view, kind)
            if kind == "CATS" and isinstance(block, dict):
                # any category the page has no entry for gets a neutral colour, so one stray event cannot blank the grid
                for ev in events:
                    c = ev.get("cat") or ""
                    if c and c not in block:
                        block[c] = {"name": c.replace("_", " ").title(), "color": "var(--ink-2)"}
            parts.append(f"const {kind}_{sfx} = {js(block)};")
        if view == "movies":
            # the page builds EVENTS_V from FILMS itself, plus SCREENINGS_V for the outdoor films
            films = store.get_json("films")
            parts.append(f"const FILMS = {js(films)};")
            parts.append("const DIM = {" + ",".join(f"{m}:{months_table(months, breaks)[m]['days']}" for _, m in months) + "};")
            parts.append("const DAYS_IN = [0,31,28,31,30,31,30,31,31,30,31,30,31];")
            parts.append("""const EVENTS_V = [];
for(const f of FILMS){
  if(!f.start) continue;
  let [m,d] = f.start; let count = 0, max = f.end ? 99 : 14;
  while(count < max){
    if(f.end && ((m===f.end[0] && d > f.end[1]) || (m!==f.end[0] && m===((f.end[0]%12)+1)))) break;
    const key = m+"-"+d, tt = f.times[key]; const open = (count===0);
    EVENTS_V.push({m, d, cat: f.tba ? "soon" : (f.family ? "family" : "general"), t: tt || "", name: f.title + (open ? (f.tba ? " (expected from today)" : " opens") : ""),
      time: tt ? "Showtime " + tt + (f.aud ? ", " + f.aud : "") : "Showtimes are posted about four days ahead; evening shows are usually 6:15 to 7pm, with matinees on weekends",
      venue: "Speciality Cinema, 12 Church Street, Hamilton", ages: f.rating, cost: "Tickets at the box office or online; call 292-2135 for prices",
      status: tt ? "ok" : (f.tba ? "pattern" : "check"), note: f.syn + (f.runtime ? " Runtime " + f.runtime + "." : ""), link: f.link});
    count++; d++; const dim = DIM[m] || DAYS_IN[m]; if(d > dim){ d = 1; m = (m % 12) + 1; }
  }
}""")
            parts.append(f"const SCREENINGS_V = {js(events)};")
            parts.append("EVENTS_V.push(...SCREENINGS_V);")
        else:
            parts.append(f"const EVENTS_{sfx} = {js(events)};")
        if view == "sports":
            parts.append(f"const LEAGUES = {js(store.get_json('leagues'))};")
    parts.append(f"const TODAY_M = {today.month}, TODAY = {today.day};")
    parts.append("const ORD = m => m < TODAY_M - 3 ? m + 12 : (m > TODAY_M + 6 ? m - 12 : m);")
    parts.append(f"const MONTHS = {js(months_table(months, breaks))};")
    parts.append(f"let MONTH = {today.month};")
    return "\n".join(parts)


def render(store: Store, template: Path, out: Path, *, today: date | None = None, breaks: dict | None = None, footer_note: str = "") -> Path:
    today = today or date.today()
    months = window(today)
    breaks = breaks or {}
    html = template.read_text(encoding="utf-8")
    html = html.replace("{{DATA}}", data_block(store, today, months, breaks))
    buttons = "".join(
        f'<button type="button" data-m="{m}" aria-pressed="{"true" if i == 0 else "false"}">{MONTH_NAMES[m]}</button>' for i, (y, m) in enumerate(months)
    )
    html = re.sub(r'(<div class="months"[^>]*>).*?(</div>)', lambda mm: mm.group(1) + buttons + mm.group(2), html, count=1, flags=re.S)
    first, last = months[0], months[-1]
    cover = f"Covers {MONTH_NAMES[first[1]]} {first[0]} to {MONTH_NAMES[last[1]]} {last[0]}."
    html = re.sub(r"Covers [^.]*\.", cover, html, count=1)
    html = re.sub(r"Last refreshed [^;.]*", f"Last refreshed {fmt_date_long(today)} by Tidewatch" + (f" ({footer_note})" if footer_note else ""), html, count=1)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
