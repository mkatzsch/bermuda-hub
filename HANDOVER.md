# Bermuda Hub handover, Tuesday 24 November 2026 (updated 5:25pm after the first full build of 1.90 to 1.96)

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub

## Start here

1. A full build ran at 5:19pm on Tuesday 24 November with the laptop awake. The log ended "hub done" and
   pushed to GitHub. EVERYTHING in this note is now live on the website: run.py 1.96, 216 On this day
   events, 298 Explore places. The section below headed "Saved on the laptop, waiting for a build" is
   therefore live too. Read it as a list of what was added, not as work still waiting.
2. The built page was opened in a phone sized browser: no page errors, 18 cards on Today, 22 kinds in
   Explore. Nothing from 1.90 to 1.96 has been checked on a real phone yet.
3. `otd_mine.bat` was run at 5:25pm with otd_mine.py 1.1: 396 candidates, 269 of them on dates not yet in
   the Hub. The extra titles found nothing new and 14 titles still have no article (see
   otd_mine_output.log). All 269 were then read: 17 were added to onthisday.json (233 events now, sources
   in onthisday_drafts.json under mined_drafts) and went live with the 5:40pm build, which ended "hub
   done". The rest were lists, citation dates, politics, not about Bermuda, or dates that disagree.
   Still worth a read of the full article: six candidates from the 1649 to 1652 standoff with Parliament
   (Governor of Bermuda article) and five garrison and Dockyard lines that do not name the unit or ship.
4. The Claude artifact has not been republished since 7:03am. The website is the current copy.
5. Christmas is live now (Matt said yes to the look on 24 Nov and asked for it at once). seasons.json: the
   Christmas occasion starts 11-24, not 12-01. Next year set the start date again. run.py 1.97: the planner
   events for an occasion are put in date order and days gone are dropped before the cut to 60 (the cut used
   to come first and lost late events). Built 5:45pm, "hub done". The built page was opened at phone size
   with no ?season on the address: lights, tree, Today card and a list of 64 from 25 Nov to 21 Dec, no page
   errors. Later dates roll in as days pass. run.py 1.98 (built 5:51pm, "hub done"): the Today card leads
   with the next three things on, and planner events listed twice under two names (same day, same time,
   names and venues sharing words) show once. Left alone because the two listings disagree: the Nutcracker
   on 11 Dec (6.30pm Earl Cameron Theatre or 7.30pm Ruth Seaton James), the UberVida parade cruise on 6 Dec
   (5pm or 6.45pm). Still twice: the UberVida Ugly Sweater party on 18 Dec (venues worded differently). Not seen on a real phone.
