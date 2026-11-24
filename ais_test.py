"""Bermuda Hub AIS coverage test: listens to AISStream for a few minutes and reports which ships it hears near Bermuda.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.1
Last Updated: 2026-11-22

Change Log
  1.1 2026-11-22  The first run heard no ships at Bermuda. Two additions to tell "no coverage" from "something is
                  wrong": any message that is not about a ship is now kept and printed (shortened), and when
                  Bermuda is silent the test listens to New York harbour for one minute as a control. If New
                  York answers, the key and the code work and AISStream simply has no receiver near Bermuda.
  1.0 2026-11-22  First release. A test only: nothing on the Hub page uses it yet.

What it does
  Opens the AISStream live feed, asks for every ship message inside a box around Bermuda, listens for a set
  number of minutes (10 unless told otherwise), then writes what it heard. The point is to find out whether
  AISStream hears ships at Bermuda well enough to build "tap a ship for info" on it.

Depends on
  .env in this folder, holding one line: AISSTREAM_KEY=your key. The key is never printed or saved elsewhere.
  The "websockets" Python package (ais_test.bat installs it).
  The internet (wss://stream.aisstream.io/v0/stream).

Writes
  events/data/ais_test.json  every ship heard, with its last position and details.
  The summary is printed, and ais_test.bat saves that in ais_test_output.log.

Run
  Double click ais_test.bat, or in the terminal: python ais_test.py --minutes 10
"""
import asyncio
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ENV = os.path.join(ROOT, ".env")
OUT = os.path.join(ROOT, "events", "data", "ais_test.json")
URL = "wss://stream.aisstream.io/v0/stream"
# The box: south west corner then north east corner, as [latitude, longitude]. About 60 nautical miles around the island.
BOX = [[31.3, -66.0], [33.4, -63.6]]
CONTROL_BOX = [[40.45, -74.30], [40.90, -73.70]]  # New York harbour: always busy, so a good check that the key works
# AIS ship type codes, by their first digit, in plain words.
TYPE_WORDS = {2: "wing in ground craft", 3: "fishing, towing, sailing or pleasure craft", 4: "high speed craft",
              5: "pilot, tug, rescue or port service", 6: "passenger ship", 7: "cargo ship", 8: "tanker", 9: "other"}


def read_key() -> str:
    """The AISStream key from .env. Stops with a plain message if it is missing."""
    if not os.path.exists(ENV):
        sys.exit("No .env file found in %s. Create it with one line: AISSTREAM_KEY=your key" % ROOT)
    with open(ENV, encoding="utf-8-sig") as f:
        for line in f:
            name, _, value = line.strip().partition("=")
            if name.strip() == "AISSTREAM_KEY" and value.strip():
                return value.strip().strip('"').strip("'")
    sys.exit("The .env file has no AISSTREAM_KEY=... line with a key after the equals sign.")


def type_word(code) -> str:
    """Plain words for an AIS ship type code such as 70 (cargo ship)."""
    try:
        code = int(code)
    except (TypeError, ValueError):
        return ""
    if code == 0:
        return ""
    return TYPE_WORDS.get(code // 10, "other")


def take(ships: dict, msg: dict) -> bool:
    """Fold one AISStream message into ships (keyed by MMSI). True when the ship is new."""
    meta = msg.get("MetaData") or {}
    mmsi = str(meta.get("MMSI") or meta.get("MMSI_String") or "").strip()
    if not mmsi:
        return False
    new = mmsi not in ships
    s = ships.setdefault(mmsi, {"mmsi": mmsi, "name": "", "messages": 0, "kinds": []})
    s["messages"] += 1
    kind = msg.get("MessageType") or ""
    if kind and kind not in s["kinds"]:
        s["kinds"].append(kind)
    name = (meta.get("ShipName") or "").strip()
    if name:
        s["name"] = name
    if meta.get("latitude") is not None and meta.get("longitude") is not None:
        s["lat"], s["lon"] = round(float(meta["latitude"]), 5), round(float(meta["longitude"]), 5)
    if meta.get("time_utc"):
        s["last_heard_utc"] = str(meta["time_utc"])[:19]
    body = (msg.get("Message") or {}).get(kind) or {}
    for src, dst in (("Sog", "speed_knots"), ("Cog", "course"), ("TrueHeading", "heading"), ("NavigationalStatus", "nav_status")):
        if body.get(src) is not None:
            s[dst] = body[src]
    if kind == "ShipStaticData":
        if (body.get("Name") or "").strip():
            s["name"] = body["Name"].strip()
        for src, dst in (("ImoNumber", "imo"), ("CallSign", "callsign"), ("Destination", "destination"), ("MaximumStaticDraught", "draught_m")):
            v = body.get(src)
            if v not in (None, "", 0):
                s[dst] = v.strip() if isinstance(v, str) else v
        if body.get("Type") is not None:
            s["type_code"], s["type"] = body["Type"], type_word(body["Type"])
        dim = body.get("Dimension") or {}
        if dim:
            length, beam = (dim.get("A") or 0) + (dim.get("B") or 0), (dim.get("C") or 0) + (dim.get("D") or 0)
            if length:
                s["length_m"], s["beam_m"] = length, beam
    return new


def save(ships: dict, started: dt.datetime, minutes: float, total: int, note: str, odd: list, control: dict) -> None:
    """Write the result file (to a temporary name first, so a half written file never replaces a good one)."""
    doc = {"test": "AISStream coverage near Bermuda", "started_utc": started.strftime("%Y-%m-%d %H:%M:%S"),
           "listened_minutes": round(minutes, 1), "box": BOX, "messages": total, "ships_heard": len(ships), "note": note, "other_messages": odd, "control": control,
           "ships": sorted(ships.values(), key=lambda x: (-x["messages"], x["mmsi"]))}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)


