"""Parser tests on small synthetic pages, so a site change shows up as a failing test rather than an empty calendar."""
from datetime import date
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tidewatch.sources import ptix, gotobermuda, sky
from tidewatch import classify
from tidewatch.util import parse_date, parse_time


def test_parse_date_rolls_forward_without_year():
    d = parse_date("Sat, Jan 9")
    assert d.month == 1 and d.day == 9
    assert parse_date("November 21, 2026") == date(2026, 11, 21)


def test_parse_time():
    assert parse_time("Doors 7:30 PM") == "7:30pm"
    assert parse_time("from 6 pm") == "6pm"


PTIX_CARD = '''<div class="show-module {cls}"><a href='/Event/8957/Jingle-Mingle' style="display: none;"></a>
<div class="show-image-thumbnail"><img src="x.webp" alt="Jingle &amp; Mingle"></div>
<div class="show-content"><div class="row"><div class="col-xs-3 left-content"><div class="title">Fri</div><div class="sub-title">Dec 18</div>
<div style="display: none" class="sub-title-end-time">{end}</div></div>
<div class="col-xs-9 right-content"><div class="title">Jingle &amp; Mingle</div><div class="sub-title">The Loren Hotel at Pink Beach</div><div class="sub-title">6:00 PM</div></div></div></div></div>'''


def test_ptix_card_real_markup():
    rows = ptix.parse(PTIX_CARD.format(cls="overlay-sold-out", end="-<br/>"), "https://www.ptix.bm")
    assert len(rows) == 1
    r = rows[0]
    assert r["name"] == "Jingle & Mingle" and r["date"] == date(2026, 12, 18) and r["time"] == "6pm"
    assert r["venue"] == "The Loren Hotel at Pink Beach" and r["sold_out"] and r["link"].endswith("/Event/8957/Jingle-Mingle")


def test_ptix_range_expands_per_day():
    rows = ptix.expand(ptix.parse(PTIX_CARD.format(cls="", end="- Dec 20"), "https://www.ptix.bm"))
    assert [r["date"] for r in rows] == [date(2026, 12, 18), date(2026, 12, 19), date(2026, 12, 20)]
    assert rows[0]["name"].endswith("(opens)")


def test_cinema_board():
    from tidewatch.sources import cinema
    html = '''<div class="wpbaw-blog-list"><div class="wpbaw-blog-categories"><a>Now Playing</a></div>
    <h2 class="wpbaw-blog-title"><a href="https://specialitycinema.bm/blog-post/the-cat-in-the-hat/">The Cat in the Hat</a></h2>
    <div class="wpbaw-blog-short-content">Start Date: Friday, November 6 --  End Date: Thursday, November 19 -- Genres: Animation Meet the Cat in the Hat you don't know.</div></div>'''
    f = cinema.parse_whats_playing(html)[0]
    assert f["title"] == "The Cat in the Hat" and f["start"] == [11, 6] and f["end"] == [11, 19]
    assert f["genre"] == "Animation" and f["family"] and not f["tba"] and f["syn"].startswith("Meet the Cat")


def test_gotobermuda_settings_and_mapping():
    html = '''<script>{"algolia_index":"EVENTS2025","algolia_app_id":"0WTIY3QYA0","algolia_api_key":"abc"}</script>'''
    assert gotobermuda.settings(html) == {"algolia_app_id": "0WTIY3QYA0", "algolia_api_key": "abc", "algolia_index": "EVENTS2025"}
    r = gotobermuda.map_hit({"objectID": "1", "title": "Christmas Walkabout", "startDate": "2026-12-04", "venue": "St George's", "url": "/event/x/3102"})
    assert r["date"] == date(2026, 12, 4) and r["venue"] == "St George's" and r["link"].endswith("/event/x/3102")


def test_classify():
    v = classify.classify("Kids Halloween party with bouncy castle, all ages, National Sports Centre")
    assert v.get("kids") == "xmas"  # the seasonal key
    assert "kids" not in classify.classify("Afro Boat party 18+ DJ cruise")


def test_sky_full_moon_nov_2026():
    evs = sky.build([(2026, 11, ), (2026, 12)])
    full = [e for e in evs if e["name"] == "Full moon" and e["m"] == 11]
    assert full and full[0]["d"] == 24
    glow = sorted((e["m"], e["d"]) for e in evs if e["name"] == "Glow worms" and e["m"] == 11)
    assert glow == [(11, 26), (11, 27)]
