"""Bermuda Hub orchestrator: one scheduled run for the deals collector and the what's-on planner.

Developed by AiTide Ltd. | www.AiTide.com
Version: 1.59
Last Updated: 2026-11-22

Change Log
  1.59 2026-11-22  Snorkel and Scuba each have a map: snorkel spots coloured by the call for the chosen day, wrecks
                   and dive operators on the scuba map. Tapping a wreck or a snorkel spot opens its own sheet in
                   place (the Explore sheet, with Deep dive) and no longer jumps to the Explore tab. New
                   photos_collect (--photos, or every 30 days): finds a reusable photo for Field guide species
                   that have none (other iNaturalist photos, then the Wikipedia picture) and for Explore places
                   (Wikimedia Commons), and saves the credit and licence with each. Writes
                   events/data/explore_photos.json and events/data/photos_report.json. Place sheets show the
                   photo and its credit on the website copy.
                   (Island Eats in short pages with food buttons is in deals/template.html 1.2.)
  1.58 2026-11-22  Bus and ferry: rebuilt around "Where to?". Pick a start and an end (a stop, a ferry dock, a
                   beach or fort from Explore, or your own location) and it gives the next departures, the ride
                   time and where to get off, with one change of bus when nothing runs direct, and ferries from
                   the typed in schedule. A map shows every stop (tap one to start or end there) and draws the
                   chosen ride. The full timetable is folded away underneath. transit_doc now passes the ferry
                   dock positions to the page. Pickleball: a button per venue plus "All venues" narrows the
                   sessions, events and details to one place. Leaflet is now loaded once and shared by the maps.
                   (Deals: section buttons, compact specials and a narrow Head to head are in deals/template.html 1.2.)
  1.57 2026-11-22  Fix: the Explore map felt frozen on a phone. Its edges were pinned so tightly to Bermuda that
                   at the opening zoom there was no room to slide up or down, and a finger on the map could not
                   scroll the page either. The edges now sit well out to sea, the pull back at the edge is
                   gentle, and the map opens fitted to the island on any screen size.
  1.56 2026-11-22  Explore: two new groups, "Bermuda Triangle" and "Haunted Bermuda", each with a guide and
                   pinned places. The entries live in events/data/explore.json. This file only gains their
                   two map colours. Yoga: a row of buttons, one per studio or hotel plus "All studios",
                   narrows the classes, the special sessions and the directory to that one place.
                   (The planner's Today button and folded past days are in events/template/planner.html 1.1.)
  1.55 2026-11-22  Sports: Snorkel and Scuba sections. Snorkel is beaches you can swim out from, ranked each day
                   by whether the wind blows onto them; scuba is boat diving, with the operators, the wrecks
                   and a weather call. Both are kept by hand in events/data/dive.json and reuse the beaches
                   and wrecks already in Explore. Explore: two new groups, "Science and conservation" and
                   "Lionfish", and a place can now carry its own headed sections ("sections" in explore.json).
                   The addresses ending #snorkel and #scuba open those sections. Search covers all of it.
  1.54 2026-11-22  Whole Hub search: a Search button in the header opens one box that looks across events,
                   grocery specials, everyday prices, restaurants and menu items, shops, Explore places, the
                   Field guide, bus stops and routes, ferries, pickleball, yoga, ships and superyachts. Tapping
                   a result opens the right tab and fills in that tab's own search box where it has one.
                   Superyachts: the news list is headed "Notable visits in the news", since the stories are
                   occasional and can be months old.
  1.53 2026-11-22  Ocean: a Superyachts card. Recent visits come from the Bernews super yacht stories, read once
                   a day by superyachts_collect into events/data/superyachts_news.json (or on demand with
                   --yachts). Where they berth, the size each berth takes and the season are kept by hand in
                   events/data/superyachts.json. No free source lists the yachts in port right now, so the card
                   links to the VesselFinder port pages for Hamilton and St George's.
  1.52 2026-11-22  Yoga: the timetables of Shamana Circle and Salt Yoga are now read by the laptop. Both studios
                   book through TeamUp, whose public data service lists every class. yoga_collect asks it for
                   the next eight days and saves the classes in events/data/yoga_live.json. It runs once a day
                   with the normal run, or on demand with --yoga, and a failure keeps the copy already saved.
                   The page shows these classes by date beside the hand kept weekly ones.
  1.51 2026-11-22  Ocean: tap a ship in "Due in port this week" for a small panel: what it is, when it was built
                   and how long it is (where looked up), what the schedule called it, and links that open the
                   ship on VesselFinder and MarineTraffic to see where it is now. A test showed AISStream has no
                   receiver within range of Bermuda, so live positions stay with those two sites. Ships looked
                   up by hand are in SHIP_INFO with their IMO numbers, which makes the link exact; any other
                   ship gets a search by name. The saved file moves to format 3.
  1.50 2026-11-22  Explore: tattoo studios get their own colour on the map and cards. The five studios themselves
                   are in events/data/explore.json under a new kind, "Tattoo studios".
  1.49 2026-11-22  Sports: a Yoga section. Pick a day to see every class across the studios and hotels whose
                   timetables could be read, then special sessions coming up, then a directory of every studio
                   and hotel with a link to its own schedule. Kept by hand in events/data/yoga.json with a
                   review_after date. Today gets a Yoga card, and the address ending #yoga opens the section.
                   The Sports switch is now its own small piece of code: each sport turns its button on once
                   its data has loaded.
  1.48 2026-11-22  Sports: a Pickleball section beside Wind sports, picked with a switch at the top of the tab. It
                   shows a call on outdoor play for today and the next four days (hour by hour wind and chance
                   of rain, from the saved forecast), the regular drop in sessions for the week ahead, what is
                   coming up, every place to play with a Public, Indoor or Members filter, and how to join or
                   find a coach. The details are kept by hand in events/data/pickleball.json, read from the
                   Pickleball Association of Bermuda website, with a review_after date like the ferries. Today
                   gets a Pickleball card. The address ending #pickleball opens the section directly.
  1.47 2026-11-22  Ship list tidy. The schedule story sometimes gives a ship by a short form of its name and
                   uses port jargon for its type, so three small tables kept by hand now put those into plain
                   words. SHIP_NAMES: "CCL Eclipse" reads "Celebrity Eclipse". SHIP_KNOWN: a ship whose type
                   and usual cargo have been looked up shows that (Cartagena is a general cargo ship, Grit
                   Cement IV a cement ship). SHIP_KINDS: any other "discharge ship" reads "bulk cargo ship".
                   The wording the story used is kept beside each one in events/data/ships.json ("said_name",
                   "said_kind"). The saved file carries a format number (SHIPS_V) and is read again whenever
                   that number changes.
  1.46 2026-11-22  Bus & ferry: "Next bus at a stop". Type part of a stop name, or on the website tap Near me, and
                   the page lists the closest stops with the next buses through each one, worked out from the
                   stop patterns and running times saved in 1.45.
  1.45 2026-11-22  The timetable reader now keeps every bus stop and the time each bus reaches it, stored
                   compactly (each distinct run of stops once, each distinct set of running times once), so the
                   page can show the next buses at a stop. The saved file carries a format number (TRANSIT_V) and
                   is read again whenever that number changes.
  1.44 2026-11-22  Ferries on the Bus & ferry tab: the winter schedule in force from 2 Nov 2026, kept by hand in
                   events/data/ferries.json because the official feed still holds the summer one. Each route
                   shows its table for the chosen day (weekday, or weekend and public holiday), the next ferry
                   from Hamilton, and Today names the next ferry too. The build log warns once the file passes
                   its review_after date, and the page then says the times may be out of date.
  1.43 2026-11-22  A "Bus & ferry" tab: every bus route with its next departures and the full day, for today and
                   the six days after, from the saved timetable feed (transit_doc picks the services that run on
                   each date, holidays included). Today gets a "Next buses from Hamilton" card. Where the feed
                   has let a timetable run out (its Sunday buses stop on 1 Nov), the last one published is shown
                   with a warning. Ferry times are not shown: the feed still holds the summer ferry timetable.
  1.42 2026-11-22  Bus and ferry timetables: transit_collect reads the official Bermuda bus and ferry feed (the
                   standard GTFS zip the Department of Public Transportation publishes through Trillium) and
                   saves every departure in events/data/transit.json. Runs once a week with the normal run, when
                   the saved feed has run out, or on demand with --transit. Nothing is shown on the page yet.
  1.41 2026-11-22  Ocean: a "Best beaches" card. Each beach in events/data/explore.json now carries the compass
                   bearing it faces ("faces") and whether a cove shelters it ("cove"). The page sets the saved
                   hourly wind against that bearing to say where the water should be calmest for the rest of
                   today, or tomorrow once the sun is down. Tap a beach to open its Explore sheet.
  1.40 2026-11-22  Ocean: a card of the ships due in port this week (cruise ships, container ships and the rest),
                   read by ships_collect from the Department of Marine and Ports weekly schedule as Bernews
                   publishes it each Saturday, and saved in events/data/ships.json. Runs once a day with the
                   morning run, or on demand with --ships. Today: a wind sports card with the day's call.
  1.39 2026-11-22  Made for sharing. A Share button in the header sends the website link for the tab you are on
                   (or copies it). The site now has a home screen icon and name (site/manifest.webmanifest and
                   three icon pictures, drawn by write_share_files with Pillow), a link preview title and
                   description for messages, and a one time tip on phones showing how to add it to the home
                   screen. Depends on: Pillow for the icons; without it the icons are skipped and all else works.
  1.38 2026-11-22  An Ocean tab. The live ship map moves there from the Weather map panel and sits at the top, with
                   the boat day planner, the sea state, the marine forecast and the tides under it. Weather keeps
                   the sky: radar, Windy, the forecast, the dials, the week and the tank. Sports stays separate.
  1.37 2026-11-22  Explore: half-day routes. Eight outings built from places already in the guide (explore.json
                   "routes": a name, how to get around, how long to allow and the stops in order). Each route
                   opens a sheet with the stops numbered, the distance between them, a tick for the ones you have
                   been to, the whole route in Google Maps, and a line drawn on the Hub's own map.
  1.36 2026-11-22  Sports tab: one wind sports view instead of a Kite, Wing foil and Windsurf switch, since the three
                   said nearly the same thing. A light wind day is now called out as a foil day.
  1.35 2026-11-22  A Sports tab, starting with wind sports: kite, wing foil and windsurf. For today and the next four
                   days it shows the daylight wind hour by hour, the best window, a rough kite size, and which
                   Bermuda spots work in that wind direction, with what the water is like and what to watch for.
                   Uses the hourly wind already in weather.json, so it needs nothing new from the morning run.
                   Spot directions and notes follow the Bermuda Kitesurfing community spot guide.
  1.34 2026-11-22  Explore: a Near me button beside the search box sorts the places by how far they are from you,
                   shows the distance on each card and puts a dot for you on the map (website copy only, since
                   the artifact cannot ask for a location). Read it to me on every place sheet and every Field
                   guide sheet reads the story aloud with the phone's own voice; tap again to stop.
  1.33 2026-11-22  One dusk look across the whole Hub. What's on and Deals get the Weather and Explore colours (dark
                   navy, teal, pink), the Outfit font and rounded cards through DUSK_SKIN, a style block added to
                   each page as it is embedded in hub.html; their own templates under events and deals are not
                   changed. The header, the tab bar and the List tab use the same colours. Clear all on the
                   List now asks with a second tap, because the artifact ignores the browser's confirm box.
  1.32 2026-11-22  The Field guide is saved into the Hub. The morning run asks iNaturalist once for each group (all
                   year, this month, only in Bermuda, native, introduced), keeps each species' description,
                   conservation status and latest sightings in events/data/fieldguide.json, and keeps a small copy
                   of each shared photo in site/guide. The page reads that saved copy, so the Field guide opens
                   instantly and also works in the Claude artifact. Run with --guide to refresh it on demand.
                   The site/guide photos are copied to docs/guide for GitHub Pages.
  1.31 2026-11-22  A Today tab that opens first: the weather in a few lines, the boat verdict, what is on today and
                   tomorrow, the best buys and somewhere to go. Boat day on the Weather tab: the daytime wind for
                   today and tomorrow with the anchorages that sit out of it. Explore: badges for finishing sets,
                   and trails with their length and time.
  1.30 2026-11-22  Ships view: MarineTraffic is now the default source (more vessels, and a satellite layer on the
                   map itself), with VesselFinder as the alternative.
  1.29 2026-11-22  Turtles stand alone: our own sighting log (a pin with date and time, kept on the device, photo
                   optional) replaces the links to the outside turtle app; the hotline stays. On the artifact copy
                   the Field guide and Deep dive say plainly that they need the website instead of failing.
  1.28 2026-11-22  Weather map panel: a Ships view beside Radar and Windy, with live ship positions around Bermuda
                   from VesselFinder (around the island, or zoomed out to ships on the way).
  1.27 2026-11-22  Explore: Bermuda National Trust places (museums, protected houses, reserves, cemeteries) with a
                   National Trust filter, and a sea turtle card in the Field guide (report a sighting, follow
                   tagged turtles, the hotline for a turtle in trouble).
  1.26 2026-11-22  Explore title is plain bold, without the script or the glow.
  1.25 2026-11-22  Explore: a Field guide beside Places. Birds, fish, mammals and whales, lizards and turtles, snails,
                   insects, plants and trees, corals and fungi recorded in Bermuda, by this month or all year, with
                   only in Bermuda, native and introduced filters, photos, a summary, latest sightings, a deep
                   dive and a tick for the ones you have seen. Live from iNaturalist. Parks and reserves added to
                   Places. Weather: the hourly wind arrows now point the way the wind blows, matching the dial.
  1.24 2026-11-22  Explore: tag street art with a photo. Tag a mosaic takes a photo, then drops a pin where you are
                   standing; any place can also have a photo added, changed or removed from its sheet. Photos are
                   shrunk and kept on the device.
  1.23 2026-11-22  Explore: a Deep dive button on every place brings the full Wikipedia article (or articles) for
                   it onto the page, with headings, minus the reference lists. Titles are set per place in
                   explore.json (wiki); places with no article of their own get their parish or area.
  1.22 2026-11-22  Explore map background fixed: the CARTO map now demands an account key, so it uses OpenStreetMap
                   streets (darkened to suit the page) with a Map / Satellite switch to Esri satellite pictures.
  1.21 2026-11-22  Explore tab rebuilt: an interactive map of the island (GitHub Pages copy) with a coloured pin for
                   each place, filters, a search box, and a story sheet that opens on the page when you tap a pin or
                   a card. The sheet has room for who built it, who has been there, what is only here and other
                   facts (built, visitors, unique, tidbits in explore.json). Same dusk look as the Weather tab.
                   The hunt: tick off places you have been and Invader mosaics you have found, with a tally, and pin
                   mosaics of your own where you are standing. Kept on each device.
  1.20 2026-11-22  Toned the neon script down: section headings are plain bold again, and the headline keeps the
                   script with a much softer glow.
  1.19 2026-11-22  Rain for the tank uses Bermuda's own figures: Imperial gallons, the Department of Health yield,
                   the 55.5 inch average year, the Government's tank size formula and fill to half advice, and a
                   box for your own roof size (kept on that device).
  1.18 2026-11-22  Weather tab extras: feels like and a comfort word, a line on the rain over the coming hours,
                   Go / Maybe / Skip for beach, boat, snorkel, run and laundry, dials for wind, sun, UV and moon,
                   a sea state card, the best daytime low tide for the beach, rain for the tank, the NHC tropics
                   outlook in hurricane season (GitHub Pages copy only), and links to live cameras.
  1.17 2026-11-22  Tide graph: the rise and fall at St George's across today and tomorrow against the clock, each
                   high and low labelled, with a line at the time now and whether the tide is rising or falling.
  1.16 2026-11-22  Weather scene redrawn as Harbour Road at dusk: proper Bermuda cottages (stepped hip roofs,
                   chimneys, shutters, arched doors) in two rows on a hillside, a moongate, hibiscus hedge, palms.
  1.15 2026-11-22  Weather tab restyled as a tropical neon dusk: purple to pink to orange sky, striped setting sun,
                   palm silhouettes, glowing script headings (Yellowtail, with Outfit for the rest), teal and hot
                   pink accents. The Bermuda houses with white stepped roofs stay. One palette for light and dark.
  1.14 2026-11-22  Weather tab redesign: a Bermuda scene at the top (pastel houses, white stepped roofs, the sea, a
                   sky that follows the conditions and the time of day), its own island palette in light and dark,
                   Fraunces for headings. Radar and Windy share one map panel with a Radar / Windy toggle, and the
                   radar has plus and minus buttons that step through the five views.
  1.13 2026-11-22  Live radar moved to the top of the Weather tab, straight under the headline.
  1.12 2026-11-22  Weather tab: Windy forecast map (Wind, Gusts, Rain, Waves buttons) under the live radar, on the
                   GitHub Pages copy. It is the official Windy embed, centred on Bermuda, wind in knots.
  1.11 2026-11-22  Live radar: five view buttons that step outward (Parishes, Satellite, 100 km, 250 km, 500 km),
                   each its own BWS animation. The last view picked is remembered on that device.
  1.10 2026-11-22  Weather tab: live Bermuda Weather Service radar animation (100 km) on the GitHub Pages copy. The
                   page finds the newest frames itself, so it stays current between laptop runs. The artifact
                   copy keeps the links only, because the artifact viewer blocks outside images.
                   GitHub Pages home page: docs/index.html is now a copy of hub.html, so Weather and Explore
                   have their data there (the laptop front door has none inside it).
  1.9  2026-11-22  GitHub: the built pages are copied to docs/ (the folder GitHub Pages serves) and each run
                   commits and pushes with the git that GitHub Desktop installed. A failed push is logged, never fatal.
  1.8  2026-11-21  Explore tab: forts and batteries, wrecks, abandoned sites, from events/data/explore.json
                   (filters, cards, a detail sheet; coordinates kept for the map once the site is on GitHub).
  1.7  2026-11-21  Weather tab: BWS warnings, latest conditions, headline, today and tonight, hourly strip, the
                   week, marine with seas inside and outside the reef, tides, radar links. Built from
                   events/data/weather.json.
  1.6  2026-11-21  Weather collected every morning (tidewatch weather) and the planner re-rendered daily.
  1.5  2026-11-21  List tab on the Hub: a shared grocery list (artifact db capability, both of them edit it
                   from their phones, kept across republishes) with this week's best buys per store as one
                   tap adds, tick in the aisle, clear ticked. site/index.html shows it read only.
  1.4  2026-11-21  Links inside the embedded pages are handed to the front door to open: the artifact viewer
                   lets the outer page open a new tab but not a nested frame, so ticket and venue links did
                   nothing on the published Hub.
  1.3  2026-11-16  site/hub.html: one self contained page with the planner and the deals page folded inside
                   (each as an inline frame), the file that becomes the single Bermuda Hub artifact.
  1.2  2026-11-16  Report planner step failures instead of "ok".
  1.1  2026-11-16  Nightly backup of the data that only exists on this laptop to OneDrive (BermudaHub-backup).
  1.0  2026-11-16  First release. Wraps deals/collect.py (daily) and events/ Tidewatch (Mondays and
                   Fridays), copies both pages into site/ and writes the front door site/index.html.

Usage:  python run.py            deals every day; events only on Mondays and Fridays
        python run.py --all      both, now
        python run.py --deals    deals only
        python run.py --events   events only
        python run.py --build    rebuild the pages from existing data, no collection

Dependencies: deals/ (BermudaDeals collector, its own config.json and data/), events/ (Tidewatch, its
own config.yaml and data/tidewatch.sqlite). Output: site/deals.html, site/planner.html, site/index.html.
"""
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DEALS = os.path.join(ROOT, "deals")
EVENTS = os.path.join(ROOT, "events")
SITE = os.path.join(ROOT, "site")
DOCS = os.path.join(ROOT, "docs")  # what GitHub Pages serves: a copy of site/ made at the end of every run
LOG = os.path.join(ROOT, "log.txt")
EVENT_DAYS = (0, 4)  # Monday, Friday
# The dusk look for the two embedded pages. Both pages are styled through their own CSS variables, so the skin only
# has to set those variables again and round a few corners. It is added in front_door(); the templates stay as they are.
DUSK_SKIN = """<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap">
<style id="dusk-skin">
:root:root:root{color-scheme:dark;
  --bg:#170f3a;--paper:#241552;--ink:#fdf3ff;--ink-2:#cdbbea;--line:#4b2d8a;--muted:{{MUTED}};
  --fg:#fdf3ff;--rule:#4b2d8a;--chip:#2e1a66;--save:#ff4fa3;
  --accent:#2af0d9;--accent-ink:#170f3a;--today:#ff4fa3;--past:#8f7cbd;
  --c-hallow:#ff9452;--c-arts:#c3a6ff;--c-sport:#5bdf97;--c-fest:#ff6fb0;--c-nature:#2af0d9;--c-camp:#ffc83d;--c-story:#8fb0ff;--c-water:#5db3ff;--c-build:#f79a5b;--c-sky:#b9bbff;
  --ok:#5bdf97;--warn:#ffc83d;--off:#a596c9;--shadow:0 10px 30px rgba(0,0,0,.45);
  --mp:#ff8fc0;--ld:#c3a6ff;--sm:#7fe3b0;--ml:#ffc66a;--pr:#8fc0ff;--fm:#b6e07a;--prc:#ff9a9a;
  --display:Outfit,"Segoe UI",system-ui,sans-serif;--body:Outfit,"Segoe UI",system-ui,sans-serif}
html{background:#170f3a}
body{background:linear-gradient(#170f3a,#2a1058 900px,#3d1260 2200px) #3d1260;color:#fdf3ff}
h1,h2,h3{letter-spacing:0;font-stretch:100%}
h1{font-weight:800}
.store{color:#170f3a}
.day.today .num span,.aday.today .num{color:#170f3a}
.months button[aria-pressed="true"],#leagueTabs .chip[aria-pressed="true"]{background:#2af0d9;color:#170f3a;border-color:#2af0d9}
.month,.aday,.card,table,dialog{border-radius:18px}
.note,.best .card,.deal,.pl,.others .o{border-radius:18px}
.tablewrap{border-radius:18px;overflow:hidden;overflow-x:auto}
.topsearch{background:#170f3a;border-bottom-color:#4b2d8a}
.topsearch input,input[type=search]{border-radius:14px}
.filters button{border-radius:999px}
.views{border-radius:999px}
.pl .dl{border-radius:999px}
.best .card .store{align-self:flex-start}
td.num.win,.win{color:#2af0d9}
</style>"""
FERRY_JSON = os.path.join(EVENTS, "data", "ferries.json")  # the ferry schedule in force, kept by hand
PICKLEBALL_JSON = os.path.join(EVENTS, "data", "pickleball.json")  # pickleball venues, sessions and events, kept by hand
YOGA_JSON = os.path.join(EVENTS, "data", "yoga.json")  # yoga studios, hotel classes and timetables, kept by hand
YOGA_LIVE_JSON = os.path.join(EVENTS, "data", "yoga_live.json")  # classes read from the studios' booking service
DIVE_JSON = os.path.join(EVENTS, "data", "dive.json")  # snorkel spots and scuba operators, kept by hand
YACHTS_JSON = os.path.join(EVENTS, "data", "superyachts.json")  # superyacht berths and season, kept by hand
YACHTS_NEWS_JSON = os.path.join(EVENTS, "data", "superyachts_news.json")  # recent visits read from Bernews
TRANSIT_JSON = os.path.join(EVENTS, "data", "transit.json")  # bus and ferry departures
TRANSIT_FEED = "https://data.trilliumtransit.com/gtfs/bermuda-bm/bermuda-bm.zip"  # official GTFS feed
TRANSIT_V = 2  # format of transit.json: 2 added stops, patterns and timings
SHIPS_JSON = os.path.join(EVENTS, "data", "ships.json")  # ships due in port this week
GUIDE_JSON = os.path.join(EVENTS, "data", "fieldguide.json")  # the saved Field guide (species, counts, stories)
GUIDE_PHOTOS = os.path.join(SITE, "guide")  # one small photo per species, named by its iNaturalist number
GUIDE_API = "https://api.inaturalist.org/v1/"
GUIDE_PLACE = 8638  # Bermuda on iNaturalist
GUIDE_AGENT = "BermudaHub/1.32 (+https://github.com/mkatzsch/bermuda-hub)"
GUIDE_GROUPS = ["Aves", "Actinopterygii", "Mammalia", "Reptilia,Amphibia", "Mollusca", "Insecta,Arachnida", "Plantae",
                "Animalia", "Fungi"]  # must match GROUPS in the Explore script
GUIDE_STATUS = {"EX": "Extinct", "EW": "Extinct in the wild", "CR": "Critically endangered", "EN": "Endangered",
                "VU": "Vulnerable", "NT": "Near threatened", "LC": "Least concern", "DD": "Data deficient"}


def log(msg: str) -> None:
    line = "[%s] %s" % (dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(cmd: list[str], cwd: str, label: str) -> bool:
    log("%s: %s" % (label, " ".join(cmd)))
    r = subprocess.run([sys.executable] + cmd, cwd=cwd)
    log("%s: %s" % (label, "ok" if r.returncode == 0 else "exit %d" % r.returncode))
    return r.returncode == 0


def deals(collect: bool) -> None:
    if collect:
        run(["collect.py"], DEALS, "deals collect")
    else:
        run(["build.py"], DEALS, "deals build")
    src = os.path.join(DEALS, "report.html")
    if os.path.exists(src):
        shutil.copy(src, os.path.join(SITE, "deals.html"))


def events(collect: bool) -> None:
    db = os.path.join(EVENTS, "data", "tidewatch.sqlite")
    if not os.path.exists(db):
        run(["-m", "tidewatch", "seed"], EVENTS, "events seed")
    ok = run(["-m", "tidewatch", "run" if collect else "render"], EVENTS, "events " + ("run" if collect else "render"))
    if not ok:
        log("events: one or more steps failed; see run_output.txt for the lines starting with !!")


BACKUP_ITEMS = [
    "events/data/tidewatch.sqlite", "events/config.yaml", "events/data/football_fixtures.txt", "events/data/football_results.csv",
    "events/data/manual_events.json", "events/data/manual_blocks.json", "events/data/weather.json",
    "deals/history.csv", "deals/editorial.json", "deals/config.json", "deals/status.json",
    "deals/data/latest.json", "deals/data/menus.json", "deals/data/menus_meta.json", "deals/data/flyers",
]


def backup() -> None:
    """Copy the files that exist nowhere else to OneDrive. Code is backed up by GitHub; flyer images and
    the rendered pages are rebuildable, so they stay local. Skipped quietly when OneDrive is not present."""
    base = os.environ.get("OneDrive") or os.environ.get("OneDriveCommercial") or os.environ.get("OneDriveConsumer")
    if not base or not os.path.isdir(base):
        log("backup: no OneDrive folder found, skipped")
        return
    dest = os.path.join(base, "BermudaHub-backup")
    n = 0
    for rel in BACKUP_ITEMS:
        src = os.path.join(ROOT, rel)
        if not os.path.exists(src):
            continue
        tgt = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(tgt), exist_ok=True)
        if os.path.isdir(src):
            shutil.copytree(src, tgt, dirs_exist_ok=True)
        else:
            shutil.copy2(src, tgt)
        n += 1
    # keep the last 14 daily deal snapshots too
    snaps = os.path.join(ROOT, "deals", "data")
    if os.path.isdir(snaps):
        days = sorted(d for d in os.listdir(snaps) if len(d) == 10 and d[4] == "-")[-14:]
        for d in days:
            shutil.copytree(os.path.join(snaps, d), os.path.join(dest, "deals", "data", d), dirs_exist_ok=True)
    log("backup: %d items copied to %s" % (n, dest))


def find_git() -> str | None:
    """git on the PATH, or the copy GitHub Desktop installs under the user's profile."""
    import glob
    if shutil.which("git"):
        return "git"
    for pat in (os.path.join(os.environ.get("LOCALAPPDATA", ""), "GitHubDesktop", "app-*", "resources", "app", "git", "cmd", "git.exe"),
                os.path.join(os.environ.get("PROGRAMFILES", ""), "Git", "cmd", "git.exe")):
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


def publish_github() -> None:
    """Copy site/ to docs/, commit everything the ignore file allows, push. Skipped when the folder is not a repository."""
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        log("github: not a repository yet, skipped")
        return
    git = find_git()
    if not git:
        log("github: git not found (install GitHub Desktop or Git for Windows), skipped")
        return
    os.makedirs(DOCS, exist_ok=True)
    for name in os.listdir(SITE):
        src = os.path.join(SITE, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(DOCS, name))
    if os.path.isdir(GUIDE_PHOTOS):  # the Field guide photos, copied only when new or changed
        os.makedirs(os.path.join(DOCS, "guide"), exist_ok=True)
        for name in os.listdir(GUIDE_PHOTOS):
            src, dst = os.path.join(GUIDE_PHOTOS, name), os.path.join(DOCS, "guide", name)
            if os.path.isfile(src) and (not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src)):
                shutil.copy2(src, dst)
    hub = os.path.join(SITE, "hub.html")
    if os.path.isfile(hub):  # the Pages home page is the full Hub: site/index.html has no weather or explore data inside
        shutil.copy2(hub, os.path.join(DOCS, "index.html"))
    with open(os.path.join(DOCS, ".nojekyll"), "w") as f:  # serve files as they are
        f.write("")
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    def g(*args):
        return subprocess.run([git, "-C", ROOT] + list(args), capture_output=True, text=True)
    g("add", "-A")
    r = g("commit", "-m", "Build " + stamp)
    if r.returncode != 0 and "nothing to commit" in (r.stdout + r.stderr):
        log("github: nothing new to commit")
    elif r.returncode != 0:
        log("github: commit failed: " + (r.stderr or r.stdout).strip()[:200])
        return
    r = g("push")
    if r.returncode == 0:
        log("github: pushed build " + stamp)
    else:
        log("github: push failed (open GitHub Desktop and press Push origin): " + (r.stderr or r.stdout).strip()[-200:])


def front_door() -> None:
    """site/index.html: a shell with a What's on / Deals switch that loads the two pages (for the laptop),
    and site/hub.html: the same shell with both pages embedded, one file that can be published anywhere."""
    stamp = dt.date.today().strftime("%d %b %Y").lstrip("0")
    html = FRONT.replace("{{STAMP}}", stamp)
    try:
        write_share_files()
    except Exception as e:  # the icons are a nicety: never let them stop a build
        log("share files: skipped (%s)" % str(e)[:80])
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    pages = {}
    for name in ("planner", "deals"):
        fp = os.path.join(SITE, name + ".html")
        if os.path.exists(fp):
            with open(fp, encoding="utf-8") as f:
                html_in = f.read()
            # a nested frame may not open new windows in the artifact viewer, so links are passed up to the front door
            relay = ("<script>document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href]');"
                     "if(!a)return;var h=a.getAttribute('href')||'';if(!/^https?:/i.test(h))return;e.preventDefault();"
                     "try{parent.postMessage({hubOpen:a.href},'*')}catch(x){}},true);</script>")
            html_in = html_in.replace("</body>", relay + "</body>", 1) if "</body>" in html_in else html_in + relay
            # the dusk skin goes at the very end of the page so it wins over the page's own colours. The two pages
            # use the name --muted differently (a background tint on the planner, soft text on deals).
            skin = DUSK_SKIN.replace("{{MUTED}}", "#2e1a66" if name == "planner" else "#cdbbea")
            head, sep, tail = html_in.rpartition("</body>")
            html_in = head + skin + sep + tail if sep else html_in + skin
            pages[name] = html_in.replace("</script", "<\\/script")  # keep the embedded page out of its holder tag
    if len(pages) == 2:
        best = best_buys(os.path.join(SITE, "deals.html"))
        hub = html.replace("<title>Bermuda Hub</title>", "<title>Bermuda Hub</title>" + "".join(
            '\n<script type="text/plain" id="page-%s">%s</script>' % (n, pages[n]) for n in ("planner", "deals"))
            + '\n<script type="application/json" id="best-buys">%s</script>' % json.dumps(best, ensure_ascii=False).replace("</", "<\\/")
            + '\n<script type="application/json" id="weather-data">%s</script>' % json.dumps(weather_doc(), ensure_ascii=False).replace("</", "<\\/")
            + '\n<script type="application/json" id="explore-data">%s</script>' % json.dumps(explore_doc(), ensure_ascii=False).replace("</", "<\\/")
            + '\n<script type="application/json" id="today-data">%s</script>' % json.dumps(today_doc(), ensure_ascii=False).replace("</", "<\\/")
            + '\n<script type="application/json" id="transit-data">%s</script>' % json.dumps(transit_doc(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
            + '\n<script type="application/json" id="ferry-data">%s</script>' % json.dumps(ferry_doc(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
            + '\n<script type="application/json" id="ships-data">%s</script>' % json.dumps(ships_doc(), ensure_ascii=False).replace("</", "<\\/")
            + '\n<script type="application/json" id="pickleball-data">%s</script>' % json.dumps(pickleball_doc(), ensure_ascii=False).replace("</", "<\\/")
            + '\n<script type="application/json" id="yoga-data">%s</script>' % json.dumps(yoga_doc(), ensure_ascii=False).replace("</", "<\\/")
            + '\n<script type="application/json" id="yachts-data">%s</script>' % json.dumps(superyachts_doc(), ensure_ascii=False).replace("</", "<\\/")
            + '\n<script type="application/json" id="dive-data">%s</script>' % json.dumps(dive_doc(), ensure_ascii=False).replace("</", "<\\/")
            + '\n<script type="application/json" id="guide-data">%s</script>' % json.dumps(guide_doc(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
        swap = "f.srcdoc=document.getElementById('page-'+p).textContent.replace(/<\\\\\\/script/g,'</script')"
        assert "f.src=p+'.html'" in hub, "front door template changed: the page swap no longer matches"
        hub = hub.replace("f.src=p+'.html'", swap)
        hub = hub.replace('<iframe id="f" src="planner.html" title="page"></iframe>', '<iframe id="f" title="page"></iframe>')
        with open(os.path.join(SITE, "hub.html"), "w", encoding="utf-8") as f:
            f.write(hub)
        log("hub.html written, %d KB" % (len(hub.encode("utf-8")) // 1024))


def write_share_files() -> None:
    """The home screen name and icons for the website: site/manifest.webmanifest, icon-192.png, icon-512.png and
    apple-touch-icon.png. Depends on: Pillow for the pictures (they are drawn here, a dusk sky, a sun and the sea);
    without Pillow only the manifest is written."""
    manifest = {"name": "Bermuda Hub", "short_name": "Bermuda Hub", "description": "The Bermuda everything app",
                "start_url": "./", "scope": "./", "display": "standalone", "background_color": "#170f3a", "theme_color": "#170f3a",
                "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
                          {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}
    with open(os.path.join(SITE, "manifest.webmanifest"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return
    big = 1024
    im = Image.new("RGB", (big, big), "#170f3a")
    d = ImageDraw.Draw(im)
    for y in range(big):  # dusk sky: navy at the top to purple at the horizon
        t = y / big
        d.line([(0, y), (big, y)], fill=(int(23 + (61 - 23) * t), int(15 + (18 - 15) * t), int(58 + (96 - 58) * t)))
    d.ellipse([big * 0.28, big * 0.22, big * 0.72, big * 0.66], fill="#ff4fa3")  # the sun
    for i, col in enumerate(("#2af0d9", "#16b9c9", "#0f6f8f")):  # three bands of sea
        top = big * (0.56 + 0.13 * i)
        d.rectangle([0, top, big, big], fill=col)
        for x in range(0, big, 128):  # a scalloped wave edge along the top of each band
            d.ellipse([x - 16 + 64 * (i % 2), top - 34, x + 112 + 64 * (i % 2), top + 34], fill=col)
    for name, size in (("icon-512.png", 512), ("icon-192.png", 192), ("apple-touch-icon.png", 180)):
        im.resize((size, size), Image.LANCZOS).save(os.path.join(SITE, name), "PNG", optimize=True)


def today_doc() -> dict:
    """The coming week of what's on, lifted from the planner page's own event lists, for the Today tab."""
    out = {"events": []}
    fp = os.path.join(SITE, "planner.html")
    if not os.path.exists(fp):
        return out
    with open(fp, encoding="utf-8") as f:
        html_in = f.read()
    start = dt.date.today()
    days = {((start + dt.timedelta(days=i)).month, (start + dt.timedelta(days=i)).day) for i in range(8)}
    seen = set()
    for key, view in (("K", "Kids"), ("A", "Adults"), ("M", "Music"), ("S", "Sports")):
        m = re.search(r"const EVENTS_%s = (\[.*?\]);\n" % key, html_in, flags=re.S)
        if not m:
            continue
        try:
            rows = json.loads(m.group(1))
        except ValueError:
            continue
        for e in rows:
            k = (e.get("m"), e.get("d"), (e.get("name") or "").strip().lower())
            if (e.get("m"), e.get("d")) in days and k not in seen and not e.get("remove"):
                seen.add(k)
                out["events"].append({"m": e.get("m"), "d": e.get("d"), "name": e.get("name", ""), "t": e.get("t", ""),
                                      "venue": e.get("venue", ""), "view": view})
    return out


SHIP_DAYS = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]  # the schedule week runs Saturday to Friday
SHIP_DAY_RE = re.compile(r"\b[Oo]n (" + "|".join(SHIP_DAYS) + r")\b")
SHIP_NAME_RE = re.compile(r"\bthe ((?:[A-Z0-9][\w'’.\-]*)(?: (?:of|the|de|del|la|[A-Z0-9][\w'’.\-]*))*)")
SHIP_KIND_RE = re.compile(r"\b((?:[a-z]+(?: and | |/))*?(?:ships?|vessels?|carriers?|tankers?|transfers?|tugs?|yachts?|barges?))\b")


# Kept by hand. Keys are in lower case, as the schedule story prints them. Values are what the page shows.
SHIPS_V = 3  # format number of events/data/ships.json. Raise it whenever these tables or the reader change.
SHIP_NAMES = {
    "ccl eclipse": "Celebrity Eclipse",  # the port schedule shortens Celebrity Cruises to CCL
}
SHIP_KNOWN = {  # ships looked up one by one: the type, and the usual cargo where that is known. These win over the story.
    "cartagena": "general cargo ship",  # IMO 9521863, 150 m, Liberia flag. Usual cargo not established
    "grit cement iv": "cement ship",  # brings bulk cement for the Maxcem silos in Dockyard
}
SHIP_INFO = {  # ships looked up one by one: IMO number (the ship's permanent number), year built, length in metres
    "oleander": {"imo": 9827334, "built": 2019, "length_m": 120},
    "somers isles": {"imo": 9375147, "built": 2012, "length_m": 99},
    "bermuda islander": {"imo": 9234434, "built": 2001, "length_m": 100},
    "cartagena": {"imo": 9521863, "built": 2012, "length_m": 150},
}
SHIP_KINDS = {  # for ships not in SHIP_KNOWN
    "discharge ship": "bulk cargo ship",  # a ship in port to unload loose cargo such as cement or gravel
    "discharge vessel": "bulk cargo ship",
}


def ships_tidy(name: str, kind: str) -> dict:
    """Plain words for one ship: {"name", "kind"}, plus "said_name" and "said_kind" where the story's wording was changed.
    Where the ship is in SHIP_INFO its "imo", "built" and "length_m" are added.
    Depends on: SHIP_NAMES, SHIP_KNOWN, SHIP_INFO and SHIP_KINDS above."""
    shown = SHIP_NAMES.get(name.lower(), name)
    out = {"name": shown, "kind": SHIP_KNOWN.get(shown.lower(), SHIP_KINDS.get(kind.lower(), kind))}
    if out["name"] != name:
        out["said_name"] = name
    if out["kind"] != kind:
        out["said_kind"] = kind
    out.update(SHIP_INFO.get(shown.lower(), {}))
    return out


def ships_parse(text: str) -> list:
    """[(weekday, ship name, kind)] from the sentences of a weekly shipping schedule story, which read
    'On Tuesday the Celebrity Apex cruise ship is expected, on Wednesday the X and the Y cruise ships will arrive'."""
    text = re.sub(r"\s+", " ", text or "")
    marks = [(m.start(), m.group(1)) for m in SHIP_DAY_RE.finditer(text)]
    out, seen = [], set()
    for i, (pos, day) in enumerate(marks):
        chunk = text[pos:marks[i + 1][0] if i + 1 < len(marks) else len(text)]
        cut = re.search(r"The weekly shipping schedule|Read More|Category:", chunk)
        if cut:
            chunk = chunk[:cut.start()]
        for m in SHIP_NAME_RE.finditer(chunk):
            name = m.group(1).strip(" .,")
            if name.split()[0] == "Department" or name in SHIP_DAYS:
                continue
            t = SHIP_KIND_RE.search(chunk, m.end())
            if t and re.search(r"\b(expected|arrive|scheduled)\b", chunk[m.end():t.start()]):
                t = None  # the kind found belongs to a later sentence
            kind = re.sub(r"^(is|are|and|the|will|a) ", "", re.sub(r"s$", "", t.group(1).strip())) if t else "ship"
            if (day, name.lower()) not in seen:
                seen.add((day, name.lower()))
                out.append((day, name, "cruise ship" if kind.startswith("cruise") else kind))
    return out


def ships_collect(force: bool = False) -> None:
    """Save the ships due in port this week.

    Depends on: the internet (bernews.com, which posts the Department of Marine and Ports weekly shipping schedule
    every Saturday under a web address that names the week). Writes: events/data/ships.json.
    Runs once a day at most unless forced (--ships). Any failure keeps the copy already saved."""
    import html as htmllib
    import urllib.request
    today = dt.date.today()
    old = {}
    if os.path.exists(SHIPS_JSON):
        try:
            with open(SHIPS_JSON, encoding="utf-8") as f:
                old = json.load(f)
        except ValueError:
            old = {}
    if not force and old.get("read") == today.isoformat() and old.get("v") == SHIPS_V:
        return
    sat = today - dt.timedelta(days=(today.weekday() - 5) % 7)  # the Saturday this schedule week began

    def get(url: str) -> str:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BermudaHub/1.40 (+https://github.com/mkatzsch/bermuda-hub)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "replace")

    def story(page: str) -> str:
        body = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", page)
        body = htmllib.unescape(re.sub(r"<[^>]+>", " ", body))
        m = SHIP_DAY_RE.search(body)
        return body[m.start():m.start() + 4000] if m else ""

    month, tried, found = sat.strftime("%B").lower(), [], None
    base = "https://bernews.com/%d/%02d/shipping-schedule-week-starting-" % (sat.year, sat.month)
    for slug in ("%s-%d" % (month, sat.day), "%s-%d-2" % (month, sat.day), "%s-%d" % (month[:3], sat.day), "%s-%d-2" % (month[:3], sat.day), "%s-%d-3" % (month, sat.day)):
        url = base + slug + "/"
        try:
            rows = ships_parse(story(get(url)))
            tried.append(slug + ": %d ships" % len(rows))
            if rows:
                found = (url, rows)
                break
        except Exception as e:
            tried.append(slug + ": " + str(e)[:40])
    if not found:  # the address did not follow the usual pattern: look for this week's story in the site's own search
        try:
            page = get("https://bernews.com/?s=shipping+schedule+week+starting")
            for link in re.findall(r'href="(https://bernews\.com/%d/\d\d/shipping-schedule-week-starting-[a-z0-9\-]+/?)"' % sat.year, page):
                if re.search(r"-%d(-\d)?/?$" % sat.day, link) and (month in link or month[:3] in link):
                    rows = ships_parse(story(get(link)))
                    if rows:
                        found = (link, rows)
                        break
        except Exception as e:
            tried.append("search: " + str(e)[:40])
    if not found:
        log("ships: this week's schedule was not found (%s), the saved copy stays as it is" % "; ".join(tried)[:200])
        return
    url, rows = found
    ships = [{"date": (sat + dt.timedelta(days=SHIP_DAYS.index(day))).isoformat(), "day": day, **ships_tidy(name, kind)} for day, name, kind in rows]
    tmp = SHIPS_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"v": SHIPS_V, "week": sat.isoformat(), "read": today.isoformat(), "source": url, "ships": ships}, f, ensure_ascii=False, indent=1)
    os.replace(tmp, SHIPS_JSON)
    log("ships: %d due in the week of %s (%d cruise)" % (len(ships), sat.isoformat(), sum(1 for x in ships if x["kind"] == "cruise ship")))


def transit_parse(blob: bytes) -> dict:
    """Turn a GTFS zip (the standard public transport timetable format) into the small document the Hub keeps.

    Reads routes.txt, trips.txt, stop_times.txt, stops.txt, calendar.txt, calendar_dates.txt and feed_info.txt.
    Every trip is kept as its first and last stop with their times. Ferry trips also keep every stop they call at."""
    import csv
    import io
    import zipfile
    z = zipfile.ZipFile(io.BytesIO(blob))
    names = {n.lower().split("/")[-1]: n for n in z.namelist()}

    def table(name: str) -> list:
        if name not in names:
            return []
        with z.open(names[name]) as f:
            rows = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline=""))
            return [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in rows]

    def day(v: str) -> str:
        return "%s-%s-%s" % (v[:4], v[4:6], v[6:8]) if len(v) == 8 and v.isdigit() else ""

    def clock(v: str) -> str:
        m = re.match(r"^(\d{1,2}):(\d\d)", v or "")
        return "%02d:%s" % (int(m.group(1)), m.group(2)) if m else ""  # hours past 24 mean after midnight, kept as given

    stops = {r.get("stop_id"): r for r in table("stops.txt")}
    services = {}
    for r in table("calendar.txt"):
        services[r.get("service_id")] = {"days": "".join("1" if r.get(d) == "1" else "0" for d in ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")),
                                         "start": day(r.get("start_date", "")), "end": day(r.get("end_date", "")), "add": [], "remove": []}
    for r in table("calendar_dates.txt"):
        sv = services.setdefault(r.get("service_id"), {"days": "0000000", "start": "", "end": "", "add": [], "remove": []})
        if day(r.get("date", "")):
            sv["add" if r.get("exception_type") == "1" else "remove"].append(day(r.get("date", "")))
    calls = {}
    n_times = n_blank = 0
    for r in table("stop_times.txt"):
        n_times += 1
        t = clock(r.get("departure_time") or r.get("arrival_time")), clock(r.get("arrival_time") or r.get("departure_time"))
        if not t[0]:
            n_blank += 1
        try:
            seq = int(float(r.get("stop_sequence") or 0))
        except ValueError:
            seq = 0
        calls.setdefault(r.get("trip_id"), []).append((seq, r.get("stop_id"), t[0], t[1]))
    def minute(v: str) -> int:
        return int(v[:2]) * 60 + int(v[3:5])

    stop_ix, stop_list, pat_ix, patterns, tim_ix, timings = {}, [], {}, [], {}, []

    def intern(key, index: dict, store: list, value) -> int:
        if key not in index:
            index[key] = len(store)
            store.append(value)
        return index[key]

    routes, order = {}, []
    for r in table("routes.txt"):
        kind = r.get("route_type", "")
        routes[r.get("route_id")] = {"id": r.get("route_id"), "short": r.get("route_short_name", ""), "long": r.get("route_long_name", ""),
                                     "mode": "ferry" if kind in ("4", "1200") else "bus" if kind in ("3", "700") or kind.startswith("7") else "other",
                                     "color": r.get("route_color", ""), "groups": {}}
        order.append(r.get("route_id"))
    n_trips = 0
    for r in table("trips.txt"):
        rt, seq = routes.get(r.get("route_id")), sorted(calls.get(r.get("trip_id"), []))
        timed = [c for c in seq if c[2]]
        if not rt or len(seq) < 2 or len(timed) < 2:
            continue
        name = lambda c: (stops.get(c[1]) or {}).get("stop_name", c[1])
        first, last = timed[0], timed[-1]
        g = rt["groups"].setdefault((name(first), name(last), r.get("trip_headsign", "")), {"from": name(first), "to": name(last), "headsign": r.get("trip_headsign", ""), "dir": r.get("direction_id", ""), "stops": len(seq), "trips": []})
        row = [r.get("service_id"), first[2], last[3] or last[2]]
        if rt["mode"] == "ferry":
            row.append([[name(c), c[2]] for c in timed])
        else:  # every stop on the run and the minutes from the first stop to each one
            ids = []
            for c in timed:
                st = stops.get(c[1]) or {}
                try:
                    where = [st.get("stop_name", c[1]), round(float(st.get("stop_lat")), 5), round(float(st.get("stop_lon")), 5)]
                except (TypeError, ValueError):
                    where = [st.get("stop_name", c[1]), None, None]
                ids.append(intern(c[1], stop_ix, stop_list, where))
            offs = [minute(c[2]) - minute(first[2]) for c in timed]
            row += [intern(tuple(ids), pat_ix, patterns, ids), intern(tuple(offs), tim_ix, timings, offs)]
        g["trips"].append(row)
        g["stops"] = max(g["stops"], len(seq))
        n_trips += 1
    out = []
    for rid in order:
        rt = routes[rid]
        rt["groups"] = sorted(rt["groups"].values(), key=lambda g: (-len(g["trips"]), g["from"], g["to"]))
        for g in rt["groups"]:
            g["trips"].sort(key=lambda t: (t[1], t[0]))
        if rt["groups"]:
            out.append(rt)
    info = (table("feed_info.txt") or [{}])[0]
    used = {t[0] for rt in out for g in rt["groups"] for t in g["trips"]}
    ferry_stops = sorted({c[0] for rt in out if rt["mode"] == "ferry" for g in rt["groups"] for t in g["trips"] for c in t[3]})
    by_name = {v.get("stop_name"): v for v in stops.values()}
    return {"feed": {"start": day(info.get("feed_start_date", "")), "end": day(info.get("feed_end_date", "")) or max([v["end"] for v in services.values() if v["end"]] or [""]),
                     "version": info.get("feed_version", ""), "publisher": info.get("feed_publisher_name", "")},
            "stats": {"routes": len(out), "trips": n_trips, "stops": len(stops), "stop_times": n_times, "stop_times_without_a_time": n_blank, "files": sorted(names),
                      "bus_stops": len(stop_list), "patterns": len(patterns), "timings": len(timings)},
            "stops": stop_list, "patterns": patterns, "timings": timings,
            "services": {k: v for k, v in services.items() if k in used},
            "docks": [{"name": n, "lat": float(by_name[n]["stop_lat"]), "lon": float(by_name[n]["stop_lon"])} for n in ferry_stops if n in by_name and by_name[n].get("stop_lat") and by_name[n].get("stop_lon")],
            "routes": out}


def transit_collect(force: bool = False) -> None:
    """Save the bus and ferry timetables.

    Depends on: the internet (TRANSIT_FEED, the official GTFS feed for Bermuda's buses and ferries). The zip is read
    in memory and never saved or run. Writes: events/data/transit.json.
    Runs when there is no saved copy, the saved copy is a week old, its feed has run out, or when forced (--transit).
    Any failure keeps the copy already saved."""
    import urllib.request
    today = dt.date.today()
    old = {}
    if os.path.exists(TRANSIT_JSON):
        try:
            with open(TRANSIT_JSON, encoding="utf-8") as f:
                old = json.load(f)
        except ValueError:
            old = {}
    if not force and old.get("v") == TRANSIT_V and old.get("read") and (today - dt.date.fromisoformat(old["read"])).days < 7 and (old.get("feed", {}).get("end") or "9999") >= today.isoformat():
        return
    req = urllib.request.Request(TRANSIT_FEED, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BermudaHub/1.42 (+https://github.com/mkatzsch/bermuda-hub)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        blob = r.read(40 * 1024 * 1024)
    doc = transit_parse(blob)
    if not doc["routes"]:
        log("transit: the feed was read (%d KB) but held no trips, the saved copy stays as it is" % (len(blob) // 1024))
        return
    doc = dict({"v": TRANSIT_V, "read": today.isoformat(), "source": TRANSIT_FEED}, **doc)
    tmp = TRANSIT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, TRANSIT_JSON)
    st = doc["stats"]
    log("transit: %d routes (%d ferry), %d trips, %d bus stops, %d stop patterns, %d timings, feed %s to %s, %d KB saved" % (
        st["routes"], sum(1 for x in doc["routes"] if x["mode"] == "ferry"), st["trips"], st["bus_stops"], st["patterns"], st["timings"], doc["feed"]["start"], doc["feed"]["end"], os.path.getsize(TRANSIT_JSON) // 1024))


def transit_doc(days: int = 7) -> dict:
    """The bus timetable for the page: which services run on each of the next few days, and every bus departure
    on those services. Ferries are left out while the feed only holds the summer ferry timetable."""
    if not os.path.exists(TRANSIT_JSON):
        return {}
    try:
        with open(TRANSIT_JSON, encoding="utf-8") as f:
            doc = json.load(f)
    except ValueError:
        return {}
    svc = doc.get("services", {})
    buses = [r for r in doc.get("routes", []) if r.get("mode") == "bus"]
    regular = {t[0] for r in buses if r.get("short") for g in r["groups"] for t in g["trips"]}  # services the numbered routes use
    every = {t[0] for r in buses for g in r["groups"] for t in g["trips"]}

    def runs(sid: str, date: dt.date, ignore_end: bool = False) -> bool:
        sv, iso = svc.get(sid), date.isoformat()
        if not sv:
            return False
        if iso in sv["add"]:
            return True
        if iso in sv["remove"] or sv["days"][date.weekday()] != "1":
            return False
        return (ignore_end and sv["end"] < iso) or (sv["start"] <= iso <= sv["end"])

    today, out_days, keep = dt.date.today(), [], set()
    for i in range(days):
        date = today + dt.timedelta(days=i)
        on, old = sorted(x for x in every if runs(x, date)), ""
        if not any(x in regular for x in on):  # nothing published for this day: fall back to the last timetable that covered this weekday
            past = [x for x in regular if runs(x, date, ignore_end=True)]
            if past:
                old = max(svc[x]["end"] for x in past)
                on += sorted(x for x in past if svc[x]["end"] == old)
        keep.update(on)
        out_days.append({"date": date.isoformat(), "on": on, "old": old})
    sids = sorted(keep)
    routes = []
    for r in buses:
        groups = []
        for g in r["groups"]:
            trips = [[sids.index(t[0]), t[1], t[2]] + t[3:5] for t in g["trips"] if t[0] in keep]
            if trips:
                groups.append({"from": g["from"], "to": g["to"], "head": g.get("headsign", ""), "trips": trips})
        if groups:
            routes.append({"short": r.get("short", ""), "long": r.get("long", ""), "color": r.get("color", ""), "groups": groups})
    routes.sort(key=lambda r: (not r["short"], int(r["short"]) if r["short"].isdigit() else 999, r["long"]))
    for d in out_days:
        d["on"] = [sids.index(x) for x in d["on"]]
    return {"read": doc.get("read", ""), "feed_end": doc.get("feed", {}).get("end", ""), "days": out_days, "routes": routes,
            "stops": doc.get("stops", []), "patterns": doc.get("patterns", []), "timings": doc.get("timings", []),
            "docks": doc.get("docks", []),
            "ferry_feed_ended": max([v["end"] for k, v in svc.items() if "ferry" in k.lower()] or [""])}


def ferry_doc() -> dict:
    """The ferry schedule for the page.

    Depends on: events/data/ferries.json (typed in from the Marine and Ports brochure, see its "how" note) and, for
    public holidays, events/data/transit.json (a day the bus feed takes its weekday service off is a holiday)."""
    if not os.path.exists(FERRY_JSON):
        return {}
    try:
        with open(FERRY_JSON, encoding="utf-8") as f:
            doc = json.load(f)
    except ValueError:
        return {}
    today = dt.date.today().isoformat()
    if today < doc.get("effective", ""):
        return {}
    doc.pop("how", None)
    doc["stale"] = bool(doc.get("review_after")) and today > doc["review_after"]
    if doc["stale"]:
        log("ferries: events/data/ferries.json passed its review date (%s). Check for a new schedule and update the file." % doc["review_after"])
    holidays = []
    try:
        with open(TRANSIT_JSON, encoding="utf-8") as f:
            svc = json.load(f).get("services", {})
        holidays = sorted({d for k, v in svc.items() if v.get("days") == "1111100" for d in v.get("remove", []) if d >= today})
    except (OSError, ValueError):
        pass
    doc["holidays"] = holidays
    return doc


def pickleball_doc() -> dict:
    """Pickleball venues, weekly sessions and events for the Sports tab.

    Depends on: events/data/pickleball.json (kept by hand, see its "how" note). Past its review_after date the
    build log warns and the page says the details may be out of date."""
    if not os.path.exists(PICKLEBALL_JSON):
        return {}
    try:
        with open(PICKLEBALL_JSON, encoding="utf-8") as f:
            doc = json.load(f)
    except ValueError:
        log("pickleball: events/data/pickleball.json could not be read, the section is left out")
        return {}
    doc.pop("how", None)
    doc["stale"] = bool(doc.get("review_after")) and dt.date.today().isoformat() > doc["review_after"]
    if doc["stale"]:
        log("pickleball: events/data/pickleball.json passed its review date (%s). Check the association website and update the file." % doc["review_after"])
    return doc


# Studios that book through TeamUp: the id used in events/data/yoga.json, then the provider number in the studio's
# TeamUp address (goteamup.com/p/<number>-<name>/).
YOGA_TEAMUP = {"shamana": "7167098", "salt": "7577870"}
YOGA_LIVE_V = 1  # format number of events/data/yoga_live.json
YOGA_DAYS = 8  # how many days ahead to keep, today included


def yoga_teamup(provider: str, first: dt.date, last: dt.date, get=None) -> list:
    """The classes one TeamUp studio lists from first to last, as [{date, start, end, name, with, venue}].

    Depends on: the internet (goteamup.com/api/v2/events, the public data service behind every TeamUp booking page).
    The service lists a studio's classes oldest first, a page at a time. It is first asked for the date range
    directly, under the few names that filter could have; an answer only counts if its classes really fall in the
    range. If none works, the last pages of the full list are read instead, newest last, until they reach back
    past the first date. get is only passed in by tests."""
    import urllib.parse
    import urllib.request

    def fetch(params: dict) -> dict:
        url = "https://goteamup.com/api/v2/events?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BermudaHub/1.52 (+https://github.com/mkatzsch/bermuda-hub)",
                                                   "Accept": "application/json", "TeamUp-Provider-ID": provider, "TeamUp-Request-Mode": "customer"})
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.loads(r.read().decode("utf-8", "replace"))

    get = get or fetch
    a, b = first.isoformat(), last.isoformat()
    base = {"page_size": 200, "expand": "instructors,venue"}
    inside = lambda rows: [e for e in rows if a <= (e.get("starts_at") or "")[:10] <= b]
    rows = None
    for lo, hi in (("starts_at_gte", "starts_at_lte"), ("starts_at__gte", "starts_at__lte"), ("start_date", "end_date"), ("startdate", "enddate"), ("starts_at_min", "starts_at_max")):
        try:
            doc = get(dict(base, **{lo: a + "T00:00:00", hi: b + "T23:59:59"}))
        except Exception:
            continue
        got = doc.get("results") or []
        if got and len(inside(got)) == len(got) and not doc.get("next"):
            rows = got
            break
    if rows is None:  # no filter was understood: walk back from the end of the whole list
        doc = get(dict(base, page=1))
        pages = max(1, -(-int(doc.get("count") or 0) // 200))
        rows = []
        for page in range(pages, max(0, pages - 8), -1):
            got = (get(dict(base, page=page)) if page > 1 else doc).get("results") or []
            rows = got + rows
            if not got or min((e.get("starts_at") or "9")[:10] for e in got) < a:
                break
    out = []
    for e in inside(rows):
        venue = e.get("venue") if isinstance(e.get("venue"), dict) else {}
        if e.get("status") != "active" or e.get("is_appointment") or venue.get("is_online"):
            continue
        who = [str(i.get("name") or "").strip().split(" ")[0].title() for i in (e.get("instructors") if isinstance(e.get("instructors"), list) else [])]
        out.append({"date": e["starts_at"][:10], "start": e["starts_at"][11:16], "end": (e.get("ends_at") or e["starts_at"])[11:16],
                    "name": re.sub(r"\s+", " ", str(e.get("name") or "")).strip(), "with": " and ".join(w for w in who if w),
                    "venue": re.sub(r"\s+", " ", str(venue.get("name") or "")).strip()})
    return sorted(out, key=lambda x: (x["date"], x["start"], x["name"]))


def yoga_collect(force: bool = False) -> None:
    """Save the coming week of classes at the studios in YOGA_TEAMUP.

    Depends on: yoga_teamup above and the internet. Writes: events/data/yoga_live.json.
    Runs once a day at most unless forced (--yoga). A studio that cannot be read keeps the classes saved before."""
    today = dt.date.today()
    old = {}
    if os.path.exists(YOGA_LIVE_JSON):
        try:
            with open(YOGA_LIVE_JSON, encoding="utf-8") as f:
                old = json.load(f)
        except ValueError:
            old = {}
    if not force and old.get("read") == today.isoformat() and old.get("v") == YOGA_LIVE_V:
        return
    studios, notes = {}, []
    for sid, provider in YOGA_TEAMUP.items():
        try:
            studios[sid] = yoga_teamup(provider, today, today + dt.timedelta(days=YOGA_DAYS - 1))
            notes.append("%s %d" % (sid, len(studios[sid])))
        except Exception as e:
            kept = [c for c in (old.get("studios") or {}).get(sid, []) if c.get("date", "") >= today.isoformat()]
            studios[sid] = kept
            notes.append("%s not read (%s), %d kept" % (sid, str(e)[:60], len(kept)))
    tmp = YOGA_LIVE_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"v": YOGA_LIVE_V, "read": today.isoformat(), "days": YOGA_DAYS, "studios": studios}, f, ensure_ascii=False, indent=1)
    os.replace(tmp, YOGA_LIVE_JSON)
    log("yoga: classes for the next %d days: %s" % (YOGA_DAYS, ", ".join(notes)))


YACHTS_FEED = "https://bernews.com/tag/super-yacht/feed/"  # the news feed of every Bernews story tagged super yacht
YACHTS_V = 1  # format number of events/data/superyachts_news.json


def superyachts_parse(xml_text: str) -> list:
    """[{date, title, url, feet, place}] from the Bernews super yacht news feed, newest first.

    Only the headline, date and link are kept, plus two facts picked out of the story's opening line: the
    length in feet and where the yacht stopped. The story text itself is not kept."""
    import email.utils
    import html as htmllib
    import xml.etree.ElementTree as ET
    out = []
    root = ET.fromstring(xml_text.encode("utf-8"))
    for item in root.iter("item"):
        title = re.sub(r"\s+", " ", htmllib.unescape(item.findtext("title") or "")).strip()
        url = (item.findtext("link") or "").strip()
        if not title or not url.startswith("https://bernews.com/"):
            continue
        try:
            date = email.utils.parsedate_to_datetime(item.findtext("pubDate") or "").date().isoformat()
        except (TypeError, ValueError):
            date = ""
        lead = re.sub(r"<[^>]+>", " ", htmllib.unescape(item.findtext("description") or ""))
        feet = re.search(r"\b(\d{2,3})(?:\.\d)?[- ]f(?:oo|ee)t\b", lead)
        place = re.search(r"St\.? George|Hamilton|Dockyard|[Ee]ast [Ee]nd|[Ww]est [Ee]nd", title + " " + lead)
        where = {"st": "St George's", "ha": "Hamilton", "do": "Dockyard", "ea": "the east end", "we": "the west end"}.get(place.group(0)[:2].lower(), "") if place else ""
        out.append({"date": date, "title": re.sub(r"^(Photos?|Videos?)(\s*[/&]\s*(Photos?|Videos?))?\s*:\s*", "", title), "url": url,
                    "feet": int(feet.group(1)) if feet else None, "place": where})
    return sorted(out, key=lambda x: x["date"], reverse=True)


def superyachts_collect(force: bool = False) -> None:
    """Save the recent superyacht visits Bernews has written up.

    Depends on: the internet (YACHTS_FEED) and superyachts_parse above. Writes: events/data/superyachts_news.json.
    Runs once a day at most unless forced (--yachts). Any failure keeps the copy already saved."""
    import urllib.request
    today = dt.date.today()
    old = {}
    if os.path.exists(YACHTS_NEWS_JSON):
        try:
            with open(YACHTS_NEWS_JSON, encoding="utf-8") as f:
                old = json.load(f)
        except ValueError:
            old = {}
    if not force and old.get("read") == today.isoformat() and old.get("v") == YACHTS_V:
        return
    try:
        req = urllib.request.Request(YACHTS_FEED, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BermudaHub/1.53 (+https://github.com/mkatzsch/bermuda-hub)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            visits = superyachts_parse(r.read().decode("utf-8", "replace"))
    except Exception as e:
        log("superyachts: the news feed was not read (%s), the saved copy stays as it is" % str(e)[:100])
        return
    if not visits:
        log("superyachts: the news feed had no stories, the saved copy stays as it is")
        return
    tmp = YACHTS_NEWS_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"v": YACHTS_V, "read": today.isoformat(), "source": "https://bernews.com/tag/super-yacht/", "visits": visits[:12]}, f, ensure_ascii=False, indent=1)
    os.replace(tmp, YACHTS_NEWS_JSON)
    log("superyachts: %d recent visits from Bernews, newest %s" % (len(visits[:12]), visits[0]["date"]))


def dive_doc() -> dict:
    """Snorkel spots and scuba operators for the Sports tab.

    Depends on: events/data/dive.json (kept by hand, see its "how" note). The snorkel beaches and the wrecks are
    named by their ids in events/data/explore.json, so the page takes their positions from there."""
    if not os.path.exists(DIVE_JSON):
        return {}
    try:
        with open(DIVE_JSON, encoding="utf-8") as f:
            doc = json.load(f)
    except ValueError:
        log("dive: events/data/dive.json could not be read, the snorkel and scuba sections are left out")
        return {}
    doc.pop("how", None)
    doc["stale"] = bool(doc.get("review_after")) and dt.date.today().isoformat() > doc["review_after"]
    if doc["stale"]:
        log("dive: events/data/dive.json passed its review date (%s). Check the operators and update the file." % doc["review_after"])
    return doc


def superyachts_doc() -> dict:
    """Superyacht berths, season and recent visits for the Ocean tab.

    Depends on: events/data/superyachts.json (kept by hand, see its "how" note) and, for recent visits,
    events/data/superyachts_news.json (written by superyachts_collect)."""
    if not os.path.exists(YACHTS_JSON):
        return {}
    try:
        with open(YACHTS_JSON, encoding="utf-8") as f:
            doc = json.load(f)
    except ValueError:
        log("superyachts: events/data/superyachts.json could not be read, the card is left out")
        return {}
    doc.pop("how", None)
    doc["stale"] = bool(doc.get("review_after")) and dt.date.today().isoformat() > doc["review_after"]
    if doc["stale"]:
        log("superyachts: events/data/superyachts.json passed its review date (%s). Check the marinas and update the file." % doc["review_after"])
    doc["visits"], doc["visits_read"], doc["visits_source"] = [], "", ""
    try:
        with open(YACHTS_NEWS_JSON, encoding="utf-8") as f:
            news = json.load(f)
        doc["visits"], doc["visits_read"], doc["visits_source"] = news.get("visits") or [], news.get("read", ""), news.get("source", "")
    except (OSError, ValueError):
        pass
    return doc


def yoga_doc() -> dict:
    """Yoga studios, hotel classes, weekly timetables and special sessions for the Sports tab.

    Depends on: events/data/yoga.json (kept by hand, see its "how" note). Past its review_after date the build log
    warns and the page says the details may be out of date."""
    if not os.path.exists(YOGA_JSON):
        return {}
    try:
        with open(YOGA_JSON, encoding="utf-8") as f:
            doc = json.load(f)
    except ValueError:
        log("yoga: events/data/yoga.json could not be read, the section is left out")
        return {}
    doc.pop("how", None)
    doc["stale"] = bool(doc.get("review_after")) and dt.date.today().isoformat() > doc["review_after"]
    if doc["stale"]:
        log("yoga: events/data/yoga.json passed its review date (%s). Check the studio websites and update the file." % doc["review_after"])
    # classes read from the booking service: only today onward, and a studio with classes counts as fully listed
    doc["live"], doc["live_read"] = [], ""
    try:
        with open(YOGA_LIVE_JSON, encoding="utf-8") as f:
            live = json.load(f)
        today = dt.date.today().isoformat()
        doc["live_read"] = live.get("read", "")
        for sid, rows in (live.get("studios") or {}).items():
            rows = [dict(c, p=sid) for c in rows if c.get("date", "") >= today]
            doc["live"].extend(rows)
            for place in doc.get("places", []):
                if place.get("id") == sid and rows:
                    place["full"] = True
    except (OSError, ValueError):
        pass
    return doc


def ships_doc() -> dict:
    """The saved week of ship arrivals for the page, dropped once the week it covers is over."""
    if not os.path.exists(SHIPS_JSON):
        return {}
    try:
        with open(SHIPS_JSON, encoding="utf-8") as f:
            doc = json.load(f)
        if (dt.date.today() - dt.date.fromisoformat(doc.get("week", "2000-01-01"))).days > 6:
            return {}
        return doc
    except ValueError:
        return {}


def explore_doc() -> dict:
    fp = os.path.join(EVENTS, "data", "explore.json")
    if not os.path.exists(fp):
        return {}
    try:
        with open(fp, encoding="utf-8") as f:
            doc = json.load(f)
    except ValueError:
        return {}
    try:  # web photos found by photos_collect, each with its credit and licence
        with open(os.path.join(EVENTS, "data", "explore_photos.json"), encoding="utf-8") as f:
            photos = json.load(f)
        for s in doc.get("sites", []):
            if s.get("id") in photos:
                s["photo"] = photos[s["id"]]
    except (OSError, ValueError):
        pass
    return doc


PHOTOS_JSON = os.path.join(EVENTS, "data", "explore_photos.json")  # one web photo per Explore place, with its credit
PHOTOS_REPORT = os.path.join(EVENTS, "data", "photos_report.json")  # what the photo collector found and did not find
PHOTO_LICENCES = ("cc0", "cc-by", "cc-by-sa", "cc-by-nc", "cc-by-nc-sa")  # iNaturalist codes that allow reuse and resizing
PHOTO_GENERIC = {"fort", "beach", "park", "house", "church", "bermuda", "island", "islands", "point", "battery", "nature",
                 "reserve", "museum", "historic", "cemetery", "national", "trust", "saint", "royal", "naval", "with",
                 "from", "that", "this", "near", "town", "road", "hill", "site", "wreck", "ruins", "ruin", "trail",
                 "walk", "gardens", "garden", "burial", "ground", "memorial", "tower", "station", "bridge", "cove"}


def photos_collect(force: bool = False) -> None:
    """Find a reusable photo for Field guide species and Explore places that have none.

    Depends on: the internet (api.inaturalist.org, en.wikipedia.org, commons.wikimedia.org), events/data/fieldguide.json
    and events/data/explore.json. Only photos whose licence allows reuse are taken (Creative Commons without the
    no changes clause, or public domain), and the credit and licence are saved with each one. Nothing is taken from
    news or tourism sites.
    Writes: events/data/fieldguide.json (an "alt" photo on a species iNaturalist has no shared photo for) and
    site/guide/<species number>.jpg, events/data/explore_photos.json, and events/data/photos_report.json.
    Runs when forced (--photos), or once every 30 days on a collecting run. Any failure keeps what is saved."""
    import html as htmllib
    import io
    import time
    import urllib.parse
    import urllib.request
    today = dt.date.today()
    report = {}
    if os.path.exists(PHOTOS_REPORT):
        try:
            with open(PHOTOS_REPORT, encoding="utf-8") as f:
                report = json.load(f)
        except ValueError:
            report = {}
    if not force and report.get("run") and (today - dt.date.fromisoformat(report["run"])).days < 30:
        return

    def get(url: str, binary: bool = False, pause: float = 0.5):
        last = None
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": GUIDE_AGENT})
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = r.read()
                time.sleep(pause)
                return data if binary else json.loads(data.decode("utf-8"))
            except Exception as e:  # network trouble of any kind: wait and try again
                last = e
                time.sleep(3 * (attempt + 1))
        raise last

    def plain(v: str, n: int = 80) -> str:
        t = re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", "", v or ""))).strip()
        return t if len(t) <= n else t[:n - 1].rstrip() + "…"

    def commons(params: str) -> list:
        """Files from Wikimedia Commons with a licence that allows reuse: [{title, thumb, page, by, lic, text}]."""
        j = get("https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo"
                "&iiprop=url|extmetadata|mime&iiurlwidth=640&" + params)
        pages = sorted((j.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
        out = []
        for p in pages:
            ii = (p.get("imageinfo") or [{}])[0]
            md = ii.get("extmetadata") or {}
            lic = plain((md.get("LicenseShortName") or {}).get("value", ""), 40)
            low = lic.lower()
            ok = (low.startswith("cc") and "nd" not in low) or low.startswith("public domain") or low in ("pd", "cc0")
            if not ok or ii.get("mime") not in ("image/jpeg", "image/png") or not ii.get("thumburl"):
                continue
            out.append({"title": p.get("title", ""), "thumb": ii["thumburl"], "page": ii.get("descriptionurl", ""),
                        "by": plain((md.get("Artist") or {}).get("value", "")) or "Unknown author", "lic": lic,
                        "text": (p.get("title", "") + " " + plain((md.get("ImageDescription") or {}).get("value", ""), 400) + " "
                                 + plain((md.get("Categories") or {}).get("value", ""), 400)).lower()})
        return out

    def wiki_image(title: str):
        """The lead picture of a Wikipedia article, if it lives on Commons under a reusable licence."""
        j = get("https://en.wikipedia.org/w/api.php?action=query&format=json&redirects=1&prop=pageimages&piprop=name&titles="
                + urllib.parse.quote(title))
        for p in (j.get("query") or {}).get("pages", {}).values():
            if p.get("pageimage"):
                hits = commons("titles=" + urllib.parse.quote("File:" + p["pageimage"]))
                return hits[0] if hits else None
        return None

    def words(name: str) -> set:
        return {w for w in re.sub(r"[^a-z0-9 ]", " ", name.lower().replace("'", "")).split() if len(w) >= 4 and w not in PHOTO_GENERIC}

    # ---- Field guide species with no photo
    sp_found = sp_missing = 0
    missing_species = []
    try:
        with open(GUIDE_JSON, encoding="utf-8") as f:
            guide = json.load(f)
    except (OSError, ValueError):
        guide = {}
    species = guide.get("sp") or {}
    need = [sid for sid, sp in species.items() if not sp.get("pu") and (force or sp.get("altdt", "") < (today - dt.timedelta(days=30)).isoformat())]
    try:
        from PIL import Image
    except ImportError:
        Image = None
    os.makedirs(GUIDE_PHOTOS, exist_ok=True)
    try:
        for i in range(0, len(need), 30):
            batch = need[i:i + 30]
            alt = {}
            j = get(GUIDE_API + "taxa/" + ",".join(batch), pause=1.1)
            for x in j.get("results", []):
                for tp in x.get("taxon_photos") or []:
                    ph = tp.get("photo") or {}
                    if ph.get("license_code") in PHOTO_LICENCES and ph.get("medium_url"):
                        alt[str(x.get("id"))] = {"u": ph["medium_url"], "at": ph.get("attribution", ""), "id": ph.get("id")}
                        break
            for sid in batch:
                sp = species[sid]
                sp["altdt"] = today.isoformat()
                if sid not in alt and sp.get("w"):
                    hit = wiki_image(sp["w"])
                    if hit:
                        alt[sid] = {"u": hit["thumb"], "at": "(c) %s, %s, via Wikimedia Commons" % (hit["by"], hit["lic"]), "id": "w" + sid}
                if sid not in alt:
                    sp_missing += 1
                    missing_species.append(sp.get("n") or sp.get("s") or sid)
                    continue
                try:
                    raw = get(alt[sid]["u"], binary=True, pause=0.2)
                    fp = os.path.join(GUIDE_PHOTOS, sid + ".jpg")
                    if Image:
                        im = Image.open(io.BytesIO(raw)).convert("RGB")
                        im.thumbnail((360, 360))
                        im.save(fp, "JPEG", quality=68, optimize=True)
                    else:
                        with open(fp, "wb") as f:
                            f.write(raw)
                    sp["alt"] = alt[sid]
                    sp["pu"], sp["at"], sp["pid"], sp["pf"] = alt[sid]["u"], alt[sid]["at"], alt[sid]["id"], alt[sid]["id"]
                    sp_found += 1
                except Exception:
                    sp_missing += 1
                    missing_species.append(sp.get("n") or sp.get("s") or sid)
            log("photos: field guide %d of %d looked up" % (min(i + 30, len(need)), len(need)))
    except Exception as e:
        log("photos: field guide stopped early (%s), the rest come next run" % str(e)[:120])
    if need and guide:
        tmp = GUIDE_JSON + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(guide, f, ensure_ascii=False)
        os.replace(tmp, GUIDE_JSON)

    # ---- Explore places
    saved = {}
    if os.path.exists(PHOTOS_JSON):
        try:
            with open(PHOTOS_JSON, encoding="utf-8") as f:
                saved = json.load(f)
        except ValueError:
            saved = {}
    sites = explore_doc().get("sites", [])
    pl_found, missing_places = 0, []
    try:
        for s in sites:
            if s.get("kind") in ("art", "turtle", "triangle", "tattoo", "lionfish") or s["id"] in saved:
                continue
            want, hit = words(s["name"]), None
            if not want:
                missing_places.append([s["name"], "name too general to match safely"])
                continue
            for title in (s.get("wiki") or [])[:2]:  # an article counts only when it is about this very place
                tw = words(title)
                if tw and (tw <= want or want <= tw):
                    hit = wiki_image(title)
                    if hit:
                        break
            if not hit:
                for c in commons("generator=search&gsrnamespace=6&gsrlimit=6&gsrsearch=" + urllib.parse.quote(s["name"] + " Bermuda")):
                    if "bermuda" in c["text"] and all(w in c["text"].replace("'", "") for w in want):
                        hit = c
                        break
            if hit:
                saved[s["id"]] = {"u": hit["thumb"], "page": hit["page"], "by": hit["by"], "lic": hit["lic"]}
                pl_found += 1
            else:
                missing_places.append([s["name"], "nothing reusable found"])
    except Exception as e:
        log("photos: places stopped early (%s), the rest come next run" % str(e)[:120])
    tmp = PHOTOS_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(saved, f, ensure_ascii=False, indent=1)
    os.replace(tmp, PHOTOS_JSON)
    with open(PHOTOS_REPORT, "w", encoding="utf-8") as f:
        json.dump({"run": today.isoformat(), "species_found": sp_found, "species_missing": missing_species,
                   "places_with_photo": len(saved), "places_found_this_run": pl_found, "places_missing": missing_places},
                  f, ensure_ascii=False, indent=1)
    log("photos: %d species photos found, %d species still without; %d places have a photo (%d new), %d places without" % (
        sp_found, sp_missing, len(saved), pl_found, len(missing_places)))


def fieldguide_collect(force: bool = False) -> None:
    """Save the Field guide so the page never has to ask iNaturalist itself.

    Depends on: the internet (api.inaturalist.org and its photo store). Pillow is used to shrink photos when it
    is installed; without it the small size is downloaded as it is.
    Writes: events/data/fieldguide.json and site/guide/<species number>.jpg.
    Runs once a day at most unless forced (--guide). Any failure keeps the copy already saved."""
    import html as htmllib
    import io
    import time
    import urllib.parse
    import urllib.request
    today = dt.date.today()
    old = {}
    if os.path.exists(GUIDE_JSON):
        try:
            with open(GUIDE_JSON, encoding="utf-8") as f:
                old = json.load(f)
        except ValueError:
            old = {}
    if not force and old.get("updated") == today.isoformat():
        log("field guide: already saved today")
        return
    species = old.get("sp") if isinstance(old.get("sp"), dict) else {}

    def get(url: str, binary: bool = False):
        last = None
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": GUIDE_AGENT})
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = r.read()
                if binary:
                    return data
                time.sleep(1.1)  # iNaturalist asks for about one request a second
                return json.loads(data.decode("utf-8"))
            except Exception as e:  # network trouble of any kind: wait and try again
                last = e
                time.sleep(4 * (attempt + 1))
        raise last

    base = GUIDE_API + "observations/species_counts?place_id=%d&preferred_place_id=%d&locale=en&quality_grade=research" % (
        GUIDE_PLACE, GUIDE_PLACE)
    wanted = (("year", "", 40), ("month", "&month=%d" % today.month, 40), ("endemic", "&endemic=true", 20),
              ("native", "&native=true", 20), ("introduced", "&introduced=true", 20))
    groups, listed, counts = {}, [], {}
    try:
        for grp in GUIDE_GROUPS:
            entry = {}
            for key, extra, n in wanted:
                j = get(base + "&per_page=%d&iconic_taxa=%s%s" % (n, grp, extra))
                rows = []
                for r in j.get("results", []):
                    t = r.get("taxon") or {}
                    if not t.get("id"):
                        continue
                    sid = str(t["id"])
                    sp = species.setdefault(sid, {})
                    sp["n"] = t.get("preferred_common_name") or t.get("name", "")
                    sp["s"] = t.get("name", "")
                    sp["em"] = t.get("preferred_establishment_means") or ""
                    ph = t.get("default_photo") or {}
                    if ph.get("license_code") and ph.get("medium_url"):  # only photos shared under Creative Commons
                        sp["pu"], sp["at"], sp["pid"] = ph["medium_url"], ph.get("attribution", ""), ph.get("id")
                    elif sp.get("alt"):  # no shared default photo: the one photos_collect found stays
                        sp["pu"], sp["at"], sp["pid"] = sp["alt"]["u"], sp["alt"]["at"], sp["alt"]["id"]
                    else:
                        for k in ("pu", "at", "pid"):
                            sp.pop(k, None)
                    w = t.get("wikipedia_url") or ""
                    sp["w"] = urllib.parse.unquote(w.rsplit("/", 1)[-1]).replace("_", " ") if w else ""
                    flags = set(sp.get("o", []))
                    if key in ("endemic", "native", "introduced"):
                        flags.add(key)
                    if sp["em"] in ("endemic", "native", "introduced"):
                        flags.add(sp["em"])
                    sp["o"] = sorted(flags)
                    if key != "month":
                        counts[sid] = max(counts.get(sid, 0), r.get("count", 0))
                    else:
                        counts.setdefault(sid, r.get("count", 0))
                    if sid not in listed:
                        listed.append(sid)
                    rows.append([t["id"], r.get("count", 0)])
                entry[key] = rows
                if key in ("year", "month"):
                    entry[key + "_total"] = j.get("total_results", len(rows))
            groups[grp] = entry
    except Exception as e:
        log("field guide: could not reach iNaturalist (%s), the saved copy stays as it is" % str(e)[:120])
        return
    log("field guide: %d species listed across %d groups" % (len(listed), len(groups)))

    # each species' description and conservation status, thirty at a time, refreshed monthly
    stale = (today - dt.timedelta(days=30)).isoformat()
    need = [sid for sid in listed if "sum" not in species[sid] or species[sid].get("dt", "") < stale]
    try:
        for i in range(0, len(need), 30):
            batch = need[i:i + 30]
            j = get(GUIDE_API + "taxa/" + ",".join(batch) + "?locale=en&preferred_place_id=%d" % GUIDE_PLACE)
            for x in j.get("results", []):
                sp = species.get(str(x.get("id")))
                if sp is None:
                    continue
                txt = re.sub(r"<[^>]+>", "", x.get("wikipedia_summary") or "")
                sp["sum"] = re.sub(r"\s+", " ", htmllib.unescape(txt)).strip()
                cs = x.get("conservation_status") or {}
                sp["cs"] = cs.get("status_name") or GUIDE_STATUS.get((cs.get("status") or "").upper(), "")
            for sid in batch:
                species[sid].setdefault("sum", "")
                species[sid]["dt"] = today.isoformat()
    except Exception as e:
        log("field guide: descriptions stopped early (%s), the rest come next run" % str(e)[:120])

    # the latest sightings, asked again only when a species' count has moved
    need = [sid for sid in listed if "last" not in species[sid] or species[sid].get("lc") != counts.get(sid)]
    done = 0
    try:
        for sid in need[:450]:
            j = get(GUIDE_API + "observations?place_id=%d&taxon_id=%s&quality_grade=research&order=desc&order_by=observed_on&per_page=5"
                    % (GUIDE_PLACE, sid))
            species[sid]["last"] = [[o["observed_on"], o.get("place_guess") or ""] for o in j.get("results", []) if o.get("observed_on")]
            species[sid]["lc"] = counts.get(sid)
            done += 1
            if done % 50 == 0:
                log("field guide: latest sightings %d of %d" % (done, len(need)))
    except Exception as e:
        log("field guide: latest sightings stopped early (%s), the rest come next run" % str(e)[:120])

    # one small photo per species, fetched once and again only if iNaturalist picks a different photo
    os.makedirs(GUIDE_PHOTOS, exist_ok=True)
    try:
        from PIL import Image
    except ImportError:
        Image = None
    got = failed = 0
    for sid in listed:
        sp = species[sid]
        fp = os.path.join(GUIDE_PHOTOS, sid + ".jpg")
        if not sp.get("pu") or (os.path.exists(fp) and sp.get("pf") == sp.get("pid")):
            continue
        try:
            if Image:
                im = Image.open(io.BytesIO(get(sp["pu"], binary=True))).convert("RGB")
                im.thumbnail((360, 360))
                im.save(fp, "JPEG", quality=68, optimize=True)
            else:
                with open(fp, "wb") as f:
                    f.write(get(sp["pu"].replace("/medium.", "/small."), binary=True))
            sp["pf"] = sp.get("pid")
            got += 1
        except Exception:
            failed += 1
        time.sleep(0.15)
    doc = {"updated": today.isoformat(), "month": today.month, "groups": groups, "sp": {sid: species[sid] for sid in listed}}
    tmp = GUIDE_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False)
    os.replace(tmp, GUIDE_JSON)
    log("field guide: saved %d species, %d new photos%s" % (len(listed), got, ", %d photos failed" % failed if failed else ""))


def guide_doc() -> dict:
    """The saved Field guide for the page, minus the bookkeeping. Depends on: events/data/fieldguide.json, site/guide."""
    if not os.path.exists(GUIDE_JSON):
        return {}
    try:
        with open(GUIDE_JSON, encoding="utf-8") as f:
            doc = json.load(f)
    except ValueError:
        return {}
    for sid, sp in (doc.get("sp") or {}).items():
        if sp.get("pu") and os.path.exists(os.path.join(GUIDE_PHOTOS, sid + ".jpg")):
            sp["ph"] = 1
        else:
            sp.pop("at", None)
        for k in ("pu", "pid", "pf", "lc", "dt", "alt", "altdt"):
            sp.pop(k, None)
    return doc


def weather_doc() -> dict:
    fp = os.path.join(EVENTS, "data", "weather.json")
    if not os.path.exists(fp):
        return {}
    try:
        with open(fp, encoding="utf-8") as f:
            w = json.load(f)
    except ValueError:
        return {}
    w.pop("raw_pages", None)
    if "now" in w and isinstance(w["now"], dict):
        w["now"].pop("rows", None)
    return w


STORES = {"mp": "MarketPlace", "ld": "Lindo's", "sm": "Supermart", "ml": "Miles", "pr": "Pronto", "prc": "Price Rite", "ar": "Arnold's"}


def best_buys(deals_html: str, n: int = 16) -> dict:
    """This week's best buys from the deals page's own data block, for the List tab."""
    out = {"asof": "", "items": []}
    if not os.path.exists(deals_html):
        return out
    with open(deals_html, encoding="utf-8") as f:
        h = f.read()
    m = re.search(r'<script id="data" type="application/json">(.*?)</script>', h, re.S)
    if not m:
        return out
    try:
        d = json.loads(m.group(1).replace("<\\/", "</"))
    except ValueError:
        return out
    out["asof"] = d.get("asof") or ""
    seen = set()
    for b in d.get("best") or []:
        name = (b.get("n") or "").strip()
        key = name.lower()
        if not name or key in seen:
            continue
        seen.add(key)
        out["items"].append({"store": STORES.get(b.get("s"), b.get("s") or ""), "code": b.get("s") or "", "price": b.get("p") or "",
                             "unit": b.get("u") or "", "name": name, "why": (b.get("w") or "")[:220]})
        if len(out["items"]) >= n:
            break
    return out


FRONT = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bermuda Hub</title>
<meta name="description" content="The Bermuda everything app: what is on, grocery deals, weather, ocean, wind sports and places to explore."><meta name="theme-color" content="#170f3a"><meta name="apple-mobile-web-app-title" content="Bermuda Hub"><meta name="apple-mobile-web-app-capable" content="yes"><link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="icon-192.png"><link rel="apple-touch-icon" href="apple-touch-icon.png"><meta property="og:title" content="Bermuda Hub"><meta property="og:description" content="The Bermuda everything app: what is on, grocery deals, weather, ocean, wind sports and places to explore."><meta property="og:image" content="https://mkatzsch.github.io/bermuda-hub/icon-512.png"><meta property="og:url" content="https://mkatzsch.github.io/bermuda-hub/">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Yellowtail&display=swap">
<style>
:root{color-scheme:dark;--bg:#170f3a;--ink:#fdf3ff;--line:#4b2d8a;--accent:#2af0d9;--accent-ink:#170f3a}
html,body{margin:0;background:var(--bg);color:var(--ink);font:15px Outfit,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
#app{display:flex;flex-direction:column;height:100vh;height:100dvh;overflow:hidden}
header{flex:none;display:flex;align-items:center;gap:14px;padding:10px 16px;border-bottom:1px solid var(--line)}
h1{font-size:17px;margin:0;font-weight:800;letter-spacing:.01em}
.seg{display:inline-flex;border:1.5px solid var(--line);border-radius:999px;padding:3px;gap:3px;margin-left:auto;max-width:100%;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.seg::-webkit-scrollbar{display:none}
.seg button{border:0;background:transparent;color:var(--ink);font:700 14px inherit;padding:7px 14px;border-radius:999px;cursor:pointer;white-space:nowrap;flex:none}
@media (max-width:640px){header{flex-wrap:wrap;gap:8px 14px}.seg{margin-left:0;width:100%;justify-content:flex-start}}
.seg button[aria-pressed=true]{background:var(--accent);color:var(--accent-ink)}
small{opacity:.65}
#hshare{border:1.5px solid var(--line);background:transparent;color:var(--ink);border-radius:999px;padding:5px 14px;font:700 13px inherit;cursor:pointer}
#hshare:hover,#hfind:hover{border-color:var(--accent)}
#hfind{border:1.5px solid var(--line);background:transparent;color:var(--ink);border-radius:999px;padding:5px 14px;font:700 13px inherit;cursor:pointer}
#hs{position:fixed;inset:0;z-index:60;background:#170f3a;color:#fdf3ff;display:flex;flex-direction:column}
#hs .hsbar{flex:none;display:flex;gap:8px;padding:12px 14px;border-bottom:1px solid #4b2d8a}
#hs input{flex:1;min-width:0;font:600 17px inherit;padding:11px 14px;border-radius:14px;border:1.5px solid #4b2d8a;background:#241456;color:#fff}
#hs #hsx{border:1.5px solid #4b2d8a;background:transparent;color:#fff;border-radius:14px;padding:0 14px;font:700 14px inherit;cursor:pointer}
#hs #hsr{flex:1;overflow-y:auto;padding:6px 14px 40px;max-width:760px;width:100%;margin:0 auto;box-sizing:border-box}
#hs h3{font:800 13px/1.2 Outfit,"Segoe UI",sans-serif;text-transform:uppercase;letter-spacing:.08em;color:#2af0d9;margin:18px 0 6px}
#hs h3 span{color:#cdbbea;font-weight:600}
#hs #hsr button{display:flex;flex-direction:column;gap:2px;width:100%;text-align:left;background:#241456;border:1px solid #3a2378;color:#fff;border-radius:14px;padding:10px 12px;margin:0 0 6px;font:inherit;cursor:pointer}
#hs #hsr button b{font-size:15px}
#hs #hsr button span{font-size:13px;color:#cdbbea}
#hs .hsnote,#hs .hsmore{color:#cdbbea;font-size:14px;margin:14px 2px}
#hs .hsmore{margin:2px 2px 8px;font-size:13px}
.ttip{background:#4d1c63;border:1px solid #ff4fa3;border-radius:18px;padding:12px 44px 12px 16px;position:relative;font-size:14px;line-height:1.45}
.ttip b{display:block;font:700 15px/1.2 Outfit,"Segoe UI",sans-serif;margin-bottom:2px}
.ttip button{position:absolute;top:6px;right:8px;border:0;background:transparent;color:#fdf3ff;font-size:22px;cursor:pointer;padding:4px 8px}
iframe{display:block;width:100%;flex:1 1 auto;min-height:0;border:0}
[hidden]{display:none!important}
#list{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;background:linear-gradient(#170f3a,#2a1058 55%,#3d1260)}
#list h2{font:800 20px/1.2 Outfit,"Segoe UI",sans-serif}
#ladd input,#ladd select{background:#241552!important}
#ladd input::placeholder{color:#cdbbea}
#litems:not(:empty),#lbest:not(:empty){background:#241552;border:1px solid #4b2d8a;border-radius:18px;padding:4px 14px}
#list .litem:last-child,#list .bcard:last-child{border-bottom:0}
.litem input{accent-color:#ff4fa3}
.lgroup h3{color:#2af0d9;opacity:1!important}
.lwrap{max-width:720px;margin:0 auto;padding:14px 16px 60px;display:flex;flex-direction:column;gap:12px}
.lnote{color:var(--ink);opacity:.7;font-size:13px;margin:0}
#ladd{display:flex;gap:6px;flex-wrap:wrap}
#ladd input{flex:1 1 180px;font:inherit;padding:10px 12px;border:1.5px solid var(--line);border-radius:10px;background:transparent;color:var(--ink)}
#ladd select{font:inherit;padding:10px;border:1.5px solid var(--line);border-radius:10px;background:transparent;color:var(--ink)}
#ladd button,.lbtns button{font:700 14px inherit;padding:10px 16px;border:0;border-radius:999px;background:var(--accent);color:var(--accent-ink);cursor:pointer}
.lbtns{display:flex;gap:8px}
.lbtns .ghost{background:transparent;color:var(--ink);border:1.5px solid var(--line)}
.lgroup{margin-top:6px}
.lgroup h3{font-size:12px;letter-spacing:.08em;text-transform:uppercase;opacity:.65;margin:10px 0 4px}
.litem{display:flex;align-items:center;gap:10px;padding:10px 4px;border-bottom:1px solid var(--line)}
.litem input{width:22px;height:22px;flex:none}
.litem .n{flex:1;font-size:16px}
.litem.done .n{text-decoration:line-through;opacity:.5}
.litem .p{font-size:13px;opacity:.7;white-space:nowrap}
.litem .x{border:0;background:transparent;color:var(--ink);opacity:.5;font-size:18px;cursor:pointer;padding:4px 8px}
h2{font-size:18px;margin:18px 0 0}
.bcard{display:flex;gap:10px;align-items:flex-start;padding:10px 0;border-bottom:1px solid var(--line)}
.bcard .b{flex:1}
.bcard .b .t{font-weight:700}
.bcard .b .s{font-size:13px;opacity:.75}
.bcard .b .w{font-size:13px;opacity:.65;margin-top:3px}
.bcard button{flex:none;font:700 20px inherit;width:40px;height:40px;border-radius:50%;border:1.5px solid var(--accent);background:transparent;color:var(--accent);cursor:pointer}
.bcard button[disabled]{opacity:.4}
#weather,#explore,#sports,#ocean,#transit{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;--w-bg:#170f3a;--w-ink:#fdf3ff;--w-soft:#cdbbea;--w-card:#241552;--w-line:#4b2d8a;--w-sea:#2af0d9;--w-deep:#2af0d9;--w-pink:#ff4fa3;--w-sand:#4d1c63;--w-night-ink:#fdf3ff;--w-water:#16356b;background:linear-gradient(#170f3a,#2a1058 55%,#3d1260);color:var(--w-ink)}
.wwrap{max-width:760px;margin:0 auto;padding:14px 16px 60px;display:flex;flex-direction:column;gap:16px}
.wwarn{background:#ffd166;color:#1b1b1f;border-radius:14px;padding:10px 14px;font-weight:700}
.wwarn small{display:block;font-weight:400;opacity:.8}
.whero{position:relative;border-radius:22px;overflow:hidden;min-height:300px;box-sizing:border-box;color:#fff;padding:18px 20px 150px;background:linear-gradient(#3a1a7a 0%,#b02a9a 38%,#ff5f8f 64%,#ffb25e 100%);box-shadow:0 0 0 1.5px #ff4fa3,0 10px 40px rgba(255,79,163,.28)}
.whero.cloud{background:linear-gradient(#34205f,#7a4a8f 55%,#e08aa6)}
.whero.rain{background:linear-gradient(#1d1640,#4a2f73 58%,#9a5f9c)}
.whero.night{background:linear-gradient(#0a0624,#2a1160 68%,#6a2385)}
.wscene{position:absolute;inset:0;width:100%;height:100%;display:block}
.wnow{position:relative;display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;text-shadow:0 0 18px rgba(255,79,163,.75),0 1px 3px rgba(20,5,45,.6)}
.wnow .big{font:800 68px/0.9 Outfit,"Segoe UI",sans-serif;letter-spacing:-.03em}
.wnow .sky{font:700 24px/1.1 Outfit,"Segoe UI",sans-serif}
.wnow .meta{font-size:14px;width:100%;margin-top:6px;font-weight:600}
.whead{font:400 36px/1.15 Yellowtail,"Segoe Script",cursive;margin-top:4px;color:#fff;text-shadow:0 0 10px rgba(255,79,163,.45)}
.wsyn{color:var(--w-soft);font-size:15px;line-height:1.5;margin:0;max-width:68ch}
.wcards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
.wcard{background:var(--w-card);border:1px solid var(--w-line);border-radius:18px;padding:14px 16px}
.wcard h3{margin:0 0 4px;font:700 19px/1.2 Outfit,"Segoe UI",sans-serif}
.wcard .hl{font-weight:700;margin-bottom:6px;color:var(--w-deep)}
.wcard p{margin:0;font-size:14px;line-height:1.45}
.wcard.day{background:linear-gradient(135deg,#ffb25e,#ff5f8f);border-color:transparent;color:#2a0b3d}
.wcard.day .hl{color:#2a0b3d}
.wcard.eve{background:linear-gradient(135deg,#2b1570,#0f6f8f);border-color:transparent;color:var(--w-night-ink)}
.wcard.eve .hl{color:#8ff7ea}
.wcard.sea{background:linear-gradient(160deg,#16356b,#0e5f7a);border-color:transparent}
.wstrip{display:flex;gap:8px;overflow-x:auto;padding:4px 0 8px;-webkit-overflow-scrolling:touch}
.whr{flex:none;width:60px;text-align:center;background:var(--w-card);border:1px solid var(--w-line);border-radius:16px;padding:8px 2px;font-size:12px}
.whr .t{font:700 18px/1.3 Outfit,"Segoe UI",sans-serif}
.whr .r{color:var(--w-sea);font-weight:700}
.whr .w{color:var(--w-soft)}
.whr.now{background:var(--w-sand);border-color:var(--w-pink)}
.wweek{display:flex;flex-direction:column;background:var(--w-card);border:1px solid var(--w-line);border-radius:18px;padding:4px 16px}
.wday{display:grid;grid-template-columns:96px 1fr 70px;gap:10px;align-items:baseline;padding:11px 0;border-bottom:1px solid var(--w-line);font-size:14px}
.wday:last-child{border-bottom:0}
.wday .d{font:700 16px/1.2 Outfit,"Segoe UI",sans-serif}
.wday .hl{text-align:right;white-space:nowrap;font-weight:700;color:var(--w-deep)}
.wday .tx{color:var(--w-soft)}
.wnext{margin:-6px 0 0;font-size:16px;font-weight:600;color:#8ff7ea}
.wacts{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}
.wact{background:var(--w-card);border:1.5px solid var(--w-line);border-radius:16px;padding:10px 8px;text-align:center;display:flex;flex-direction:column;gap:2px}
.wact b{font-size:14px}
.wact .v{font:800 17px/1.2 Outfit,"Segoe UI",sans-serif}
.wact .y{font-size:11px;color:var(--w-soft);line-height:1.25}
.wact.go{border-color:#2af0d9}.wact.go .v{color:#2af0d9}
.wact.maybe{border-color:#fff27a}.wact.maybe .v{color:#fff27a}
.wact.skip{border-color:#ff4fa3}.wact.skip .v{color:#ff7ab8}
.wdials{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.wdial{background:var(--w-card);border:1px solid var(--w-line);border-radius:18px;padding:12px 10px;text-align:center}
.wdial h3{margin:0 0 4px;font:700 14px/1.2 Outfit,"Segoe UI",sans-serif;color:var(--w-soft)}
.wdial svg{display:block;width:100%;max-width:130px;height:auto;margin:0 auto;font-family:Outfit,"Segoe UI",sans-serif}
.wdial p{margin:6px 0 0;font-size:12.5px;line-height:1.3}
.wseac{grid-column:1/-1}
.wsea{display:grid;grid-template-columns:120px 1fr 78px;gap:10px;align-items:center;font-size:14px;margin:6px 0}
.wsea .trk{height:12px;border-radius:999px;background:rgba(255,255,255,.14);overflow:hidden}
.wsea .trk i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,#2af0d9,#ff4fa3)}
.wsea b{text-align:right}
.wtank .big{font:800 40px/1 Outfit,"Segoe UI",sans-serif;color:#2af0d9;margin-bottom:6px}
.wtank p{margin:0 0 10px}
.wtank .trk{height:12px;border-radius:999px;background:rgba(255,255,255,.14);overflow:hidden;margin:0 0 14px}
.wtank .trk i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,#2af0d9,#ff4fa3)}
.wroof{display:block;font-weight:700;margin:0 0 8px}
.wroof input{width:92px;font:inherit;font-weight:800;padding:6px 8px;margin:0 4px;border-radius:10px;border:1.5px solid #2af0d9;background:transparent;color:inherit;text-align:right}
.wtrop{display:block;border-radius:18px;overflow:hidden;border:1.5px solid var(--w-line);background:#fff}
.wtrop img{display:block;width:100%;height:auto}
@media (max-width:620px){.wacts{grid-template-columns:repeat(3,1fr)}.wdials{grid-template-columns:repeat(2,1fr)}.wsea{grid-template-columns:104px 1fr 70px}}
.wtg{background:var(--w-card);border:1.5px solid #2af0d9;border-radius:18px;padding:10px 12px;box-shadow:0 8px 34px rgba(42,240,217,.14)}
.wtgs{overflow-x:auto;-webkit-overflow-scrolling:touch}
.wtgs svg{display:block;width:100%;min-width:640px;height:auto;font-family:Outfit,"Segoe UI",sans-serif}
.wtides{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.wtide{background:var(--w-water);border-radius:16px;padding:10px 12px;font-size:13px;line-height:1.6}
.wtide b{display:block;margin-bottom:2px;font:700 16px/1.2 Outfit,"Segoe UI",sans-serif}
.wtide .hi{font-weight:700}
.wlinks a{display:inline-block;margin:0 12px 6px 0;color:var(--w-deep);font-weight:700;text-decoration:none}
h2.w{font:700 21px/1.2 Outfit,"Segoe UI",sans-serif;margin:12px 0 0;color:#fff}
.wsrc{font-size:12px;color:var(--w-soft);margin:0}
.wmap{background:var(--w-card);border:1.5px solid #2af0d9;box-shadow:0 8px 34px rgba(42,240,217,.18);border-radius:22px;padding:12px;display:flex;flex-direction:column;gap:10px}
.wmtog{display:inline-flex;align-self:flex-start;background:var(--w-water);border-radius:999px;padding:4px;gap:4px}
.wmtog button,.wrseg button{font-family:inherit;font-weight:700;font-size:14px;padding:7px 18px;border-radius:999px;border:0;background:none;color:var(--w-ink);cursor:pointer}
.wmtog button[aria-pressed="true"],.wrseg button[aria-pressed="true"]{background:var(--w-deep);color:var(--w-bg)}
.wrseg{display:flex;flex-wrap:wrap;gap:4px}
.wrseg button{font-size:13px;padding:5px 12px;background:var(--w-water)}
.wradar{position:relative;border-radius:16px;overflow:hidden;background:#0b1820;min-height:120px}
.wradar img{display:block;width:100%;height:auto}
.wrview{position:absolute;left:10px;top:10px;background:rgba(8,30,45,.78);color:#fff;font-weight:700;font-size:13px;padding:5px 12px;border-radius:999px}
.wrzoom{position:absolute;right:10px;top:10px;display:flex;flex-direction:column;border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.35)}
.wrzoom button{width:42px;height:42px;border:0;background:#fff;color:#12344a;font-family:inherit;font-weight:700;font-size:26px;line-height:1;cursor:pointer}
.wrzoom button+button{border-top:1px solid #d5dde2}
.wrzoom button[disabled]{color:#a9b7c0;cursor:default}
.wrbar{display:flex;align-items:center;gap:10px;font-size:13px}
.wrbar button{font-family:inherit;font-weight:700;font-size:13px;padding:5px 14px;border-radius:999px;border:1px solid var(--w-line);background:none;color:inherit;cursor:pointer}
.wrbar .t{font-weight:700}
.wrbar .n{color:var(--w-soft)}
.wwf{display:block;width:100%;height:460px;border:0;border-radius:16px}
#weather button:focus-visible,#weather a:focus-visible{outline:3px solid var(--w-pink);outline-offset:2px}
@media (max-width:520px){.wnow .big{font-size:56px}.whead{font-size:29px}.wwf{height:380px}}
#today{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;background:linear-gradient(#170f3a,#2a1058 55%,#3d1260);color:#fdf3ff}
.twrap{max-width:860px;margin:0 auto;padding:14px 16px 60px;display:flex;flex-direction:column;gap:14px}
.tgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.tcard{background:#241552;border:1px solid #4b2d8a;border-radius:20px;padding:16px 18px;display:flex;flex-direction:column;gap:8px}
.tcard h3{margin:0;font:700 14px/1.2 Outfit,"Segoe UI",sans-serif;color:#2af0d9}
.tcard p{margin:0;font-size:15px;line-height:1.45}
.tcard .tmuted{color:#cdbbea;font-size:13px}
.tcard .tbig{font:800 44px/1 Outfit,"Segoe UI",sans-serif}
.tcard .tbig span{font:600 16px/1.2 Outfit,"Segoe UI",sans-serif;color:#cdbbea}
.tcard button{align-self:flex-start;margin-top:4px;border:0;border-radius:999px;padding:8px 16px;font-family:inherit;font-weight:700;font-size:13px;cursor:pointer;background:#2af0d9;color:#170f3a}
.tcard button+button{background:transparent;border:1.5px solid #4b2d8a;color:#fdf3ff}
.tlist{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}
.tlist li{display:flex;flex-direction:column;font-size:15px}
.tlist li span{font-size:13px;color:#cdbbea}
.tacts{display:flex;flex-wrap:wrap;gap:6px}
.tacts span{font-size:12px;font-weight:700;padding:4px 10px;border-radius:999px;border:1.5px solid #4b2d8a}
.tacts .go{border-color:#2af0d9;color:#2af0d9}.tacts .maybe{border-color:#fff27a;color:#fff27a}.tacts .skip{border-color:#ff4fa3;color:#ff7ab8}
.wboat{padding:8px 0;border-top:1px solid rgba(255,255,255,.14)}
.wboat:first-of-type{border-top:0}
.wboat .hd{display:flex;align-items:baseline;gap:10px}
.wboat .v{font:800 15px/1 Outfit,"Segoe UI",sans-serif}
.wboat.go .v{color:#2af0d9}.wboat.maybe .v{color:#fff27a}.wboat.skip .v{color:#ff7ab8}
.wboat p{margin:3px 0 0;font-size:14px}
.wboat .lee{font-weight:800;color:#2af0d9}
.xbadges{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px;-webkit-overflow-scrolling:touch}
.xbadge{position:relative;flex:none;min-width:118px;border:1.5px solid var(--w-line);border-radius:14px;padding:8px 12px 12px;background:var(--w-card);overflow:hidden;display:flex;flex-direction:column;gap:2px;opacity:.75}
.xbadge b{font-size:13px}.xbadge span{font-size:12px;color:var(--w-soft)}
.xbadge i{position:absolute;left:0;bottom:0;height:4px;background:linear-gradient(90deg,#2af0d9,#ff4fa3)}
.xbadge.on{opacity:1;border-color:#fff27a;box-shadow:0 0 14px rgba(255,242,122,.35)}.xbadge.on span{color:#fff27a;font-weight:800}
.xwrap{max-width:860px;margin:0 auto;padding:14px 16px 60px;display:flex;flex-direction:column;gap:14px}
.xtitle{font:800 28px/1.15 Outfit,"Segoe UI",sans-serif;margin:2px 0 0;color:#fff}
.xlead{margin:-6px 0 0;color:var(--w-soft);font-size:15px}
.xchips{display:flex;gap:8px;flex-wrap:wrap}
.xchips button{display:inline-flex;align-items:center;gap:7px;border:1.5px solid var(--w-line);background:var(--w-card);color:var(--w-ink);border-radius:999px;padding:8px 14px;font-family:inherit;font-weight:700;font-size:13px;cursor:pointer}
.xchips button i{width:11px;height:11px;border-radius:50%;display:inline-block}
.xchips button[aria-pressed=true]{background:#fff;color:#170f3a;border-color:#fff}
.xpane{display:flex;flex-direction:column;gap:14px}
#xmode{align-self:flex-start}
.gturtle .acts{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.gturtle .acts a,.gturtle .acts button{border:0;font-family:inherit;cursor:pointer;border-radius:999px;padding:8px 14px;font-weight:700;font-size:13px;background:#2af0d9;color:#170f3a;text-decoration:none}
.gcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px}
.gcard{border:1px solid var(--w-line);border-radius:18px;padding:0 0 12px;overflow:hidden;text-align:left;background:var(--w-card);color:var(--w-ink);cursor:pointer;font:inherit;display:flex;flex-direction:column;gap:4px}
.gcard:hover{border-color:#2af0d9}
.gcard img,.gcard .noimg{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;background:#16356b}
.gcard .noimg{display:flex;align-items:center;justify-content:center;font-size:12px;color:var(--w-soft)}
.gcard span{padding:0 12px}
.gcard .n{font:800 15px/1.2 Outfit,"Segoe UI",sans-serif;margin-top:6px}
.gcard .sci{font-size:12px;font-style:italic;color:var(--w-soft)}
.gcard .em{align-self:flex-start;margin-left:12px;padding:2px 9px;border-radius:999px;font-size:11px;font-weight:800;background:#2af0d9;color:#170f3a}
.gcard .em.endemic{background:#ff4fa3;color:#fff}
.gcard .em.introduced{background:transparent;border:1px solid var(--w-line);color:var(--w-soft)}
.gcard .c{font-size:12px;color:var(--w-soft)}
.xprog{display:flex;align-items:center;gap:10px;flex-wrap:wrap;font-size:13px;font-weight:600;color:var(--w-soft)}
.xprog .bar{flex:0 0 120px;height:10px;border-radius:999px;background:rgba(255,255,255,.14);overflow:hidden}
.xprog .bar i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,#2af0d9,#ff4fa3)}
.xprog button{border:0;border-radius:999px;padding:8px 14px;font-family:inherit;font-weight:700;font-size:13px;cursor:pointer;background:#ff4fa3;color:#fff}
.xsheet .acts #xseen{background:#ff4fa3;color:#fff;border:0}
.xsheet .acts #xseen.on{background:#fff;color:#170f3a}
.xphoto img{display:block;width:100%;max-height:420px;object-fit:cover;border-radius:16px;border:1.5px solid #ff4fa3}
.xname{font-weight:700;font-size:14px}
.xname input{font:inherit;padding:8px 10px;margin-left:6px;border-radius:10px;border:1.5px solid #2af0d9;background:transparent;color:inherit;width:60%}
.xmapbox{position:relative;border-radius:22px;overflow:hidden;border:1.5px solid #2af0d9;box-shadow:0 8px 34px rgba(42,240,217,.18);background:#0b1820}
#xmap{height:min(62vh,520px);min-height:340px;width:100%}
.xmaphint{position:absolute;left:12px;bottom:12px;z-index:500;background:rgba(8,30,45,.82);color:#fff;font-size:12px;font-weight:700;padding:6px 12px;border-radius:999px;pointer-events:none}
.leaflet-container{font-family:inherit;background:#0b1820}
#xmap.xdark .leaflet-tile-pane{filter:invert(1) hue-rotate(180deg) brightness(.9) contrast(.9) saturate(.7)}
.xbase{position:absolute;right:12px;top:12px;z-index:500;display:inline-flex;background:rgba(8,30,45,.85);border-radius:999px;padding:4px;gap:4px}
.xbase button{border:0;background:none;color:#fff;font-family:inherit;font-weight:700;font-size:13px;padding:6px 13px;border-radius:999px;cursor:pointer}
.xbase button[aria-pressed=true]{background:#2af0d9;color:#170f3a}
.xtip{background:#170f3a;color:#fff;border:1.5px solid #ff4fa3;border-radius:10px;font-weight:700;font-size:12px;padding:4px 9px;box-shadow:none}
.xtip:before{display:none}
#xfind,#bq,#bto{font:inherit;padding:11px 14px;border:1.5px solid var(--w-line);border-radius:14px;background:var(--w-card);color:var(--w-ink);width:100%;box-sizing:border-box}
#xfind::placeholder{color:var(--w-soft)}
.xcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}
.xcard{border:1px solid var(--w-line);border-radius:18px;padding:13px 14px;text-align:left;background:var(--w-card);color:var(--w-ink);cursor:pointer;font:inherit;display:flex;flex-direction:column;gap:5px}
.xcard:hover{border-color:#2af0d9}
.xcard .k{display:flex;align-items:center;gap:7px;font-size:12px;font-weight:700;color:var(--w-soft)}
.xcard .k i{width:10px;height:10px;border-radius:50%;flex:none}
.xcard .n{font:800 17px/1.2 Outfit,"Segoe UI",sans-serif}
.xcard .a{font-size:13px;color:var(--w-soft);line-height:1.4}
.xcard .go{font-size:12px;font-weight:700}
.xcard.ok .go{color:#2af0d9}.xcard.look .go{color:#fff27a}.xcard.no .go{color:#ff7ab8}
#xdlg{border:0;border-radius:22px;padding:0;max-width:min(600px,calc(100vw - 24px));width:100%;max-height:calc(100dvh - 40px);background:#1d1248;color:#fdf3ff;box-shadow:0 0 0 1.5px #ff4fa3,0 20px 60px rgba(0,0,0,.6)}
#xdlg::backdrop{background:rgba(10,5,35,.7)}
#xdlg{--w-bg:#170f3a;--w-ink:#fdf3ff;--w-soft:#cdbbea;--w-card:#241552;--w-line:#4b2d8a}
.xweb{margin:0}
.xweb img{display:block;width:100%;max-height:300px;object-fit:cover;border-radius:14px;background:#0b1820}
.xweb figcaption{font-size:11.5px;color:#cdbbea;margin-top:4px}
.xweb figcaption a{color:#cdbbea}
.smap{height:min(44vh,360px);min-height:260px;width:100%}
.smap.xdark .leaflet-tile-pane{filter:invert(1) hue-rotate(180deg) brightness(.9) contrast(.9) saturate(.7)}
.skeyrow{display:flex;flex-wrap:wrap;gap:12px;font-size:12.5px;color:var(--w-soft);margin-top:8px}
.skeyrow i{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:5px;border:1.5px solid #170f3a;vertical-align:-1px}
.xsheet{display:flex;flex-direction:column}
.xsheet .top{padding:20px 22px 16px;background:linear-gradient(135deg,#3a1a7a,#b02a9a 70%,#ff5f8f)}
.xsheet .top .k{font-size:12px;font-weight:700;opacity:.9}
.xsheet h2{font:800 26px/1.15 Outfit,"Segoe UI",sans-serif;margin:4px 0 4px}
.xsheet .top .era{font-size:14px;font-weight:600}
.xsheet .body{padding:16px 22px 20px;display:flex;flex-direction:column;gap:14px}
.xsheet p{margin:0;font-size:15px;line-height:1.5}
.xsheet h3{margin:0 0 3px;font:700 13px/1.2 Outfit,"Segoe UI",sans-serif;color:#2af0d9}
.xsheet ul{margin:0;padding-left:18px;font-size:15px;line-height:1.5}
.xsheet .facts{display:grid;gap:12px}
.xsheet #xdive{background:linear-gradient(135deg,#ffb25e,#ff4fa3);color:#2a0b3d;border:0}
.xdeep{border-top:1.5px solid #4b2d8a;padding-top:14px;display:flex;flex-direction:column;gap:18px}
.xdeep section{display:flex;flex-direction:column;gap:10px}
.xdeep h3{font:800 21px/1.2 Outfit,"Segoe UI",sans-serif;color:#fff;margin:0}
.xdeep h4{font:700 17px/1.25 Outfit,"Segoe UI",sans-serif;color:#2af0d9;margin:8px 0 0}
.xdeep h5{font:700 15px/1.25 Outfit,"Segoe UI",sans-serif;color:#ffb25e;margin:4px 0 0}
.xdeep p{font-size:15px;line-height:1.6}
.xsheet .acts{display:flex;gap:10px;flex-wrap:wrap}
.xfindrow{display:flex;gap:8px;align-items:stretch}
#xroutes h3{margin:0 0 8px;font:700 17px/1.2 Outfit,"Segoe UI",sans-serif;color:#fff}
.xrrow{display:flex;gap:10px;overflow-x:auto;padding-bottom:6px;scrollbar-width:none}
.xrrow::-webkit-scrollbar{display:none}
.xroute{flex:0 0 220px;text-align:left;border:1px solid var(--w-line);border-radius:18px;padding:12px 14px;background:linear-gradient(135deg,#2b1570,#0f6f8f);color:#fdf3ff;cursor:pointer;font:inherit;display:flex;flex-direction:column;gap:4px}
.xroute b{font:800 16px/1.2 Outfit,"Segoe UI",sans-serif}
.xroute span{font-size:12px;color:#d9f7f3}
.xroute .p{font-weight:700;color:#fff}
.xstops{list-style:none;margin:0;padding:0;counter-reset:st}
.xstops li{counter-increment:st;display:flex;gap:12px;align-items:flex-start;padding:10px 0;border-bottom:1px solid #4b2d8a;cursor:pointer}
.xstops li:last-child{border-bottom:0}
.xstops li::before{content:counter(st);flex:none;width:28px;height:28px;border-radius:50%;background:#2af0d9;color:#170f3a;font-weight:800;display:grid;place-items:center;font-size:14px}
.xstops li.done::before{content:"✓";background:#ff4fa3;color:#fff}
.xstops li b{display:block;font-size:15px}
.xstops li span{display:block;font-size:12px;color:#cdbbea}
.broute{background:var(--w-card);border:1px solid var(--w-line);border-radius:18px;padding:14px 16px}
.broute h3{margin:0 0 2px;font:700 18px/1.25 Outfit,"Segoe UI",sans-serif;display:flex;gap:10px;align-items:center}
.bnum{flex:0 0 auto;min-width:34px;height:34px;border-radius:10px;display:inline-flex;align-items:center;justify-content:center;font-weight:800;font-size:17px;color:#0b1b3a;padding:0 6px}
.bdir{padding:10px 0 4px;border-top:1px solid var(--w-line);margin-top:10px}
.bdir p{margin:0;font-size:14px}
.bdir p.bfrom{color:var(--w-soft);font-size:12.5px}
.bnext{font-size:15px;margin-top:4px !important}
.bnext b{color:#2af0d9}
.btimes{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 4px}
.btimes span{font-size:13px;font-variant-numeric:tabular-nums;border:1px solid var(--w-line);border-radius:8px;padding:3px 7px}
.btimes span.gone{opacity:.4}
#transit details summary{cursor:pointer;font-weight:700;color:#2af0d9;padding:8px 0;min-height:40px}
.bstop{padding:10px 0 6px;border-top:1px solid var(--w-line);margin-top:10px}
.bstop p{margin:0 0 4px;font-size:15px}
.bstop p span{color:var(--w-soft);font-size:12.5px;font-weight:400}
.bcall{display:flex;align-items:center;gap:8px;padding:3px 0;font-size:14px}
.bcall i{font-style:normal;font-variant-numeric:tabular-nums;font-weight:700;min-width:62px}
.bnum.sm{min-width:26px;height:22px;border-radius:6px;font-size:12px}
#bq,#bto{flex:1 1 auto;min-width:0}
.jplan{display:flex;flex-direction:column;gap:8px}
.jfield{display:flex;gap:8px;align-items:center}
.jfield label{flex:0 0 42px;font-weight:700;font-size:13px;color:var(--w-soft)}
.jfield button{flex:0 0 auto;border:1.5px solid var(--w-line);background:transparent;color:var(--w-ink);border-radius:999px;font:inherit;font-weight:700;font-size:13px;padding:9px 12px;min-height:42px;cursor:pointer}
.jfield button[aria-pressed=true]{background:#2af0d9;color:#170f3a;border-color:#2af0d9}
.jsug{display:flex;flex-direction:column;margin-left:50px}
.jsug:empty{display:none}
.jsug button{display:flex;flex-direction:column;align-items:flex-start;gap:1px;text-align:left;background:transparent;border:0;border-bottom:1px solid var(--w-line);color:var(--w-ink);font:inherit;padding:9px 4px;min-height:44px;cursor:pointer}
.jsug button span{font-size:12px;color:var(--w-soft)}
.jnote{margin:4px 0 0;font-size:13px;color:var(--w-soft)}
.jsum{margin:6px 0 2px;font-size:14.5px}
.jrow{border:1.5px solid var(--w-line);border-radius:14px;padding:10px 12px;margin-top:8px;cursor:pointer}
.jrow.on{border-color:#2af0d9;box-shadow:0 0 0 1px #2af0d9 inset}
.jtop{display:flex;flex-wrap:wrap;align-items:center;gap:8px;font-variant-numeric:tabular-nums}
.jtop b{font:800 20px/1.1 Outfit,"Segoe UI",sans-serif}
.jtop span{font-size:14px}
.jtop i{font-style:normal;font-size:13px;color:var(--w-soft)}
.jtop em{font-style:normal;margin-left:auto;font-weight:800;font-size:13px;color:#170f3a;background:#2af0d9;border-radius:999px;padding:2px 9px}
.jleg{display:flex;gap:8px;align-items:flex-start;margin-top:8px;font-size:13.5px;line-height:1.4}
.jleg b{font-variant-numeric:tabular-nums}
.jmore{margin-top:10px}
.jmore .jrow{padding:8px 12px;margin-top:6px}
.jmore .jtop b{font-size:16px}
#bmap{height:min(48vh,400px);min-height:280px;width:100%}
#bmap.xdark .leaflet-tile-pane{filter:invert(1) hue-rotate(180deg) brightness(.9) contrast(.9) saturate(.7)}
.jpop{display:flex;gap:8px;margin-top:8px}
.jpop button{border:0;border-radius:999px;background:#170f3a;color:#fff;font:inherit;font-weight:700;font-size:13px;padding:8px 12px;min-height:38px;cursor:pointer}
.ball>summary{cursor:pointer;font-weight:700;font-size:16px;padding:14px 16px;border:1.5px solid var(--w-line);border-radius:14px;min-height:44px;box-sizing:border-box}
.ball[open]>summary{margin-bottom:6px}
#bnear{border:1.5px solid var(--w-line);background:var(--w-card);color:var(--w-ink);border-radius:999px;padding:8px 14px;font-family:inherit;font-weight:700;font-size:13px;cursor:pointer;white-space:nowrap}
#bnear[aria-pressed=true]{background:#fff;color:#170f3a;border-color:#fff}
.ftab{overflow-x:auto;margin:8px 0 2px}
.ftab table{width:100%;border-collapse:collapse;font-size:13px;font-variant-numeric:tabular-nums}
.ftab th{font-size:11px;font-weight:600;color:var(--w-soft);text-align:left;padding:4px 6px 6px 0;vertical-align:bottom;line-height:1.2}
.ftab td{padding:6px 6px 6px 0;border-top:1px solid var(--w-line);white-space:nowrap}
.ftab tr.gone td{opacity:.4}
.bold{background:#4d1c63;border:1px solid #ff4fa3;border-radius:14px;padding:10px 14px;font-size:14px}
.bbeach{display:flex;flex-wrap:wrap;align-items:center;gap:2px 10px;width:100%;min-height:48px;text-align:left;background:none;border:0;border-bottom:1px solid var(--w-line);color:inherit;font:inherit;padding:9px 0;cursor:pointer}
.bbeach b{flex:1 1 60%;font-size:15px}
.bbeach span{order:3;flex:0 0 100%;font-size:12.5px;color:var(--w-soft)}
.bbeach i{font-style:normal;font-size:12px;font-weight:700;border-radius:999px;padding:3px 10px;white-space:nowrap}
.bbeach i.c{background:#2af0d9;color:#0b1b3a}
.bbeach i.m{background:#ffd166;color:#3a2a00}
.bbeach i.r{background:#ff4fa3;color:#fff}
.bbeach:focus-visible{outline:2px solid #2af0d9;outline-offset:2px}
.bmore{margin-top:8px}
.bmore summary{cursor:pointer;font-weight:700;padding:10px 0;min-height:44px}
.sdue{display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center;padding:9px 0;border-bottom:1px solid var(--w-line);font-size:14px}
.sdue:last-of-type{border-bottom:0}
.sdue b{flex:0 0 100%;font-size:13px;color:var(--w-soft)}
.sdue.now b{color:#ff4fa3}
.sdue.past{opacity:.55}
.sdue span{background:#16356b;border-radius:999px;padding:4px 12px;font-weight:700}
.sdue span.cr{background:#ff4fa3;color:#fff}
.sdue span i,.sdue button i{font-style:normal;font-weight:400;opacity:.8;font-size:12px}
.sdue button.sbtn{background:#16356b;color:inherit;border:0;border-radius:999px;padding:6px 12px;font:inherit;font-weight:700;cursor:pointer}
.sdue button.sbtn.cr{background:#ff4fa3;color:#fff}
.sdue button.sbtn[aria-expanded=true]{outline:2px solid #fff}
.sdue .sinfo{flex:0 0 100%;background:rgba(0,0,0,.22);border-radius:14px;padding:10px 12px;font-size:14px;line-height:1.45}
.sdue .sinfo p{margin:0 0 4px}
.sdue .sinfo .wlinks{margin-top:6px}
.sdue .sinfo .wlinks a{color:#2af0d9}
.shours{display:flex;gap:4px;overflow-x:auto;padding:4px 0 6px;scrollbar-width:none}
.shours::-webkit-scrollbar{display:none}
.shr{flex:1 0 44px;text-align:center;border-radius:12px;padding:7px 2px;font-size:11px;font-weight:700;background:#2e1a66;color:#cdbbea;display:flex;flex-direction:column;gap:3px;align-items:center}
.shr b{font:800 17px/1 Outfit,"Segoe UI",sans-serif;color:inherit}
.shr i{font-style:normal;font-size:15px;line-height:1;display:inline-block}
.shr.ok{background:#16356b;color:#fdf3ff}
.shr.prime{background:#2af0d9;color:#170f3a}
.shr.strong{background:#ff4fa3;color:#fff}
.shr.over{background:#7a1030;color:#fff}
.skey{display:flex;gap:10px;flex-wrap:wrap;font-size:12px;color:var(--w-soft)}
.skey span{display:inline-flex;align-items:center;gap:5px}
.skey i{width:11px;height:11px;border-radius:3px;display:inline-block}
.wcard p.sbig{font:800 22px/1.2 Outfit,"Segoe UI",sans-serif;margin:0 0 4px}
.wcard p.sbig.go{color:#2af0d9}.wcard p.sbig.maybe{color:#ffc83d}.wcard p.sbig.skip{color:#ff8fc0}
.pbtag{display:inline-block;font:800 11px/1.5 "Segoe UI",sans-serif;border-radius:999px;padding:1px 8px;margin-left:6px;vertical-align:middle;background:#2e1a66;color:#cdbbea;white-space:nowrap}
.pbtag.pub{background:#2af0d9;color:#170f3a}
.pbtag.in{background:#ffc83d;color:#170f3a}
.pbv{padding:12px 0;border-bottom:1px solid var(--w-line);display:flex;flex-direction:column;gap:4px}
.pbv:last-child{border-bottom:0;padding-bottom:0}
.pbv h4{margin:0;font:700 16px/1.3 Outfit,"Segoe UI",sans-serif}
.pbv .wlinks{margin-top:4px}
.pbd{padding:10px 0;border-bottom:1px solid var(--w-line)}
.pbd>b{display:block;margin-bottom:6px;color:#2af0d9}
.wcard p.pbnote{margin-top:10px}
.wcard ul.tlist{padding:0;margin:0}
#pb .skey{margin:2px 0 8px}
#pb .wsrc{margin-top:10px}
.sspot{display:flex;gap:12px;align-items:flex-start;padding:12px 0;border-bottom:1px solid var(--w-line)}
.sspot:last-of-type{border-bottom:0}
.sspot svg{flex:none}
.sspot h4{margin:0;font:700 16px/1.2 Outfit,"Segoe UI",sans-serif}
.sspot p{margin:3px 0 0;font-size:13px;line-height:1.4;color:var(--w-soft)}
.sspot p b{color:var(--w-ink);font-weight:700}
.swarn{background:#4d1c63;border:1px solid #ff4fa3;border-radius:18px;padding:12px 16px;font-weight:700}
#sports details summary{cursor:pointer;font-weight:700;color:#2af0d9;margin-top:8px}
#sports .wcard ul{margin:6px 0 0;padding-left:18px;font-size:14px;line-height:1.5}
.xfindrow #xfind{flex:1 1 auto;min-width:0}
#xnear{flex:none;border:1.5px solid #4b2d8a;border-radius:999px;padding:0 16px;font-family:inherit;font-weight:700;font-size:14px;cursor:pointer;background:transparent;color:#fdf3ff;white-space:nowrap}
#xnear[aria-pressed=true]{background:#2af0d9;color:#170f3a;border-color:#2af0d9}
.xsheet .acts #xsay.on{background:#2af0d9;color:#170f3a;border-color:#2af0d9}
.xsheet .acts a,.xsheet .acts button{border:0;border-radius:999px;padding:10px 18px;font-family:inherit;font-weight:700;font-size:14px;cursor:pointer;background:#2af0d9;color:#170f3a;text-decoration:none}
.xsheet .acts button{background:transparent;border:1.5px solid #4b2d8a;color:#fdf3ff}
.xsheet .src{font-size:12px;color:#cdbbea}
.xsheet .src a{color:#cdbbea}
#explore button:focus-visible,#explore a:focus-visible,#explore input:focus-visible{outline:3px solid #ff4fa3;outline-offset:2px}
</style></head><body><div id="app">
<header><h1>Bermuda Hub</h1><small>updated {{STAMP}}</small><button type="button" id="hshare">Share</button><button type="button" id="hfind">Search</button>
<div class="seg" role="group"><button data-p="today" aria-pressed="false">Today</button><button data-p="planner" aria-pressed="true">What's on</button><button data-p="deals" aria-pressed="false">Deals</button><button data-p="list" aria-pressed="false">List</button><button data-p="weather" aria-pressed="false">Weather</button><button data-p="ocean" aria-pressed="false">Ocean</button><button data-p="sports" aria-pressed="false">Sports</button><button data-p="transit" aria-pressed="false">Bus &amp; ferry</button><button data-p="explore" aria-pressed="false">Explore</button></div></header>
<iframe id="f" src="planner.html" title="page"></iframe>
<section id="ocean" hidden><div class="wwrap" id="oc"><p class="lnote">No marine forecast in this build yet.</p></div></section>
<section id="sports" hidden><div class="wwrap" style="padding-bottom:0"><div class="xchips" id="spsw" role="group" aria-label="Which sport" hidden><button type="button" data-s="wind" aria-pressed="true">Wind sports</button><button type="button" data-s="pb" aria-pressed="false" hidden>Pickleball</button><button type="button" data-s="yoga" aria-pressed="false" hidden>Yoga</button><button type="button" data-s="snorkel" aria-pressed="false" hidden>Snorkel</button><button type="button" data-s="scuba" aria-pressed="false" hidden>Scuba</button></div></div><div class="wwrap" id="pb" hidden></div><div class="wwrap" id="yg" hidden></div><div class="wwrap" id="snk" hidden></div><div class="wwrap" id="scu" hidden></div><div class="wwrap" id="sp"><p class="lnote">No wind forecast in this build yet.</p></div></section>
<section id="transit" hidden><div class="wwrap" id="bs"><p class="lnote">No bus timetable in this build yet.</p></div></section>
<section id="explore" hidden><div class="xwrap" id="xp"><p class="lnote">Nothing to explore in this build yet.</p></div>
<dialog id="xdlg"><div class="xsheet" id="xsheet"></div></dialog></section>
<section id="today" hidden><div class="twrap"><h2 class="xtitle" id="tdate">Today in Bermuda</h2><div id="ttip" hidden></div><div class="tgrid"><div class="tcard" id="td-wx"><h3>Weather</h3><p class="tmuted">No weather in this build yet.</p></div><div class="tcard" id="td-boat" hidden></div><div class="tcard" id="td-wind" hidden></div><div class="tcard" id="td-pb" hidden></div><div class="tcard" id="td-yg" hidden></div><div class="tcard" id="td-bus" hidden></div><div class="tcard" id="td-on"><h3>On today</h3><p class="tmuted">Nothing listed in this build.</p></div><div class="tcard" id="td-deal" hidden></div><div class="tcard" id="td-go" hidden></div></div></div></section>
<section id="weather" hidden><div class="wwrap" id="wx"><p class="lnote">No weather in this build yet.</p></div></section>
<section id="list" hidden>
  <div class="lwrap">
    <p class="lnote" id="lstatus">Loading the shared list...</p>
    <form id="ladd" autocomplete="off"><input id="lname" placeholder="Add something (e.g. bananas)" maxlength="80" required><select id="lstore"><option value="">Any store</option><option>MarketPlace</option><option>Lindo's</option><option>Supermart</option><option>Miles</option><option>Pronto</option><option>Price Rite</option><option>Arnold's</option></select><button type="submit">Add</button></form>
    <div id="litems"></div>
    <div class="lbtns"><button type="button" id="lclear">Clear ticked</button><button type="button" id="lclearall" class="ghost">Clear all</button></div>
    <h2>This week's best buys</h2>
    <p class="lnote" id="lbestnote"></p>
    <div id="lbest"></div>
  </div>
</section>
<script>
const f=document.getElementById('f');
const listSec=document.getElementById('list'), wxSec=document.getElementById('weather'), xpSec=document.getElementById('explore'), tdSec=document.getElementById('today'), spSec=document.getElementById('sports'), ocSec=document.getElementById('ocean'), bsSec=document.getElementById('transit');
// Leaflet (the map library) is fetched once, the first time any map is needed, and shared by every map on the page.
window.hubLeaflet=(function(){let st=0;const q=[];return function(ok,bad){if(st===2){ok();return}if(st===3){if(bad)bad();return}q.push([ok,bad]);if(st===1)return;st=1;
  const css=document.createElement('link');css.rel='stylesheet';css.href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';document.head.appendChild(css);
  const js=document.createElement('script');js.src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
  js.onload=()=>{st=2;q.forEach(x=>x[0]())};js.onerror=()=>{st=3;q.forEach(x=>{if(x[1])x[1]()})};document.head.appendChild(js)}})();
function go(p){const isList=p==='list', isWx=p==='weather', isXp=p==='explore', isTd=p==='today', isSp=p==='sports', isOc=p==='ocean'||p==='transit';ocSec.hidden=p!=='ocean';bsSec.hidden=p!=='transit';listSec.hidden=!isList;wxSec.hidden=!isWx;xpSec.hidden=!isXp;tdSec.hidden=!isTd;spSec.hidden=!isSp;f.hidden=isList||isWx||isXp||isTd||isSp||isOc;if(!isList&&!isWx&&!isXp&&!isTd&&!isSp&&!isOc)f.src=p+'.html';document.querySelectorAll('.seg button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.p===p?'true':'false'));const cur=document.querySelector('.seg button[aria-pressed=true]');if(cur&&cur.scrollIntoView)cur.scrollIntoView({block:'nearest',inline:'center'});try{localStorage.setItem('hub-page',p)}catch(e){}location.hash=p==='sports'?({pb:'pickleball',yoga:'yoga',snorkel:'snorkel',scuba:'scuba'}[window.hubSport]||'sports'):p}
document.querySelector('.seg').addEventListener('click',e=>{const b=e.target.closest('button');if(b)go(b.dataset.p)});
window.addEventListener('message',e=>{const u=e.data&&e.data.hubOpen;if(typeof u!=='string'||!/^https?:/i.test(u))return;const a=document.createElement('a');a.href=u;a.target='_blank';a.rel='noopener';document.body.appendChild(a);a.click();a.remove()});
let p='today';
if(['#today','#deals','#planner','#list','#weather','#ocean','#sports','#transit','#explore'].includes(location.hash))p=location.hash.slice(1);
if(location.hash==='#pickleball'){p='sports';window.hubSport='pb'}
if(location.hash==='#yoga'){p='sports';window.hubSport='yoga'}
if(location.hash==='#snorkel'||location.hash==='#scuba'){p='sports';window.hubSport=location.hash.slice(1)}
tdSec.addEventListener('click',e=>{const b=e.target.closest('button[data-go]');if(b)go(b.dataset.go)});
// Share: always the public website address for the tab in view, so a link sent from the artifact still opens for anyone.
document.getElementById('hshare').addEventListener('click',e=>{const b=e.currentTarget, url='https://mkatzsch.github.io/bermuda-hub/'+(location.hash||''), done=t=>{b.textContent=t;setTimeout(()=>{b.textContent='Share'},2500)};
  const copy=()=>{try{navigator.clipboard.writeText(url).then(()=>done('Link copied'),()=>done('Copy failed'))}catch(x){done('Copy failed')}};
  if(navigator.share){try{navigator.share({title:'Bermuda Hub',text:'The Bermuda everything app',url:url}).catch(err=>{if(!err||err.name!=='AbortError')copy()})}catch(x){copy()}}else copy()});
// Add to home screen: a one time tip on phones, on the website only, until it is installed or dismissed.
(function(){const tip=document.getElementById('ttip'), ua=navigator.userAgent||''; let off=false; try{off=localStorage.getItem('hub-tip-home')==='1'}catch(e){}
  const phone=/iPhone|iPad|iPod|Android/i.test(ua), installed=(window.matchMedia&&window.matchMedia('(display-mode: standalone)').matches)||navigator.standalone===true;
  if(!tip||off||!phone||installed||!location.hostname.endsWith('github.io'))return;
  const ios=/iPhone|iPad|iPod/i.test(ua);
  tip.className='ttip'; tip.hidden=false;
  tip.innerHTML='<b>Keep the Hub on your home screen</b>'+(ios?'In Safari, tap the Share button at the bottom of the screen, then Add to Home Screen.':'Tap the three dots at the top of the browser, then Add to Home screen.')+'<button type="button" aria-label="Dismiss">×</button>';
  tip.querySelector('button').addEventListener('click',()=>{tip.hidden=true;try{localStorage.setItem('hub-tip-home','1')}catch(e){}});})();
go(p);

// ---- Today tab: the date, what is on, and this week's best buys
(function(){
  const esc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const now=new Date(), iso=now.toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'}), m=+iso.slice(5,7), d=+iso.slice(8,10);
  document.getElementById('tdate').textContent=now.toLocaleDateString('en-GB',{timeZone:'Atlantic/Bermuda',weekday:'long',day:'numeric',month:'long'})+' in Bermuda';
  let T={events:[]};try{T=JSON.parse(document.getElementById('today-data').textContent)}catch(e){}
  const ev=(T.events||[]).filter(e=>e.m===m&&e.d===d), tm=new Date(now.getTime()+86400000).toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'}), ev2=(T.events||[]).filter(e=>e.m===+tm.slice(5,7)&&e.d===+tm.slice(8,10));
  const row=e=>'<li><b>'+esc(e.name)+'</b><span>'+esc([e.t,e.venue].filter(Boolean).join(', '))+'</span></li>';
  if(ev.length||ev2.length)document.getElementById('td-on').innerHTML='<h3>On today</h3>'+(ev.length?'<ul class="tlist">'+ev.slice(0,5).map(row).join('')+'</ul>'+(ev.length>5?'<p class="tmuted">and '+(ev.length-5)+' more</p>':''):'<p class="tmuted">Nothing listed for today.</p>')+(ev2.length?'<h3 style="margin-top:12px">Tomorrow</h3><ul class="tlist">'+ev2.slice(0,3).map(row).join('')+'</ul>':'')+'<button type="button" data-go="planner">All of what&#39;s on</button>';
  let B={items:[]};try{B=JSON.parse(document.getElementById('best-buys').textContent)}catch(e){}
  if(B.items&&B.items.length){const c=document.getElementById('td-deal');c.hidden=false;c.innerHTML='<h3>Best buys this week</h3><ul class="tlist">'+B.items.slice(0,4).map(b=>'<li><b>'+esc(b.name)+'</b><span>'+esc(b.store)+', $'+esc(b.price)+' '+esc(b.unit)+'</span></li>').join('')+'</ul><button type="button" data-go="deals">All the deals</button>';}
})();

// ---- Explore tab: a map of the island you tap through, with each place's story opening right here on the page.
(function(){
  let X={};try{X=JSON.parse(document.getElementById('explore-data').textContent)}catch(e){}
  const el=document.getElementById('xp'); if(!X||!X.sites||!X.sites.length)return;
  const esc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const kinds=Object.assign({},X.kinds||{},{turtle:'Turtle sightings'}); let kind='all', q='', map=null, layer=null, pins={};
  const COL={trail:'#9fd3ff',turtle:'#3fe0a0',house:'#f7a8ff',grave:'#b8c4d6',fort:'#ffb25e',wreck:'#2af0d9',ruin:'#c9a7ff',beach:'#fff27a',art:'#ff4fa3',park:'#7ff0a8',nature:'#7ff0a8',tattoo:'#ff7a59',science:'#5ad1ff',lionfish:'#ff3b3b',triangle:'#b3ff5a',haunted:'#f2f2f7'};
  const col=k=>COL[k]||'#ffffff';
  const cls=s=>/^(no |no,|not |closed|private|by boat only, no)/i.test(s.access)?'no':/look only|look from|from a boat|from the ferry|from the harbour|visible from|seen from|^dive/i.test(s.access+' '+s.kids)?'look':'ok';
  const goWord={ok:'You can go',look:'Look from outside, or a dive',no:'Closed or private'};
  // The hunt: tick off places you have been and mosaics you have found, and add mosaics of your own where you stand.
  // Kept on this device only (browser storage), so each phone has its own tally.
  const load=(k,d)=>{try{const v=JSON.parse(localStorage.getItem(k));return v==null?d:v}catch(e){return d}}, save=(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}};
  const seen=new Set(load('hub-seen',[])); let mine=load('hub-my-finds',[]);
  const MOSAICS=47;
  X.sites=X.sites.concat(mine);
  // Photos: one per place, taken or picked on the phone, shrunk to 1280 pixels and kept in this browser's own
  // database (IndexedDB), so they stay on the device and never leave it.
  const hasPhoto=new Set();
  const pdb=()=>new Promise((res,rej)=>{const r=indexedDB.open('hub-photos',1);r.onupgradeneeded=()=>r.result.createObjectStore('photos');r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)});
  const ptx=async(mode,fn)=>{const d=await pdb();return new Promise((res,rej)=>{const t=d.transaction('photos',mode), q=fn(t.objectStore('photos'));t.oncomplete=()=>res(q.result);t.onerror=()=>rej(t.error)})};
  const putPhoto=(id,blob)=>ptx('readwrite',st=>st.put(blob,id)).then(()=>{hasPhoto.add(id)});
  const getPhoto=id=>ptx('readonly',st=>st.get(id));
  const delPhoto=id=>ptx('readwrite',st=>st.delete(id)).then(()=>{hasPhoto.delete(id)});
  const shrink=file=>new Promise((res,rej)=>{const im=new Image(), u=URL.createObjectURL(file);
    im.onload=()=>{const k=Math.min(1,1280/Math.max(im.naturalWidth,im.naturalHeight)), c=document.createElement('canvas');c.width=Math.round(im.naturalWidth*k);c.height=Math.round(im.naturalHeight*k);
      c.getContext('2d').drawImage(im,0,0,c.width,c.height);URL.revokeObjectURL(u);c.toBlob(b=>b?res(b):rej(new Error('no picture')),'image/jpeg',0.82)};
    im.onerror=()=>{URL.revokeObjectURL(u);rej(new Error('not a picture'))};im.src=u});
  const pick=()=>new Promise(res=>{const f=document.createElement('input');f.type='file';f.accept='image/*';f.onchange=()=>res(f.files&&f.files[0]?f.files[0]:null);f.click()});
  const shown=()=>X.sites.filter(s=>(kind==='all'||s.kind===kind||(kind==='bnt'&&s.bnt))&&(!q||(s.name+' '+s.parish+' '+(kinds[s.kind]||'')).toLowerCase().includes(q)));
  const live=location.hostname.endsWith('github.io')||location.hostname==='localhost'||location.hostname==='127.0.0.1'||location.protocol==='file:';
  el.innerHTML='<h2 class="xtitle">Explore the island</h2><p class="xlead">'+X.sites.length+' places. Tap a pin or a card and its story opens right here.</p>'
    +'<div class="wmtog" id="xmode" role="group" aria-label="Explore"><button type="button" data-m="places" aria-pressed="true">Places</button><button type="button" data-m="guide" aria-pressed="false">Field guide</button></div>'
    +'<div class="xbadges" id="xbadges"></div><div id="xplaces" class="xpane"><div id="xroutes"></div><div class="xchips" id="xchips"></div><div class="xprog" id="xprog"></div>'
    +(live?'<div class="xmapbox"><div id="xmap" role="application" aria-label="Map of Bermuda with a pin for each place"></div><span class="xmaphint" id="xmaphint">Loading the map...</span><div class="xbase" id="xbase" role="group" aria-label="Map style" hidden><button type="button" data-b="street">Map</button><button type="button" data-b="sat">Satellite</button></div></div>':'')
    +'<div class="xfindrow"><input id="xfind" type="search" placeholder="Find a place, a parish or a kind" aria-label="Find a place">'+(live&&navigator.geolocation?'<button type="button" id="xnear" aria-pressed="false">Near me</button>':'')+'</div>'
    +'<div class="xcards" id="xcards"></div><p class="wsrc">'+esc(X.note||'')+'</p></div>'
    +'<div id="xguide" class="xpane" hidden><p class="xlead">What people are seeing in Bermuda, from the sightings islanders and visitors log on iNaturalist. Tap one for its story and where it was last seen.</p><div class="wcard sea gturtle"><h3>Seen a sea turtle?</h3><p>Young green turtles and hawksbills grow up on Bermuda&#39;s seagrass beds and reefs. Log each one you see and it goes on your own map with the date, the time and the spot.</p><div class="acts"><button type="button" id="gturtlelog">Log a turtle sighting</button><a href="tel:+14412932727">Hurt or stranded turtle: call 293-2727, then #999</a></div></div><div class="xchips" id="gchips"></div><div class="xchips" id="gopts"></div><div class="xprog" id="gprog"></div><div class="gcards" id="gcards"></div><p class="wsrc">Sightings, names and photos from iNaturalist (inaturalist.org), limited to confirmed records in Bermuda, saved into the Hub by the morning run. Descriptions from Wikipedia. Photos are shown only where the photographer has shared them under a Creative Commons licence.</p></div>';
  // Near me: where the phone is, kept only while the page is open. Distances are straight lines in kilometres.
  let me=null, meDot=null;
  const far=s=>{if(!me||!s.lat||!s.lon)return Infinity;const R=6371,r=Math.PI/180,a=Math.sin((s.lat-me.lat)*r/2),b=Math.sin((s.lon-me.lon)*r/2),h=a*a+Math.cos(me.lat*r)*Math.cos(s.lat*r)*b*b;return 2*R*Math.asin(Math.sqrt(h))};
  const farText=d=>d===Infinity?'':(d<1?Math.round(d*100)*10+' m away':d.toFixed(1)+' km away');
  const inBda=()=>me&&me.lat>32.18&&me.lat<32.46&&me.lon>-65.02&&me.lon<-64.52;
  function drawMe(){if(!map)return;if(meDot){map.removeLayer(meDot);meDot=null}if(!me||!inBda())return;
    meDot=L.circleMarker([me.lat,me.lon],{radius:8,color:'#ffffff',weight:3,fillColor:'#2f7bff',fillOpacity:1,interactive:false}).addTo(map);}
  // Read it to me: the phone reads the sheet aloud, a sentence or two at a time so long stories are not cut off.
  const canSay='speechSynthesis' in window&&'SpeechSynthesisUtterance' in window;
  const hush=()=>{try{speechSynthesis.cancel()}catch(e){}};
  function say(btn,texts){
    if(btn.classList.contains('on')){hush();btn.classList.remove('on');btn.textContent='Read it to me';return}
    const bits=[];texts.filter(Boolean).forEach(t=>{String(t).replace(/([.!?])[ ]+/g,'$1|').split('|').forEach(x=>{x=x.trim();if(!x)return;const last=bits[bits.length-1];if(last&&last.length+x.length<180)bits[bits.length-1]=last+' '+x;else bits.push(x)})});
    if(!bits.length)return;
    try{hush();bits.forEach((t,i)=>{const u=new SpeechSynthesisUtterance(t);u.lang='en-GB';u.rate=0.95;if(i===bits.length-1)u.onend=()=>{btn.classList.remove('on');btn.textContent='Read it to me'};speechSynthesis.speak(u)});
      btn.classList.add('on');btn.textContent='Stop reading';}catch(e){btn.textContent='This device cannot read aloud'}
  }
  function chips(){
    document.getElementById('xchips').innerHTML='<button type="button" data-k="all" aria-pressed="'+(kind==='all')+'">Everything ('+X.sites.length+')</button>'+Object.keys(kinds).map(k=>'<button type="button" data-k="'+k+'" aria-pressed="'+(kind===k)+'"><i style="background:'+col(k)+'"></i>'+esc(kinds[k])+' ('+X.sites.filter(s=>s.kind===k).length+')</button>').join('')+'<button type="button" data-k="bnt" aria-pressed="'+(kind==='bnt')+'"><i style="background:#fff"></i>National Trust ('+X.sites.filter(s=>s.bnt).length+')</button>';
  }
  function cards(){
    const list=me?shown().slice().sort((a,b)=>far(a)-far(b)):shown();
    document.getElementById('xcards').innerHTML=list.length?list.map(s=>{const c=cls(s);return '<button type="button" class="xcard '+c+'" data-id="'+esc(s.id)+'"><span class="k"><i style="background:'+col(s.kind)+'"></i>'+esc(kinds[s.kind]||s.kind)+', '+esc(s.parish)+'</span><span class="n">'+esc(s.name)+'</span><span class="a">'+esc(s.kids)+'</span><span class="go">'+(s.kind==='turtle'?'Logged ✓':seen.has(s.id)?(s.kind==='art'?'Found ✓':'Been here ✓'):goWord[c])+(hasPhoto.has(s.id)?', photo ✓':'')+(me&&far(s)!==Infinity?', '+farText(far(s)):'')+'</span></button>'}).join(''):'<p class="xlead">Nothing matches that. Try a parish, or clear the box.</p>';
  }
  function drawPins(){
    if(!map)return;
    layer.clearLayers(); pins={};
    const list=shown().filter(s=>s.lat&&s.lon&&s.id!=='invader-hunt');
    for(const s of list){
      const m=L.circleMarker([s.lat,s.lon],{radius:9,color:seen.has(s.id)?'#ffffff':'#170f3a',weight:seen.has(s.id)?3.5:2,fillColor:col(s.kind),fillOpacity:1});
      m.bindTooltip(s.name,{direction:'top',offset:[0,-8],className:'xtip'}); m.on('click',()=>open(s.id)); m.addTo(layer); pins[s.id]=m;
    }
    document.getElementById('xmaphint').textContent=list.length+' on the map. Tap a pin.';
    drawMe();
  }
  function prog(){
    const pool=X.sites.filter(s=>s.id!=='invader-hunt'&&(kind==='all'||s.kind===kind||(kind==='bnt'&&s.bnt))), n=pool.filter(s=>seen.has(s.id)).length;
    let t=kind==='turtle'?'You have logged '+pool.length+' turtle sighting'+(pool.length===1?'':'s')+' on this device.':kind==='art'?'Mosaics found: '+n+' of '+MOSAICS+'. Only '+pool.filter(s=>!s.mine).length+' have been named publicly, so add the others as you find them.':'You have been to '+n+' of '+pool.length+(kind==='all'?' places':kind==='bnt'?' National Trust places':' '+(kinds[kind]||'').toLowerCase())+'.';
    document.getElementById('xprog').innerHTML='<div class="bar"><i style="width:'+(kind==='turtle'?100:100*n/(kind==='art'?MOSAICS:Math.max(1,pool.length))).toFixed(0)+'%"></i></div><span>'+esc(t)+'</span>'+(kind==='art'?'<button type="button" id="xadd">Tag a mosaic: photo and pin</button>':kind==='turtle'?'<button type="button" id="xadd">I just saw a turtle here</button>':'');
  }
  // Badges: sets to finish. Counted from the places ticked, mosaics tagged, turtles logged and species seen.
  function badges(){
    const cnt=f=>X.sites.filter(s=>s.id!=='invader-hunt'&&f(s)&&seen.has(s.id)).length, sp=[...seen].filter(k=>String(k).startsWith('sp-')).length;
    const B=[['Explorer',cnt(s=>true),25],['Fort finder',cnt(s=>s.kind==='fort'),10],['Beach hopper',cnt(s=>s.kind==='beach'),10],['Mosaic hunter',cnt(s=>s.kind==='art'),10],['Trust regular',cnt(s=>s.bnt),10],['Trail walker',cnt(s=>s.kind==='trail'),5],['Wreck diver',cnt(s=>s.kind==='wreck'),3],['Naturalist',sp,10],['Turtle spotter',X.sites.filter(s=>s.kind==='turtle').length,3]];
    document.getElementById('xbadges').innerHTML=B.map(b=>{const done=b[1]>=b[2];return '<div class="xbadge'+(done?' on':'')+'" title="'+b[0]+'"><b>'+b[0]+'</b><span>'+(done?'Earned ✓':Math.min(b[1],b[2])+' of '+b[2])+'</span><i style="width:'+Math.min(100,100*b[1]/b[2]).toFixed(0)+'%"></i></div>'}).join('');
    return B;
  }
  // Half-day routes: outings made of places already in the guide, listed in explore.json under routes.
  const ROUTES=(X.routes||[]).map(r=>Object.assign({},r,{sites:(r.stops||[]).map(id=>X.sites.find(s=>s.id===id)).filter(s=>s&&s.lat&&s.lon)})).filter(r=>r.sites.length>=2);
  const gap=(a,b)=>{const R=6371,q=Math.PI/180,u=Math.sin((b.lat-a.lat)*q/2),v=Math.sin((b.lon-a.lon)*q/2),h=u*u+Math.cos(a.lat*q)*Math.cos(b.lat*q)*v*v;return 2*R*Math.asin(Math.sqrt(h))};
  const gapText=d=>d<1?Math.max(10,Math.round(d*100)*10)+' m':d.toFixed(1)+' km';
  let routeLine=null;
  function routes(){
    const box=document.getElementById('xroutes'); if(!box)return; if(!ROUTES.length){box.innerHTML='';return}
    box.innerHTML='<h3>Half-day routes</h3><div class="xrrow">'+ROUTES.map(r=>{const n=r.sites.filter(s=>seen.has(s.id)).length;return '<button type="button" class="xroute" data-r="'+esc(r.id)+'"><b>'+esc(r.name)+'</b><span>'+r.sites.length+' stops. '+esc(r.allow||'')+'</span><span>'+esc(r.how||'')+'</span><span class="p">'+(n===r.sites.length?'Done ✓':n?n+' of '+r.sites.length+' visited':'Not started')+'</span></button>'}).join('')+'</div>';
  }
  function openRoute(id){
    const r=ROUTES.find(x=>x.id===id); if(!r)return;
    const dlg=document.getElementById('xdlg'), sh=document.getElementById('xsheet'), st=r.sites;
    const total=st.slice(1).reduce((t,s,i)=>t+gap(st[i],s),0), pt=s=>s.lat+','+s.lon;
    const gm='https://www.google.com/maps/dir/?api=1&amp;destination='+encodeURIComponent(pt(st[st.length-1]))+(st.length>1?'&amp;waypoints='+encodeURIComponent(st.slice(0,-1).map(pt).join('|')):'')+'&amp;travelmode='+(String(r.how||'').indexOf('foot')>=0?'walking':'driving');
    sh.innerHTML='<div class="top"><span class="k">Half-day route</span><h2>'+esc(r.name)+'</h2><span class="era">'+esc(r.allow||'')+'. '+esc(r.how||'')+'.</span></div>'
      +'<div class="body"><p>'+esc(r.blurb||'')+'</p><ol class="xstops">'+st.map((s,i)=>'<li data-id="'+esc(s.id)+'" class="'+(seen.has(s.id)?'done':'')+'"><div><b>'+esc(s.name)+'</b><span>'+esc(kinds[s.kind]||s.kind)+(i?', '+gapText(gap(st[i-1],s))+' from the last stop':', the start')+'</span></div></li>').join('')+'</ol>'
      +'<p class="src">About '+gapText(total)+' between the stops in a straight line, so the real walk or ride is longer. Pins are approximate. Tap a stop for its story.</p>'
      +'<div class="acts"><a href="'+gm+'" target="_blank" rel="noopener">Open the route in Google Maps</a>'+(map?'<button type="button" id="xrmap">Show it on the map</button>':'')+(canSay?'<button type="button" id="xsay">Read it to me</button>':'')+'<button type="button" id="xclose">Close</button></div></div>';
    try{dlg.showModal()}catch(x){dlg.setAttribute('open','')}
    dlg.scrollTop=0; hush();
    document.getElementById('xclose').onclick=()=>dlg.close();
    sh.querySelector('.xstops').onclick=e=>{const li=e.target.closest('li[data-id]');if(li)open(li.dataset.id)};
    const sy=document.getElementById('xsay'); if(sy)sy.onclick=()=>say(sy,[r.name+'.',(r.allow||'')+'. '+(r.how||'')+'.',r.blurb,'The stops, in order: '+st.map(s=>s.name).join('. ')+'.']);
    const mb=document.getElementById('xrmap'); if(mb)mb.onclick=()=>{if(routeLine)map.removeLayer(routeLine);routeLine=L.polyline(st.map(s=>[s.lat,s.lon]),{color:'#ff4fa3',weight:5,opacity:0.9,dashArray:'2 10',lineCap:'round'}).addTo(map);kind='all';q='';document.getElementById('xfind').value='';refresh();map.fitBounds(routeLine.getBounds().pad(0.25));dlg.close();document.getElementById('xmap').scrollIntoView({behavior:'smooth',block:'center'})};
  }
  function refresh(){chips();prog();cards();drawPins();badges();routes()}
  // One place to go today, picked for the weather, shown on the Today tab. Changes each day.
  window.hubSuggest=function(mood){
    const c=document.getElementById('td-go'); if(!c)return;
    const wet=mood==='rain', dayNo=Math.floor(Date.now()/86400000);
    const indoor=['park-bamz','park-crystal-caves','bnt-globe','bnt-verdmont','bnt-samaritans-lodge','bnt-the-keep','park-botanical-gardens'];
    const pool=wet?X.sites.filter(s=>indoor.includes(s.id)):X.sites.filter(s=>!s.mine&&cls(s)==='ok'&&['fort','beach','park','trail'].includes(s.kind)&&!seen.has(s.id));
    const list=pool.length?pool:X.sites.filter(s=>cls(s)==='ok'); if(!list.length)return;
    const s=list[dayNo%list.length], n=X.sites.filter(x=>seen.has(x.id)).length;
    c.hidden=false; c.innerHTML='<h3>'+(wet?'Somewhere dry to go':'Somewhere to go')+'</h3><p><b>'+esc(s.name)+'</b>, '+esc(s.parish)+'</p><p class="tmuted">'+esc(s.kids)+'</p><p class="tmuted">You have been to '+n+' of '+X.sites.filter(x=>x.id!=='invader-hunt').length+' places.</p><button type="button" id="tdopen">Its story</button><button type="button" data-go="explore">Explore the map</button>';
    document.getElementById('tdopen').onclick=()=>{go('explore');open(s.id)};
  };
  // Dropping your own pin. A mosaic is tagged with a photo first; a turtle sighting is logged straight away (a photo
  // can be added afterwards from its sheet). Both are kept on this device.
  async function addFind(what){
    const turtle=what==='turtle', tell=t=>{const b=document.getElementById('xadd');if(b)b.textContent=t};
    if(!navigator.geolocation){tell('This device cannot share its location');return}
    let blob=null;
    if(!turtle){const file=await pick(); if(!file){return}
      try{blob=await shrink(file)}catch(e){tell('That file is not a picture. Tap to try again');return}}
    tell((turtle?'':'Photo taken. ')+'Finding where you are...');
    navigator.geolocation.getCurrentPosition(async p=>{
      const day=new Date().toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'}), n=mine.filter(m=>m.kind===(turtle?'turtle':'art')).length+1;
      const s=turtle?{id:'mine-'+Date.now(),kind:'turtle',name:'Turtle sighting '+n,parish:'Seen by you',lat:+p.coords.latitude.toFixed(5),lon:+p.coords.longitude.toFixed(5),approx:false,mine:true,era:'Seen '+day+', '+new Date().toLocaleTimeString('en-GB',{hour:'numeric',minute:'2-digit'}),access:'',kids:'A turtle you saw and logged yourself.',see:'',story:'You logged this sighting where you were. Rename it with what you saw, such as a green turtle near the seagrass, and add a photo if you got one.',links:[]}
        :{id:'mine-'+Date.now(),kind:'art',name:'My find '+n,parish:'Tagged by you',lat:+p.coords.latitude.toFixed(5),lon:+p.coords.longitude.toFixed(5),approx:false,mine:true,era:'Tagged '+day,access:'',kids:'A mosaic you found, photographed and pinned yourself.',see:'',story:'You tagged this one where you were standing.',links:[]};
      mine.push(s); save('hub-my-finds',mine); X.sites.push(s); seen.add(s.id); save('hub-seen',[...seen]);
      if(blob){try{await putPhoto(s.id,blob)}catch(e){}}
      refresh(); open(s.id);
    },()=>tell('Could not get your location. Allow location for this page and tap again.'),{enableHighAccuracy:true,timeout:15000});
  }
  // The story sheet. History sits here in full: who built it, who came, what is found only here, odd facts.
  document.addEventListener('hub-open',e=>{go('explore');open(e.detail)});  // other tabs ask for a place this way
  function open(id){
    const s=X.sites.find(x=>x.id===id);if(!s)return;
    const dlg=document.getElementById('xdlg'), sh=document.getElementById('xsheet');
    const part=(h,v)=>v?'<div><h3>'+h+'</h3>'+(Array.isArray(v)?'<ul>'+v.map(t=>'<li>'+esc(t)+'</li>').join('')+'</ul>':'<p>'+esc(v)+'</p>')+'</div>':'';
    sh.innerHTML='<div class="top"><span class="k">'+esc(kinds[s.kind]||s.kind)+', '+esc(s.parish)+(s.bnt?', Bermuda National Trust':'')+'</span><h2>'+esc(s.name)+'</h2><span class="era">'+esc(s.era)+'</span></div>'
      +'<div class="body">'+(s.photo&&live?'<figure class="xweb"><img loading="lazy" alt="" src="'+esc(s.photo.u)+'"><figcaption>Photo: '+esc(s.photo.by)+', '+esc(s.photo.lic)+', <a href="'+esc(s.photo.page)+'" target="_blank" rel="noopener">Wikimedia Commons</a></figcaption></figure>':'')+'<div class="xphoto" id="xphoto" hidden></div><p>'+esc(s.story)+'</p><div class="facts">'+part('Who built it',s.built)+part('Who has been here',s.visitors)+part('Only here',s.unique)+part('Good to know',s.tidbits)+part('The walk',s.walk)+part('Look for',s.see)+part('With children',s.kids)+part('Getting there',s.access)+(s.sections||[]).map(z=>part(esc(z[0]),z[1])).join('')+'</div>'
      +((s.wiki||[]).length?'<div class="acts"><button type="button" id="xdive">Deep dive: the full history</button></div><div class="xdeep" id="xdeep" hidden></div>':'')
      +(s.mine?'<label class="xname">Name it <input id="xname" type="text" maxlength="60" value="'+esc(s.name)+'"></label>':'')
      +(s.id==='invader-hunt'?'':'<div class="acts">'+(s.kind==='turtle'?'':'<button type="button" id="xseen" class="'+(seen.has(s.id)?'on':'')+'">'+(seen.has(s.id)?(s.kind==='art'?'Found ✓ (tap to undo)':'Been here ✓ (tap to undo)'):(s.kind==='art'?'I found it':'I have been here'))+'</button>')+'<button type="button" id="xpic">'+(hasPhoto.has(s.id)?'Change my photo':(s.kind==='art'?'Tag it with a photo':'Add my photo'))+'</button>'+(hasPhoto.has(s.id)?'<button type="button" id="xpicdel">Remove photo</button>':'')+(s.mine?'<button type="button" id="xdrop">Remove this pin</button>':'')+'</div>')
      +'<div class="acts">'+(s.kind==='turtle'?'':'<a href="https://www.google.com/maps/dir/?api=1&amp;destination='+encodeURIComponent(s.lat+','+s.lon)+'" target="_blank" rel="noopener">Directions'+(s.approx?' (pin is approximate)':'')+'</a>')+(canSay?'<button type="button" id="xsay">Read it to me</button>':'')+'<button type="button" id="xclose">Close</button></div>'
      +((s.links||[]).length?'<p class="src">Sources: '+s.links.map(l=>'<a href="'+esc(l[1])+'" target="_blank" rel="noopener">'+esc(l[0])+'</a>').join(', ')+'</p>':'')+'</div>';
    try{dlg.showModal()}catch(x){dlg.setAttribute('open','')}
    dlg.scrollTop=0;
    document.getElementById('xclose').onclick=()=>dlg.close();
    hush(); const sy=document.getElementById('xsay'); if(sy)sy.onclick=()=>{const flat=v=>Array.isArray(v)?v.join('. '):v;say(sy,[s.name+'.',s.era?s.era+'.':'',s.story,s.built&&'Who built it. '+flat(s.built),s.visitors&&'Who has been here. '+flat(s.visitors),s.unique&&'Only here. '+flat(s.unique),s.tidbits&&'Good to know. '+flat(s.tidbits),s.walk&&'The walk. '+flat(s.walk),s.see&&'Look for. '+flat(s.see),s.kids&&'With children. '+flat(s.kids),s.access&&'Getting there. '+flat(s.access)])};
    const dv=document.getElementById('xdive'); if(dv)dv.onclick=()=>dive(s);
    if(hasPhoto.has(id))getPhoto(id).then(b=>{const ph=document.getElementById('xphoto');if(b&&ph){ph.innerHTML='<img alt="Your photo of '+esc(s.name)+'" src="'+URL.createObjectURL(b)+'">';ph.hidden=false}}).catch(()=>{});
    const pc=document.getElementById('xpic'); if(pc)pc.onclick=async()=>{const f=await pick();if(!f)return;try{await putPhoto(id,await shrink(f));if(s.kind==='art'&&!seen.has(id)){seen.add(id);save('hub-seen',[...seen])}refresh();open(id)}catch(e){pc.textContent='That did not work. Tap to try again'}};
    const pd=document.getElementById('xpicdel'); if(pd)pd.onclick=async()=>{try{await delPhoto(id)}catch(e){}refresh();open(id)};
    const sb=document.getElementById('xseen'); if(sb)sb.onclick=()=>{if(seen.has(id))seen.delete(id);else seen.add(id);save('hub-seen',[...seen]);refresh();open(id)};
    const nm=document.getElementById('xname'); if(nm)nm.onchange=()=>{s.name=nm.value.trim()||s.name;save('hub-my-finds',mine);refresh()};
    const dr=document.getElementById('xdrop'); if(dr)dr.onclick=()=>{delPhoto(id).catch(()=>{});mine=mine.filter(m=>m.id!==id);save('hub-my-finds',mine);X.sites=X.sites.filter(m=>m.id!==id);seen.delete(id);save('hub-seen',[...seen]);dlg.close();refresh()};
    if(map&&pins[id])map.panTo(pins[id].getLatLng());
  }
  // Deep dive: the full encyclopedia article (or articles) for the place, fetched from Wikipedia when asked for and
  // laid out here on the page. Reference lists and link sections are left out. Needs a connection.
  const SKIP=['references','external links','see also','notes','bibliography','further reading','sources','citations','footnotes','gallery'];
  async function dive(s){
    const box=document.getElementById('xdeep'), btn=document.getElementById('xdive'); if(!box)return;
    if(!live){box.hidden=false;btn.hidden=true;box.innerHTML='<p class="src">The deep dive fetches the full article, which this copy of the Hub is not allowed to do. It works on the website: <a href="https://mkatzsch.github.io/bermuda-hub/#explore" target="_blank" rel="noopener" style="color:#2af0d9">mkatzsch.github.io/bermuda-hub</a></p>';return}
    box.hidden=false; btn.disabled=true; btn.textContent='Fetching the history...';
    let out='';
    for(const title of s.wiki){
      try{
        const j=await fetch('https://en.wikipedia.org/w/api.php?action=query&format=json&origin=*&redirects=1&prop=extracts&explaintext=1&exsectionformat=wiki&titles='+encodeURIComponent(title)).then(r=>r.json());
        const pg=Object.values((j.query&&j.query.pages)||{})[0]; if(!pg||!pg.extract)continue;
        let skip=false, body='';
        for(const raw of pg.extract.split(String.fromCharCode(10))){
          const line=raw.trim(); if(!line)continue;
          if(line.startsWith('==')&&line.endsWith('==')){
            const lvl=line.length-line.replace(new RegExp('^=+'),'').length, name=line.split('=').join('').trim();
            if(lvl===2)skip=SKIP.includes(name.toLowerCase());
            if(!skip)body+=(lvl===2?'<h4>':'<h5>')+esc(name)+(lvl===2?'</h4>':'</h5>');
          }else if(!skip)body+='<p>'+esc(line)+'</p>';
        }
        out+='<section><h3>'+esc(pg.title)+'</h3>'+body+'<p class="src">From Wikipedia, the free encyclopedia, shared under the CC BY-SA licence. <a href="https://en.wikipedia.org/wiki/'+encodeURIComponent(pg.title.split(' ').join('_'))+'" target="_blank" rel="noopener">Original article</a></p></section>';
      }catch(e){}
    }
    if(out){box.innerHTML=(s.wiki_general?'<p class="src">This place has no article of its own yet, so this is the history of the area around it.</p>':'')+out;btn.hidden=true;}
    else{box.hidden=true;btn.disabled=false;btn.textContent='Could not fetch it. Check your connection and tap again';}
  }
  chips(); prog(); cards(); badges(); routes(); window.hubSuggest(document.body.dataset.mood||'');
  ptx('readonly',st=>st.getAllKeys()).then(ks=>{(ks||[]).forEach(k=>hasPhoto.add(k));if(hasPhoto.size)cards()}).catch(()=>{});
  document.getElementById('xchips').addEventListener('click',e=>{const c=e.target.closest('button[data-k]');if(c){kind=c.dataset.k;refresh()}});
  document.getElementById('xcards').addEventListener('click',e=>{const c=e.target.closest('.xcard');if(c)open(c.dataset.id)});
  document.getElementById('xprog').addEventListener('click',e=>{if(e.target.id==='xadd')addFind(kind==='turtle'?'turtle':'art')});
  document.getElementById('xfind').addEventListener('input',e=>{q=e.target.value.trim().toLowerCase();cards();drawPins()});
  document.body.appendChild(document.getElementById('xdlg'));
  window.hubOpenPlace=open;
  document.getElementById('xdlg').addEventListener('click',e=>{if(e.target.id==='xdlg')e.target.close()});
  document.getElementById('xdlg').addEventListener('error',e=>{const f=e.target&&e.target.closest?e.target.closest('.xweb'):null;if(f)f.remove()},true);
  document.getElementById('xdlg').addEventListener('close',hush);
  document.getElementById('xroutes').addEventListener('click',e=>{const b=e.target.closest('.xroute');if(b)openRoute(b.dataset.r)});
  const nb=document.getElementById('xnear'); if(nb)nb.addEventListener('click',()=>{
    if(me){me=null;nb.setAttribute('aria-pressed','false');nb.textContent='Near me';cards();drawMe();return}
    nb.textContent='Finding you...';
    navigator.geolocation.getCurrentPosition(p=>{me={lat:p.coords.latitude,lon:p.coords.longitude};nb.setAttribute('aria-pressed','true');nb.textContent=inBda()?'Nearest first ✓':'Not in Bermuda ✓';cards();drawMe();if(map&&inBda())map.setView([me.lat,me.lon],Math.max(map.getZoom(),14))},
      ()=>{nb.textContent='Location is off';setTimeout(()=>{if(!me)nb.textContent='Near me'},4000)},{enableHighAccuracy:true,timeout:15000,maximumAge:60000});
  });
  // ---- Field guide: what is being seen in Bermuda, by group and by month, straight from iNaturalist's public
  // records for the island (place 8638). Only confirmed ("research grade") sightings count. Needs a connection.
  const INAT='https://api.inaturalist.org/v1/', BDA=8638;
  const GROUPS=[['Aves','Birds'],['Actinopterygii','Fish'],['Mammalia','Mammals and whales'],['Reptilia,Amphibia','Lizards, turtles and frogs'],['Mollusca','Snails and shells'],['Insecta,Arachnida','Insects and spiders'],['Plantae','Plants, trees and flowers'],['Animalia','Corals and other sea life'],['Fungi','Fungi']];
  const ORIGIN=[['all','Everything'],['endemic','Only in Bermuda'],['native','Native'],['introduced','Introduced']];
  const MEANS={endemic:'Only in Bermuda',native:'Native',introduced:'Introduced'};
  const monthNo=+new Date().toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'}).slice(5,7), monthName=new Date().toLocaleDateString('en-GB',{timeZone:'Atlantic/Bermuda',month:'long'});
  let gGroup='Aves', gWhen='month', gOrigin='all', gList=[], gTok=0; const gCache={};
  // The saved copy made by the morning run (guide-data). When it is there the guide never goes online, so it
  // opens at once and works in the artifact. Without it the guide falls back to asking iNaturalist live.
  const FG=(()=>{try{return JSON.parse(document.getElementById('guide-data').textContent)}catch(e){return null}})();
  const baked=!!(FG&&FG.sp&&FG.groups&&Object.keys(FG.sp).length);
  const gMonth=baked?['January','February','March','April','May','June','July','August','September','October','November','December'][FG.month-1]:monthName;
  const gCard=(t,ph,count)=>{const em=MEANS[t.preferred_establishment_means]||'';return '<button type="button" class="gcard" data-t="'+t.id+'">'+(ph?'<img loading="lazy" alt="" src="'+esc(ph)+'">':'<span class="noimg">No shared photo</span>')+'<span class="n">'+esc(t.preferred_common_name||t.name)+'</span><span class="sci">'+esc(t.name)+'</span>'+(em?'<span class="em '+esc(t.preferred_establishment_means)+'">'+em+'</span>':'')+'<span class="c">'+count+' sighting'+(count===1?'':'s')+(seen.has('sp-'+t.id)?', seen by you ✓':'')+'</span></button>'};
  const gget=async u=>{if(!gCache[u])gCache[u]=await fetch(u).then(r=>{if(!r.ok)throw new Error('http');return r.json()});return gCache[u]};
  function gChips(){
    document.getElementById('gchips').innerHTML=GROUPS.map(g=>'<button type="button" data-g="'+g[0]+'" aria-pressed="'+(gGroup===g[0])+'">'+g[1]+'</button>').join('');
    document.getElementById('gopts').innerHTML='<button type="button" data-w="month" aria-pressed="'+(gWhen==='month')+'">Seen in '+gMonth+'</button><button type="button" data-w="year" aria-pressed="'+(gWhen==='year')+'">All year</button>'+ORIGIN.map(o=>'<button type="button" data-o="'+o[0]+'" aria-pressed="'+(gOrigin===o[0])+'">'+o[1]+'</button>').join('');
  }
  async function gLoad(){
    const mine=++gTok, box=document.getElementById('gcards'); gChips();
    if(baked){
      const G=FG.groups[gGroup]||{}, src=(gOrigin!=='all'&&gWhen==='year')?(G[gOrigin]||[]):(gWhen==='month'?(G.month||[]):(G.year||[]));
      const rows=src.filter(r=>{const s=FG.sp[r[0]];return s&&(gOrigin==='all'||(s.o||[]).indexOf(gOrigin)>=0)});
      gList=rows.map(r=>{const s=FG.sp[r[0]];return {count:r[1],sp:s,taxon:{id:r[0],name:s.s,preferred_common_name:s.n,preferred_establishment_means:s.em||''}}});
      const total=gOrigin==='all'?((gWhen==='month'?G.month_total:G.year_total)||rows.length):rows.length;
      const saved=new Date(FG.updated+'T12:00:00Z').toLocaleDateString('en-GB',{day:'numeric',month:'short'});
      document.getElementById('gprog').innerHTML='<span>'+total+' kinds recorded'+(gWhen==='month'?' in '+gMonth+' over the years':'')+(total>rows.length?', the '+rows.length+' most seen shown':', most seen first')+'. You have ticked '+[...seen].filter(k=>String(k).startsWith('sp-')).length+' species in all. Saved '+esc(saved)+'.</span>';
      box.innerHTML=gList.length?gList.map(r=>gCard(r.taxon,r.sp.ph?'guide/'+r.taxon.id+'.jpg':'',r.count)).join(''):'<p class="xlead">Nothing recorded for that choice. Try All year or Everything.</p>';
      return}
    if(!live){document.getElementById('gprog').innerHTML='';box.innerHTML='<p class="xlead">The Field guide loads live sightings, which this copy of the Hub is not allowed to fetch. It works on the website: <a href="https://mkatzsch.github.io/bermuda-hub/#explore" target="_blank" rel="noopener" style="color:#2af0d9">mkatzsch.github.io/bermuda-hub</a></p>';return}
    box.innerHTML='<p class="xlead">Looking up the sightings...</p>';
    try{
      const j=await gget(INAT+'observations/species_counts?place_id='+BDA+'&preferred_place_id='+BDA+'&locale=en&quality_grade=research&per_page=48&iconic_taxa='+gGroup+(gWhen==='month'?'&month='+monthNo:'')+(gOrigin!=='all'?'&'+gOrigin+'=true':''));
      if(mine!==gTok)return;
      gList=j.results||[];
      const n=gList.filter(r=>seen.has('sp-'+r.taxon.id)).length;
      document.getElementById('gprog').innerHTML='<span>'+(j.total_results||0)+' kinds recorded'+(gWhen==='month'?' in '+monthName+' over the years':'')+', most seen first. You have ticked '+[...seen].filter(k=>String(k).startsWith('sp-')).length+' species in all.</span>';
      box.innerHTML=gList.length?gList.map(r=>{const t=r.taxon, ph=t.default_photo&&t.default_photo.license_code?t.default_photo.medium_url:'', em=MEANS[t.preferred_establishment_means]||'';
        return '<button type="button" class="gcard" data-t="'+t.id+'">'+(ph?'<img loading="lazy" alt="" src="'+esc(ph)+'">':'<span class="noimg">No shared photo</span>')+'<span class="n">'+esc(t.preferred_common_name||t.name)+'</span><span class="sci">'+esc(t.name)+'</span>'+(em?'<span class="em '+esc(t.preferred_establishment_means)+'">'+em+'</span>':'')+'<span class="c">'+r.count+' sighting'+(r.count===1?'':'s')+(seen.has('sp-'+t.id)?', seen by you ✓':'')+'</span></button>'}).join(''):'<p class="xlead">Nothing recorded for that choice. Try All year or Everything.</p>';
    }catch(e){if(mine===gTok)box.innerHTML='<p class="xlead">Could not reach iNaturalist. Check your connection and tap a group again.</p>';}
  }
  async function gOpen(id){
    const r=gList.find(x=>String(x.taxon.id)===String(id)); if(!r)return;
    const t=r.taxon, dlg=document.getElementById('xdlg'), sh=document.getElementById('xsheet'), key='sp-'+t.id, em=MEANS[t.preferred_establishment_means]||'';
    const ph=r.sp?(r.sp.ph?{medium_url:'guide/'+t.id+'.jpg',attribution:r.sp.at}:null):(t.default_photo&&t.default_photo.license_code?t.default_photo:null);
    const wtitle=r.sp?(r.sp.w||''):t.wikipedia_url?decodeURIComponent(t.wikipedia_url.slice(t.wikipedia_url.lastIndexOf('/')+1)).split('_').join(' '):'';
    sh.innerHTML='<div class="top"><span class="k">'+esc((GROUPS.find(g=>g[0]===gGroup)||['',''])[1])+(em?', '+em:'')+'</span><h2>'+esc(t.preferred_common_name||t.name)+'</h2><span class="era"><i>'+esc(t.name)+'</i></span></div>'
      +'<div class="body">'+(ph?'<div class="xphoto"><img alt="'+esc(t.preferred_common_name||t.name)+'" src="'+esc(ph.medium_url)+'"></div><p class="src">Photo '+esc(ph.attribution||'')+'</p>':'')
      +'<p id="gsum">Loading its description...</p><div class="facts"><div><h3>Seen in Bermuda</h3><p>'+r.count+' confirmed sighting'+(r.count===1?'':'s')+(gWhen==='month'?' in '+gMonth+' over the years':' on record')+'.</p></div><div id="glast"></div></div>'
      +(wtitle?'<div class="acts"><button type="button" id="xdive">Deep dive: the full article</button></div><div class="xdeep" id="xdeep" hidden></div>':'')
      +'<div class="acts"><button type="button" id="xseen" class="'+(seen.has(key)?'on':'')+'">'+(seen.has(key)?'Seen it ✓ (tap to undo)':'I have seen one')+'</button>'+(canSay&&r.sp?'<button type="button" id="xsay">Read it to me</button>':'')+'<button type="button" id="xclose">Close</button></div></div>';
    try{dlg.showModal()}catch(x){dlg.setAttribute('open','')}
    dlg.scrollTop=0;
    document.getElementById('xclose').onclick=()=>dlg.close();
    document.getElementById('xseen').onclick=()=>{if(seen.has(key))seen.delete(key);else seen.add(key);save('hub-seen',[...seen]);gLoad().then(()=>gOpen(id))};
    hush(); const gsy=document.getElementById('xsay'); if(gsy)gsy.onclick=()=>say(gsy,[(t.preferred_common_name||t.name)+'.',em?em+'.':'',r.sp.sum,r.sp.cs?'Conservation status: '+r.sp.cs+'.':'']);
    const dv=document.getElementById('xdive'); if(dv)dv.onclick=()=>dive({wiki:[wtitle]});
    if(r.sp){const el2=document.getElementById('gsum'), g=document.getElementById('glast'), obs=r.sp.last||[];
      el2.textContent=r.sp.sum||'No summary is available for this one yet.';
      if(r.sp.cs){const d=document.createElement('p');d.className='src';d.textContent='Conservation status: '+r.sp.cs+'.';el2.after(d);}
      if(obs.length)g.innerHTML='<h3>Latest sightings</h3><ul>'+obs.map(o=>'<li>'+esc(new Date(o[0]+'T12:00:00Z').toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'}))+(o[1]?', '+esc(o[1]):'')+'</li>').join('')+'</ul>';
      return}
    gget(INAT+'taxa/'+t.id+'?locale=en').then(j=>{const x=(j.results||[])[0]||{}, el2=document.getElementById('gsum'); if(!el2)return;
      const txt=x.wikipedia_summary?new DOMParser().parseFromString(x.wikipedia_summary,'text/html').body.textContent:'';
      el2.textContent=txt||'No summary is available for this one yet.';
      if(x.conservation_status&&x.conservation_status.status_name){const d=document.createElement('p');d.className='src';d.textContent='Conservation status: '+x.conservation_status.status_name+'.';el2.after(d);}
    }).catch(()=>{const el2=document.getElementById('gsum');if(el2)el2.textContent='Could not fetch its story just now.'});
    gget(INAT+'observations?place_id='+BDA+'&taxon_id='+t.id+'&quality_grade=research&order=desc&order_by=observed_on&per_page=5').then(j=>{const g=document.getElementById('glast'), obs=(j.results||[]).filter(o=>o.observed_on); if(!g||!obs.length)return;
      g.innerHTML='<h3>Latest sightings</h3><ul>'+obs.map(o=>'<li>'+esc(new Date(o.observed_on+'T12:00:00Z').toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'}))+(o.place_guess?', '+esc(o.place_guess):'')+'</li>').join('')+'</ul>';
    }).catch(()=>{});
  }
  let gStarted=false;
  document.getElementById('xmode').addEventListener('click',e=>{const b=e.target.closest('button[data-m]');if(!b)return;const guide=b.dataset.m==='guide';
    document.getElementById('xmode').querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',x===b?'true':'false'));
    document.getElementById('xplaces').hidden=guide; document.getElementById('xguide').hidden=!guide;
    if(guide&&!gStarted){gStarted=true;gLoad()} if(!guide&&map)setTimeout(()=>map.invalidateSize(),60);});
  document.getElementById('gturtlelog').addEventListener('click',()=>{kind='turtle';document.querySelector('#xmode button[data-m="places"]').click();refresh();addFind('turtle')});
  document.getElementById('gchips').addEventListener('click',e=>{const b=e.target.closest('button[data-g]');if(b){gGroup=b.dataset.g;gLoad()}});
  document.getElementById('gopts').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;if(b.dataset.w)gWhen=b.dataset.w;if(b.dataset.o)gOrigin=b.dataset.o;gLoad()});
  document.getElementById('gcards').addEventListener('click',e=>{const c=e.target.closest('.gcard');if(c)gOpen(c.dataset.t)});
  document.getElementById('gcards').addEventListener('error',e=>{const im=e.target;if(im&&im.tagName==='IMG'){const sp=document.createElement('span');sp.className='noimg';sp.textContent='No photo yet';im.replaceWith(sp)}},true);
  // The map itself (Leaflet). Two backgrounds: OpenStreetMap streets, darkened to suit the page, and Esri satellite
  // pictures. Neither needs an account or a key. GitHub Pages copy only: the artifact
  // viewer blocks outside scripts and pictures, so that copy shows the cards without the map.
  if(live){
    let started=false;
    const boot=()=>{
      window.hubLeaflet(()=>{
        map=L.map('xmap',{zoomControl:true,attributionControl:true,minZoom:10,maxZoom:18,maxBounds:[[31.85,-65.6],[32.8,-63.95]],maxBoundsViscosity:0.3}).fitBounds([[32.245,-64.89],[32.395,-64.645]]);
        const street=L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; OpenStreetMap contributors'});
        const sat=L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',{maxZoom:18,attribution:'Imagery &copy; Esri, Maxar, Earthstar Geographics'});
        let base='street'; try{if(localStorage.getItem('hub-map-base')==='sat')base='sat'}catch(e){}
        const box=document.getElementById('xmap'), tog=document.getElementById('xbase');
        const setBase=b=>{base=b;map.removeLayer(street);map.removeLayer(sat);(b==='sat'?sat:street).addTo(map);box.classList.toggle('xdark',b!=='sat');
          tog.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',x.dataset.b===b?'true':'false'));try{localStorage.setItem('hub-map-base',b)}catch(e){}};
        tog.hidden=false; tog.addEventListener('click',e=>{const b=e.target.closest('button[data-b]');if(b)setBase(b.dataset.b)});
        setBase(base);
        layer=L.layerGroup().addTo(map); drawPins();
        setTimeout(()=>map.invalidateSize(),300);
      },()=>{document.getElementById('xmaphint').textContent='The map could not load. The cards below still work.'});
    };
    const wait=setInterval(()=>{if(xpSec.hidden)return;if(!started){started=true;boot()}else if(map){map.invalidateSize();clearInterval(wait)}},400);
  }
})();

// ---- Bus & ferry tab. The timetable comes from the official feed, saved by transit_collect and trimmed by transit_doc
// to the services that run on each of the next seven days. Every time shown is the departure from the first stop.
(function(){
  const el=document.getElementById('bs'); let T=null;
  try{T=JSON.parse(document.getElementById('transit-data').textContent)}catch(e){}
  if(!el||!T||!(T.routes||[]).length||!(T.days||[]).length)return;
  const esc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const now=new Date(), bdaDay=now.toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'}), hm=now.toLocaleTimeString('en-GB',{timeZone:'Atlantic/Bermuda',hour:'2-digit',minute:'2-digit',hour12:false}), nowMin=(+hm.slice(0,2)%24)*60+ +hm.slice(3,5);
  const days=T.days.filter(d=>d.date>=bdaDay); if(!days.length)return;
  let day=days[0].date;
  const mins=t=>+t.slice(0,2)*60+ +t.slice(3,5), t12=t=>{const h=+t.slice(0,2)%24;return (h%12||12)+':'+t.slice(3,5)+(h<12?'am':'pm')};
  const dayName=d=>d===bdaDay?'Today':new Date(d+'T12:00:00Z').toLocaleDateString('en-GB',{weekday:'short',day:'numeric',timeZone:'UTC'});
  const longDay=d=>new Date(d+'T12:00:00Z').toLocaleDateString('en-GB',{day:'numeric',month:'long',timeZone:'UTC'});
  const place=n=>n==='Central Bus Terminal'?'Hamilton bus terminal':n;
  // one direction of one route on the chosen day: its departures in order, with repeats removed
  const runsOn=(g,on)=>{const seen=new Set();return g.trips.filter(t=>on.has(t[0])).filter(t=>!seen.has(t[1])&&seen.add(t[1])).sort((a,b)=>mins(a[1])-mins(b[1]))};
  function dirHTML(g,trips,live){
    const up=live?trips.filter(t=>mins(t[1])>=nowMin):trips, len=Math.round(trips.reduce((a,t)=>a+Math.max(0,mins(t[2])-mins(t[1])),0)/trips.length);
    return '<div class="bdir"><p><b>To '+esc(g.head||place(g.to))+'</b>'+(len?', about '+len+' min end to end':'')+'</p><p class="bfrom">Leaves '+esc(place(g.from))+(g.head&&g.head!==g.to?', ends at '+esc(place(g.to)):'')+'</p>'
      +'<p class="bnext">'+(live?(up.length?'Next: <b>'+up.slice(0,3).map(t=>t12(t[1])).join('</b>, <b>')+'</b>':'No more today. Last one left at '+t12(trips[trips.length-1][1])+'.'):'First '+t12(trips[0][1])+', last '+t12(trips[trips.length-1][1])+'.')+'</p>'
      +'<details><summary>All '+trips.length+' departures</summary><div class="btimes">'+trips.map(t=>'<span'+(live&&mins(t[1])<nowMin?' class="gone"':'')+'>'+t12(t[1])+'</span>').join('')+'</div></details></div>';
  }
  function routeHTML(r,on,live){
    const gs=r.groups.map(g=>[g,runsOn(g,on)]).filter(x=>x[1].length); if(!gs.length)return '';
    const main=gs.filter(x=>x[1].length>=3), few=gs.filter(x=>x[1].length<3);
    return '<div class="broute"><h3>'+(r.short?'<span class="bnum" style="background:#'+esc(r.color||'2af0d9')+'">'+esc(r.short)+'</span>':'')+esc(r.long)+'</h3>'
      +(main.length?main:few).map(x=>dirHTML(x[0],x[1],live)).join('')
      +(main.length&&few.length?'<details><summary>'+few.length+' other run'+(few.length>1?'s':'')+' on this route</summary>'+few.map(x=>'<p class="bfrom" style="color:var(--w-soft);font-size:13.5px;margin:4px 0">'+x[1].map(t=>t12(t[1])).join(', ')+' from '+esc(place(x[0].from))+' to '+esc(x[0].head||place(x[0].to))+'</p>').join('')+'</details>':'')+'</div>';
  }
  // Ferries: the schedule in force, typed in from the Marine and Ports brochure (ferry-data). A table is for weekdays
  // or for weekends and public holidays, so the chosen date picks which tables show.
  let F={};try{F=JSON.parse(document.getElementById('ferry-data').textContent)}catch(e){}
  const dayType=d=>{const wd=new Date(d+'T12:00:00Z').getUTCDay();return (wd===0||wd===6||(F.holidays||[]).includes(d))?'weekend':'weekday'};
  const ferryNext=(d,live)=>{const out=[];(F.routes||[]).forEach(r=>r.tables.filter(t=>t.days===dayType(d)).forEach(t=>t.rows.forEach(row=>{if(row[0]&&(!live||mins(row[0])>=nowMin))out.push([mins(row[0]),row[0],r])})));return out.sort((a,b)=>a[0]-b[0])};
  function ferryHTML(d,live){
    if(!(F.routes||[]).length)return '';
    const kind=dayType(d);
    let o='<h2 class="w" id="bferry">Ferries</h2>'+(F.stale?'<div class="bold"><b>Check before you travel.</b> This is the '+esc((F.name||'').toLowerCase())+', and a newer one may have replaced it.</div>':'');
    for(const r of F.routes){
      const tabs=r.tables.filter(t=>t.days===kind), nx=tabs.length?tabs[0].rows.filter(row=>row[0]&&(!live||mins(row[0])>=nowMin)):[];
      o+='<div class="broute"><h3><span class="bnum" style="background:#'+esc(r.color)+'">&nbsp;</span>'+esc(r.name)+'</h3><p class="bfrom" style="color:var(--w-soft);font-size:13px;margin:2px 0 0">'+esc(r.line)+'. '+esc(r.note||'')+'</p>';
      if(!tabs.length)o+=r.tables.length?'<p class="bnext">No service on this day. Runs: '+esc(r.tables.map(t=>t.label).join('; '))+'.</p>':'';
      for(const t of tabs){
        o+='<p class="bnext">'+(live?(nx.length?'Next from Hamilton: <b>'+nx.slice(0,3).map(row=>t12(row[0])).join('</b>, <b>')+'</b>':'No more today. The last one left Hamilton at '+t12(t.rows[t.rows.length-1][0])+'.'):'First from Hamilton '+t12(t.rows[0][0])+', last '+t12(t.rows[t.rows.length-1][0])+'.')+'</p>'
          +'<div class="ftab"><table><thead><tr>'+t.cols.map(c=>'<th>'+esc(c)+'</th>').join('')+'</tr></thead><tbody>'+t.rows.map(row=>'<tr'+(live&&mins(row[0])<nowMin?' class="gone"':'')+'>'+row.map(v=>'<td>'+(v?t12(v):'')+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';
      }
      o+='</div>';
    }
    return o+'<p class="wsrc">'+esc(F.name)+' from the '+esc(F.publisher)+', in force from '+esc(longDay(F.effective))+', checked against <a href="'+esc(F.source)+'" target="_blank" rel="noopener" style="color:#2af0d9">the published brochure</a> on '+esc(longDay(F.checked))+'. Service can change on the day, so for anything that matters ring the Hamilton terminal on '+esc(F.phone)+'.</p>';
  }
  // Where to? The front of the tab works the way the big transit apps do: pick where you are leaving from and where
  // you are going, and it answers with the next departures and how long the ride is, and draws the ride on a map.
  // Each trip carries a stop pattern and a set of running times, so the time at any stop is the trip start plus the
  // minutes to that stop. A place can be a bus stop, a ferry dock or a place from Explore; a place stands for the
  // stops within a short walk of it, so both sides of the road count. Ferries come from the typed in schedule.
  const hasStops=(T.stops||[]).length&&(T.patterns||[]).length, atStop={};
  function stopTimes(d){
    if(atStop[d])return atStop[d];
    const on=new Set(days.find(x=>x.date===d).on), by={};
    T.routes.forEach(r=>r.groups.forEach(g=>g.trips.forEach(t=>{
      if(!on.has(t[0])||t[3]==null)return;
      const pat=T.patterns[t[3]], tim=T.timings[t[4]], st=mins(t[1]);
      for(let i=0;i<pat.length-1;i++)(by[pat[i]]=by[pat[i]]||[]).push([st+tim[i],r.short||'School',r.color,g.head||place(g.to)]);
    })));
    for(const k in by){const seen=new Set();by[k]=by[k].sort((a,b)=>a[0]-b[0]).filter(x=>{const key=x[0]+'|'+x[1]+'|'+x[3];return !seen.has(key)&&seen.add(key)})}
    return atStop[d]=by;
  }
  const clock=m=>{const h=Math.floor(m/60)%24, mm=m%60;return (h%12||12)+':'+(mm<10?'0':'')+mm+(h<12?'am':'pm')};
  const metres=(a,b,c,d)=>{const R=6371000,r=Math.PI/180,x=Math.sin((c-a)*r/2),y=Math.sin((d-b)*r/2),h=x*x+Math.cos(a*r)*Math.cos(c*r)*y*y;return 2*R*Math.asin(Math.sqrt(h))};
  const walkText=m=>m<60?'':(m<1000?Math.round(m/10)*10+' m walk':(m/1000).toFixed(1)+' km walk');
  const mapLive=location.hostname.endsWith('github.io')||location.hostname==='localhost'||location.hostname==='127.0.0.1'||location.protocol==='file:';
  const canFind=mapLive&&!!navigator.geolocation;
  const DOCKS=T.docks||[];
  // every place the two boxes can find
  const PL=[];
  if(hasStops)T.stops.forEach((s,i)=>{if(s[1]!=null&&!DOCKS.some(d=>d.name===s[0]))PL.push({n:place(s[0]),raw:s[0],s:'Bus stop',lat:s[1],lon:s[2],k:'stop',i:i})});
  DOCKS.forEach((d,i)=>PL.push({n:d.name,s:'Ferry dock',lat:d.lat,lon:d.lon,k:'dock',d:i}));
  (function(){let X={};try{X=JSON.parse(document.getElementById('explore-data').textContent)}catch(e){}
    const skip={wreck:1,triangle:1,art:1}, kinds=X.kinds||{};
    (X.sites||[]).forEach(s=>{if(!s.lat||!s.lon||skip[s.kind]||!hasStops)return;
      if(!T.stops.some(t=>t[1]!=null&&metres(s.lat,s.lon,t[1],t[2])<900))return;
      PL.push({n:s.name,s:(kinds[s.kind]||'Place')+', '+s.parish,lat:s.lat,lon:s.lon,k:'place'})})})();
  const stopsNear=p=>{const R=p.k==='stop'?170:450, out=[];
    T.stops.forEach((s,i)=>{if(s[1]==null)return;const m=metres(p.lat,p.lon,s[1],s[2]);if(m<=R)out.push([i,m])});
    if(!out.length){const all=T.stops.map((s,i)=>[i,s[1]==null?1e9:metres(p.lat,p.lon,s[1],s[2])]).sort((a,b)=>a[1]-b[1]).slice(0,2).filter(x=>x[1]<1500);return all}
    return out};
  const docksNear=p=>{const out={};DOCKS.forEach((d,i)=>{const m=metres(p.lat,p.lon,d.lat,d.lon);if(m<=(p.k==='dock'?60:600))out[i]=m});return out};
  // a ferry table column, such as "Leave Dockyard" or "Salt Kettle (Paget)", matched to its dock
  const dockOf=label=>{let k=String(label).replace('Leave ','').replace('Arrive ','');const b=k.indexOf(' (');if(b>0)k=k.slice(0,b);k=k.toLowerCase();
    for(let i=0;i<DOCKS.length;i++)if(DOCKS[i].name.toLowerCase().indexOf(k)===0)return i;return -1};
  // stops that are a few steps apart count as one place to change buses
  let CL=null;
  const clusters=()=>{if(CL)return CL;CL=[];for(let i=0;i<T.stops.length;i++){CL[i]=i;const a=T.stops[i];if(a[1]==null)continue;
    for(let j=0;j<i;j++){const b=T.stops[j];if(b[1]!=null&&Math.abs(a[1]-b[1])<0.001&&metres(a[1],a[2],b[1],b[2])<90){CL[i]=CL[j];break}}}return CL};
  let F0=null, T0=null, me=null, JL=[], jsel=0, jd=null;
  function journeys(d){
    const A=new Map(stopsNear(F0)), B=new Map(stopsNear(T0)), on=new Set(days.find(x=>x.date===d).on), out=[], seen=new Set();
    const leg=(r,g,pat,tim,st,i,j)=>({r:r,g:g,pat:pat,i:i,j:j,dep:st+tim[i],arr:st+tim[j]});
    const each=fn=>T.routes.forEach(r=>r.groups.forEach(g=>g.trips.forEach(t=>{if(!on.has(t[0])||t[3]==null)return;fn(r,g,t,T.patterns[t[3]],T.timings[t[4]],mins(t[1]))})));
    each((r,g,t,pat,tim,st)=>{let la=-1,best=null;
      for(let i=0;i<pat.length;i++){const inA=A.has(pat[i]);if(!inA&&B.has(pat[i])&&la>=0){if(!best||tim[i]-tim[la]<tim[best[1]]-tim[best[0]])best=[la,i]}if(inA)la=i}
      if(!best)return;const l=leg(r,g,pat,tim,st,best[0],best[1]), key=l.dep+'|'+l.arr+'|'+r.short;
      if(seen.has(key)||l.arr<=l.dep)return;seen.add(key);out.push({dep:l.dep,arr:l.arr,legs:[l],w0:A.get(pat[best[0]]),w1:B.get(pat[best[1]])})});
    // ferries: a row is one sailing, and a dock later in time on the same row can be reached from an earlier one
    const da=docksNear(F0), db=docksNear(T0);
    (F.routes||[]).forEach(r=>r.tables.filter(t=>t.days===dayType(d)).forEach(t=>{const cd=t.cols.map(dockOf);
      t.rows.forEach(row=>{let best=null;
        for(let i=0;i<cd.length;i++){if(!row[i]||da[cd[i]]==null||String(t.cols[i]).indexOf('Arrive')===0)continue;
          for(let j=0;j<cd.length;j++){if(j===i||j===0||!row[j]||db[cd[j]]==null||cd[j]===cd[i])continue;const a=mins(row[i]),b=mins(row[j]);if(b>a&&(!best||b-a<best[1]-best[0]))best=[a,b,cd[i],cd[j]]}}
        if(best)out.push({dep:best[0],arr:best[1],legs:[{ferry:true,r:r,a:DOCKS[best[2]],b:DOCKS[best[3]],dep:best[0],arr:best[1]}],w0:da[best[2]],w1:db[best[3]]})})}));
    if(!out.length){
      // no direct bus or ferry on this day: one change of bus. Ride from the start to any stop, then a second bus
      // that leaves that spot at least three minutes later and reaches the destination.
      const C=clusters(), first={};
      each((r,g,t,pat,tim,st)=>{let la=-1;for(let i=0;i<pat.length;i++){if(A.has(pat[i]))la=i;else if(la>=0)(first[C[pat[i]]]=first[C[pat[i]]]||[]).push([st+tim[i],st+tim[la],r,g,pat,tim,st,la,i])}});
      const cand=[];
      each((r,g,t,pat,tim,st)=>{let jb=-1;for(let i=1;i<pat.length;i++)if(B.has(pat[i])){jb=i;break}if(jb<1)return;let best=null,bk=-1;
        for(let k=0;k<jb;k++){if(A.has(pat[k])){best=null;break}const li=first[C[pat[k]]];if(!li)continue;const board=st+tim[k];
          for(let n=0;n<li.length;n++){const e=li[n];if(e[0]<=board-3&&board-e[0]<=45&&e[3]!==g&&(!best||e[1]>best[1])){best=e;bk=k}}}
        if(best)cand.push({dep:best[1],arr:st+tim[jb],legs:[leg(best[2],best[3],best[4],best[5],best[6],best[7],best[8]),leg(r,g,pat,tim,st,bk,jb)],w0:A.get(best[4][best[7]]),w1:B.get(pat[jb])})});
      cand.sort((a,b)=>a.arr-b.arr||b.dep-a.dep);let top=-1;cand.forEach(x=>{if(x.dep>top){top=x.dep;out.push(x)}});
    }
    // drop any ride that another one beats outright: leaving no earlier and arriving no later
    const keep=[];let top=-1;out.sort((a,b)=>a.arr-b.arr||b.dep-a.dep).forEach(x=>{if(x.dep>top){top=x.dep;keep.push(x)}});
    return keep.sort((a,b)=>a.dep-b.dep||a.arr-b.arr);
  }
  const badge=l=>l.ferry?'<span class="bnum sm" style="background:#'+esc(l.r.color||'01aeef')+'">Ferry</span>':'<span class="bnum sm" style="background:#'+esc(l.r.color||'2af0d9')+'">'+esc(l.r.short||'School')+'</span>';
  const sname=i=>place(T.stops[i][0]);
  function legHTML(l){
    if(l.ferry)return '<div class="jleg">'+badge(l)+'<span><b>'+clock(l.dep)+'</b> '+esc(l.r.name)+' from '+esc(l.a.name)+'. At '+esc(l.b.name)+' by <b>'+clock(l.arr)+'</b>.</span></div>';
    return '<div class="jleg">'+badge(l)+'<span><b>'+clock(l.dep)+'</b> from '+esc(sname(l.pat[l.i]))+', the bus to '+esc(l.g.head||place(l.g.to))+'. Get off at '+esc(sname(l.pat[l.j]))+' at <b>'+clock(l.arr)+'</b>, '+(l.j-l.i)+(l.j-l.i===1?' stop':' stops')+'.</span></div>';
  }
  function jHTML(x,k,liveDay,full){
    const wait=x.dep-nowMin, w=[walkText(x.w0||0),walkText(x.w1||0)];
    return '<div class="jrow'+(k===jsel?' on':'')+'" data-j="'+k+'" role="button" tabindex="0"><div class="jtop"><b>'+clock(x.dep)+'</b><span>to '+clock(x.arr)+'</span><i>'+(x.arr-x.dep)+' min</i>'+x.legs.map(badge).join('')+(liveDay&&wait>=0&&wait<=90?'<em>'+(wait<1?'now':'in '+wait+' min')+'</em>':'')+'</div>'
      +(full?x.legs.map(legHTML).join('')+(x.legs.length>1?'<p class="jnote">Change at '+esc(sname(x.legs[1].pat[x.legs[1].i]))+', '+(x.legs[1].dep-x.legs[0].arr)+' min to spare.</p>':'')
        +((w[0]||w[1])?'<p class="jnote">'+[w[0]?w[0]+' to the start':'',w[1]?w[1]+' at the far end':''].filter(Boolean).join(', ')+'.</p>':''):'')+'</div>';
  }
  function board(liveDay){
    // only a start is chosen: the next buses through the stops beside it
    const by=stopTimes(day), near=stopsNear(F0).sort((a,b)=>a[1]-b[1]), rows=[];
    near.forEach(n=>(by[n[0]]||[]).forEach(t=>{if(!liveDay||t[0]>=nowMin)rows.push([t[0],t[1],t[2],t[3],n[0]])}));
    rows.sort((a,b)=>a[0]-b[0]);
    const many=new Set(rows.map(r=>r[4])).size>1, row=t=>'<div class="bcall"><i>'+clock(t[0])+'</i><span class="bnum sm" style="background:#'+esc(t[2]||'2af0d9')+'">'+esc(t[1])+'</span><span>to '+esc(t[3])+(many?', from '+esc(sname(t[4])):'')+'</span></div>';
    return '<p class="jnote">Add where you are going to see the ride and how long it takes. Until then, these are the next buses from here.</p>'
      +(rows.length?rows.slice(0,6).map(row).join('')+(rows.length>6?'<details><summary>'+(rows.length-6)+' more '+(liveDay?'today':'that day')+'</summary>'+rows.slice(6).map(row).join('')+'</details>':''):'<p class="bfrom">No '+(liveDay?'more ':'')+'buses from here on this day.</p>');
  }
  function update(){
    const box=document.getElementById('jres'); if(!box)return;
    const liveDay=day===bdaDay; JL=[]; jsel=0;
    if(!F0&&!T0)box.innerHTML='<p class="jnote">Pick a start and an end. Type a stop, a beach, a fort or a ferry dock'+(mapLive?', or tap a stop on the map':'')+'.</p>';
    else if(F0&&!T0)box.innerHTML=hasStops?board(liveDay):'';
    else if(!F0)box.innerHTML='<p class="jnote">Now pick where you are leaving from.</p>';
    else{
      const all=journeys(day); JL=liveDay?all.filter(x=>x.dep>=nowMin):all;
      const D=days.find(x=>x.date===day);
      let o=D.old?'<p class="jnote">From an older timetable, so check before you travel.</p>':'';
      if(!all.length)o+='<p class="bfrom" style="font-size:14.5px">No bus or ferry links these two on '+(liveDay?'this day':esc(longDay(day)))+', even with one change. Try a stop on a main road nearby, or another day.</p>';
      else if(!JL.length)o+='<p class="bfrom" style="font-size:14.5px">No more today. The last one left at '+clock(all[all.length-1].dep)+'. Pick tomorrow above for the morning times.</p>';
      else{const fast=Math.min(...JL.map(x=>x.arr-x.dep));
        o+='<p class="jsum"><b>'+esc(F0.n)+'</b> to <b>'+esc(T0.n)+'</b>: about '+fast+' min'+(JL[0].legs.length>1?', with one change':'')+'. '+JL.length+(liveDay?' more today.':' that day.')+'</p>'
          +JL.slice(0,3).map((x,k)=>jHTML(x,k,liveDay,true)).join('')
          +(JL.length>3?'<details class="jmore"><summary>'+(JL.length-3)+' later</summary>'+JL.slice(3).map((x,k)=>jHTML(x,k+3,liveDay,false)).join('')+'</details>':'');}
      box.innerHTML=o;
    }
    draw();
  }
  // the two boxes: type and pick from the list under the box
  const kindRank={dock:0,place:1,stop:2};
  function suggest(q){
    q=q.trim().toLowerCase();
    if(q.length<2){const want=['central bus terminal','hamilton ferry terminal','royal naval dockyard','st. george','airport','horseshoe bay'], out=[];
      want.forEach(w=>{const p=PL.find(x=>(x.raw||x.n).toLowerCase().indexOf(w)===0)||PL.find(x=>x.n.toLowerCase().indexOf(w)>-1);if(p&&out.indexOf(p)<0)out.push(p)});return out}
    const hit=[];PL.forEach(p=>{const n=p.n.toLowerCase(), at=n.indexOf(q);if(at<0)return;hit.push([at===0?0:n.charAt(at-1)===' '?1:2,p])});
    return hit.sort((a,b)=>a[0]-b[0]||kindRank[a[1].k]-kindRank[b[1].k]||a[1].n.localeCompare(b[1].n)).slice(0,7).map(x=>x[1]);
  }
  let sugFor=null, sugList=[];
  function showSug(which){
    const inp=document.getElementById(which==='F'?'bq':'bto'), box=document.getElementById('jsug'+which), other=document.getElementById('jsug'+(which==='F'?'T':'F'));
    if(other)other.innerHTML=''; if(!inp||!box)return;
    sugFor=which; sugList=suggest(inp.value);
    box.innerHTML=sugList.length?(inp.value.trim().length<2?'<p class="jnote" style="margin:6px 0 2px">Popular</p>':'')+sugList.map((p,i)=>'<button type="button" data-s="'+i+'"><b>'+esc(p.n)+'</b><span>'+esc(p.s)+'</span></button>').join(''):'<p class="jnote">Nothing matches that. Stops are named after what they are beside, so try a road, a shop or a beach.</p>';
  }
  function setPlace(which,p){
    if(which==='F')F0=p;else T0=p;
    const inp=document.getElementById(which==='F'?'bq':'bto'); if(inp)inp.value=p?p.n:'';
    ['F','T'].forEach(w=>{const b=document.getElementById('jsug'+w);if(b)b.innerHTML=''});
    if(which==='F'&&p!==me){const nb=document.getElementById('bnear');if(nb){nb.setAttribute('aria-pressed','false');nb.textContent='Near me'}}
    update();
  }
  // The map (GitHub Pages copy only, like the Explore map). Every stop is a dot: tap one to start or end there.
  // The chosen ride is drawn along its stops in the colour of its route.
  let bmap=null, dots=null, ride=null;
  function draw(){
    if(!bmap)return; ride.clearLayers();
    const hint=document.getElementById('bmaphint'), x=JL[jsel], pts=[];
    const pin=(p,c,label)=>{L.circleMarker([p.lat,p.lon],{radius:10,color:'#ffffff',weight:3,fillColor:c,fillOpacity:1,interactive:false}).addTo(ride).bindTooltip(label,{permanent:true,direction:'top',offset:[0,-10],className:'xtip'});pts.push([p.lat,p.lon])};
    if(x)x.legs.forEach(l=>{
      if(l.ferry){const ll=[[l.a.lat,l.a.lon],[l.b.lat,l.b.lon]];L.polyline(ll,{color:'#'+(l.r.color||'01aeef'),weight:5,dashArray:'4 10',lineCap:'round'}).addTo(ride);ll.forEach(p=>pts.push(p));return}
      const ll=l.pat.slice(l.i,l.j+1).map(s=>[T.stops[s][1],T.stops[s][2]]).filter(p=>p[0]!=null);
      L.polyline(ll,{color:'#170f3a',weight:9,opacity:0.9}).addTo(ride);L.polyline(ll,{color:'#'+(l.r.color||'2af0d9'),weight:5}).addTo(ride);
      ll.forEach(p=>{L.circleMarker(p,{radius:3,color:'#170f3a',weight:1,fillColor:'#ffffff',fillOpacity:1,interactive:false}).addTo(ride);pts.push(p)})});
    if(F0)pin(F0,'#2af0d9','Start'); if(T0)pin(T0,'#ff4fa3','End');
    if(pts.length>1)bmap.fitBounds(pts,{padding:[36,36],maxZoom:16});else if(pts.length)bmap.setView(pts[0],15);
    if(hint)hint.textContent=x?'The ride, stop by stop':F0||T0?'Tap a stop to set the other end':'Tap a stop to start or end there';
  }
  function bootMap(){
    if(bmap||!window.L)return; const box=document.getElementById('bmap'); if(!box)return;
    bmap=L.map('bmap',{zoomControl:true,minZoom:10,maxZoom:18,maxBounds:[[31.85,-65.6],[32.8,-63.95]],maxBoundsViscosity:0.3,preferCanvas:true}).fitBounds([[32.245,-64.89],[32.395,-64.645]]);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; OpenStreetMap contributors'}).addTo(bmap);
    box.classList.add('xdark');
    dots=L.layerGroup().addTo(bmap); ride=L.layerGroup().addTo(bmap);
    PL.forEach((p,i)=>{if(p.k==='place')return;
      const m=L.circleMarker([p.lat,p.lon],p.k==='dock'?{radius:8,color:'#170f3a',weight:2,fillColor:'#01aeef',fillOpacity:1}:{radius:5,color:'#170f3a',weight:1,fillColor:'#ffc83d',fillOpacity:0.95});
      m.bindPopup('<b>'+esc(p.n)+'</b><br>'+esc(p.s)+'<div class="jpop"><button type="button" data-pf="'+i+'">Start here</button><button type="button" data-pt="'+i+'">End here</button></div>');m.addTo(dots)});
    setTimeout(()=>{bmap.invalidateSize();draw()},300);
  }
  function listHTML(){
    const D=days.find(x=>x.date===day), on=new Set(D.on), liveDay=day===bdaDay;
    let o='<details class="ball"><summary>Full timetable: every bus route and ferry</summary><p class="xlead" style="margin-top:10px">Bus times are when the bus leaves its first stop.</p>';
    if(D.old)o+='<div class="bold"><b>Check before you travel.</b> The official timetable feed has nothing for this day. These are the times from the last timetable it published for this day of the week, which ran until '+esc(longDay(D.old))+'.</div>';
    const reg=T.routes.filter(r=>r.short).map(r=>routeHTML(r,on,liveDay)).filter(Boolean), sch=T.routes.filter(r=>!r.short).map(r=>routeHTML(r,on,false)).filter(Boolean);
    o+='<h2 class="w">Buses</h2>';
    if((F.routes||[]).length)o+='<p style="margin:-4px 0 0"><button type="button" id="bjump" style="background:none;border:0;color:#2af0d9;font:inherit;font-weight:700;padding:8px 0;min-height:44px;cursor:pointer">Skip down to the ferries</button></p>';
    o+=reg.length?reg.join(''):'<div class="wcard"><p>No buses are listed for this day.</p></div>';
    if(sch.length)o+='<details><summary>School buses on this day ('+sch.length+' parishes)</summary>'+sch.join('')+'</details>';
    o+=ferryHTML(day,liveDay)||'<div class="wcard sea"><h3>Ferries</h3><p>No ferry schedule is saved in this build.</p></div>';
    return o+'</details><p class="wsrc">Bus times from the Department of Public Transportation timetable feed, read '+esc(T.read)+'. It is the planned timetable, not live positions, and it does not know about cancelled runs. Times along a route are the timetable&#39;s own estimates. Bus alerts are on the Shorelink site.</p>';
  }
  const dayChips=()=>days.map(d=>'<button type="button" data-d="'+d.date+'" aria-pressed="'+(d.date===day)+'">'+dayName(d.date)+'</button>').join('');
  function paint(){
    el.innerHTML='<h2 class="xtitle">Bus &amp; ferry</h2>'
      +'<div class="wcard jplan"><h3>Where to?</h3>'
      +'<div class="jfield"><label for="bq">From</label><input id="bq" type="search" autocomplete="off" placeholder="Stop, beach, fort or dock">'+(canFind?'<button type="button" id="bnear" aria-pressed="false">Near me</button>':'')+'</div><div class="jsug" id="jsugF"></div>'
      +'<div class="jfield"><label for="bto">To</label><input id="bto" type="search" autocomplete="off" placeholder="Where are you going?"><button type="button" id="bswap" aria-label="Swap start and end">Swap</button></div><div class="jsug" id="jsugT"></div>'
      +'<div class="xchips" id="bdays">'+dayChips()+'</div><div id="jres"></div></div>'
      +(mapLive&&hasStops?'<div class="xmapbox"><div id="bmap" role="application" aria-label="Map of bus stops and ferry docks"></div><span class="xmaphint" id="bmaphint">Loading the map...</span></div>':'')
      +'<div id="blist">'+listHTML()+'</div>';
    update();
  }
  el.addEventListener('input',e=>{const id=e.target.id; if(id!=='bq'&&id!=='bto')return; const which=id==='bq'?'F':'T', v=e.target.value.trim().toLowerCase();
    const exact=v?PL.filter(p=>p.n.toLowerCase()===v||(p.raw||'').toLowerCase()===v):[];
    if(exact.length===1){setPlace(which,exact[0]);return}
    if(which==='F')F0=null;else T0=null; showSug(which); update()});
  el.addEventListener('focusin',e=>{const id=e.target.id; if(id==='bq'&&!F0)showSug('F'); else if(id==='bto'&&!T0)showSug('T')});
  el.addEventListener('keydown',e=>{if(e.key!=='Enter')return;const r=e.target.closest('.jrow');if(r){r.click();return}if((e.target.id==='bq'||e.target.id==='bto')&&sugList.length){setPlace(e.target.id==='bq'?'F':'T',sugList[0]);e.target.blur()}});
  el.addEventListener('click',e=>{
    const s=e.target.closest('.jsug button[data-s]'); if(s&&sugFor&&sugList[+s.dataset.s]){setPlace(sugFor,sugList[+s.dataset.s]);return}
    const pf=e.target.closest('button[data-pf]'), pt=e.target.closest('button[data-pt]');
    if(pf||pt){if(bmap)bmap.closePopup();setPlace(pf?'F':'T',PL[+(pf||pt).dataset[pf?'pf':'pt']]);const c=el.querySelector('.jplan');if(c)c.scrollIntoView({block:'start',behavior:'smooth'});return}
    const jr=e.target.closest('.jrow'); if(jr&&JL[+jr.dataset.j]){jsel=+jr.dataset.j;el.querySelectorAll('.jrow').forEach(x=>x.classList.toggle('on',x===jr));draw();
      const mb=document.getElementById('bmap');if(mb&&bmap&&!jr.closest('.jmore'))mb.scrollIntoView({block:'nearest',behavior:'smooth'});return}
    if(e.target.closest('#bswap')){const a=F0,b=T0;F0=b;T0=a;const i1=document.getElementById('bq'),i2=document.getElementById('bto');if(i1)i1.value=F0?F0.n:'';if(i2)i2.value=T0?T0.n:'';
      const nb=document.getElementById('bnear');if(nb&&F0!==me){nb.setAttribute('aria-pressed','false');nb.textContent='Near me'}update();return}
    const b=e.target.closest('#bdays button[data-d]');
    if(b){day=b.dataset.d;document.getElementById('bdays').innerHTML=dayChips();document.getElementById('blist').innerHTML=listHTML();update();return}
    const nb=e.target.closest('#bnear');
    if(nb){ if(F0&&F0===me){me=null;setPlace('F',null);return}
      nb.textContent='Finding you';
      navigator.geolocation.getCurrentPosition(p=>{const la=p.coords.latitude,lo=p.coords.longitude;
          if(!(la>32.18&&la<32.46&&lo>-65.02&&lo<-64.52)){nb.textContent='Near me';document.getElementById('jsugF').innerHTML='<p class="jnote">You do not seem to be in Bermuda, so type a start instead.</p>';return}
          me={n:'My location',s:'',lat:la,lon:lo,k:'place'};setPlace('F',me);nb.setAttribute('aria-pressed','true');nb.textContent='Near me ✓'},
        ()=>{nb.textContent='Near me';document.getElementById('jsugF').innerHTML='<p class="jnote">Your location was not shared. Type a start instead.</p>'},{enableHighAccuracy:true,timeout:15000,maximumAge:60000});
      return}
    if(e.target.closest('#bjump')){const h=document.getElementById('bferry');if(h)h.scrollIntoView({block:'start'})}});
  paint();
  if(mapLive&&hasStops&&window.hubLeaflet){let asked=false;const wait=setInterval(()=>{if(bsSec.hidden)return;
    if(!asked){asked=true;window.hubLeaflet(bootMap,()=>{const h=document.getElementById('bmaphint');if(h)h.textContent='The map could not load. The planner above still works.'})}
    else if(bmap){bmap.invalidateSize();clearInterval(wait)}},400)}
  // Today: the next buses out of Hamilton, all routes together
  const tb=document.getElementById('td-bus'), D0=days[0];
  if(tb&&D0.date===bdaDay){
    const on=new Set(D0.on), list=[], fn=ferryNext(bdaDay,true);
    T.routes.filter(r=>r.short).forEach(r=>r.groups.forEach(g=>{if(g.from==='Central Bus Terminal')runsOn(g,on).forEach(t=>{if(mins(t[1])>=nowMin)list.push([mins(t[1]),t[1],r,g])})}));
    list.sort((a,b)=>a[0]-b[0]);
    tb.hidden=false;
    tb.innerHTML='<h3>Next buses from Hamilton</h3>'+(list.length?'<ul class="tlist">'+list.slice(0,5).map(x=>'<li><b>'+t12(x[1])+'</b><span>Route '+esc(x[2].short)+' to '+esc(x[3].head||x[3].to)+'</span></li>').join('')+'</ul>':'<p class="tmuted">No more buses leave the Hamilton terminal today in the timetable.</p>')
      +(D0.old?'<p class="tmuted">From an older timetable. Check before you travel.</p>':'')+(fn.length?'<p class="tmuted"><b>Next ferry:</b> '+t12(fn[0][1])+', '+esc(fn[0][2].name)+'</p>':(F.routes||[]).length?'<p class="tmuted">No more ferries from Hamilton today.</p>':'')+'<button type="button" data-go="transit">All routes and times</button>';
  }
})();
// ---- Sports tab. First group: wind sports (kite, wing foil, windsurf), worked out from the hourly wind forecast
// the morning run already saves. Each spot lists the wind directions it works in as a compass arc, read clockwise
// from the first bearing to the second. Directions and notes follow the Bermuda Kitesurfing community spot guide.
(function(){
  const el=document.getElementById('sp'); let W=null;
  try{W=JSON.parse(document.getElementById('weather-data').textContent)}catch(e){}
  if(!el||!W||!(W.hourly||[]).length)return;
  const esc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const pts16=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'], pt=d=>pts16[Math.round(d/22.5)%16];
  // knots, one scale for kite, wing foil and windsurf: too light below LIM[0], best from LIM[1] to LIM[2], too much
  // above LIM[3]. Rough figures for an average rider.
  const LIM=[10,15,25,32];
  const SPOTS=[
    ['Elbow Beach','Paget, south shore',45,225,'The biggest beach and the most wind directions. Deep water and heavy chop.','Swimmers in the warmer months.','Parking on the public access road, steps down to the sand.'],
    ['Horseshoe Bay','Southampton, south shore',135,180,'The wave spot. Shore break, best around mid to high tide.','Very little room, surfers when there is swell, crowds on cruise ship days.','Parking, showers and bathrooms.'],
    ['Somerset Long Bay','Sandys',292,23,'Flat with small chop. The friendliest spot for beginners.','Sea turtles, old glass on the beach, wind shadow if you launch from the grass.','Parking and plenty of grass to rig on.'],
    ['Daniel&#39;s Head, south side','Sandys',202,270,'Small chop with shallows you can stand in. Easier to launch at lower tides.','Turtles, and trees beside the launch.','Parking, rig on the grass, launch from the sand.'],
    ['Daniel&#39;s Head, north side','Sandys',315,45,'Small chop, close to the wreck of the Vixen.','Turtles, and trees beside the launch.','Parking, rig on the grass, launch from the sand.'],
    ['West Side Road','Sandys',225,315,'Small clean chop, shallow a long way out.','Debris on the beach, and the beach can disappear at high tide.','Very little parking, then a short walk between two houses.'],
    ['Grape Bay','Paget, south shore',67,203,'Deep water and heavy chop, much like Elbow.','Shallow reef at low tide.','No public parking.'],
    ['Shelly Bay','Hamilton Parish, north shore',235,275,'Onshore, with small clean waves. A small riding area.','Swimmers in the warmer months, the road right behind you, hard to launch at high tide.','Parking and restrooms.'],
    ['Cooper&#39;s Island and Clearwater','St David&#39;s',45,113,'Chop or flat water depending on where you ride.','Keep well away from the airport end. Swimmers in the warmer months.','Parking and bathrooms, then a walk to the far beaches.'],
    ['Fort St Catherine','St George&#39;s',67,113,'Mostly chop.','People on the beach, the old jetty, gusty in some directions.','Parking by the beach.'],
    ['Spanish Point','Pembroke',225,23,'Chop, with flat water behind Cobbler Island.','A very hard launch among rocks, trees and flagpoles. Experienced riders only.','Parking, rig on the grass.'],
    ['Blue Hole Park','Hamilton Parish',0,135,'Smaller chop than most. A favourite with wing foilers.','Wind shadows, rocks beside the launch, and a beach only at lower tides.','Roadside parking.']];
  const inArc=(d,a,b)=>a<=b?(d>=a&&d<=b):(d>=a||d<=b);
  const band=k=>k<LIM[0]?'low':k<LIM[1]?'ok':k<=LIM[2]?'prime':k<=LIM[3]?'strong':'over';
  const now=new Date(), bdaDay=now.toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'}), bdaHour=+now.toLocaleTimeString('en-GB',{timeZone:'Atlantic/Bermuda',hour:'2-digit',hour12:false}).slice(0,2);
  const dates=[...new Set(W.hourly.map(r=>r.t.slice(0,10)))].filter(d=>d>=bdaDay).slice(0,5);
  let day=dates[0];
  const hoursFor=d=>{const info=(W.days||[]).find(x=>x.date===d)||{}, up=info.sunrise?+info.sunrise.slice(0,2)+1:7, dn=info.sunset?+info.sunset.slice(0,2):18;
    return W.hourly.filter(r=>r.t.slice(0,10)===d&&r.dir!=null&&r.wind!=null).map(r=>({h:+r.t.slice(11,13),k:r.wind,dir:r.dir,rain:r.rain||0})).filter(r=>r.h>=up&&r.h<dn&&(d!==bdaDay||r.h>=bdaHour))};
  const hr=h=>(h%12||12)+(h<12?'am':'pm');
  const meanDir=rows=>{const sx=rows.reduce((t,r)=>t+Math.sin(r.dir*Math.PI/180),0), cx=rows.reduce((t,r)=>t+Math.cos(r.dir*Math.PI/180),0);return (Math.atan2(sx,cx)*180/Math.PI+360)%360};
  // the best window: the longest unbroken run of hours that are neither too light nor too strong
  function windowFor(rows){let best=[],cur=[];for(const r of rows){const b=band(r.k);if(b==='low'||b==='over'){if(cur.length>best.length)best=cur;cur=[]}else cur.push(r)}if(cur.length>best.length)best=cur;return best}
  const kiteSize=k=>k<12?'':k<16?'12 to 14 m':k<21?'10 to 12 m':k<27?'8 to 9 m':'7 m or smaller';
  function dial(a,b,wind,on){
    const P=(deg,r)=>[(24+r*Math.sin(deg*Math.PI/180)).toFixed(1),(24-r*Math.cos(deg*Math.PI/180)).toFixed(1)], span=(b-a+360)%360, p1=P(a,18), p2=P(b,18), w=P(wind,18);
    return '<svg width="48" height="48" viewBox="0 0 48 48" role="img" aria-label="Works in winds from '+pt(a)+' round to '+pt(b)+'"><circle cx="24" cy="24" r="18" fill="none" stroke="#4b2d8a" stroke-width="5"/><path d="M'+p1[0]+' '+p1[1]+' A18 18 0 '+(span>180?1:0)+' 1 '+p2[0]+' '+p2[1]+'" fill="none" stroke="#2af0d9" stroke-width="5" stroke-linecap="round"/><text x="24" y="10" text-anchor="middle" font-size="7" font-weight="800" fill="#cdbbea">N</text><circle cx="'+w[0]+'" cy="'+w[1]+'" r="5" fill="'+(on?'#ff4fa3':'#8f7cbd')+'" stroke="#170f3a" stroke-width="1.5"/></svg>';
  }
  const spotRow=(s,wind,on)=>'<div class="sspot">'+dial(s[2],s[3],wind,on)+'<div><h4>'+s[0]+'</h4><p>'+s[1]+'. Works in winds from '+pt(s[2])+' round to '+pt(s[3])+'.</p><p><b>Water:</b> '+s[4]+'</p><p><b>Watch for:</b> '+s[5]+'</p><p><b>Getting in:</b> '+s[6]+'</p></div></div>';
  let todayCall=null;
  function paint(){
    const rows=hoursFor(day), win=windowFor(rows);
    const dayName=d=>d===bdaDay?'Today':new Date(d+'T12:00:00Z').toLocaleDateString('en-GB',{weekday:'short',day:'numeric',timeZone:'UTC'});
    let o='<h2 class="xtitle">Wind sports</h2><p class="xlead">Kite, wing foil and windsurf. When it is on, how strong, and which beach works in that wind.</p>';
    if(day===bdaDay&&(W.warnings||[]).length)o+='<div class="swarn">'+W.warnings.map(x=>esc(x.title)+(x.valid?': '+esc(x.valid):'')).join('. ')+'. Read the marine forecast before you rig.</div>';
    o+='<div class="xchips" id="sdays">'+dates.map(d=>'<button type="button" data-d="'+d+'" aria-pressed="'+(d===day)+'">'+dayName(d)+'</button>').join('')+'</div>';
    let dir=null;
    if(!rows.length){o+='<div class="wcard"><p class="sbig skip">No daylight left in this forecast.</p><p class="wsyn">Pick another day.</p></div>'}
    else{
      const hi=Math.round(Math.max(...rows.map(r=>r.k))), lo=Math.round(Math.min(...rows.map(r=>r.k)));
      let head, cls, sub;
      if(win.length>=2){const a=Math.round(Math.min(...win.map(r=>r.k))), b=Math.round(Math.max(...win.map(r=>r.k))), avg=win.reduce((t,r)=>t+r.k,0)/win.length; dir=meanDir(win);
        const prime=win.filter(r=>band(r.k)==='prime').length, strong=win.filter(r=>band(r.k)==='strong').length;
        cls=prime>=2?'go':'maybe'; head=(prime>=2?'It is on: ':strong>win.length/2?'Strong, for confident riders: ':'Light, a foil day: ')+hr(win[0].h)+' to '+hr(win[win.length-1].h+1);
        sub='Wind from the '+pt(dir)+', '+(a===b?b:a+' to '+b)+' kt.'+(kiteSize(avg)?' Roughly a '+kiteSize(avg)+' kite for an average weight rider.':' Enough for a wing or kite foil, light for a twin tip.')+(Math.max(...win.map(r=>r.rain))>=50?' Showers likely, and the wind gusts harder in them.':'');}
      else if(lo>LIM[3]){cls='skip';head='Too much wind';sub=lo+' to '+hi+' kt all day. More than most riders want.';dir=meanDir(rows)}
      else{cls='skip';head='Not enough wind';sub='Peaks at '+hi+' kt. You want about '+LIM[0]+' kt or more, even on a foil.';dir=meanDir(rows)}
      if(day===bdaDay)todayCall=[head,sub];
      o+='<div class="wcard"><p class="sbig '+cls+'">'+head+'</p><p class="wsyn">'+sub+'</p><div class="shours">'+rows.map(r=>'<div class="shr '+band(r.k)+'"><span>'+hr(r.h)+'</span><b>'+Math.round(r.k)+'</b><i style="transform:rotate('+((r.dir+180)%360)+'deg)" title="From the '+pt(r.dir)+'">↑</i><span>'+pt(r.dir)+'</span></div>').join('')+'</div>'
        +'<div class="skey"><span><i style="background:#2e1a66"></i>Too light</span><span><i style="background:#16356b"></i>Light</span><span><i style="background:#2af0d9"></i>Best</span><span><i style="background:#ff4fa3"></i>Strong</span><span><i style="background:#7a1030"></i>Too much</span></div>'
        +'<p class="wsrc">Knots, from this morning&#39;s forecast. Arrows show where the wind is blowing to. This is a forecast, not a live reading: gusts and lulls at the beach will differ.</p></div>';
      const good=SPOTS.filter(s=>inArc(dir,s[2],s[3])), rest=SPOTS.filter(s=>!inArc(dir,s[2],s[3]));
      o+='<div class="wcard"><h3>Where it works when the wind is '+pt(dir)+'</h3>'+(good.length?good.map(s=>spotRow(s,dir,true)).join(''):'<p class="wsyn">No spot on the list is known to work in this direction.</p>')
        +(rest.length?'<details><summary>The other '+rest.length+' spots</summary>'+rest.map(s=>spotRow(s,dir,false)).join('')+'</details>':'')+'</div>';
    }
    const td=(W.tides||[]).find(x=>x.date===day), info=(W.days||[]).find(x=>x.date===day)||{};
    o+='<div class="wcard"><h3>Before you go</h3><ul>'
      +(td&&(td.events||[]).length?'<li>Tides: '+td.events.map(e=>esc(e.kind)+' '+esc(e.time)).join(', ')+'. Several spots launch more easily at lower tides.</li>':'')
      +(W.climate&&W.climate.sea_surface?'<li>Sea temperature '+esc(W.climate.sea_surface)+'.</li>':'')
      +(info.sunset?'<li>Sunset '+esc(info.sunset)+'. Be off the water before it.</li>':'')
      +'<li>Never ride alone, and tell someone where you are going.</li><li>Give swimmers and beachgoers a wide berth. Access to these beaches depends on it.</li><li>If in doubt, do not go out.</li></ul>'
      +'<p class="wsrc">Spot directions and notes follow the <a href="https://www.bermudakitesurfing.com/spotguide" target="_blank" rel="noopener" style="color:#2af0d9">Bermuda Kitesurfing spot guide</a>, written by local riders. Wind limits and kite sizes are rough figures for an average rider: your weight, board and skill change them.</p></div>';
    el.innerHTML=o;
  }
  el.addEventListener('click',e=>{const b=e.target.closest('button[data-d]');if(b){day=b.dataset.d;paint()}});
  paint();
  const tw=document.getElementById('td-wind'); if(tw&&todayCall){tw.hidden=false;tw.innerHTML='<h3>Wind sports</h3><p><b>'+esc(todayCall[0])+'</b></p><p class="tmuted">'+esc(todayCall[1])+'</p><button type="button" data-go="sports">Hour by hour and where it works</button>';}
})();

// ---- Sports tab switch. Wind sports is always there. Each other sport turns its own button on (hubSportOn) once its
// data has loaded, so a sport with no data never shows an empty view. hubShowSport flips the view and, when asked,
// puts the sport in the page address so a link can open it directly.
(function(){
  const sw=document.getElementById('spsw'); if(!sw)return;
  const ids={wind:'sp',pb:'pb',yoga:'yg',snorkel:'snk',scuba:'scu'}, tags={wind:'sports',pb:'pickleball',yoga:'yoga',snorkel:'snorkel',scuba:'scuba'}, on={wind:true};
  window.hubSport=window.hubSport||'wind';
  window.hubShowSport=function(which,setHash){ if(!on[which])which='wind'; window.hubSport=which;
    Object.keys(ids).forEach(k=>{const e=document.getElementById(ids[k]);if(e)e.hidden=k!==which});
    sw.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.s===which?'true':'false'));
    if(setHash)location.hash=tags[which]};
  window.hubSportOn=function(which){ on[which]=true; const b=sw.querySelector('button[data-s='+which+']'); if(b)b.hidden=false; sw.hidden=false;
    if(window.hubSport===which)window.hubShowSport(which,false)};
  sw.addEventListener('click',e=>{const b=e.target.closest('button[data-s]');if(b)window.hubShowSport(b.dataset.s,true)});
})();

// ---- Sports tab, second group: pickleball. Where to play, the regular drop in sessions, what is coming up, and a
// call on outdoor play worked out from the same hourly forecast as wind sports. The venues, sessions and events
// are kept by hand in events/data/pickleball.json (pickleball-data), read from the Pickleball Association of
// Bermuda website. The switch at the top of the tab is the shared code just above.
(function(){
  const el=document.getElementById('pb'); if(!el||!window.hubSportOn)return;
  let P={}, W={};
  try{P=JSON.parse(document.getElementById('pickleball-data').textContent)}catch(e){}
  try{W=JSON.parse(document.getElementById('weather-data').textContent)}catch(e){}
  if(!(P.venues||[]).length)return;
  const esc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const now=new Date(), bdaDay=now.toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'}), bdaHour=+now.toLocaleTimeString('en-GB',{timeZone:'Atlantic/Bermuda',hour:'2-digit',hour12:false}).slice(0,2);
  const hr=h=>(h%12||12)+(h<12?'am':'pm'), t12=t=>{const h=+t.slice(0,2), m=t.slice(3,5);return (h%12||12)+(m==='00'?'':':'+m)+(h<12?'am':'pm')};
  const addDays=(d,n)=>{const x=new Date(d+'T12:00:00Z');x.setUTCDate(x.getUTCDate()+n);return x.toISOString().slice(0,10)};
  const dow=d=>new Date(d+'T12:00:00Z').getUTCDay();
  const longDay=d=>new Date(d+'T12:00:00Z').toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'short',timeZone:'UTC'});
  const shortDay=d=>d===bdaDay?'Today':new Date(d+'T12:00:00Z').toLocaleDateString('en-GB',{weekday:'short',day:'numeric',timeZone:'UTC'});
  // Outdoor play, hour by hour from 7am to 9pm. Knots: comfortable under CALM, playable up to BREEZY, and above
  // that the ball goes where the wind wants. An hour counts as wet when rain is likely or already falling.
  const CALM=10, BREEZY=15;
  const kind=r=>(r.rain>=70||r.mm>=0.5)?'wet':r.k<CALM?'good':r.k<=BREEZY?'breezy':'windy';
  const cls={good:'prime',breezy:'ok',windy:'strong',wet:'over'};
  const dates=[...new Set((W.hourly||[]).map(r=>r.t.slice(0,10)))].filter(d=>d>=bdaDay).slice(0,5);
  let day=dates[0]||bdaDay, filt='all', who='all';
  const hoursFor=d=>(W.hourly||[]).filter(r=>r.t.slice(0,10)===d&&r.wind!=null).map(r=>({h:+r.t.slice(11,13),k:r.wind,rain:r.rain||0,mm:r.mm||0})).filter(r=>r.h>=7&&r.h<21&&(d!==bdaDay||r.h>=bdaHour));
  function run(rows,ok){let best=[],cur=[];for(const r of rows){if(ok(kind(r)))cur.push(r);else{if(cur.length>best.length)best=cur;cur=[]}}if(cur.length>best.length)best=cur;return best}
  const indoor=(P.venues||[]).filter(v=>v.indoor).map(v=>v.name);
  function callFor(d){
    const rows=hoursFor(d); if(!rows.length)return null;
    const lo=Math.round(Math.min(...rows.map(r=>r.k))), hi=Math.round(Math.max(...rows.map(r=>r.k))), span=w=>hr(w[0].h)+' to '+hr(w[w.length-1].h+1);
    const good=run(rows,k=>k==='good'), fair=run(rows,k=>k==='good'||k==='breezy'), wet=rows.filter(r=>kind(r)==='wet').length;
    const inside=indoor.length?' '+indoor.join(' and ')+(indoor.length>1?' are':' is')+' indoors.':'';
    if(good.length>=2)return {rows:rows,cls:'go',head:'Good for outdoor play: '+span(good),sub:'Light wind, '+Math.round(Math.min(...good.map(r=>r.k)))+' to '+Math.round(Math.max(...good.map(r=>r.k)))+' kt.'+(wet?' Showers at other times of the day.':'')};
    if(fair.length>=2)return {rows:rows,cls:'maybe',head:'Breezy but playable: '+span(fair),sub:'Wind '+Math.round(Math.min(...fair.map(r=>r.k)))+' to '+Math.round(Math.max(...fair.map(r=>r.k)))+' kt. Expect the ball to drift: lobs and soft dinks suffer most.'+inside};
    if(wet>rows.length/2)return {rows:rows,cls:'skip',head:'A wet one: play indoors',sub:'Showers are likely for most of the day, and outdoor courts are slippery when wet.'+inside};
    return {rows:rows,cls:'skip',head:'Too windy outside: play indoors',sub:'Wind '+(lo===hi?hi:lo+' to '+hi)+' kt '+(d===bdaDay?'for the rest of the day':'all day')+'. The ball will go where the wind wants.'+inside};
  }
  const sessionsOn=(d,all)=>(P.sessions||[]).filter(s=>(all||who==='all'||s.venue===who)&&s.day===dow(d)&&(d!==bdaDay||+s.end.slice(0,2)>bdaHour)).sort((a,b)=>a.start<b.start?-1:1);
  const tag=v=>(v.indoor?'<span class="pbtag in">Indoor</span>':'')+(v.access==='public'?'<span class="pbtag pub">Public</span>':'<span class="pbtag">Members or guests</span>');
  const venueRow=v=>'<div class="pbv"><h4>'+esc(v.name)+tag(v)+'</h4><p>'+esc(v.parish)+(v.courts?', '+v.courts+(v.courts===1?' court':' courts'):'')+(v.hours?'. '+esc(v.hours):'')+'.</p>'
    +(v.note?'<p>'+esc(v.note)+'</p>':'')+(v.fee?'<p><b>Cost:</b> '+esc(v.fee)+'</p>':'')+(v.book?'<p><b>Booking:</b> '+esc(v.book)+'</p>':'')
    +'<div class="wlinks">'+(v.phone?'<a href="tel:+1'+v.phone.replace(/[^0-9]/g,'')+'">'+esc(v.phone)+'</a>':'')+(v.site?'<a href="'+esc(v.site)+'" target="_blank" rel="noopener">Website</a>':'')
    +'<a href="https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(v.name+', '+v.address+', Bermuda')+'" target="_blank" rel="noopener">Map</a></div></div>';
  function paint(){
    const A=P.pab||{};
    let o='<h2 class="xtitle">Pickleball</h2><p class="xlead">Where to play, when the drop in games are, and whether the wind will let you play outside.</p>';
    if(P.stale)o+='<div class="swarn">These details were last checked on '+esc(P.asof)+' and may be out of date. Confirm with the venue.</div>';
    // one button per venue plus All: picking one narrows the sessions, the events and the details to that place
    const short=n=>n.replace(' Tennis and Pickleball Club','').replace(' and Tennis Club','').replace(' Tennis Stadium','').replace(' Squash and Wellness','').replace(' at Newstead','').replace(' Resort','').replace(' Bermuda','');
    const one=who==='all'?null:(P.venues||[]).find(v=>v.name===who);
    o+='<div class="xchips" id="pbwho" style="margin-bottom:8px">'+[['all','All venues']].concat(P.venues.map(v=>[v.name,v.short||short(v.name)])).map(x=>'<button type="button" data-w="'+esc(x[0])+'" aria-pressed="'+(x[0]===who)+'">'+esc(x[1])+'</button>').join('')+'</div>';
    if(one)o+='<div class="wcard">'+venueRow(one)+'</div>';
    if(dates.length&&!(one&&one.indoor)){
      const c=callFor(day);
      o+='<div class="xchips" id="pbdays">'+dates.map(d=>'<button type="button" data-d="'+d+'" aria-pressed="'+(d===day)+'">'+shortDay(d)+'</button>').join('')+'</div>';
      if(!c)o+='<div class="wcard"><p class="sbig skip">No playing hours left in this forecast.</p><p class="wsyn">Pick another day.</p></div>';
      else{const info=(W.days||[]).find(x=>x.date===day)||{};
        o+='<div class="wcard"><p class="sbig '+c.cls+'">'+c.head+'</p><p class="wsyn">'+esc(c.sub)+'</p><div class="shours">'+c.rows.map(r=>'<div class="shr '+cls[kind(r)]+'"><span>'+hr(r.h)+'</span><b>'+Math.round(r.k)+'</b><span>kt</span><span>'+Math.round(r.rain)+'%</span></div>').join('')+'</div>'
          +'<div class="skey"><span><i style="background:#2af0d9"></i>Good</span><span><i style="background:#16356b"></i>Breezy</span><span><i style="background:#ff4fa3"></i>Windy</span><span><i style="background:#7a1030"></i>Wet</span></div>'
          +'<p class="wsrc">Wind in knots and the chance of rain, from this morning&#39;s forecast. A rough guide: under '+CALM+' kt is comfortable, up to '+BREEZY+' kt is playable, more than that is hard work.'+(info.sunset?' Sunset is at '+esc(info.sunset)+': after that you need a lit court.':'')+'</p></div>';}
    }
    const week=[]; for(let i=0;i<8;i++){const d=addDays(bdaDay,i), ss=sessionsOn(d); if(ss.length)week.push([d,ss])}
    o+='<div class="wcard"><h3>Drop in this week</h3>'+(week.length?week.map(x=>'<div class="pbd"><b>'+(x[0]===bdaDay?'Today, ':'')+esc(longDay(x[0]))+'</b><ul class="tlist">'+x[1].map(s=>'<li><b>'+t12(s.start)+' to '+t12(s.end)+': '+esc(s.name)+'</b><span>'+esc(s.venue)+'. '+esc(s.level)+'. '+esc(s.cost)+'. Run by '+esc(s.by)+'.</span></li>').join('')+'</ul></div>').join(''):'<p class="wsyn">'+(one?'No regular drop in sessions are listed here. Ring the venue to book a court.':'No regular sessions listed.')+'</p>')
      +(one&&one.name!=='WER Joell Tennis Stadium'?'':(A.mixers?'<p class="pbnote"><b>Association mixers:</b> '+esc(A.mixers)+'</p>':'')+(A.chat?'<p class="pbnote">'+esc(A.chat)+'</p>':''))
      +'<p class="wsrc">Regular weekly sessions as the association lists them. They move for weather, holidays and tournaments, so check before you travel.</p></div>';
    const ev=(P.events||[]).filter(e=>e.end>=bdaDay&&(!one||e.venue===who)).sort((a,b)=>a.start<b.start?-1:1);
    if(ev.length)o+='<div class="wcard"><h3>Coming up</h3>'+ev.map(e=>'<div class="pbv"><h4>'+esc(e.name)+(e.start<=bdaDay?'<span class="pbtag pub">On now</span>':'')+'</h4><p>'+esc(longDay(e.start))+' to '+esc(longDay(e.end))+', '+esc(e.venue)+'.</p>'+(e.note?'<p>'+esc(e.note)+'</p>':'')+(e.url?'<div class="wlinks"><a href="'+esc(e.url)+'" target="_blank" rel="noopener">Details</a></div>':'')+'</div>').join('')+'</div>';
    const vs=(P.venues||[]).filter(v=>filt==='all'||(filt==='public'&&v.access==='public')||(filt==='indoor'&&v.indoor)||(filt==='members'&&v.access!=='public'));
    if(!one)o+='<div class="wcard"><h3>Where to play</h3><div class="xchips" id="pbfilt" style="margin:6px 0 4px">'+[['all','All '+P.venues.length],['public','Public'],['indoor','Indoor'],['members','Members and resorts']].map(x=>'<button type="button" data-f="'+x[0]+'" aria-pressed="'+(x[0]===filt)+'">'+x[1]+'</button>').join('')+'</div>'+vs.map(venueRow).join('')+'</div>';
    if(!one)o+='<div class="wcard"><h3>New to it, or want to get better</h3>'
      +(A.membership?'<p class="pbnote"><b>Join the association:</b> '+esc(A.membership)+'</p>':'')
      +((P.coaches||[]).length?'<p class="pbnote"><b>Lessons and clinics:</b></p><ul class="tlist">'+P.coaches.map(c=>'<li><b>'+esc(c.name)+'</b><span>'+esc(c.what)+'</span></li>').join('')+'</ul>':'')
      +(A.league?'<p class="pbnote"><b>League:</b> '+esc(A.league)+'</p>':'')
      +'<div class="wlinks" style="margin-top:10px">'+(A.training?'<a href="'+esc(A.training)+'" target="_blank" rel="noopener">Coach contacts</a>':'')+(A.join?'<a href="'+esc(A.join)+'" target="_blank" rel="noopener">Membership</a>':'')+(A.rules?'<a href="'+esc(A.rules)+'" target="_blank" rel="noopener">Rules and ratings</a>':'')+(A.league_url?'<a href="'+esc(A.league_url)+'" target="_blank" rel="noopener">League</a>':'')+(A.instagram?'<a href="'+esc(A.instagram)+'" target="_blank" rel="noopener">Instagram</a>':'')+'</div>'
      +'<p class="wsrc">Venues, sessions and prices are from the <a href="'+esc((P.source||{}).url||'')+'" target="_blank" rel="noopener" style="color:#2af0d9">'+esc((P.source||{}).name||'')+'</a> website, read on '+esc(P.asof)+'. '+(A.email?'Corrections go to them at '+esc(A.email)+'.':'')+'</p></div>';
    el.innerHTML=o;
  }
  el.addEventListener('click',e=>{const b=e.target.closest('button[data-d]'), f=e.target.closest('button[data-f]'), w=e.target.closest('#pbwho button[data-w]');if(w){who=w.dataset.w;paint()}else if(b){day=b.dataset.d;paint()}else if(f){filt=f.dataset.f;paint()}});
  paint();
  window.hubSportOn('pb');
  // Today: one card with the outdoor call and what is left of today&#39;s sessions
  const tp=document.getElementById('td-pb'), c0=dates.length?callFor(bdaDay):null, s0=sessionsOn(bdaDay,true);
  if(tp&&(c0||s0.length)){tp.hidden=false;
    tp.innerHTML='<h3>Pickleball</h3>'+(c0?'<p><b>'+esc(c0.head)+'</b></p>':'')+(s0.length?'<p class="tmuted">'+s0.map(s=>t12(s.start)+' '+esc(s.name).toLowerCase()+' at '+esc(s.venue)).join('. ')+'.</p>':(c0?'<p class="tmuted">'+esc(c0.sub)+'</p>':''))+'<button type="button" data-go="sports" id="td-pbgo">Courts, sessions and the hour by hour</button>';
    document.getElementById('td-pbgo').addEventListener('click',()=>{window.hubSport='pb';window.hubShowSport('pb',false)});}
})();

// ---- Sports tab, third group: yoga. The classes on each day across the studios and hotels whose timetables could
// be read, special sessions coming up, and a directory of every studio and hotel with a link to its own schedule.
// Kept by hand in events/data/yoga.json (yoga-data), read from each studio&#39;s own website.
(function(){
  const el=document.getElementById('yg'); if(!el||!window.hubSportOn)return;
  let Y={}; try{Y=JSON.parse(document.getElementById('yoga-data').textContent)}catch(e){}
  if(!(Y.places||[]).length)return;
  const esc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const now=new Date(), bdaDay=now.toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'}), bdaTime=now.toLocaleTimeString('en-GB',{timeZone:'Atlantic/Bermuda',hour:'2-digit',minute:'2-digit',hour12:false}).slice(0,5);
  const t12=t=>{const h=+t.slice(0,2), m=t.slice(3,5);return (h%12||12)+(m==='00'?'':':'+m)+(h<12?'am':'pm')};
  const addDays=(d,n)=>{const x=new Date(d+'T12:00:00Z');x.setUTCDate(x.getUTCDate()+n);return x.toISOString().slice(0,10)};
  const dow=d=>new Date(d+'T12:00:00Z').getUTCDay();
  const longDay=d=>new Date(d+'T12:00:00Z').toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'short',timeZone:'UTC'});
  const shortDay=d=>d===bdaDay?'Today':new Date(d+'T12:00:00Z').toLocaleDateString('en-GB',{weekday:'short',day:'numeric',timeZone:'UTC'});
  const PL={}; Y.places.forEach(p=>{PL[p.id]=p});
  const dates=[]; for(let i=0;i<7;i++)dates.push(addDays(bdaDay,i));
  let day=bdaDay, filt='all', who='all';
  // everything on a given date: the weekly classes for that weekday, plus any dated special session
  const onDay=d=>(Y.sessions||[]).filter(s=>s.day===dow(d)&&(!s.until||d<=s.until)).map(s=>Object.assign({},s))
    .concat((Y.events||[]).filter(e=>e.date===d).map(e=>Object.assign({special:true},e)))
    .concat((Y.live||[]).filter(e=>e.date===d).map(e=>{const p=PL[e.p]||{}, v=(e.venue||'').toLowerCase(), n=(p.name||'').toLowerCase();return Object.assign({},e,{note:e.venue&&v&&n.indexOf(v)<0&&v.indexOf(n.split(' ')[0])<0?'At '+e.venue:''})}))
    .filter(s=>d!==bdaDay||s.end>bdaTime).sort((a,b)=>a.start<b.start?-1:a.start>b.start?1:0);
  const row=s=>{const p=PL[s.p]||{};return '<li><b>'+t12(s.start)+' to '+t12(s.end)+': '+esc(s.name)+(s.special?'<span class="pbtag in">Special</span>':'')+'</b><span>'+esc(p.name||'')+', '+esc(p.area||'')+(s.with?'. With '+esc(s.with):'')+(s.cost?'. '+esc(s.cost):'')+(s.note?'. '+esc(s.note):'')+'.</span></li>'};
  const placeRow=p=>'<div class="pbv"><h4>'+esc(p.name)+(p.kind==='hotel'?'<span class="pbtag in">Hotel</span>':'<span class="pbtag pub">Studio</span>')+(p.full?'':'<span class="pbtag">See their site</span>')+'</h4><p>'+esc(p.address)+'.</p>'
    +(p.note?'<p>'+esc(p.note)+'</p>':'')+(p.price?'<p><b>Cost:</b> '+esc(p.price)+'</p>':'')+(p.book?'<p><b>Booking:</b> '+esc(p.book)+'</p>':'')
    +'<div class="wlinks">'+(p.site?'<a href="'+esc(p.site)+'" target="_blank" rel="noopener">'+(p.full?'Website':'Their schedule')+'</a>':'')+(p.insta?'<a href="'+esc(p.insta)+'" target="_blank" rel="noopener">Instagram</a>':'')
    +'<a href="https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(p.name+', '+p.address+', Bermuda')+'" target="_blank" rel="noopener">Map</a></div></div>';
  function paint(){
    const list=onDay(day).filter(s=>who==='all'||s.p===who), one=PL[who], listed=Y.places.filter(p=>p.full).map(p=>p.name), unlisted=Y.places.filter(p=>!p.full).map(p=>p.name);
    let o='<h2 class="xtitle">Yoga</h2><p class="xlead">Classes across the island by day, special sessions coming up, and every studio and hotel with a link to its own schedule.</p>';
    if(Y.stale)o+='<div class="swarn">These details were last checked on '+esc(Y.asof)+' and may be out of date. Confirm with the studio.</div>';
    o+='<div class="xchips" id="ygwho" style="margin-bottom:8px">'+[['all','All studios']].concat(Y.places.map(p=>[p.id,p.short||p.name])).map(x=>'<button type="button" data-w="'+esc(x[0])+'" aria-pressed="'+(x[0]===who)+'">'+esc(x[1])+'</button>').join('')+'</div>';
    o+='<div class="xchips" id="ygdays">'+dates.map(d=>'<button type="button" data-d="'+d+'" aria-pressed="'+(d===day)+'">'+shortDay(d)+'</button>').join('')+'</div>';
    o+='<div class="wcard"><h3>'+(one?esc(one.name)+': ':'')+(day===bdaDay?(one?'still to come today':'Still to come today'):esc(longDay(day)))+'</h3>'+(one&&!one.full?'<p class="wsyn">'+esc(one.name)+' publishes no fixed timetable. Use the link to its own schedule below.</p>':list.length?'<ul class="tlist">'+list.map(row).join('')+'</ul>':'<p class="wsyn">'+(day===bdaDay?'Nothing more today in the timetables listed here.':'Nothing in the timetables listed here.')+'</p>')
      +(one?'':'<p class="wsrc">Timetables listed: '+esc(listed.join(', '))+'.'+(unlisted.length?' Not listed, because they publish no fixed timetable: '+esc(unlisted.join(', '))+'. Use the links below for those.':'')+(Y.live_read?' Classes from the studios&#39; booking service were read on '+esc(Y.live_read)+' and cover the next week only.':'')+' Classes move for holidays and teachers&#39; leave, so check before you travel.</p>')+'</div>';
    const ev=(Y.events||[]).filter(e=>e.date>=bdaDay&&(who==='all'||e.p===who)).sort((a,b)=>a.date<b.date?-1:1).slice(0,8);
    if(ev.length)o+='<div class="wcard"><h3>Special sessions coming up</h3><ul class="tlist">'+ev.map(e=>{const p=PL[e.p]||{};return '<li><b>'+esc(longDay(e.date))+', '+t12(e.start)+': '+esc(e.name)+'</b><span>'+esc(p.name||'')+', '+esc(p.area||'')+(e.cost?'. '+esc(e.cost):'')+'.</span></li>'}).join('')+'</ul>'+(Y.monthly?'<p class="pbnote">'+esc(Y.monthly)+'</p>':'')+'</div>';
    const ps=one?[one]:Y.places.filter(p=>filt==='all'||p.kind===filt);
    o+='<div class="wcard"><h3>'+(one?'About '+esc(one.name):'Studios and hotels')+'</h3><div class="xchips" id="ygfilt" style="margin:6px 0 4px;'+(one?'display:none':'')+'">'+[['all','All '+Y.places.length],['studio','Studios'],['hotel','Hotels']].map(x=>'<button type="button" data-f="'+x[0]+'" aria-pressed="'+(x[0]===filt)+'">'+x[1]+'</button>').join('')+'</div>'+ps.map(placeRow).join('')
      +'<p class="wsrc">Read from each studio&#39;s or hotel&#39;s own website on '+esc(Y.asof)+'. Facebook and Instagram pages were not read.</p></div>';
    el.innerHTML=o;
  }
  el.addEventListener('click',e=>{const b=e.target.closest('button[data-d]'), f=e.target.closest('button[data-f]'), w=e.target.closest('button[data-w]');if(w){who=w.dataset.w;paint()}else if(b){day=b.dataset.d;paint()}else if(f){filt=f.dataset.f;paint()}});
  paint();
  window.hubSportOn('yoga');
  // Today: the next classes still to come today, or tomorrow&#39;s first ones once today is done
  const ty=document.getElementById('td-yg'); if(ty){
    let d0=bdaDay, l0=onDay(d0); if(!l0.length){d0=addDays(bdaDay,1);l0=onDay(d0)}
    if(l0.length){ty.hidden=false;
      ty.innerHTML='<h3>Yoga</h3><p><b>'+(d0===bdaDay?'Still to come today':'Tomorrow')+'</b></p><ul class="tlist">'+l0.slice(0,3).map(s=>'<li><b>'+t12(s.start)+' '+esc(s.name)+'</b><span>'+esc((PL[s.p]||{}).name||'')+'</span></li>').join('')+'</ul><button type="button" data-go="sports" id="td-yggo">All classes and studios</button>';
      document.getElementById('td-yggo').addEventListener('click',()=>{window.hubSport='yoga';window.hubShowSport('yoga',false)});}
  }
})();

// ---- Sports tab, fourth and fifth groups: snorkel and scuba. Snorkel is places you can swim to from a beach; scuba is
// sites you need a boat for. Spots, operators and notes are kept by hand in events/data/dive.json (dive-data). The
// snorkel beaches and the wrecks are the same ones Explore holds, linked by id, so their positions and the compass
// bearing each beach faces come from explore-data. The calls use the hourly wind forecast the morning run saves.
(function(){
  const sn=document.getElementById('snk'), sc=document.getElementById('scu'); if(!sn||!sc||!window.hubSportOn)return;
  let V={}, W={}, X={};
  try{V=JSON.parse(document.getElementById('dive-data').textContent)}catch(e){}
  try{W=JSON.parse(document.getElementById('weather-data').textContent)}catch(e){}
  try{X=JSON.parse(document.getElementById('explore-data').textContent)}catch(e){}
  if(!(V.snorkel||[]).length&&!(V.operators||[]).length)return;
  const esc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const SITE={}; (X.sites||[]).forEach(s=>{SITE[s.id]=s});
  const pts16=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'], pt=d=>pts16[Math.round(d/22.5)%16];
  const now=new Date(), bdaDay=now.toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'}), bdaHour=+now.toLocaleTimeString('en-GB',{timeZone:'Atlantic/Bermuda',hour:'2-digit',hour12:false}).slice(0,2);
  const dates=[...new Set((W.hourly||[]).map(r=>r.t.slice(0,10)))].filter(d=>d>=bdaDay).slice(0,5);
  const shortDay=d=>d===bdaDay?'Today':new Date(d+'T12:00:00Z').toLocaleDateString('en-GB',{weekday:'short',day:'numeric',timeZone:'UTC'});
  // the daylight wind for a day: average strength and average direction
  function windFor(d){const info=(W.days||[]).find(x=>x.date===d)||{}, up=info.sunrise?+info.sunrise.slice(0,2)+1:7, dn=info.sunset?+info.sunset.slice(0,2):18;
    const rows=(W.hourly||[]).filter(r=>r.t.slice(0,10)===d&&r.wind!=null&&r.dir!=null).map(r=>({h:+r.t.slice(11,13),k:r.wind,dir:r.dir})).filter(r=>r.h>=up&&r.h<dn&&(d!==bdaDay||r.h>=bdaHour));
    if(!rows.length)return null;
    const sx=rows.reduce((t,r)=>t+Math.sin(r.dir*Math.PI/180),0), cx=rows.reduce((t,r)=>t+Math.cos(r.dir*Math.PI/180),0);
    return {k:rows.reduce((t,r)=>t+r.k,0)/rows.length, hi:Math.max(...rows.map(r=>r.k)), dir:(Math.atan2(sx,cx)*180/Math.PI+360)%360}}
  const off=(a,b)=>{const x=Math.abs(a-b)%360;return x>180?360-x:x};
  // how a beach sits to the wind: onto the beach within 60 degrees of the way it faces means chop and cloudy water
  function rate(site,w){ if(!w||site.faces==null)return {r:1,c:'maybe',t:'No forecast for this day'};
    if(w.k<8)return {r:0,c:'go',t:'Light wind, should be calm'};
    const on=off(w.dir,site.faces)<=60;
    if(!on)return {r:0,c:'go',t:'Sheltered from the '+pt(w.dir)+' wind'};
    return w.k<15?{r:1,c:'maybe',t:'Wind onto the beach, expect some chop'}:{r:2,c:'skip',t:'Wind straight onto the beach, rough and cloudy'}}
  const mapLink=(lat,lon)=>'https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(lat+','+lon);
  function toExplore(name){go('explore');const el=document.getElementById('xfind');if(el){el.value=name;el.dispatchEvent(new Event('input',{bubbles:true}))}}
  // A place opens in its own sheet right here (the same sheet Explore uses, with its Deep dive button), so nobody
  // is sent to another tab to hunt for it.
  const openPlace=id=>{if(window.hubOpenPlace&&SITE[id])window.hubOpenPlace(id);else if(SITE[id])toExplore(SITE[id].name)};
  // The maps (GitHub Pages copy only, like the Explore map). A map is rebuilt each time its section is painted,
  // once the section is on screen. Each pin carries the colour of the call for the chosen day.
  const mapLive=location.hostname.endsWith('github.io')||location.hostname==='localhost'||location.hostname==='127.0.0.1'||location.protocol==='file:';
  const MAPS={}, WAIT={}, TONE={go:'#2af0d9',maybe:'#ffc83d',skip:'#ff4fa3',op:'#ffffff'};
  const mapBox=id=>mapLive?'<div class="xmapbox" style="margin-top:10px"><div class="smap" id="'+id+'" role="application" aria-label="Map"></div></div>':'';
  function drawMap(id,pins){
    if(!mapLive||!window.hubLeaflet||!pins.length)return;
    const make=()=>{const box=document.getElementById(id); if(!box||box.offsetParent===null)return false;
      window.hubLeaflet(()=>{const b=document.getElementById(id); if(!b||b.offsetParent===null||b.classList.contains('leaflet-container'))return;
        if(MAPS[id]){try{MAPS[id].remove()}catch(e){}}
        const m=L.map(id,{zoomControl:true,minZoom:10,maxZoom:18,maxBounds:[[31.85,-65.6],[32.8,-63.95]],maxBoundsViscosity:0.3});
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; OpenStreetMap contributors'}).addTo(m);
        b.classList.add('xdark');
        pins.forEach(p=>{const mk=L.circleMarker([p.lat,p.lon],{radius:p.c==='op'?7:10,color:'#170f3a',weight:2,fillColor:TONE[p.c]||'#2af0d9',fillOpacity:1}).addTo(m);
          mk.bindTooltip(p.label,{direction:'top',offset:[0,-8],className:'xtip'});
          if(p.id)mk.on('click',()=>openPlace(p.id));else if(p.pop)mk.bindPopup(p.pop)});
        m.fitBounds(pins.map(p=>[p.lat,p.lon]),{padding:[34,34],maxZoom:14});
        MAPS[id]=m; setTimeout(()=>m.invalidateSize(),250);});
      return true};
    clearInterval(WAIT[id]); if(!make())WAIT[id]=setInterval(()=>{if(make())clearInterval(WAIT[id])},500);
  }
  let dayS=dates[0]||bdaDay, dayC=dates[0]||bdaDay;
  const chips=(id,day)=>dates.length?'<div class="xchips" id="'+id+'">'+dates.map(d=>'<button type="button" data-d="'+d+'" aria-pressed="'+(d===day)+'">'+shortDay(d)+'</button>').join('')+'</div>':'';
  function paintSnorkel(){
    const w=windFor(dayS), list=(V.snorkel||[]).map(s=>({s:s,site:SITE[s.id]})).filter(x=>x.site).map(x=>Object.assign(x,{rt:rate(x.site,w)})).sort((a,b)=>a.rt.r-b.rt.r);
    const good=list.filter(x=>x.rt.r===0);
    let o='<h2 class="xtitle">Snorkel</h2><p class="xlead">Places you can swim to from the beach, and which of them the wind leaves calm.</p>'+chips('snkdays',dayS);
    o+='<div class="wcard">'+(w?'<p class="sbig '+(good.length?'go':'skip')+'">'+(good.length?'Best bets: '+good.slice(0,3).map(x=>esc(x.site.name)).join(', '):'A rough day for snorkelling')+'</p><p class="wsyn">Wind from the '+pt(w.dir)+', about '+Math.round(w.k)+' kt in daylight, up to '+Math.round(w.hi)+' kt.'+(good.length?'':' Every beach on the list has the wind blowing onto it.')+'</p>':'<p class="sbig skip">No daylight left in this forecast.</p><p class="wsyn">Pick another day.</p>')
      +'<p class="wsrc">Worked out from this morning&#39;s wind forecast and the way each beach faces. It does not know about swell, so look at the water before you get in.</p></div>';
    o+='<div class="wcard"><h3>The spots on the map</h3><p>Tap a pin for the place and its story.</p>'+mapBox('snkmap')+'<div class="skeyrow"><span><i style="background:#2af0d9"></i>Good</span><span><i style="background:#ffc83d"></i>Choppy</span><span><i style="background:#ff4fa3"></i>Rough</span></div></div>';
    o+='<div class="wcard"><h3>Where to snorkel from shore</h3>'+list.map(x=>'<div class="pbv"><h4>'+esc(x.site.name)+'<span class="pbtag'+(x.rt.c==='go'?' pub':x.rt.c==='maybe'?' in':'')+'">'+(x.rt.c==='go'?'Good':x.rt.c==='maybe'?'Choppy':'Rough')+'</span></h4><p>'+esc(x.site.parish)+'. '+esc(x.rt.t)+'.</p><p>'+esc(x.s.note)+'</p><p><b>For:</b> '+esc(x.s.level)+'</p>'
      +'<div class="wlinks"><a href="'+mapLink(x.site.lat,x.site.lon)+'" target="_blank" rel="noopener">Map</a><a href="#explore" data-id="'+esc(x.site.id)+'">The full story</a></div></div>').join('')+'</div>';
    o+='<div class="wcard"><h3>Before you get in</h3><ul>'+(V.snorkel_tips||[]).map(t=>'<li>'+esc(t)+'</li>').join('')+(W.climate&&W.climate.sea_surface?'<li>Sea temperature '+esc(W.climate.sea_surface)+'.</li>':'')+'</ul></div>';
    sn.innerHTML=o;
    drawMap('snkmap',list.filter(x=>x.site.lat&&x.site.lon).map(x=>({lat:x.site.lat,lon:x.site.lon,c:x.rt.c,id:x.site.id,label:x.site.name+': '+(x.rt.c==='go'?'good':x.rt.c==='maybe'?'choppy':'rough')})));
  }
  function paintScuba(){
    const w=windFor(dayC);
    let head='No daylight left in this forecast.', cls='skip', sub='Pick another day.';
    if(w){ if(w.hi<12){cls='go';head='Good boat diving weather';sub='Light wind, about '+Math.round(w.k)+' kt from the '+pt(w.dir)+'.'}
      else if(w.hi<=18){cls='maybe';head='Lumpy, but trips usually run';sub='Wind '+Math.round(w.k)+' kt from the '+pt(w.dir)+', up to '+Math.round(w.hi)+' kt. Operators may pick a site on the sheltered side.'}
      else{cls='skip';head='Windy: call before you go';sub='Wind up to '+Math.round(w.hi)+' kt from the '+pt(w.dir)+'. Boat trips are often moved or cancelled in this.'} }
    let o='<h2 class="xtitle">Scuba</h2><p class="xlead">Boat dives: the operators, the wrecks they visit, and whether the weather suits.</p>'+chips('scudays',dayC);
    o+='<div class="wcard"><p class="sbig '+cls+'">'+head+'</p><p class="wsyn">'+esc(sub)+'</p><p class="wsrc">A rough rule from this morning&#39;s wind forecast: under 12 kt is easy, 12 to 18 kt is bumpy, more than that and trips often change. The operator decides on the day.</p></div>';
    o+='<div class="wcard"><h3>Dive operators</h3>'+(V.operators||[]).map(p=>'<div class="pbv"><h4>'+esc(p.name)+'</h4><p>'+esc(p.base)+'.</p><p>'+esc(p.note)+'</p><div class="wlinks">'+(p.phone?'<a href="tel:+1'+p.phone.replace(/[^0-9]/g,'')+'">'+esc(p.phone)+'</a>':'')+(p.site?'<a href="'+esc(p.site)+'" target="_blank" rel="noopener">Website</a>':'')+'<a href="'+mapLink(p.lat,p.lon)+'" target="_blank" rel="noopener">Map</a></div></div>').join('')+'</div>';
    const wr=(V.boat_sites||[]).map(id=>SITE[id]).filter(Boolean);
    if(wr.length)o+='<div class="wcard"><h3>Wrecks you dive from a boat</h3><p>Tap a wreck, on the map or by name, and its story opens right here. Deep dive inside it has the full history.</p>'+mapBox('scumap')
      +'<div class="skeyrow"><span><i style="background:'+TONE[cls]+'"></i>Wreck, coloured by the weather call for the day</span><span><i style="background:#ffffff"></i>Dive operator</span></div>'
      +'<div class="xchips" style="margin-top:10px">'+wr.map(s=>'<button type="button" data-id="'+esc(s.id)+'">'+esc(s.name)+'</button>').join('')+'</div></div>';
    o+='<div class="wcard"><h3>Good to know</h3><ul>'+(V.scuba_facts||[]).concat(V.scuba_tips||[]).map(t=>'<li>'+esc(t)+'</li>').join('')+(W.climate&&W.climate.sea_surface?'<li>Sea temperature now: '+esc(W.climate.sea_surface)+'.</li>':'')+'</ul><div class="wlinks" style="margin-top:8px"><a href="#explore" data-x="Hunting lionfish">Lionfish guide</a></div>'
      +'<p class="wsrc">Operators and prices from their own websites, checked on '+esc(V.asof)+'.'+(V.stale?' These details may be out of date.':'')+'</p></div>';
    sc.innerHTML=o;
    drawMap('scumap',wr.filter(s=>s.lat&&s.lon).map(s=>({lat:s.lat,lon:s.lon,c:cls,id:s.id,label:s.name+(s.approx?' (position approximate)':'')}))
      .concat((V.operators||[]).filter(p=>p.lat&&p.lon).map(p=>({lat:p.lat,lon:p.lon,c:'op',label:p.name,pop:'<b>'+esc(p.name)+'</b><br>'+esc(p.base)}))));
  }
  function onClick(e,which){const b=e.target.closest('button[data-d]'), x=e.target.closest('[data-x]'), pid=e.target.closest('[data-id]');
    if(pid){e.preventDefault();openPlace(pid.dataset.id)}
    else if(b){if(which==='s'){dayS=b.dataset.d;paintSnorkel()}else{dayC=b.dataset.d;paintScuba()}}
    else if(x){e.preventDefault();toExplore(x.dataset.x)}}
  sn.addEventListener('click',e=>onClick(e,'s')); sc.addEventListener('click',e=>onClick(e,'c'));
  if((V.snorkel||[]).length){paintSnorkel();window.hubSportOn('snorkel')}
  if((V.operators||[]).length){paintScuba();window.hubSportOn('scuba')}
})();

// ---- Whole Hub search. One box, opened from the Search button in the header, that looks across everything the page
// carries: events, grocery specials, restaurants and their menus, shops, Explore places, the Field guide, bus stops and
// routes, pickleball, yoga, ships and superyacht berths. The index is built the first time the box is opened, from
// the same data blocks the tabs use. Tapping a result opens the right tab and, where that tab has its own search
// box, fills it in.
(function(){
  const btn=document.getElementById('hfind'); if(!btn)return;
  const esc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const read=id=>{try{return JSON.parse(document.getElementById(id).textContent)||{}}catch(e){return {}}};
  const money=n=>'$'+Number(n).toFixed(2);
  let IDX=null, box=null;
  function build(){
    const I=[], add=(group,title,sub,act,extra)=>{if(title)I.push({g:group,t:String(title),s:sub||'',a:act,h:(title+' '+(sub||'')+' '+(extra||'')).toLowerCase()})};
    const now=new Date(), bd=now.toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'}), y=+bd.slice(0,4), cm=+bd.slice(5,7), cd=+bd.slice(8,10);
    // events: the month and day only are saved, so a month earlier than this one means next year
    (read('today-data').events||[]).forEach(e=>{const yr=e.m<cm?y+1:y; if(e.m===cm&&e.d<cd)return;
      const when=new Date(Date.UTC(yr,e.m-1,e.d,12)).toLocaleDateString('en-GB',{weekday:'short',day:'numeric',month:'short',timeZone:'UTC'});
      add('What&#39;s on',e.name,[when,e.t,e.venue].filter(Boolean).join(', '),{p:'planner'},e.view+' '+String(yr)+String(100+e.m).slice(1)+String(100+e.d).slice(1))});
    // the deals page keeps its data inside its own page text, so it is cut out of there
    let D={}; try{const tx=document.getElementById('page-deals').textContent, mark='id="data" type="application/json">', i=tx.indexOf(mark), j=tx.indexOf('<'+String.fromCharCode(92)+'/script',i);
      if(i>0&&j>i)D=JSON.parse(tx.slice(i+mark.length,j))}catch(e){}
    const STORE={mp:'MarketPlace',ld:'Lindo'+String.fromCharCode(39)+'s',sm:'Supermart',ml:'Miles Market',pr:'Pronto',prc:'Price Rite'};
    (D.all||[]).forEach(r=>add('Grocery specials',r[2],(STORE[r[0]]||r[0])+', '+money(r[5])+(r[3]?' '+r[3]:'')+(r[4]?' (was '+money(r[4])+')':''),{p:'deals',q:r[2]},r[1]));
    (D.staples||[]).forEach(r=>add('Everyday prices',r[0],r[1]||'',{p:'deals',q:r[0]}));
    (D.eplaces||[]).forEach(g=>(g.places||[]).forEach(p=>add('Restaurants',p.n,[g.cat,p.a||p.addr].filter(Boolean).join(', '),{p:'deals',q:p.n},(p.t||'')+' '+(p.addr||''))));
    Object.keys(D.menus||{}).forEach(id=>{const mn=D.menus[id];(mn.cats||[]).forEach(c=>(c[1]||[]).forEach(it=>{const pr=it[2]||it[1];I.push({g:'On a menu',t:String(it[0]),s:mn.n+(pr?', '+money(pr):''),a:{p:'deals',q:it[0]},h:(it[0]+' '+mn.n).toLowerCase(),n:+pr||9999})}))});
    (D.rshops||[]).forEach(g=>(g.shops||[]).forEach(o=>add('Shops',o.n,g.cat,{p:'deals',q:o.n},o.t)));
    (D.rdeals||[]).forEach(d=>add('Shop offers',d.shop,d.what,{p:'deals',q:d.shop},d.cat));
    const X=read('explore-data'); (X.sites||[]).forEach(s=>add('Places',s.name,((X.kinds||{})[s.kind]||s.kind)+', '+s.parish,{p:'explore',find:s.name},(s.see||'')+' '+(s.story||'')));
    (X.routes||[]).forEach(r=>add('Half day routes',r.name||r.title,r.blurb||'',{p:'explore'}));
    const G=read('guide-data'); Object.keys(G.sp||{}).forEach(k=>{const sp=G.sp[k];add('Field guide',sp.n,sp.s,{p:'explore'},(sp.w||'')+' '+(sp.o||[]).join(' '))});
    const T=read('transit-data'); (T.stops||[]).forEach(s=>add('Bus stops',s[0],'Next buses at this stop',{p:'transit',stop:s[0]}));
    (T.routes||[]).forEach(r=>add('Bus routes','Route '+r.short,r.long||'',{p:'transit'}));
    (read('ferry-data').routes||[]).forEach(r=>add('Ferries',r.name,'Ferry timetable',{p:'transit'}));
    const P=read('pickleball-data'); (P.venues||[]).forEach(v=>add('Pickleball',v.name,(v.indoor?'Indoor, ':'')+(v.access==='public'?'public':'members or guests')+', '+v.parish,{p:'sports',sport:'pb'},(v.note||'')+' pickleball'));
    (P.events||[]).forEach(e=>add('Pickleball',e.name,e.venue,{p:'sports',sport:'pb'},'pickleball'));
    const Y=read('yoga-data'), PL={}; (Y.places||[]).forEach(p=>{PL[p.id]=p;add('Yoga',p.name,(p.kind==='hotel'?'Hotel':'Studio')+', '+p.area,{p:'sports',sport:'yoga'},(p.note||'')+' yoga')});
    const seen={}; (Y.sessions||[]).concat(Y.live||[]).forEach(c=>{const k=c.p+'|'+String(c.name).toLowerCase(); if(seen[k])return; seen[k]=1; add('Yoga classes',c.name,(PL[c.p]||{}).name||'',{p:'sports',sport:'yoga'},'yoga class '+(c.with||''))});
    const DV=read('dive-data'), SITES={}; (X.sites||[]).forEach(s=>{SITES[s.id]=s});
    (DV.snorkel||[]).forEach(z=>{const st=SITES[z.id]; if(st)add('Snorkel',st.name,z.level+', '+st.parish,{p:'sports',sport:'snorkel'},z.note+' snorkel snorkelling snorkeling')});
    (DV.operators||[]).forEach(o=>add('Scuba',o.name,o.base,{p:'sports',sport:'scuba'},o.note+' scuba dive diving'));
    (read('ships-data').ships||[]).forEach(s=>add('Ships due',s.name,s.kind+', due '+s.day,{p:'ocean'},s.said_name||''));
    const S=read('yachts-data'); (S.berths||[]).forEach(b=>add('Superyachts',b.name,b.where+'. '+b.takes,{p:'ocean'},'superyacht yacht marina berth'));
    (S.visits||[]).forEach(v=>add('Superyachts',v.title,[v.feet?v.feet+' ft':'',v.place].filter(Boolean).join(', '),{p:'ocean'},'superyacht yacht'));
    return I;
  }
  const ORDER=['What&#39;s on','Grocery specials','Everyday prices','Restaurants','On a menu','Shops','Shop offers','Places','Half day routes','Field guide','Bus stops','Bus routes','Ferries','Pickleball','Yoga','Yoga classes','Snorkel','Scuba','Ships due','Superyachts'];
  function find(q){
    const words=q.toLowerCase().split(' ').filter(Boolean); if(!words.length||words.join('').length<2)return null;
    const hit=IDX.filter(x=>words.every(w=>x.h.indexOf(w)>-1)), ql=words.join(' '), by={};
    hit.forEach(x=>{const tl=x.t.toLowerCase();x.r=tl===ql?0:tl.indexOf(ql)===0?1:tl.indexOf(ql)>-1?2:3;(by[x.g]=by[x.g]||[]).push(x)});
    return ORDER.filter(g=>by[g]).map(g=>[g,by[g].sort((a,b)=>a.r-b.r||(a.n||0)-(b.n||0)||a.t.localeCompare(b.t))]);
  }
  let last=[];
  function paint(){
    const q=box.querySelector('input').value.trim(), out=box.querySelector('#hsr'), res=find(q); last=[];
    if(!res){out.innerHTML='<p class="hsnote">Type two or more letters. Try a food, a place, a bird, a bus stop or a class.</p>';return}
    if(!res.length){out.innerHTML='<p class="hsnote">Nothing in the Hub matches that.</p>';return}
    out.innerHTML=res.map(g=>'<h3>'+g[0]+' <span>'+g[1].length+'</span></h3>'+g[1].slice(0,6).map(x=>{last.push(x);return '<button type="button" data-i="'+(last.length-1)+'"><b>'+esc(x.t)+'</b>'+(x.s?'<span>'+esc(x.s)+'</span>':'')+'</button>'}).join('')+(g[1].length>6?'<p class="hsmore">and '+(g[1].length-6)+' more. Add a word to narrow it down.</p>':'')).join('');
  }
  const fill=(id,val)=>{const el=document.getElementById(id); if(el){el.value=val; el.dispatchEvent(new Event('input',{bubbles:true}))}};
  function act(x){
    close(); const a=x.a||{};
    if(a.sport&&window.hubShowSport){window.hubSport=a.sport;window.hubShowSport(a.sport,false)}
    // the deals page is loaded afresh each time its tab opens, so its search box is filled once it has loaded
    if(a.p==='deals'&&a.q){const fr=document.getElementById('f'); fr.addEventListener('load',()=>setTimeout(()=>{try{const d=fr.contentDocument, t=d&&d.getElementById('topq'); if(t){t.value=a.q;t.dispatchEvent(new Event('input',{bubbles:true}))}}catch(e){}},60),{once:true})}
    go(a.p);
    if(a.find)fill('xfind',a.find);
    if(a.stop)fill('bq',a.stop);
  }
  function close(){if(box)box.hidden=true}
  function open(){
    if(!box){box=document.createElement('div'); box.id='hs'; box.setAttribute('role','dialog'); box.setAttribute('aria-label','Search the Hub');
      box.innerHTML='<div class="hsbar"><input type="search" placeholder="Search the whole Hub" aria-label="Search the whole Hub" autocomplete="off"><button type="button" id="hsx">Close</button></div><div id="hsr"></div>';
      document.body.appendChild(box);
      box.querySelector('input').addEventListener('input',paint);
      box.querySelector('#hsx').addEventListener('click',close);
      box.addEventListener('click',e=>{const b=e.target.closest('#hsr button[data-i]'); if(b&&last[+b.dataset.i])act(last[+b.dataset.i])});
      box.addEventListener('keydown',e=>{if(e.key==='Escape')close()});}
    if(!IDX)IDX=build();
    box.hidden=false; paint(); const inp=box.querySelector('input'); inp.focus(); inp.select();
  }
  btn.addEventListener('click',open);
})();

// ---- Weather tab, from the Bermuda Weather Service pages the laptop fetched this morning
(function(){
  let W={};try{W=JSON.parse(document.getElementById('weather-data').textContent.replace(/<\\\\\\//g,'</'))}catch(e){}
  const el=document.getElementById('wx'); if(!W||!W.forecast||!W.forecast.length)return;
  const esc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  // arrows point the way the wind is blowing (the forecast gives where it comes from, so callers add 180)
  const arrow=d=>'↑↗→↘↓↙←↖'[Math.round(((d||0)%360)/45)%8];
  const now=new Date(); const pad=n=>String(n).padStart(2,'0');
  const nowKey=now.getFullYear()+'-'+pad(now.getMonth()+1)+'-'+pad(now.getDate())+'T'+pad(now.getHours());
  let h=[];
  if(W.hourly){const i=W.hourly.findIndex(r=>r.t.slice(0,13)>=nowKey);h=W.hourly.slice(Math.max(0,i),Math.max(0,i)+24);}
  const hr=t=>{const n=+t.slice(11,13);return n===0?'12am':n<12?n+'am':n===12?'12pm':(n-12)+'pm'};
  const today=W.forecast[0]||{}, tonight=W.forecast[1]||{};
  const sun=(W.days&&W.days[0])||{};
  const todayIso=now.getFullYear()+'-'+pad(now.getMonth()+1)+'-'+pad(now.getDate());
  const tides=(W.tides||[]).filter(d=>d.date>=todayIso).slice(0,4);
  // The picture at the top, Harbour Road at dusk: two rows of Bermuda cottages with white stepped roofs on a hillside,
  // a moongate, a hibiscus hedge, palms and the harbour, under a striped setting sun. The sky follows the latest
  // airport report and the time of day in Bermuda (rain streaks, a moon and lit windows at night).
  const bdaNow=now.toLocaleTimeString('en-GB',{timeZone:'Atlantic/Bermuda',hour:'2-digit',minute:'2-digit'});
  const skyTxt=((W.now&&W.now.sky)||(today.lines||[]).join(' ')||'').toLowerCase();
  const night=!!(sun.sunrise&&sun.sunset&&(bdaNow<sun.sunrise||bdaNow>sun.sunset));
  const mood=night?'night':/rain|shower|drizzle|thunder/.test(skyTxt)?'rain':/overcast|cloud|fog|mist|haze/.test(skyTxt)?'cloud':'sun';
  function scene(){
    const dark=night||mood==='rain', f=n=>(+n).toFixed(1);
    // one Bermuda cottage: pastel wall with a shaded side, white stepped hip roof, chimney, top hinged shutters, arched door
    const house=(x,base,w,h,col,shade)=>{
      const side=w*0.28, rh=h*0.62, ov=5, top=base-h, rx0=x-ov, rx1=x+w+ov, px0=x+w*0.24, px1=x+w*0.9, ry=top-rh, sx=x+w+side+ov;
      let s='<rect x="'+x+'" y="'+top+'" width="'+w+'" height="'+h+'" fill="'+col+'"/><rect x="'+(x+w)+'" y="'+top+'" width="'+f(side)+'" height="'+h+'" fill="'+shade+'"/>';
      s+='<path d="M'+rx0+' '+top+' L'+f(px0)+' '+f(ry)+' L'+f(px1)+' '+f(ry)+' L'+rx1+' '+top+' Z" fill="#fffdf8"/><path d="M'+rx1+' '+top+' L'+f(px1)+' '+f(ry)+' L'+f(sx)+' '+top+' Z" fill="#e9dff2"/>';
      for(let i=1;i<5;i++){const t=i/5, yy=top-rh*t;s+='<path d="M'+f(rx0+(px0-rx0)*t)+' '+f(yy)+' L'+f(rx1+(px1-rx1)*t)+' '+f(yy)+' L'+f(sx+(px1-sx)*t)+' '+f(yy)+'" stroke="#cdbfe0" stroke-width="1.1" fill="none"/>';}
      s+='<rect x="'+rx0+'" y="'+(top-1.5)+'" width="'+(w+2*ov)+'" height="3.4" fill="#fffdf8"/><rect x="'+rx0+'" y="'+(top+1.9)+'" width="'+(w+2*ov)+'" height="1.6" fill="'+shade+'" opacity=".7"/>';
      const cx=x+w*0.66;
      s+='<path d="M'+f(cx)+' '+f(ry+rh*0.42)+' L'+f(cx+2)+' '+f(ry-rh*0.2)+' L'+f(cx+11)+' '+f(ry-rh*0.2)+' L'+f(cx+13)+' '+f(ry+rh*0.42)+' Z" fill="#fffdf8"/><rect x="'+f(cx)+'" y="'+f(ry-rh*0.2-3)+'" width="13" height="3.5" fill="#fffdf8"/>';
      const pane=dark?'#ffe27a':'#3a1f6e', ww=w*0.17, wh=h*0.36, wy=base-h*0.74;
      for(const wx of [x+w*0.13,x+w*0.70]){
        s+='<rect x="'+f(wx-1.5)+'" y="'+f(wy-1.5)+'" width="'+f(ww+3)+'" height="'+f(wh+3)+'" fill="#fffdf8"/><rect x="'+f(wx)+'" y="'+f(wy)+'" width="'+f(ww)+'" height="'+f(wh)+'" fill="'+pane+'"/>';
        s+='<path d="M'+f(wx-2)+' '+f(wy-1)+' L'+f(wx+ww+2)+' '+f(wy-1)+' L'+f(wx+ww+4)+' '+f(wy+wh*0.42)+' L'+f(wx-4)+' '+f(wy+wh*0.42)+' Z" fill="#1c8f8a"/>';
      }
      const dw=w*0.17, dx=x+w*0.415, dh=h*0.56;
      s+='<path d="M'+f(dx)+' '+base+' V'+f(base-dh+dw/2)+' A'+f(dw/2)+' '+f(dw/2)+' 0 0 1 '+f(dx+dw)+' '+f(base-dh+dw/2)+' V'+base+' Z" fill="#fffdf8"/><path d="M'+f(dx+2)+' '+base+' V'+f(base-dh+dw/2+1)+' A'+f(dw/2-2)+' '+f(dw/2-2)+' 0 0 1 '+f(dx+dw-2)+' '+f(base-dh+dw/2+1)+' V'+base+' Z" fill="#1c8f8a"/>';
      return s;
    };
    const palm=(x,y,h,lean,sw)=>{
      const tx=x+lean*h*0.22, ty=y-h;
      let p='<path d="M'+x+' '+y+' Q'+f(x+lean*h*0.02)+' '+f(y-h*0.55)+' '+f(tx)+' '+f(ty)+'" stroke="#1a0b3a" stroke-width="'+sw+'" fill="none" stroke-linecap="round"/>';
      for(const [dx,dy] of [[-.42,.06],[-.34,-.18],[-.1,-.3],[.2,-.26],[.42,-.04],[.36,.2],[-.3,.22]])
        p+='<path d="M'+f(tx)+' '+f(ty)+' Q'+f(tx+dx*h*0.5)+' '+f(ty+dy*h-h*0.14)+' '+f(tx+dx*h)+' '+f(ty+dy*h+h*0.1)+' Q'+f(tx+dx*h*0.55)+' '+f(ty+dy*h+h*0.02)+' '+f(tx)+' '+f(ty+4)+' Z" fill="#1a0b3a"/>';
      return p;
    };
    // sky: the big striped sun going down behind the houses, a moon at night, pink streaks in the rain
    let b='';
    if(mood==='sun'||mood==='cloud'){
      b+='<defs><linearGradient id="wsg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff27a"/><stop offset="1" stop-color="#ff4fa3"/></linearGradient><clipPath id="wsc"><circle cx="420" cy="210" r="92"/></clipPath></defs><g clip-path="url(#wsc)"'+(mood==='cloud'?' opacity=".55"':'')+'>';
      let y=118, band=38.6, gap=2;
      while(y<302){b+='<rect x="328" y="'+f(y)+'" width="184" height="'+f(band)+'" fill="url(#wsg)"/>';y+=band+gap;band=Math.max(4,band*0.78);gap+=1.5;}
      b+='</g>';
    }
    if(mood==='night')b+='<circle cx="600" cy="70" r="40" fill="#ff4fa3" opacity=".16"/><circle cx="600" cy="70" r="24" fill="#fdf3ff"/>';
    if(mood==='rain'){for(let i=0;i<30;i++){const rx=24+i*25, ry=20+((i*47)%130);b+='<line x1="'+rx+'" y1="'+ry+'" x2="'+(rx-8)+'" y2="'+(ry+20)+'" stroke="#ffb3e6" stroke-width="1.6" stroke-linecap="round" opacity=".55"/>';}}
    b+='<path d="M0 222 Q120 176 260 196 T520 186 T760 200 V300 H0 Z" fill="#4a1d7a"/>';
    for(const h of [[60,214,46,26,'#ffc7dd','#d79ab8'],[150,206,40,24,'#fff1b8','#d9c98a'],[246,210,44,26,'#b9f3e4','#8fcab9'],[560,204,42,24,'#c5e4ff','#98b9d9'],[650,212,46,26,'#ffc7dd','#d79ab8']])b+='<g opacity=".85">'+house(...h)+'</g>';
    b+='<path d="M0 252 Q90 214 200 232 T420 236 T640 226 T760 238 V300 H0 Z" fill="#2c1160"/>';
    for(const h of [[96,250,84,50,'#ff8fb5','#d9608c'],[236,254,74,46,'#ffe37a','#d9b84a'],[372,256,90,54,'#7ff0d8','#4fc1ab'],[520,252,78,48,'#ffb08a','#d98562'],[640,256,70,44,'#9fd3ff','#6fa6d9']])b+=house(...h);
    b+='<path d="M326 258 A20 21 0 1 1 356 258" fill="none" stroke="#e9dff2" stroke-width="7"/><path d="M326 258 A20 21 0 1 1 356 258" fill="none" stroke="#b9a8d6" stroke-width="7" stroke-dasharray="1.2 6"/>';
    for(let x=0;x<760;x+=38)b+='<ellipse cx="'+(x+14)+'" cy="262" rx="26" ry="10" fill="#1d6b57"/><circle cx="'+(x+6)+'" cy="258" r="2.6" fill="#ff4fa3"/><circle cx="'+(x+24)+'" cy="261" r="2.2" fill="#ff7ab8"/>';
    b+=palm(34,268,100,1,6)+palm(726,268,160,-1,7)+palm(470,262,96,1,5);
    const sea=dark?['#16b9c9','#12b0c4','#1b2a7a']:['#2af0d9','#2af0d9','#0b6fa8'];
    b+='<defs><linearGradient id="wse" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="'+sea[1]+'"/><stop offset="1" stop-color="'+sea[2]+'"/></linearGradient></defs><rect y="268" width="760" height="32" fill="url(#wse)"/>';
    let d='M0 266';for(let i=0;i<8;i++)d+=' q47.5 -4 95 0';
    b+='<path d="'+d+' V276 H0 Z" fill="'+sea[0]+'"/>';
    if(mood==='sun'||mood==='cloud')[[360,120],[340,160],[380,90],[350,130]].forEach((r,i)=>{b+='<rect x="'+r[0]+'" y="'+(276+i*6)+'" width="'+r[1]+'" height="2" fill="#fff27a" opacity="'+f(0.6-i*0.12)+'"/>'});
    b+='<rect y="298" width="760" height="2" fill="#ff4fa3"/>';
    return '<svg class="wscene" viewBox="0 0 760 300" preserveAspectRatio="xMidYMax slice" aria-hidden="true">'+b+'</svg>';
  }
  // ---- Derived readings for the extra cards: the model row for this hour, feels like, comfort, daytime outlook, seas.
  const cur=h[0]||{};
  const num=t=>{const m=String(t==null?'':t).match(/-?[0-9]+(?:[.][0-9]+)?/);return m?+m[0]:null};
  const tNow=cur.temp!=null?cur.temp:num(W.now&&W.now.temp), rhNow=cur.rh!=null?cur.rh:num(W.now&&W.now.rh);
  const obsKt=(()=>{const m=String((W.now&&W.now.wind)||'').match(/([0-9]+) ?KT/i);return m?+m[1]:null})();
  const ktNow=cur.wind!=null?cur.wind:obsKt;
  const vap=(tNow!=null&&rhNow!=null)?rhNow/100*6.105*Math.exp(17.27*tNow/(237.7+tNow)):null;
  const feels=cur.feels!=null?cur.feels:(vap!=null?tNow+0.33*vap-0.70*(ktNow||0)*0.5144-4:null);
  const dew=cur.dew!=null?cur.dew:(vap!=null?237.7*Math.log(vap/6.105)/(17.27-Math.log(vap/6.105)):null);
  const comfort=dew==null?'':dew<13?'crisp':dew<16?'comfortable':dew<19?'a little humid':dew<22?'sticky':dew<24?'muggy':'oppressive';
  const pts16=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
  const t12h=t=>{const hh=+t.slice(0,2);return (hh%12||12)+':'+t.slice(3,5)+(hh<12?' am':' pm')};
  const hm=t=>(+t.slice(0,2))*60+(+t.slice(3,5));
  // daytime rows still to come today; after sunset, tomorrow's daytime
  const bdaDay=now.toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'});
  const late=!!(sun.sunset&&bdaNow>sun.sunset);
  const dayIso=late&&W.days&&W.days[1]?W.days[1].date:bdaDay;
  const dayRows=(W.hourly||[]).filter(r=>r.t.slice(0,10)===dayIso&&+r.t.slice(11,13)>=7&&+r.t.slice(11,13)<=18&&(late||r.t.slice(11,13)>=bdaNow.slice(0,2)));
  const mx=(k)=>dayRows.length?Math.max(...dayRows.map(r=>r[k]==null?0:r[k])):null;
  const dWind=mx('wind'), dRain=mx('rain'), dUv=mx('uv'), dTemp=mx('temp');
  const marineTxt=((W.marine&&W.marine.periods&&W.marine.periods[late?1:0])||{lines:[]}).lines.join(' ');
  const reef=w=>{const m=marineTxt.match(new RegExp(w+' the reef ([0-9]+)(?: to ([0-9]+))? ?ft','i'));return m?[+m[1],+(m[2]||m[1])]:null};
  const seaIn=reef('inside'), seaOut=reef('outside');
  const warned=(W.warnings||[]).some(w=>/small craft|gale|storm|hurricane/i.test(w.title||''));
  // 1. What the rain is doing over the coming hours, from the hourly model
  const rainLine=(()=>{
    if(!h.length||h[0].rain==null)return '';
    const p=h[0].rain, at=r=>hr(r.t).replace('am',' am').replace('pm',' pm');
    if(p>=55){const e=h.find(r=>r.rain<35);return 'Rain likely this hour ('+p+'%)'+(e?', easing around '+at(e)+'.':', and staying that way into tomorrow.');}
    if(p<35){const e=h.find(r=>r.rain>=55);return e?'Dry for now. Showers more likely from '+at(e)+'.':'Dry for now, and nothing much on the way in the next 24 hours.';}
    const e=h.find(r=>r.rain<35), u=h.find(r=>r.rain>=55);
    return 'A shower is possible this hour ('+p+'%)'+(u?', more likely from '+at(u)+'.':e?', clearing up around '+at(e)+'.':'.');
  })();
  // 7. Go, maybe or skip for five things people actually plan around
  const acts=(()=>{
    if(dWind==null)return [];
    const so=seaOut?seaOut[1]:null, si=seaIn?seaIn[1]:null, W_=Math.round(dWind), R_=Math.round(dRain||0);
    const v=(skip,maybe,why)=>({v:skip?'skip':maybe?'maybe':'go',why:why});
    return [
      ['Beach',v(R_>=60||W_>=22,R_>=35||W_>=15||(dTemp!=null&&dTemp<21),R_>=35?R_+'% chance of rain':W_>=15?'wind to '+W_+' kt':'light wind, mostly dry')],
      ['Boat',v(warned||W_>=20||(so!=null&&so>=8),W_>=13||(so!=null&&so>=5),warned?'warning in force':so!=null?so+' ft outside the reef, '+W_+' kt':'wind to '+W_+' kt')],
      ['Snorkel',v((si!=null&&si>=3)||W_>=18,(si!=null&&si>=2)||W_>=12,si!=null?si+' ft inside the reef':'wind to '+W_+' kt')],
      ['Run',v((feels!=null&&feels>=32)||R_>=70,R_>=40||(dew!=null&&dew>=22),R_>=40?R_+'% chance of rain':comfort?comfort+' air':'fine')],
      ['Laundry',v(R_>=50,R_>=30,R_+'% chance of rain')]];
  })();
  const word={go:'Go',maybe:'Maybe',skip:'Skip'};
  // 3. Boat day: the wind for the daylight hours, and the anchorages that sit in the lee of it. Each anchorage is
  // listed with the compass bearing its mouth faces and how wide that opening is; wind from inside that arc blows
  // straight in. This is a guide from the shape of the coast, not a chart.
  const COVES=[['Paradise Lakes','among the islands of the Great Sound',0,25],['Ely&#39;s Harbour','Sandys',270,45],['Mangrove Bay','Somerset',45,60],['Jew&#39;s Bay','Southampton',0,60],['Riddell&#39;s Bay','Warwick',340,60],
    ['Granaway Deep','the south side of Hamilton Harbour',10,50],['Somerset Long Bay','Sandys',315,80],['Shelly Bay','Hamilton Parish',350,80],['Bailey&#39;s Bay','Hamilton Parish',0,70],['Whalebone Bay','Ferry Reach',320,60],
    ['Convict Bay, St George&#39;s Harbour','under the town',180,50],['Tucker&#39;s Town Bay','Castle Harbour',30,70],['Grassy Bay','off Dockyard',60,70],['Horseshoe Bay','the south shore, inside the reef line',180,90]];
  const arc=(a,b)=>{const d=Math.abs(a-b)%360;return d>180?360-d:d};
  function boatFor(rows,label,marineIdx){
    if(!rows.length)return null;
    const sx=rows.reduce((t,r)=>t+Math.sin(r.dir*Math.PI/180),0), cx=rows.reduce((t,r)=>t+Math.cos(r.dir*Math.PI/180),0), dir=(Math.atan2(sx,cx)*180/Math.PI+360)%360;
    const lo=Math.round(Math.min(...rows.map(r=>r.wind))), hi=Math.round(Math.max(...rows.map(r=>r.wind))), rain=Math.max(...rows.map(r=>r.rain||0));
    const txt=((W.marine&&W.marine.periods&&W.marine.periods[marineIdx])||{lines:[]}).lines.join(' '), mo=txt.match(new RegExp('outside the reef ([0-9]+)(?: to ([0-9]+))? ?ft','i')), out=mo?+(mo[2]||mo[1]):null;
    const v=(warned&&marineIdx<2)||hi>=20||(out!=null&&out>=8)?'skip':hi>=13||(out!=null&&out>=5)?'maybe':'go';
    const lee=COVES.map(c=>({n:c[0],w:c[1],gap:arc(dir,c[2])-c[3]})).filter(c=>c.gap>=25).sort((a,b)=>b.gap-a.gap).slice(0,3);
    return {label:label,dir:dir,name:pts16[Math.round(dir/22.5)%16],lo:lo,hi:hi,rain:rain,out:out,v:v,lee:lee};
  }
  const dayHours=iso=>(W.hourly||[]).filter(r=>r.t.slice(0,10)===iso&&+r.t.slice(11,13)>=8&&+r.t.slice(11,13)<=18&&r.dir!=null);
  const boats=[boatFor(dayHours(bdaDay).filter(r=>r.t.slice(11,13)>=bdaNow.slice(0,2)),'Today',0),W.days&&W.days[1]?boatFor(dayHours(W.days[1].date),'Tomorrow',2):null].filter(Boolean);
  const boatLine=b=>'<div class="wboat '+b.v+'"><div class="hd"><b>'+b.label+'</b><span class="v">'+word[b.v]+'</span></div><p>Wind from the '+b.name+', '+(b.lo===b.hi?b.hi:b.lo+' to '+b.hi)+' kt'+(b.out!=null?', seas to '+b.out+' ft outside the reef':'')+(b.rain>=40?', '+b.rain+'% chance of rain':'')+'.</p>'+(b.lee.length?'<p><span class="lee">Out of the wind:</span> '+b.lee.map(c=>c.n+' ('+c.w+')').join(', ')+'.</p>':'<p>No anchorage on the list sits clearly in the lee of this wind.</p>')+'</div>';
  function boatCard(){
    return boats.length?'<div class="wcard sea wseac"><h3>Boat day</h3>'+boats.map(boatLine).join('')+'<p class="wsrc">Anchorages are picked from the shape of the coast and the forecast wind direction. It is a guide, not a chart: check depths, reefs, moorings and the marine forecast yourself.</p></div>':'';
  }
  // 3, 4, 6, 11. Four small dials: wind, sun, UV, moon
  function dials(){
    let o='';
    if(ktNow!=null){const d=cur.dir!=null?cur.dir:null, nm=d!=null?pts16[Math.round(d/22.5)%16]:String((W.now&&W.now.wind)||'').split(' ')[0];
      o+='<div class="wdial"><h3>Wind</h3><svg viewBox="0 0 120 120" role="img" aria-label="Wind from '+esc(nm)+' at '+Math.round(ktNow)+' knots"><circle cx="60" cy="60" r="50" fill="none" stroke="#4b2d8a" stroke-width="2"/>'+
        [['N',60,20],['E',104,64],['S',60,108],['W',16,64]].map(a=>'<text x="'+a[1]+'" y="'+a[2]+'" text-anchor="middle" font-size="11" font-weight="800" fill="#cdbbea">'+a[0]+'</text>').join('')+
        (d!=null?'<g transform="rotate('+(d+180)+' 60 60)"><path d="M60 96 V34" stroke="#2af0d9" stroke-width="4" stroke-linecap="round"/><path d="M60 18 L70 38 H50 Z" fill="#2af0d9"/></g>':'')+
        '<circle cx="60" cy="60" r="21" fill="#241552"/><text x="60" y="62" text-anchor="middle" font-size="19" font-weight="800" fill="#fff">'+Math.round(ktNow)+'</text><text x="60" y="74" text-anchor="middle" font-size="9" font-weight="700" fill="#cdbbea">kt</text></svg><p>From the '+esc(nm)+(cur.gust!=null?', gusts '+Math.round(cur.gust)+' kt':'')+'</p></div>';}
    if(sun.sunrise&&sun.sunset){const a=hm(sun.sunrise), b=hm(sun.sunset), n=hm(bdaNow), fr=Math.min(1,Math.max(0,(n-a)/(b-a))), ang=Math.PI*(1-fr), sx=60+48*Math.cos(ang), sy=84-48*Math.sin(ang), up=n>=a&&n<=b, left=b-n;
      o+='<div class="wdial"><h3>Sun</h3><svg viewBox="0 0 120 100" role="img" aria-label="Sunrise '+t12h(sun.sunrise)+', sunset '+t12h(sun.sunset)+'"><path d="M12 84 A48 48 0 0 1 108 84" fill="none" stroke="#4b2d8a" stroke-width="2" stroke-dasharray="3 5"/><path d="M4 84 H116" stroke="#ff4fa3" stroke-width="2"/>'+
        (up?'<circle cx="'+sx.toFixed(1)+'" cy="'+sy.toFixed(1)+'" r="15" fill="#ffb25e" opacity=".3"/><circle cx="'+sx.toFixed(1)+'" cy="'+sy.toFixed(1)+'" r="9" fill="#fff27a"/>':'<circle cx="60" cy="92" r="9" fill="#fff27a" opacity=".35"/>')+
        '<text x="12" y="98" text-anchor="middle" font-size="9" font-weight="700" fill="#cdbbea">'+t12h(sun.sunrise).replace(' am','')+'</text><text x="108" y="98" text-anchor="middle" font-size="9" font-weight="700" fill="#cdbbea">'+t12h(sun.sunset).replace(' pm','')+'</text></svg><p>'+
        (up?Math.floor(left/60)+' h '+(left%60)+' min of daylight left':n<a?'Sunrise at '+t12h(sun.sunrise):'Sun is down. Up again at '+t12h((W.days&&W.days[1]&&W.days[1].sunrise)||sun.sunrise))+'</p></div>';}
    const uvRows=(W.hourly||[]).filter(r=>r.t.slice(0,10)===bdaDay&&r.uv!=null), uvMax=uvRows.length?Math.max(...uvRows.map(r=>r.uv)):num(today.uv);
    if(uvMax!=null){const hot=uvRows.filter(r=>r.uv>=3), cat=uvMax<3?'Low':uvMax<6?'Moderate':uvMax<8?'High':uvMax<11?'Very high':'Extreme', px=10+100*Math.min(11,uvMax)/11;
      o+='<div class="wdial"><h3>UV</h3><svg viewBox="0 0 120 100" role="img" aria-label="UV index peaks at '+Math.round(uvMax)+', '+cat+'"><defs><linearGradient id="wuv" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2af0d9"/><stop offset=".35" stop-color="#fff27a"/><stop offset=".65" stop-color="#ffb25e"/><stop offset="1" stop-color="#ff4fa3"/></linearGradient></defs><text x="60" y="46" text-anchor="middle" font-size="34" font-weight="800" fill="#fff">'+Math.round(uvMax)+'</text><text x="60" y="62" text-anchor="middle" font-size="11" font-weight="700" fill="#cdbbea">'+cat+'</text><rect x="10" y="76" width="100" height="8" rx="4" fill="url(#wuv)"/><circle cx="'+px.toFixed(1)+'" cy="80" r="7" fill="#fff" stroke="#241552" stroke-width="3"/></svg><p>'+
        (hot.length?'Sunscreen from '+hr(hot[0].t).replace('am',' am').replace('pm',' pm')+' to '+hr(String(hot[hot.length-1].t).slice(0,11)+pad(+hot[hot.length-1].t.slice(11,13)+1)+':00').replace('am',' am').replace('pm',' pm'):'No sunscreen needed today')+'</p></div>';}
    {const P=29.530588853, age=((Date.now()/86400000-10962.76)%P+P)%P, fr=age/P, lit=(1-Math.cos(2*Math.PI*fr))/2, R=30, rx=(R*Math.abs(Math.cos(2*Math.PI*fr))).toFixed(1);
      const name=fr<0.03||fr>0.97?'New moon':fr<0.22?'Waxing crescent':fr<0.28?'First quarter':fr<0.47?'Waxing gibbous':fr<0.53?'Full moon':fr<0.72?'Waning gibbous':fr<0.78?'Last quarter':'Waning crescent';
      const path=fr<0.5?'M60 20 A30 30 0 0 1 60 80 A'+rx+' 30 0 0 '+(fr<0.25?0:1)+' 60 20 Z':'M60 20 A30 30 0 0 0 60 80 A'+rx+' 30 0 0 '+(fr>0.75?1:0)+' 60 20 Z';
      const toFull=((P/2-age)%P+P)%P, toNew=P-age, nextIsFull=toFull<toNew, dd=new Date(Date.now()+(nextIsFull?toFull:toNew)*86400000);
      o+='<div class="wdial"><h3>Moon</h3><svg viewBox="0 0 120 100" role="img" aria-label="'+name+', '+Math.round(lit*100)+' percent lit"><circle cx="60" cy="50" r="38" fill="#ff4fa3" opacity=".12"/><circle cx="60" cy="50" r="30" fill="#3a2a6e"/><path d="'+path+'" fill="#fdf3ff"/></svg><p>'+name+', '+Math.round(lit*100)+'% lit. '+(nextIsFull?'Full':'New')+' moon '+dd.toLocaleDateString('en-GB',{timeZone:'Atlantic/Bermuda',weekday:'short',day:'numeric',month:'short'})+'</p></div>';}
    return o?'<div class="wdials">'+o+'</div>':'';
  }
  // 9. Sea state at a glance, from the BWS marine forecast
  function seaCard(){
    if(!seaIn&&!seaOut)return '';
    const bar=(lab,v)=>v?'<div class="wsea"><span>'+lab+'</span><div class="trk"><i style="width:'+Math.min(100,v[1]/12*100).toFixed(0)+'%"></i></div><b>'+(v[0]===v[1]?v[1]:v[0]+' to '+v[1])+' ft</b></div>':'';
    return '<div class="wcard sea wseac"><h3>Sea state '+(late?'tonight':'today')+'</h3>'+bar('Inside the reef',seaIn)+bar('Outside the reef',seaOut)+'<p>'+(W.climate&&W.climate.sea_surface?'Water '+esc(W.climate.sea_surface.split('/')[0].trim().replace(' C','°C'))+'. ':'')+(warned?'A marine warning is in force.':'No marine warnings.')+'</p></div>';
  }
  // 8. Rain for the tank. Figures are Bermuda's own: Imperial gallons, the Department of Health's yield (a 3,000 sq ft
  // catchment gives 86,580 gallons in an average 55.5 inch year, which is 0.52 gallons per square foot per inch) and
  // the Government's tank advice. The roof size typed in is kept on that device only.
  const rainMm=num(W.climate&&W.climate.rain_month), YIELD=0.52, YEAR_IN=55.5;
  function tankCard(){
    if(rainMm==null)return '';
    const inch=rainMm/25.4, avg=YEAR_IN/12, mname=now.toLocaleDateString('en-GB',{timeZone:'Atlantic/Bermuda',month:'long'});
    return '<h2 class="w">Rain for the tank</h2><div class="wcard wtank"><div class="big">'+inch.toFixed(2)+' in</div><p>'+rainMm+' mm at the airport so far in '+mname+'. An average Bermuda month brings about '+avg.toFixed(1)+' inches ('+YEAR_IN+' inches a year).</p>'+
      '<div class="trk" role="img" aria-label="'+Math.round(inch/avg*100)+' percent of an average month"><i style="width:'+Math.min(100,inch/avg*100).toFixed(0)+'%"></i></div>'+
      '<label class="wroof">My roof is <input id="wroof" type="number" inputmode="numeric" min="100" max="20000" step="50" placeholder="1500"> square feet</label><p id="wroofout"></p>'+
      '<p class="wsrc">Tank size in Imperial gallons is length x width x depth in feet x 6.25. When you buy water, fill to about half so there is room for rain. Yield is the Department of Health figure of 0.52 gallons per square foot of roof per inch of rain.</p></div>';
  }
  function tankWire(){
    const inp=document.getElementById('wroof'), out=document.getElementById('wroofout'); if(!inp||!out)return;
    try{const v=localStorage.getItem('hub-roof-sqft');if(v)inp.value=v}catch(e){}
    const show=()=>{const a=+inp.value>0?+inp.value:1000, g=rainMm/25.4*a*YIELD, yr=YEAR_IN*a*YIELD;
      out.textContent=(+inp.value>0?'Your roof':'Every 1,000 square feet of roof')+' has caught about '+Math.round(g).toLocaleString('en-US')+' Imperial gallons this month. In an average year it catches about '+Math.round(yr).toLocaleString('en-US')+', or '+Math.round(yr/365)+' a day.';};
    inp.addEventListener('input',()=>{try{localStorage.setItem('hub-roof-sqft',inp.value)}catch(e){}show()});
    show();
  }
  // Tide graph: the rise and fall at St George's over today and tomorrow, drawn from the BWS high and low times
  // (a smooth curve between each high and low), with a line at the time now in Bermuda.
  function tideGraph(){
    const bdaDate=now.toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'});
    const dayNo=s=>Math.round(Date.UTC(+s.slice(0,4),+s.slice(5,7)-1,+s.slice(8,10))/86400000);
    const d0=dayNo(bdaDate), ev=[];
    for(const d of (W.tides||[]))for(const e of d.events){const m=(dayNo(d.date)-d0)*1440+(+e.time.slice(0,2))*60+(+e.time.slice(3,5));ev.push({m:m,ft:+e.ft,kind:e.kind,time:e.time});}
    ev.sort((a,b)=>a.m-b.m);
    const SPAN=2880, inwin=ev.filter(e=>e.m>=0&&e.m<=SPAN);
    if(ev.length<3||inwin.length<3)return '';
    const hAt=m=>{for(let i=0;i<ev.length-1;i++){const a=ev[i],b=ev[i+1];if(m>=a.m&&m<=b.m)return a.ft+(b.ft-a.ft)*(1-Math.cos(Math.PI*(m-a.m)/(b.m-a.m)))/2;}return null};
    const VW=720, VH=222, L=10, R=710, T=44, B=146;
    const lo=Math.min(...ev.map(e=>e.ft))-0.2, hi=Math.max(...ev.map(e=>e.ft))+0.2;
    const X=m=>L+(R-L)*m/SPAN, Y=ft=>B-(B-T)*(ft-lo)/(hi-lo);
    const t12=t=>{const hh=+t.slice(0,2);return (hh%12||12)+':'+t.slice(3,5)+(hh<12?' am':' pm')};
    let pts=[];
    for(let m=0;m<=SPAN;m+=10){const v=hAt(m);if(v!=null)pts.push([X(m),Y(v)]);}
    if(pts.length<2)return '';
    const line='M'+pts.map(p=>p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' L');
    let s='<svg viewBox="0 0 '+VW+' '+VH+'" role="img" aria-label="Tide height at St George&#39;s over today and tomorrow">';
    s+='<defs><linearGradient id="wtg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2af0d9" stop-opacity=".55"/><stop offset="1" stop-color="#2af0d9" stop-opacity=".04"/></linearGradient></defs>';
    const names=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'], wd=new Date(bdaDate+'T12:00:00Z').getUTCDay();
    for(let k=0;k<=8;k++){const m=k*360, x=X(m), hh=(k*6)%24, lab=hh===0?(k===8?'':names[(wd+k/4)%7]):hh===6?'6 am':hh===12?'noon':'6 pm';
      s+='<path d="M'+x.toFixed(1)+' '+(T-14)+' V'+(B+8)+'" stroke="#fdf3ff" stroke-width="'+(hh===0?1.2:0.6)+'" opacity="'+(hh===0?0.45:0.18)+'"/>';
      if(lab)s+='<text x="'+(x+(hh===0?4:0)).toFixed(1)+'" y="'+(VH-10)+'" text-anchor="'+(hh===0?'start':'middle')+'" font-size="12" font-weight="'+(hh===0?800:600)+'" fill="'+(hh===0?'#fdf3ff':'#cdbbea')+'">'+lab+'</text>';}
    s+='<path d="'+line+' L'+pts[pts.length-1][0].toFixed(1)+' '+(B+8)+' L'+pts[0][0].toFixed(1)+' '+(B+8)+' Z" fill="url(#wtg)"/>';
    s+='<path d="'+line+'" fill="none" stroke="#2af0d9" stroke-width="7" opacity=".25" stroke-linecap="round"/><path d="'+line+'" fill="none" stroke="#2af0d9" stroke-width="2.6" stroke-linecap="round"/>';
    for(const e of inwin){const x=Math.min(R-34,Math.max(L+34,X(e.m))), y=Y(e.ft), up=e.kind==='High';
      s+='<circle cx="'+X(e.m).toFixed(1)+'" cy="'+y.toFixed(1)+'" r="4.5" fill="'+(up?'#fff27a':'#ff4fa3')+'"/>';
      s+='<text x="'+x.toFixed(1)+'" y="'+(up?y-22:y+19).toFixed(1)+'" text-anchor="middle" font-size="12" font-weight="800" fill="#fdf3ff">'+t12(e.time)+'</text>';
      s+='<text x="'+x.toFixed(1)+'" y="'+(up?y-9:y+32).toFixed(1)+'" text-anchor="middle" font-size="11" font-weight="600" fill="#cdbbea">'+(up?'High ':'Low ')+e.ft+' ft</text>';}
    const nm=(+bdaNow.slice(0,2))*60+(+bdaNow.slice(3,5)), nv=hAt(nm);
    let cap='';
    if(nv!=null){const later=hAt(nm+20), dir=later==null?'':later>nv?'rising':'falling', nx=X(nm);
      s+='<path d="M'+nx.toFixed(1)+' '+(T-14)+' V'+(B+8)+'" stroke="#ff4fa3" stroke-width="2"/><circle cx="'+nx.toFixed(1)+'" cy="'+Y(nv).toFixed(1)+'" r="6" fill="#ff4fa3" stroke="#fff" stroke-width="2"/>';
      s+='<text x="'+Math.min(R-20,Math.max(L+20,nx)).toFixed(1)+'" y="'+(T-20)+'" text-anchor="middle" font-size="12" font-weight="800" fill="#ff4fa3">Now</text>';
      const nxt=ev.find(e=>e.m>nm);
      cap='About '+nv.toFixed(1)+' ft and '+dir+' now'+(nxt?', '+nxt.kind.toLowerCase()+' tide at '+t12(nxt.time):'')+'.';}
    s+='</svg>';
    if(sun.sunrise&&sun.sunset){const a=hm(sun.sunrise), b=hm(sun.sunset), lowDay=ev.find(e=>e.kind==='Low'&&e.m>nm&&e.m<SPAN&&(e.m%1440)>=a&&(e.m%1440)<=b);
      if(lowDay)cap+=' Most sand showing at the beach: '+t12(lowDay.time)+(lowDay.m>=1440?' tomorrow':' today')+' ('+lowDay.ft+' ft).';}
    return '<div class="wtg"><div class="wtgs">'+s+'</div><p class="wsrc">'+cap+' Heights between the listed highs and lows are a smooth estimate, not a measurement.</p></div>';
  }
  let html='';
  for(const w of (W.warnings||[]))html+='<div class="wwarn">'+esc(w.title)+(w.valid?'<small>'+esc(w.valid)+'</small>':'')+'</div>';
  if(W.now&&W.now.temp){
    const bits=[];
    if(feels!=null)bits.push('Feels like '+Math.round(feels)+'°'+(comfort?' and '+comfort:''));
    bits.push('wind '+esc(W.now.wind),'humidity '+esc(W.now.rh));
    if(W.climate&&W.climate.sea_surface)bits.push('sea '+esc(W.climate.sea_surface.split('/')[0]));
    html+='<div class="whero '+mood+'"><div class="wnow"><span class="big">'+esc((W.now.temp.split('/')[0]||'').replace('°C','°'))+'</span><span class="sky">'+esc(W.now.sky)+'</span><span class="meta">'+bits.join(', ')+'<br>At the airport, '+esc(W.now.time)+'</span></div>'+scene()+'</div>';
  }
  if(W.headline)html+='<div class="whead">'+esc(W.headline)+'</div>';
  if(rainLine)html+='<p class="wnext">'+esc(rainLine)+'</p>';
  if(acts.length)html+='<div class="wacts" role="list" aria-label="'+(late?'Tomorrow':'Today')+' at a glance">'+acts.map(a=>'<div class="wact '+a[1].v+'" role="listitem"><b>'+a[0]+'</b><span class="v">'+word[a[1].v]+'</span><span class="y">'+esc(a[1].why)+'</span></div>').join('')+'</div>';
  html+='<div id="wradar"></div>';
  if(W.synopsis)html+='<p class="wsyn">'+esc(W.synopsis)+'</p>';
  html+='<div class="wcards">';
  for(const [p,cls] of [[today,'day'],[tonight,'eve']]){ if(!p.label)continue; html+='<div class="wcard '+cls+'"><h3>'+esc(p.label)+'</h3><div class="hl">'+esc(p.high?'High '+p.high:'')+esc(p.low?(p.high?', ':'')+'Low '+p.low:'')+(p.uv?', UV '+esc(p.uv):'')+'</div><p>'+esc((p.lines||[]).join(' '))+'</p></div>'; }
  html+='</div>';
  if(h.length){html+='<h2 class="w">Next 24 hours</h2><div class="wstrip">'+h.map((r,i)=>'<div class="whr'+(i===0?' now':'')+'"><div>'+hr(r.t)+'</div><div class="t">'+Math.round(r.temp)+'°</div><div class="r">'+(r.rain!=null?r.rain+'%':'')+'</div><div class="w">'+Math.round(r.wind)+' '+arrow((r.dir||0)+180)+'</div></div>').join('')+'</div><p class="wsrc">Rain chance and wind in knots from the Open-Meteo model. The words on this page are the Bermuda Weather Service, which is the one to trust when they disagree.</p>';}
  html+=dials();
  const week=W.forecast.slice(2);
  if(week.length){html+='<h2 class="w">The week</h2><div class="wweek">'+week.map(p=>'<div class="wday"><span class="d">'+esc(p.label)+'</span><span class="tx">'+esc((p.lines||[])[0]||'')+'</span><span class="hl">'+esc(p.high?p.high.split(' / ')[0]:'')+(p.low?' / '+esc(p.low.split(' / ')[0]):'')+'</span></div>').join('')+'</div>';}
  // The sea has its own tab (Ocean): ships first, then the boat day, sea state, marine forecast and tides.
  let ocean='<h2 class="xtitle">Ocean</h2><p class="xlead">Ships around the island, the boat day, the sea and the tides.</p>';
  for(const w of (W.warnings||[]))ocean+='<div class="wwarn">'+esc(w.title)+(w.valid?'<small>'+esc(w.valid)+'</small>':'')+'</div>';
  ocean+='<div id="oships"></div>';
  // Ships due this week, from the saved weekly schedule (ships-data). Cruise ships are marked.
  let SH={};try{SH=JSON.parse(document.getElementById('ships-data').textContent)}catch(e){}
  // Tap a ship: a panel under its day with what is known and links to see where it is now. Live positions are
  // not shown here because no free feed hears ships at Bermuda, so the links open VesselFinder and MarineTraffic.
  document.addEventListener('click',e=>{const b=e.target.closest('button.sbtn[data-ship]');if(!b)return;
    const x=(SH.ships||[])[+b.dataset.ship], row=b.closest('.sdue'), box=row&&row.querySelector('.sinfo');if(!x||!box)return;
    const was=b.getAttribute('aria-expanded')==='true';
    row.querySelectorAll('button.sbtn').forEach(o=>o.setAttribute('aria-expanded','false'));
    if(was){box.hidden=true;return}
    b.setAttribute('aria-expanded','true');
    const facts=[x.kind.charAt(0).toUpperCase()+x.kind.slice(1)].concat(x.built?['built '+x.built]:[],x.length_m?[x.length_m+' m long']:[]).join(', ');
    const said=(x.said_name||x.said_kind)?'<p class="wsrc" style="color:inherit;opacity:.75">The schedule called it '+esc(x.said_name||x.name)+(x.said_kind?', a '+esc(x.said_kind):'')+'.</p>':'';
    const vf=x.imo?'https://www.vesselfinder.com/vessels/details/'+x.imo:'https://www.vesselfinder.com/vessels?name='+encodeURIComponent(x.name);
    const mt='https://www.marinetraffic.com/en/ais/index/search/all?keyword='+encodeURIComponent(x.imo||x.name);
    box.innerHTML='<p><b>'+esc(x.name)+'</b></p><p>'+esc(facts)+'. Due '+esc(x.day)+'.</p>'+said
      +'<div class="wlinks"><a href="'+vf+'" target="_blank" rel="noopener">Where is it now: VesselFinder</a><a href="'+mt+'" target="_blank" rel="noopener">MarineTraffic</a></div>'
      +'<p class="wsrc" style="color:inherit;opacity:.75">'+(x.imo?'':'These links search by name, so pick the right ship from the list. ')+'The schedule gives the arrival day only.</p>';
    box.hidden=false;});
  if(SH&&SH.ships&&SH.ships.length){
    const bd=now.toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'}), days=[...new Set(SH.ships.map(x=>x.date))].sort();
    ocean+='<div class="wcard sea"><h3>Due in port this week</h3>'+days.map(d=>'<div class="sdue'+(d===bd?' now':d<bd?' past':'')+'"><b>'+esc(new Date(d+'T12:00:00Z').toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'short',timeZone:'UTC'}))+(d===bd?', today':'')+'</b>'+SH.ships.map((x,i)=>[x,i]).filter(a=>a[0].date===d).map(a=>'<button type="button" class="sbtn'+(a[0].kind==='cruise ship'?' cr':'')+'" data-ship="'+a[1]+'" aria-expanded="false">'+esc(a[0].name)+' <i>'+esc(a[0].kind)+'</i></button>').join('')+'<div class="sinfo" hidden></div></div>').join('')
      +'<p class="wsrc">Arrivals from the Department of Marine and Ports weekly schedule, as published by <a href="'+esc(SH.source)+'" target="_blank" rel="noopener" style="color:#2af0d9">Bernews</a>. The schedule changes, and it lists the day a ship arrives, not how long it stays.</p></div>';
  }
  // Superyachts: recent visits from the Bernews stories (read daily), where they berth and how big a yacht each
  // berth takes (kept by hand), and links to see what is in port now. No free feed lists the yachts in port.
  let SY={};try{SY=JSON.parse(document.getElementById('yachts-data').textContent)}catch(e){}
  if(SY&&(SY.berths||[]).length){
    const dshow=d=>d?new Date(d+'T12:00:00Z').toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'}):'';
    ocean+='<div class="wcard sea"><h3>Superyachts</h3>'+(SY.intro?'<p>'+esc(SY.intro)+'</p>':'')+(SY.stat?'<p class="pbnote">'+esc(SY.stat)+'</p>':'')
      +((SY.now||[]).length?'<p class="pbnote"><b>Who is in port now</b></p><div class="wlinks">'+SY.now.map(n=>'<a href="'+esc(n.url)+'" target="_blank" rel="noopener" style="color:#2af0d9">'+esc(n.name)+'</a>').join('')+'</div><p class="wsrc" style="color:inherit;opacity:.75">These open VesselFinder, which lists recent arrivals by type and size. It shows names only to its paying members.</p>':'')
      +((SY.visits||[]).length?'<p class="pbnote"><b>Notable visits in the news</b></p><ul class="tlist">'+SY.visits.slice(0,8).map(v=>'<li><b><a href="'+esc(v.url)+'" target="_blank" rel="noopener" style="color:inherit">'+esc(v.title)+'</a></b><span style="color:inherit;opacity:.8">'+[dshow(v.date),v.feet?v.feet+' ft':'',v.place?'at '+v.place:''].filter(Boolean).map(esc).join(', ')+'</span></li>').join('')+'</ul>':'')
      +'<p class="pbnote"><b>Where they berth</b></p>'+SY.berths.map(b=>'<div class="pbv" style="border-color:rgba(255,255,255,.18)"><h4>'+esc(b.name)+'</h4><p>'+esc(b.where)+'. '+esc(b.takes)+'.</p>'+(b.note?'<p>'+esc(b.note)+'</p>':'')+'<div class="wlinks"><a href="https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(b.lat+','+b.lon)+'" target="_blank" rel="noopener" style="color:#2af0d9">Map</a></div></div>').join('')
      +'<p class="wsrc" style="color:inherit;opacity:.75">'+((SY.visits||[]).length?'Visits are the ones Bernews wrote up, read on '+esc(SY.visits_read)+', so they are the notable yachts, not every call. ':'')+'Berth sizes are from the marinas&#39; own websites, checked on '+esc(SY.asof)+'.'+(SY.stale?' These details may be out of date.':'')+'</p></div>';
  }
  // Best beaches. Wind blowing onto a beach makes chop and shore break; wind blowing off it leaves the water flat.
  // Each beach has the bearing it faces, so the part of the wind that blows onshore is wind speed times the cosine
  // of the angle between the two. A cove takes about half of that away. Swell is not in the saved data.
  let XB=[];try{XB=(JSON.parse(document.getElementById('explore-data').textContent).sites||[]).filter(s=>s.kind==='beach'&&s.faces!=null)}catch(e){}
  if(XB.length&&(W.hourly||[]).length){
    const hNow=+bdaNow.slice(0,2), dInfo=d=>(W.days||[]).find(x=>x.date===d)||{}, dn0=dInfo(bdaDay).sunset?+dInfo(bdaDay).sunset.slice(0,2):18;
    const useToday=hNow<dn0-1, bDay=useToday?bdaDay:((W.days||[])[1]||{}).date, dn=dInfo(bDay).sunset?+dInfo(bDay).sunset.slice(0,2):18;
    const rows=(W.hourly||[]).filter(r=>r.t.slice(0,10)===bDay&&r.wind!=null&&r.dir!=null&&+r.t.slice(11,13)>=(useToday?hNow:9)&&+r.t.slice(11,13)<dn);
    if(rows.length){
      const rad=Math.PI/180, sx=rows.reduce((t,r)=>t+r.wind*Math.sin(r.dir*rad),0)/rows.length, cx=rows.reduce((t,r)=>t+r.wind*Math.cos(r.dir*rad),0)/rows.length;
      const kt=Math.round(rows.reduce((t,r)=>t+r.wind,0)/rows.length), wd=(Math.atan2(sx,cx)/rad+360)%360;
      const scored=XB.map(s=>{const on=Math.max(0,sx*Math.sin(s.faces*rad)+cx*Math.cos(s.faces*rad))*(s.cove?0.5:1);return {s:s,on:on}}).sort((a,b)=>a.on-b.on||a.s.name.localeCompare(b.s.name));
      const word=on=>on<5?'flat water':on<10?'light chop':on<16?'choppy':'rough';
      const calm=scored.filter(x=>x.on<5), mid=scored.filter(x=>x.on>=5&&x.on<16), rough=scored.filter(x=>x.on>=16);
      const row=x=>'<button type="button" class="bbeach" data-site="'+esc(x.s.id)+'"><b>'+esc(x.s.name)+'</b><span>'+esc(x.s.parish)+(x.s.cove?', sheltered cove':'')+'</span><i class="'+(x.on<5?'c':x.on<16?'m':'r')+'">'+word(x.on)+'</i></button>';
      const wet=Math.max(...rows.map(r=>r.rain||0)), when=useToday?'the rest of today':'tomorrow, 9am to sunset';
      ocean+='<div class="wcard"><h3>Best beaches '+(useToday?'today':'tomorrow')+'</h3><p>Wind from the '+['north','north east','east','south east','south','south west','west','north west'][Math.round(wd/45)%8]+' at about '+kt+' kt for '+when+(wet>=60?', with rain likely':'')+'. '
        +(kt<8?'Light wind, so almost every beach should be calm.':calm.length?'These are in its lee, so the water should be flattest there.':'It is blowing onto every beach on the list, so these are only the least exposed.')+'</p>'
        +(calm.length?calm:scored).slice(0,6).map(row).join('')
        +(rough.length?'<p class="tmuted" style="margin-top:10px"><b>Taking the wind head on:</b> '+rough.slice(-6).reverse().map(x=>esc(x.s.name)).join(', ')+'.</p>':'')
        +(mid.length||calm.length>6?'<details class="bmore"><summary>All '+scored.length+' beaches, calmest first</summary>'+scored.map(row).join('')+'</details>':'')
        +'<p class="wsrc">Worked out from the wind forecast and the way each beach faces. It does not know about swell, which can wrap round onto a beach the wind is blowing off, or about rip currents. Look before you swim.</p></div>';
    }
  }
  if(W.marine&&W.marine.periods&&W.marine.periods.length){ocean+='<h2 class="w">On the water</h2>'+(W.marine.synopsis?'<p class="wsyn">'+esc(W.marine.synopsis)+'</p>':'')+'<div class="wcards">'+boatCard()+seaCard()+W.marine.periods.slice(0,3).map(p=>'<div class="wcard sea"><h3>'+esc(p.label)+'</h3><p>'+esc((p.lines||[]).join(' '))+'</p></div>').join('')+'</div>';}
  if(tides.length){ocean+='<h2 class="w">Tides at St George&#39;s</h2>'+tideGraph()+'<div class="wtides">'+tides.map(d=>'<div class="wtide"><b>'+esc(d.day)+'</b>'+d.events.map(e=>'<div class="'+(e.kind==='High'?'hi':'')+'">'+esc(e.kind)+' '+esc(e.time)+' <span style="opacity:.6">'+esc(e.ft)+' ft</span></div>').join('')+'</div>').join('')+'</div>';}
  ocean+='<div class="wcard"><h3>Kite, wing foil or windsurf?</h3><p>The wind hour by hour and the beaches that work in it are on the Sports tab.</p><div class="wlinks"><a href="#sports" id="ocsports">Open wind sports</a></div></div>';
  ocean+='<p class="wsrc">Marine forecast and tides from the Bermuda Weather Service, issued '+esc(W.issued)+'. Collected '+esc(W.asof)+'.</p>';
  const ocEl=document.getElementById('oc'); if(ocEl){ocEl.innerHTML=ocean;ocEl.addEventListener('click',e=>{const b=e.target.closest('button[data-site]');if(b)document.dispatchEvent(new CustomEvent('hub-open',{detail:b.dataset.site}))});const os=document.getElementById('ocsports');if(os)os.addEventListener('click',e=>{e.preventDefault();go('sports')});}
  html+='<div class="wcard sea"><h3>Heading out on the water?</h3><p>Ships, the boat day, the sea state, the marine forecast and the tides now live on the Ocean tab.</p><div class="wlinks"><a href="#ocean" id="wxocean">Open Ocean</a></div></div>';
  html+=tankCard()+'<div id="wtropics"></div>';
  const CAMS=[['Hamilton Harbour, RHADC','https://www.webcamtaxi.com/en/bermuda/paget-parish/rhadc-hamilton-harbor-cam.html'],['St George&#39;s Harbour','https://www.skylinewebcams.com/webcam/bermuda/st-george-s-parish/st-george-s-parish/st-george-s-harbour.html'],['King&#39;s Square, St George&#39;s','https://www.skylinewebcams.com/webcam/bermuda/st-george-s-parish/st-george-s-parish/st-george-s-town-square-bermuda.html']];
  html+='<h2 class="w">Live cameras</h2><div class="wlinks">'+CAMS.map(c=>'<a href="'+c[1]+'" target="_blank" rel="noopener">'+c[0]+' ↗</a>').join('')+'</div>';
  if(W.radar&&W.radar.links)html+='<h2 class="w">More from the weather service</h2><div class="wlinks">'+W.radar.links.map(l=>'<a href="'+esc(l.url)+'" target="_blank" rel="noopener">'+esc(l.name)+' ↗</a>').join('')+'</div>';
  html+='<p class="wsrc">Bermuda Weather Service forecast issued '+esc(W.issued)+(W.next_update?', next update '+esc(W.next_update):'')+'. Collected '+esc(W.asof)+'.</p>';
  el.innerHTML=html;
  {const wo=document.getElementById('wxocean');if(wo)wo.addEventListener('click',e=>{e.preventDefault();go('ocean')});}
  tankWire();
  // Today tab: the weather in a few lines, and the boat verdict
  {const c=document.getElementById('td-wx'), nx=(()=>{const hmNow=bdaNow;const t=(W.tides||[]).find(d=>d.date===bdaDay);const e=t&&t.events.find(x=>x.time>hmNow);return e?e.kind+' tide '+t12h(e.time):''})();
    if(c&&W.now&&W.now.temp)c.innerHTML='<h3>Weather</h3><p class="tbig">'+esc((W.now.temp.split('/')[0]||'').replace('°C','°'))+' <span>'+esc(W.now.sky)+(feels!=null?', feels like '+Math.round(feels)+'°':'')+'</span></p>'+(W.headline?'<p><b>'+esc(W.headline)+'</b></p>':'')+(rainLine?'<p>'+esc(rainLine)+'</p>':'')+'<p class="tmuted">'+[nx,sun.sunset?'sunset '+t12h(sun.sunset):''].filter(Boolean).join(', ')+'</p>'+(acts.length?'<div class="tacts">'+acts.map(a=>'<span class="'+a[1].v+'">'+a[0]+': '+word[a[1].v]+'</span>').join('')+'</div>':'')+'<button type="button" data-go="weather">Full weather and radar</button>';
    const bc=document.getElementById('td-boat'); if(bc&&boats.length){bc.hidden=false;bc.innerHTML='<h3>On the water</h3>'+boats.map(boatLine).join('')+'<button type="button" data-go="ocean">Ships, marine forecast and tides</button>';}
    document.body.dataset.mood=mood; if(window.hubSuggest)window.hubSuggest(mood);}
  // ---- Ships around Bermuda, on the Ocean tab. GitHub Pages copy only (the artifact viewer blocks outside frames).
  // Two free live maps. MarineTraffic is a plain frame and has its own satellite layer button; VesselFinder's embed is a
  // script that writes its own frame, so it runs inside a small frame of ours. The map loads the first time the tab opens.
  (function(){
    const sb=document.getElementById('oships'), host=location.hostname; if(!sb)return;
    if(!(host.endsWith('github.io')||host==='localhost'||host==='127.0.0.1'||location.protocol==='file:')){
      sb.innerHTML='<div class="wcard sea"><h3>Ships around Bermuda</h3><p>The live ship map cannot load in this copy of the Hub. It works on the website: <a href="https://mkatzsch.github.io/bermuda-hub/#ocean" target="_blank" rel="noopener" style="color:#2af0d9">mkatzsch.github.io/bermuda-hub</a></p></div>';return}
    const keep=(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}}, recall=k=>{try{return localStorage.getItem(k)}catch(e){return null}};
    let shipZoom=recall('hub-ship-zoom')==='7'?'7':'10', shipSrc=recall('hub-ship-src')==='vf'?'vf':'mt';
    sb.innerHTML='<div class="wmap"><h2 class="w" style="margin:0 0 10px">Ships around Bermuda</h2><div class="wrseg" role="group" aria-label="Ship map range" style="margin-bottom:10px"><button type="button" data-z="10">Around the island</button><button type="button" data-z="7">Ships on the way</button><button type="button" data-p="mt">MarineTraffic</button><button type="button" data-p="vf">VesselFinder</button></div><iframe class="wwf" id="wsf" title="Live map of ships around Bermuda"></iframe><p class="wsrc" id="osnote"></p></div>';
    function paint(force){
      sb.querySelectorAll('button[data-z]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.z===shipZoom?'true':'false'));
      sb.querySelectorAll('button[data-p]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.p===shipSrc?'true':'false'));
      const f=document.getElementById('wsf'), want=shipSrc+shipZoom;
      if(force||f.dataset.on!==want){
        f.dataset.on=want; f.removeAttribute('srcdoc'); f.removeAttribute('src');
        if(shipSrc==='mt')f.src='https://www.marinetraffic.com/en/ais/embed/zoom:'+(shipZoom==='7'?'8':'11')+'/centery:32.31/centerx:-64.76/maptype:1/shownames:true/mmsi:0/shipid:0/fleet:/fleet_id:/vtypes:/showmenu:/remember:false';
        else f.srcdoc='<body style="margin:0;background:#0b1820"><scr'+'ipt>var width="100%";var height="460";var latitude="32.31";var longitude="-64.76";var zoom="'+shipZoom+'";var names=true;</scr'+'ipt><scr'+'ipt src="https://www.vesselfinder.com/aismap.js"></scr'+'ipt></body>';
      }
      document.getElementById('osnote').textContent='Live ship positions from '+(shipSrc==='mt'?'MarineTraffic. Use the layers button on the map for the satellite picture.':'VesselFinder.')+' Tap a ship for its name, type and destination. Only boats that broadcast their position appear, so most small boats in the marinas will not.';
    }
    sb.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;if(b.dataset.z){shipZoom=b.dataset.z;keep('hub-ship-zoom',shipZoom)}else if(b.dataset.p){shipSrc=b.dataset.p;keep('hub-ship-src',shipSrc)}else return;paint(true)});
    const wait=setInterval(()=>{if(ocSec.hidden)return;clearInterval(wait);paint()},400);
  })();
  // ---- Live map panel, GitHub Pages copy only (the artifact viewer blocks outside pictures and frames, so that copy
  // keeps the links). One panel, two modes: Radar (Bermuda Weather Service pictures) and Windy (forecast map). Ships are on the Ocean tab.
  // BWS names each radar frame by its UTC time and drops old ones, so the page works out the recent names itself
  // and keeps the ones that load. Plus zooms in toward the parishes, minus zooms out to 500 km.
  const box=document.getElementById('wradar'), host=location.hostname;
  if(box&&(host.endsWith('github.io')||host==='localhost'||host==='127.0.0.1'||location.protocol==='file:')){
    const BASE='https://weather.bm/images/';
    const VIEWS=[
      {k:'parish',label:'Parishes',dir:'Radar/RadarParish/',suf:'_ParishRadar.png',step:6,ph:1,note:'Rainfall radar over the parishes'},
      {k:'sat',label:'Satellite',dir:'Satellite/LocalVisIRRadarSferic/',suf:'_SAT004.jpeg',step:5,ph:0,note:'Satellite cloud with radar and lightning'},
      {k:'r100',label:'100 km',dir:'Radar/CurrentRadarAnimation_100km_sri/',suf:'_100km_sri.png',step:6,ph:1,note:'Rainfall radar, 100 km'},
      {k:'r250',label:'250 km',dir:'Radar/CurrentRadarAnimation_250km_sri/',suf:'_250km_sri.png',step:6,ph:1,note:'Rainfall radar, 250 km'},
      {k:'r500',label:'500 km',dir:'Radar/CurrentRadarAnimation_500km_dBZ_0deg/',suf:'_500km_dBz_0deg.png',step:6,ph:0,note:'Radar reflectivity, 500 km'}];
    const LAYERS=[['wind','Wind'],['gust','Gusts'],['rain','Rain'],['waves','Waves']];
    const windySrc=o=>'https://embed.windy.com/embed.html?type=map&location=coordinates&metricRain=default&metricTemp=default&metricWind=kt&zoom=8&overlay='+o+'&product=ecmwf&level=surface&lat=32.31&lon=-64.76&message=true';
    const stampAt=d=>{const s=d.toISOString();return s.slice(0,10)+'-'+s.slice(11,13)+s.slice(14,16)};
    const probe=u=>new Promise(res=>{const im=new Image();im.onload=()=>res(im.naturalWidth>1?u:null);im.onerror=()=>res(null);im.src=u});
    const clock=u=>{const n=u.slice(u.lastIndexOf('/')+1);const d=new Date(n.slice(0,10)+'T'+n.slice(11,13)+':'+n.slice(13,15)+':00Z');
      return d.toLocaleTimeString('en-US',{timeZone:'Atlantic/Bermuda',hour:'numeric',minute:'2-digit'}).toLowerCase()};
    const keep=(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}}, recall=k=>{try{return localStorage.getItem(k)}catch(e){return null}};
    const $=id=>document.getElementById(id);
    let vi=Math.max(0,VIEWS.findIndex(v=>v.k===recall('hub-radar-view')));
    let mode=recall('hub-map-mode')==='windy'?'windy':'radar';
    let layer=LAYERS.some(l=>l[0]===recall('hub-windy-layer'))?recall('hub-windy-layer'):'wind';
    let frames=[], i=0, playing=true, timer=null, started=false, token=0;
    async function find(v){
      const all=[];for(let k=0;k<75;k++){const d=new Date(Date.now()-k*60000);all.push({u:BASE+v.dir+stampAt(d)+v.suf,m:d.getUTCMinutes()});}
      let hits=(await Promise.all(all.filter(x=>x.m%v.step===v.ph).map(x=>probe(x.u)))).filter(Boolean);
      if(hits.length<2)hits=(await Promise.all(all.map(x=>probe(x.u)))).filter(Boolean);
      return Array.from(new Set(hits)).sort().slice(-10);
    }
    function show(){
      $('wrimg').src=frames[i];
      $('wrtime').textContent=clock(frames[i]);
      $('wrn').textContent=(i+1)+' of '+frames.length;
    }
    function tick(){
      clearTimeout(timer); if(!playing||mode!=='radar'||frames.length<2)return;
      i=(i+1)%frames.length; show();
      timer=setTimeout(tick,i===frames.length-1?1800:500);
    }
    function shell(){
      box.innerHTML='<div class="wmap"><div class="wmtog" role="group" aria-label="Map"><button type="button" data-m="radar">Radar</button><button type="button" data-m="windy">Windy</button></div>'+
        '<div id="wmradar"><div class="wradar"><img id="wrimg" alt=""><span class="wrview" id="wrview"></span><div class="wrzoom"><button type="button" id="wrin" aria-label="Zoom in" title="Zoom in">+</button><button type="button" id="wrout" aria-label="Zoom out" title="Zoom out">−</button></div></div>'+
        '<div class="wrbar" style="margin-top:10px"><button id="wrplay" type="button">Pause</button><span class="t" id="wrtime"></span><span class="n" id="wrn"></span></div></div>'+
        '<div id="wmwindy" hidden><div class="wrseg" role="group" aria-label="Windy layer" style="margin-bottom:10px">'+LAYERS.map(l=>'<button type="button" data-o="'+l[0]+'">'+l[1]+'</button>').join('')+'</div><iframe class="wwf" id="wwf" title="Windy forecast map for Bermuda"></iframe></div>'+
        '<p class="wsrc" id="wrnote"></p></div>';
      box.querySelector('.wmtog').addEventListener('click',e=>{const b=e.target.closest('button[data-m]');if(!b)return;mode=b.dataset.m;keep('hub-map-mode',mode);paint()});
      $('wrin').addEventListener('click',()=>{if(vi>0){vi--;keep('hub-radar-view',VIEWS[vi].k);load()}});
      $('wrout').addEventListener('click',()=>{if(vi<VIEWS.length-1){vi++;keep('hub-radar-view',VIEWS[vi].k);load()}});
      $('wrplay').addEventListener('click',e=>{playing=!playing;e.target.textContent=playing?'Pause':'Play';if(playing)tick();else clearTimeout(timer)});
      $('wmwindy').addEventListener('click',e=>{const b=e.target.closest('button[data-o]');if(!b)return;layer=b.dataset.o;keep('hub-windy-layer',layer);paint(true)});
    }
    function paint(force){
      if(!$('wrimg'))shell();
      box.querySelectorAll('.wmtog button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.m===mode?'true':'false'));
      $('wmradar').hidden=mode!=='radar'; $('wmwindy').hidden=mode!=='windy';
      if(mode==='windy'){
        clearTimeout(timer);
        box.querySelectorAll('#wmwindy button[data-o]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.o===layer?'true':'false'));
        const f=$('wwf'); if(force||!f.getAttribute('src'))f.src=windySrc(layer);
        $('wrnote').textContent='Forecast model map from Windy.com. Press play on the map to run the days ahead. For rain falling right now, switch to Radar.';
      }else load();
    }
    async function load(){
      const v=VIEWS[vi], mine=++token;
      $('wrview').textContent=v.label; $('wrin').disabled=vi===0; $('wrout').disabled=vi===VIEWS.length-1;
      $('wrnote').textContent='Loading '+v.label+'...';
      const got=await find(v);
      if(mine!==token||mode!=='radar')return;
      clearTimeout(timer);
      if(!got.length){$('wrnote').textContent='No '+v.label+' pictures from the Bermuda Weather Service in the last hour. Zoom in or out, or use the links at the bottom of the page.';return;}
      frames=got; i=frames.length-1; show();
      $('wrimg').alt=v.note+', Bermuda Weather Service';
      $('wrnote').textContent=v.note+' from the Bermuda Weather Service, last hour, newest picture held longest. Plus zooms in, minus zooms out.';
      if(playing)timer=setTimeout(tick,1800);
    }
    function tropics(){
      const tb=$('wtropics'), mth=+now.toLocaleDateString('en-CA',{timeZone:'Atlantic/Bermuda'}).slice(5,7); if(!tb)return;
      if(mth<6||mth>11){tb.innerHTML='<h2 class="w">Tropics</h2><p class="wsyn">Hurricane season runs from 1 June to 30 November. Nothing to track right now.</p>';return;}
      tb.innerHTML='<h2 class="w">Tropics</h2><a class="wtrop" href="https://www.nhc.noaa.gov/gtwo.php?basin=atlc&amp;fdays=7" target="_blank" rel="noopener"><img alt="National Hurricane Center seven day tropical weather outlook for the Atlantic" loading="lazy" src="https://www.nhc.noaa.gov/xgtwo/two_atl_7d0.png?h='+Math.floor(Date.now()/3600000)+'"></a><p class="wsrc">Seven day outlook from the US National Hurricane Center, updated about every six hours in season. Tap the map for the full discussion.</p>';
    }
    const wait=setInterval(()=>{
      if(wxSec.hidden||started)return;
      started=true; clearInterval(wait); paint(); tropics();
      setInterval(()=>{if(!document.hidden&&!wxSec.hidden&&mode==='radar')load()},6*60000);
    },400);
  }
})();

// ---- Shared grocery list (artifact db capability). Works for anyone invited who can write; read only otherwise.
(function(){
  const status=document.getElementById('lstatus'), items=document.getElementById('litems'), bestEl=document.getElementById('lbest');
  const BEST=(()=>{try{return JSON.parse(document.getElementById('best-buys').textContent.replace(/<\\\\\\//g,'</'))}catch(e){return {asof:'',items:[]}}})();
  document.getElementById('lbestnote').textContent=BEST.items.length?('From the deals page'+(BEST.asof?' ('+BEST.asof+')':'')+'. Tap + to add one to the list.'):'No best buys in this build yet.';
  let db=null, canWrite=false, rows=[];
  const esc=t=>String(t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  function renderBest(){
    bestEl.innerHTML=BEST.items.map((b,i)=>'<div class="bcard"><div class="b"><div class="t">'+esc(b.name)+'</div><div class="s">'+esc(b.store)+' $'+esc(b.price)+' '+esc(b.unit)+'</div><div class="w">'+esc(b.why)+'</div></div><button type="button" data-i="'+i+'" aria-label="Add to list"'+(canWrite?'':' disabled')+'>+</button></div>').join('');
  }
  function render(){
    if(!rows.length){items.innerHTML='<p class="lnote">Nothing on the list.</p>';return}
    const groups={};
    for(const r of rows){(groups[r.store||'Any store']=groups[r.store||'Any store']||[]).push(r)}
    items.innerHTML=Object.keys(groups).sort().map(g=>'<div class="lgroup"><h3>'+esc(g)+'</h3>'+groups[g].map(r=>'<div class="litem'+(r.done?' done':'')+'" data-id="'+esc(r.id)+'"><input type="checkbox"'+(r.done?' checked':'')+(canWrite?'':' disabled')+' aria-label="Done"><span class="n">'+esc(r.name)+'</span>'+(r.note?'<span class="p">'+esc(r.note)+'</span>':'')+(canWrite?'<button class="x" type="button" aria-label="Remove">&times;</button>':'')+'</div>').join('')+'</div>').join('');
  }
  renderBest(); render();
  async function start(){
    if(!window.claude||typeof claude.use!=='function'){status.textContent='The shared list only works on the published Hub link (not the local copy).';return}
    db=await claude.use('db');
    if(!db){status.textContent='Sign in to the Hub link to see the shared list.';return}
    const user=await claude.use('user');
    const cw=user?await user.can('data.write'):null;
    canWrite=cw!==false;  // null: not told, keep the inputs and let a refused write decide
    if(!canWrite)status.textContent='You can see the list but not change it (ask Matt to share the Hub with you as an Editor).';
    renderBest(); render();
    let timer=setTimeout(()=>{status.textContent='The list cannot be reached yet; it may be out of date.'},10000);
    db.collection('list').orderBy('ts').limit(300).onSnapshot(snap=>{
      rows=snap.docs.map(d=>Object.assign({id:d.id},d.data()));
      if(!snap.metadata.fromCache){clearTimeout(timer);status.textContent=canWrite?'Shared with everyone who has the Hub. Tick things off as you shop.':status.textContent}
      render();
    },e=>{clearTimeout(timer);status.textContent='The shared list is unavailable right now.';});
  }
  async function add(name,store,note){
    if(!db||!name)return;
    try{await db.collection('list').add({name:name.slice(0,80),store:store||'',note:note||'',done:false,ts:Date.now()})}
    catch(e){if(e&&e.code==='invalid_argument'){canWrite=false;status.textContent='You can see the list but not change it (ask Matt to share the Hub with you as an Editor).';renderBest();render()}else status.textContent='Could not add that just now.'}
  }
  document.getElementById('ladd').addEventListener('submit',async e=>{e.preventDefault();const n=document.getElementById('lname');const v=n.value.trim();if(!v)return;n.value='';await add(v,document.getElementById('lstore').value,'')});
  bestEl.addEventListener('click',async e=>{const b=e.target.closest('button[data-i]');if(!b)return;const it=BEST.items[+b.dataset.i];b.disabled=true;await add(it.name,it.store,'$'+it.price+' '+it.unit);b.disabled=!canWrite});
  items.addEventListener('change',async e=>{const cb=e.target;if(cb.type!=='checkbox'||!db)return;const id=cb.closest('.litem').dataset.id;try{await db.doc('list/'+id).update({done:cb.checked})}catch(x){}});
  items.addEventListener('click',async e=>{const x=e.target.closest('.x');if(!x||!db)return;const id=x.closest('.litem').dataset.id;try{await db.doc('list/'+id).delete()}catch(y){}});
  document.getElementById('lclear').addEventListener('click',async()=>{if(!db)return;for(const r of rows.filter(r=>r.done)){try{await db.doc('list/'+r.id).delete()}catch(e){}}});
  document.getElementById('lclearall').addEventListener('click',async e=>{if(!db||!rows.length)return;const b=e.currentTarget;if(b.dataset.sure!=='1'){b.dataset.sure='1';b.textContent='Tap again to clear all';setTimeout(()=>{b.dataset.sure='';b.textContent='Clear all'},4000);return}b.dataset.sure='';b.textContent='Clear all';for(const r of rows){try{await db.doc('list/'+r.id).delete()}catch(e){}}});
  start();
})();
</script></div></body></html>
"""


def main(argv: list[str]) -> int:
    os.makedirs(SITE, exist_ok=True)
    build_only = "--build" in argv
    want_deals = "--deals" in argv or "--all" in argv or not any(a in argv for a in ("--events",))
    want_events = "--events" in argv or "--all" in argv or (dt.date.today().weekday() in EVENT_DAYS and "--deals" not in argv)
    log("=== hub run %s ===" % " ".join(argv))
    if want_deals:
        deals(collect=not build_only)
    if want_events:
        events(collect=not build_only)
    elif not build_only:
        # not a planner day: still refresh the weather and re-render (today's date, cinema board unchanged)
        db = os.path.join(EVENTS, "data", "tidewatch.sqlite")
        if os.path.exists(db):
            run(["-m", "tidewatch", "weather"], EVENTS, "weather")
            run(["-m", "tidewatch", "render"], EVENTS, "events render")
        else:
            events(collect=False)
    elif not os.path.exists(os.path.join(SITE, "planner.html")):
        events(collect=False)
    if "--guide" in argv or not build_only:
        fieldguide_collect(force="--guide" in argv)
    if "--photos" in argv or not build_only:
        try:  # once every 30 days at most
            photos_collect(force="--photos" in argv)
        except Exception as e:  # never let the photo search stop a build
            log("photos: skipped (%s)" % str(e)[:120])
    try:  # once a week at most
        transit_collect(force="--transit" in argv)
    except Exception as e:  # never let the timetables stop a build
        log("transit: skipped (%s)" % str(e)[:120])
    try:  # one small page, once a day at most, so it also runs on a plain rebuild
        ships_collect(force="--ships" in argv)
    except Exception as e:  # never let the ship list stop a build
        log("ships: skipped (%s)" % str(e)[:120])
    try:
        yoga_collect(force="--yoga" in argv)
    except Exception as e:  # never let the yoga timetables stop a build
        log("yoga: skipped (%s)" % str(e)[:120])
    try:
        superyachts_collect(force="--yachts" in argv)
    except Exception as e:  # never let the superyacht news stop a build
        log("superyachts: skipped (%s)" % str(e)[:120])
    front_door()
    backup()
    publish_github()
    log("hub done")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