async def hear(key: str, box: list, minutes: float, url: str, quiet: bool = False) -> tuple:
    """Listen to one box. Returns (ships, number of ship messages, note, messages that were not about a ship)."""
    import websockets
    end = asyncio.get_running_loop().time() + minutes * 60
    ships, total, note, odd = {}, 0, "finished normally", []
    try:
        async with websockets.connect(url, open_timeout=30) as ws:
            await ws.send(json.dumps({"APIKey": key, "BoundingBoxes": [box]}))
            while True:
                left = end - asyncio.get_running_loop().time()
                if left <= 0:
                    break
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=left)
                except asyncio.TimeoutError:
                    break
                text = raw.decode("utf-8", "replace") if isinstance(raw, (bytes, bytearray)) else str(raw)
                try:
                    msg = json.loads(text)
                except ValueError:
                    msg = None
                if not isinstance(msg, dict) or not (msg.get("MetaData") or {}).get("MMSI"):
                    short = text.replace(key, "(key hidden)")[:300]
                    if len(odd) < 10:
                        odd.append(short)
                    print("  message that is not about a ship: %s" % short, flush=True)
                    if isinstance(msg, dict) and any(k.lower() == "error" for k in msg):
                        note = "AISStream refused the request"
                        break
                    continue
                total += 1
                if take(ships, msg) and not quiet:
                    s = ships[str(msg["MetaData"]["MMSI"])]
                    print("  new ship %d: %s (MMSI %s)" % (len(ships), s["name"] or "name not sent yet", s["mmsi"]), flush=True)
    except Exception as e:  # a dropped line or a refused connection: keep whatever was heard
        note = "stopped early: %s %s" % (type(e).__name__, str(e)[:160])
        print(note, flush=True)
    return ships, total, note, odd


async def listen(minutes: float, url: str = URL) -> int:
    """Listen near Bermuda for the given number of minutes, with a New York control if Bermuda is silent.
    Returns the number of ships heard near Bermuda."""
    try:
        import websockets  # noqa: F401  (checked here so the message is a plain one)
    except ImportError:
        sys.exit('The "websockets" package is missing. Run ais_test.bat, or: python -m pip install websockets')
    key = read_key()
    started = dt.datetime.now(dt.timezone.utc)
    print("Listening to AISStream for %g minutes, box %s to %s ..." % (minutes, BOX[0], BOX[1]), flush=True)
    ships, total, note, odd = await hear(key, BOX, minutes, url)
    listened = (dt.datetime.now(dt.timezone.utc) - started).total_seconds() / 60
    control = {}
    if not ships:
        print("Nothing heard near Bermuda. Control: listening to New York harbour for 1 minute ...", flush=True)
        c_ships, c_total, c_note, c_odd = await hear(key, CONTROL_BOX, min(1.0, minutes), url, quiet=True)
        control = {"box": CONTROL_BOX, "ships_heard": len(c_ships), "messages": c_total, "note": c_note}
        odd = odd + [x for x in c_odd if x not in odd]
        print("Control: %d ships and %d messages from New York harbour (%s)." % (len(c_ships), c_total, c_note), flush=True)
        if c_ships:
            print("So the key and the code work, and AISStream has no receiver hearing ships at Bermuda right now.", flush=True)
        else:
            print("New York was silent too, so the problem is the key or the connection, not Bermuda.", flush=True)
    save(ships, started, listened, total, note, odd, control)
    named = sum(1 for s in ships.values() if s["name"])
    typed = sum(1 for s in ships.values() if s.get("type"))
    print("")
    print("Result: %d ships heard, %d messages, in %.1f minutes (%s)." % (len(ships), total, listened, note))
    print("        %d with a name, %d with a ship type." % (named, typed))
    for s in sorted(ships.values(), key=lambda x: -x["messages"]):
        print("  %-22s %-9s %4d messages  %s  %s" % ((s["name"] or "?")[:22], s["mmsi"], s["messages"], s.get("type", ""), s.get("destination", "")))
    print("Saved to %s" % OUT)
    return len(ships)


def main(argv: list) -> None:
    minutes = 10.0
    if "--minutes" in argv:
        try:
            minutes = float(argv[argv.index("--minutes") + 1])
        except (IndexError, ValueError):
            sys.exit("Use it like this: python ais_test.py --minutes 10")
    asyncio.run(listen(minutes))


if __name__ == "__main__":
    main(sys.argv[1:])