6. Close buttons (Matt's ask, 24 Nov): run.py 1.99 and events/template/planner.html 1.2, built 5:56pm, "hub
   done". Every card that opens over the page has the same Close pill in the top right (class hubx): Explore
   sheets, the timeline, the occasion list, the search panel, the Report form and the planner's event card.
   The real build was opened at phone size and each one closed, no page errors. The Explore sheets still
   have their old Close in the row of buttons at the bottom as well. Map pin bubbles keep the map's own x.
7. Matt finds the Christmas list a little overwhelming (24 Nov). Offered: fold the repeats (Tea with Santa,
   the camps) into one line each, group by This week / Next week / Later, and buttons by kind. Recommended
   the first two. Waiting for his pick. Nothing built.
8. One planner event (2026 Bermuda National Criterium Championships, 1 Nov) has a note ending in a cut off
   email address ("president@"). The repo is public: the note needs trimming at the source.

## Totals (live since the 5:19pm build)

- run.py 1.96.
- explore.json: 298 places, 24 walks, 17 Island stories cards, 19 cards under People (14 of their own, 5 shared).
- onthisday.json: 216 events. quiz.json: 60 questions and 25 for kids.
- New files on 24 Nov: seasons.json, quiz.json, feedback.json, feedback_script.gs, papers_mine.py and .bat.

## Check on a real phone

- Today: the Daily quiz and its kids switch, the timeline button, History near me, the Christmas card with
  ?season=xmas on the address, and that tapping the tree opens the list with real planner events under it.
- Explore: the People tile, a story walk (the "Read the story" button), the map after picking a kind.
- That the Report button stays hidden (no address in feedback.json yet).
- Page weight. It was 2.6 MB before 24 Nov and is heavier now.
- Whether the planner lists the Red Cross Jingle Run, the Walkabout, the MarketPlace parade and the Boat
  Parade. The "match" words in seasons.json should stop them showing twice in the Christmas list.
- Christmas switches on by itself on 1 December, Bermuda time.

## The English Market (asked for on 24 Nov, not built)

- Matt wants it on the Deals page. The Hamilton store moved in February 2026 from the Washington Mall to
  55 Front Street. Second store at the Esso station, Rose Hill, St George's.
- No readable price source found. Facebook blocks automated reading. Its own site, theenglishmarket.com,
  may show prices but could not be opened from the phone session: Matt needs to paste the link into chat.
- Standing discounts reported in the press (10 per cent on Tuesdays, 5 per cent for seniors) are from 2022
  and 2023 and need confirming before they go on the page.
- Fallback: list the store with its locations and confirmed standing discounts, no weekly prices.

## What is live (website, built 7:24am, run.py 1.89)

- Today is a home screen: search bar, a one line brief, nine tiles, "What is near me", "Your shortcuts"
  (most opened, kept on the phone), five cards in view and the rest under "More for today".
- Explore opens on kinds of place (tiles with counts). Map and cards appear after a kind is picked.
- Sports is three groups: On the water, On land, Fitness and classes.
- Timetable layout (day buttons, a button per gym, time column, fact card per gym) for Gyms, CrossFit,
  Dance and Yoga.
- Today cards: Open late and urgent care, School holidays, On this day, Roads (Bernews and Royal Gazette),
  Power (BELCO blocks its map from being embedded, the build rechecks every run).
- Works with no signal (site/sw.js). Already installable from the browser.
- Explore group "Island stories": Hamilton street names, St George's alleys, Hurricanes.
- War graves sections on three cemetery cards. BIOS card has "The long records".
- Deals: MarketPlace button stays visible when it has no ad. Gorham's line in Hamilton retail.

## Saved on the laptop, waiting for a build

- run.py 1.90: "Read the story" button on On this day events that carry an Explore card id.
- run.py 1.91: a "Report" button in the header (short form, sent to a private Google Sheet), the Hub's own
  error reports (three a day per phone at most) and a "Fixed lately" line on the Today tab. All of it is
  switched off until events/data/feedback.json holds the web app address. Tested in a phone sized browser
  with a stand in for Google, not against the real sheet.
- run.py 1.92: story walks. A route in explore.json can carry "story" (an Island stories card id). It is
  then labelled "Story walk" and gets a "Read the story" button. Three walks use it: `walk-freedom`
  (Hamilton), `walk-convicts` (Dockyard) and `walk-blockade` (St George's). Three new pinned sights in
  Hamilton (`sight-we-arrive`, `sight-when-voices-rise`, `sight-sally-bassett`), pins from Waymarking.
  Explore and the On this day card were test rendered in a phone sized browser with today's real
  explore.json and onthisday.json: every new card and walk opened, with no page errors. A full build has
  still not been run.
- run.py 1.93: Daily quiz card on Today (events/data/quiz.json, 48 questions, one a day in order), a
  "See the whole timeline" button on the On this day card, "History near me" beside "What is near me",
  and a new Explore kind, People, with the eight National Heroes (`people-...`). A fourth story walk,
  `walk-boers`. All of it was test rendered with the real data files in a phone sized browser with a
  stand in location in Hamilton: no page errors. Still no full build.
- Added after 1.93 (data only): People cards for Pilot James Darrell, Joseph Rainey, the Progressive Group
  and Chesley Trott; a pinned card for Pilot Darrell's House (pin from the Historical Marker Database);
  walks `walk-freedom-stg` and `walk-wars`; four single person cards also listed under People through
  the "also" field; 52 quiz questions.
- run.py 1.94: the Daily quiz has a kids list (20 questions under "kids" in quiz.json) and a link to
  switch. Also data only: `people-somers`, pinned cards `sight-somers-garden` (pin from the Historical
  Marker Database) and `sight-somers-statue` (pin from Waymarking), walks `walk-sea-venture` and
  `walk-mary-prince`, the Mary Prince Emancipation Park note on `devonshire-bay-beach`, 54 quiz questions.
  Test rendered with the real files, no page errors.
- Park walks (24 Nov, data only, no run.py change): `walk-ferry-reach`, `walk-spittal-pond` and
  `walk-coopers`, with story cards `story-ferry-reach`, `story-spittal-pond`, `story-hog-bay` and two
  new pins, `sight-lovers-lake` (Ramsar site map) and `sight-portuguese-rock` (OpenStreetMap). Hog Bay
  has `walk-hog-bay` (Somerset Bridge pin to the park pin, the loop told in words): no pins were found for
  its kiln, cottages or Sugar Loaf Hill. Its cards now say 32 acres (National Trust), not 38. Jeffrey's
  Cave, the Checkerboard, Ferry Island Fort and Burnt Point Fort also have no pins yet. Best fixed by
  standing on each spot with a phone and noting the position. The line that the railway closed in 1948
  rests on my own knowledge.
- run.py 1.95: seasonal trim on the Hub header only (Matt's idea, 24 Nov). December: coloured lights and a
  tree. January to March: a pale line and a whale. Other months plain. Try one with ?season=xmas, winter or
  off on the address. Matt has seen test pictures but not said yes to the look. Spring, summer and autumn
  looks, and the Events and Deals pages inside the Hub, are not done. Also new walks from existing pins:
  `walk-walsingham` and `walk-scaur`.
- run.py 1.96: occasions replace the fixed looks of 1.95. `events/data/seasons.json` (new, kept by hand)
  holds Christmas (1 Dec to 1 Jan) and whale season (1 Mar to 30 Apr). While one is on, the header emblem is
  a button and Today has a card at the top; both open the main dates plus planner events that match the
  occasion's words. Try with ?season=xmas or whales. The 2026 dates in it (Walkabout 4 Dec, MarketPlace
  parade 6 Dec, Boat Parade 12 Dec) were checked on 24 Nov. The parade date comes from a directory listing,
  not a MarketPlace press release, and the route is the 2023 to 2025 one: check again nearer the day. Tested
  with a made up planner page, not a real build. More occasions to add: Good Friday kites, Bermuda Day, Cup
  Match, Harbour Nights.
- Charities, first pass (24 Nov): `story-reserves` (Audubon Society and Buy Back Bermuda), a new pin
  `sight-somerset-long-bay-west` (Ramsar position) and `walk-long-bay`. No pin was found for Seymour's Pond,
  so it has no card of its own. Not yet mined: Keep Bermuda Beautiful, BEST, the St George's Foundation,
  the Historical Society, the Garden Club, the Turtle Project, the SPCA, and charity walks and tag days for
  the Events page.
- Sculptures (Matt's idea, 24 Nov): `sight-qe-sculpture`, `sight-point-pleasant`, `sight-figurehead` (on the
  Great Head Park pin, marked approximate), `people-ming`, a bandstand and obelisk section on
  `park-victoria-park`, and `walk-hamilton-art`. No list of sculptures in Victoria Park was found beyond the
  bandstand and the Rifle Corps obelisk: ask Matt what is there. The Queen Elizabeth Park list is three
  pieces from news reports of 2007, so it may be out of date.
- Charities, second pass: `house-historical-society` (pinned) and `story-kbb`. The St George's Foundation's
  World Heritage Centre has closed, so it has no card. The kids quiz line that hog money shows a pig is
  from Claude's own knowledge. Still to mine: BEST, the Garden Club, the Turtle Project, the SPCA, and
  charity walks and tag days for the Events page.
- The Red Cross Jingle Run and Walk (13 Dec) is in seasons.json only. It is not in manual_events.json because
  the right view and cat values for a charity run were not known. Check the planner picks it up, or add it.
- Accuracy pass, 24 Nov: all story and People cards reread. Fixed: first enslaved people 1616 not 1617 (the
  Edwin); the Enterprise came six months after Emancipation, not seven; the regular garrison left in 1957
  (the 1 May 1953 date was a plan in Hansard, and the On this day entry for it is removed); 1968 was the
  first election with one equal vote for every adult (adults over 25 voted in 1963, with an extra vote for
  owners of property, which is from Claude's own knowledge); Boer camps were on more than five islands.
  Still unchecked: Emily 1987 felling 80 to 90 per cent of trees; U-505 towed 1,700 miles (other accounts
  say 2,000 or 2,500); about 4,000 people freed in 1834; the cup first played on 12 June 1902; Chesley
  Trott's dates; the 1 June 1730 trial date.
- Lines in the heroes cards that rest on Claude's own knowledge, not a source read on 24 Nov, and need a
  check: Sir Henry Tucker as a banker, Gladys Morrell's Bermuda Woman Suffrage Society, Sir Edward
  Richards as a lawyer and the first Black Bermudian to lead the Government, the Dame Lois Browne-Evans
  Building on Court Street.
- feedback_script.gs: the Google Apps Script that receives the reports. The setup steps are at its top.
- events/data/onthisday.json: 216 events. About 32 came from Hansard and say
  what was said or done in Parliament that day.
  events/data/onthisday_drafts.json keeps the sources for the seven added by research.
- events/data/explore.json: Island stories now also has `story-boycott` (1834 to 1968), `story-blockade`,
  `story-boers`, `story-censors`, `story-portuguese`, `story-convicts` and `story-summits`. `story-slavery` gained Sally Bassett and Enterprise sections.
- events/data/manual_events.json: Clave Thursdays for 26 Nov and 3, 10, 17 Dec on the Planner (music view).
  The planner only merges this file on a full run (the 6am task on Mondays and Fridays, or run.bat), not
  on build_now.bat.
- otd_mine.py 1.1 with corrected article titles.
- papers_mine.py 1.0 and papers_mine.bat: lists research papers about Bermuda and the Sargasso Sea from
  Crossref (no key) into events/data/papers_candidates.json. Written without a live test. It also asks
  OpenAlex when OPENALEX_API_KEY is in .env (a free key, required by OpenAlex since February 2026).
- Hansard (api.parliament.uk/historic-hansard) is a good dated source: the date and the title are in each
  address. No miner yet. Samples found by web search on 24 Nov: the convict hulks (22 May 1860), the
  Dockyard closing (3 May 1950), the 1977 executions (1 and 5 December 1977).

## How On this day is built

- `otd_mine.py` reads about 90 Wikipedia articles (the TITLES list) and writes every sentence with a full
  date to events/data/onthisday_candidates.json. Nothing reaches the Hub from there.
- Each candidate is checked and rewritten by hand into events/data/onthisday.json as
  {"d": "MM-DD", "y": year, "t": text, "id": optional Explore card id}.
- Left out on purpose: footnotes and citation dates, recent politics and police matters about living
  people, dates where sources disagree.
- Done by research on 24 Nov: Theatre Boycott, Enterprise, 1977 (corrected), Princess Hotel opening.
  Still to add: exact days for the blockade runners and the censors.
- Held back because sources disagree: the first Boer prisoners (26 or 28 June 1901), Sally Bassett's
  execution (6 or 21 June 1730), the end of the 1943 Bermuda Conference (28, 29 or 30 April).

## Waiting on Matt

- Pins by walking: the kiln, cottages and Sugar Loaf Hill at Hog Bay; Jeffrey's Cave and the Checkerboard at
  Spittal Pond; Ferry Island Fort and Burnt Point Fort; Seymour's Pond. Drop a pin on the spot and send it.
- What sculptures are really in Victoria Park and Queen Elizabeth Park.
- The English Market website link, and whether its discounts still run.
- More occasions need a yes: Good Friday kites, Bermuda Day, Cup Match, Harbour Nights.
- Analytics: he was offered GoatCounter (free for non commercial use, no cookies, custom events). He must
  create the account and send the site code. Then track tab opens, home tiles, sport and Explore kind, and
  searches with no result. Not built.
- Report button: create the Google Sheet and deploy feedback_script.gs (steps at the top of that file),
  then put the web app address (it ends in /exec) in events/data/feedback.json and build.
- Someone who knows the history should read the slavery card and the new `story-boycott` card before the
  Hub is shared more widely. They rest on Wikipedia, the National Museum of Bermuda, The Royal Gazette,
  Bernews and Sankofa Bermuda. Sally Bassett, the Enterprise, segregation and the Theatre Boycott are now
  covered, each in a few lines.
- eMoo and Property Skipper: left off the Hub for now (his call, 24 Nov). A longer term idea.
- Check on a real phone: the Explore map after picking a kind (it starts hidden now), turtle sighting by
  tapping the map, "What is near me".
- Tracked ticket links and the staples "interested?" card: still need a yes.
- Flights card: needs a free key in .env.

## Not done

- Gym timetables inside booking systems: Court House (members only, no drop in rate found), Alchemy,
  Beyond Fit. LifeThyme publishes no class times.
- Gorham's and Masters prices are in flyer pictures. Reading them needs the OCR step and a test run.
- Clave Thursdays: on the Planner to 17 Dec only (manual_events.json). Later dates need adding, and
  Christmas Eve and New Year's Eve were left out because nothing confirms them.
- Named houses, research papers from Bermuda, old maps and photos: not started.
- The same fact card for every place (item 4 of the volume plan): only gyms and yoga so far.
- Graves by name: the War Graves Commission lists could not be read. Cards link to them.
- Quality debt: about 65 approximate pins, six cards on the Aquarium pin, page weight 2.6 MB.
- Report button: one button for the whole Hub, not a link on each card. It records the last card tapped.

## Things the next session must know

- Saving files from a phone session: a file changed in the outputs folder seconds before it is sent to
  the laptop can arrive as its older version. On 24 Nov three small corrections were lost this way and
  had to be redone. Write each file once, wait, send it, then read it back from the laptop and compare.

- House rules: no dashes as sentence punctuation. Every code file has the header (what it is, the credit
  line above, Version, Last Updated, Change Log newest first, dependencies). The repo is public, so no
  private phone numbers or emails. Secrets go in .env, never in chat. Pins must be looked up, not guessed.
  New features are run past Matt first. Web facts in replies carry citations. Card text is in our own
  words with the source linked.
- Building by remote control: commit files, then double click `build_now.bat` in File Explorer (zoom in
  to find the row first, the list moves). A build takes about 10 seconds. Check build_output.log for
  "hub done". It fails silently when the screen is locked.
- The Claude artifact "Bermuda Hub" was last published by something else at 7:03am (probably the Tuesday
  deals task). The website is the reliable copy. Read the artifact's version before publishing to it.
- The Tuesday deals task rewrites deals/editorial.json and may overwrite the Gorham's line.
- Testing so far is in a phone sized browser only. Maps cannot be tested there.
