"""SQLite store for Tidewatch.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 0.1
Last Updated: 2026-11-15

Tables
  events  one row per (view, date, name): the calendar entries
  blocks  the static blocks per view as JSON (cats, watch, weekly, venues, notfound, sources)
  films   the cinema FILMS array as JSON
  leagues the sports LEAGUES array as JSON
  meta    key/value: today, months window, last run
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path

VIEWS = ("kids", "adults", "sports", "music", "movies")
SUFFIX = {"kids": "K", "adults": "A", "sports": "S", "music": "M", "movies": "V"}
BLOCK_KINDS = ("CATS", "WATCH", "WEEKLY", "VENUES", "NOTFOUND", "SOURCES")

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY,
  view TEXT NOT NULL,
  year INTEGER NOT NULL,
  m INTEGER NOT NULL,
  d INTEGER NOT NULL,
  cat TEXT NOT NULL,
  t TEXT DEFAULT '',
  name TEXT NOT NULL,
  time TEXT DEFAULT '',
  venue TEXT DEFAULT '',
  ages TEXT DEFAULT '',
  cost TEXT DEFAULT '',
  status TEXT DEFAULT 'check',
  note TEXT DEFAULT '',
  link TEXT DEFAULT '',
  source TEXT DEFAULT 'seed',
  source_key TEXT DEFAULT '',
  first_seen TEXT,
  last_seen TEXT,
  active INTEGER DEFAULT 1,
  UNIQUE(view, year, m, d, name)
);
CREATE INDEX IF NOT EXISTS ix_events_view_date ON events(view, year, m, d);
CREATE TABLE IF NOT EXISTS blocks (
  view TEXT NOT NULL, kind TEXT NOT NULL, json TEXT NOT NULL,
  PRIMARY KEY (view, kind)
);
CREATE TABLE IF NOT EXISTS films (id INTEGER PRIMARY KEY CHECK (id = 1), json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS leagues (id INTEGER PRIMARY KEY CHECK (id = 1), json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""

EVENT_FIELDS = ("m", "d", "cat", "t", "name", "time", "venue", "ages", "cost", "status", "note", "link")


class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    @contextmanager
    def tx(self):
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    # meta
    def get_meta(self, key: str, default=None):
        row = self.conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return json.loads(row["value"]) if row else default

    def set_meta(self, key: str, value) -> None:
        with self.tx() as c:
            c.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", (key, json.dumps(value)))

    # blocks
    def get_block(self, view: str, kind: str):
        row = self.conn.execute("SELECT json FROM blocks WHERE view=? AND kind=?", (view, kind)).fetchone()
        return json.loads(row["json"]) if row else ({} if kind == "CATS" else [])

    def set_block(self, view: str, kind: str, value) -> None:
        with self.tx() as c:
            c.execute("INSERT OR REPLACE INTO blocks(view, kind, json) VALUES (?, ?, ?)", (view, kind, json.dumps(value)))

    def get_json(self, table: str):
        row = self.conn.execute(f"SELECT json FROM {table} WHERE id=1").fetchone()
        return json.loads(row["json"]) if row else []

    def set_json(self, table: str, value) -> None:
        with self.tx() as c:
            c.execute(f"INSERT OR REPLACE INTO {table}(id, json) VALUES (1, ?)", (json.dumps(value),))

    # events
    def upsert_event(self, view: str, year: int, ev: dict, source: str, source_key: str = "", seen: str | None = None) -> None:
        """Insert or refresh one event. A re-seen event keeps its first_seen and bumps last_seen.
        Scraped data wins over seed data for the same (view, date, name); seed never overwrites scraped."""
        seen = seen or date.today().isoformat()
        row = {k: ev.get(k, "") for k in EVENT_FIELDS}
        row["t"] = row["t"] or ""
        existing = self.conn.execute(
            "SELECT id, source FROM events WHERE view=? AND year=? AND m=? AND d=? AND name=?",
            (view, year, row["m"], row["d"], row["name"]),
        ).fetchone()
        with self.tx() as c:
            if existing is None:
                c.execute(
                    "INSERT INTO events(view, year, m, d, cat, t, name, time, venue, ages, cost, status, note, link, source, source_key, first_seen, last_seen, active)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)",
                    (view, year, row["m"], row["d"], row["cat"], row["t"], row["name"], row["time"], row["venue"], row["ages"], row["cost"], row["status"], row["note"], row["link"], source, source_key, seen, seen),
                )
            elif source != "seed" or existing["source"] == "seed":
                c.execute(
                    "UPDATE events SET cat=?, t=?, time=?, venue=?, ages=?, cost=?, status=?, note=?, link=?, source=?, source_key=?, last_seen=?, active=1 WHERE id=?",
                    (row["cat"], row["t"], row["time"], row["venue"], row["ages"], row["cost"], row["status"], row["note"], row["link"], source, source_key, seen, existing["id"]),
                )
            else:
                c.execute("UPDATE events SET last_seen=? WHERE id=?", (seen, existing["id"]))

    def events_for(self, view: str, months: list[tuple[int, int]]) -> list[dict]:
        """months is a list of (year, month). Returns plain dicts in the page's event schema."""
        out: list[dict] = []
        for year, m in months:
            rows = self.conn.execute(
                "SELECT * FROM events WHERE view=? AND year=? AND m=? AND active=1 ORDER BY d, t, name", (view, year, m)
            ).fetchall()
            for r in rows:
                out.append({k: r[k] for k in EVENT_FIELDS})
        return out

    def retire_missing(self, source: str, seen: str, view: str | None = None) -> int:
        """Mark events from a scraped source inactive when the latest run of that source did not see them.
        Only applies to future dates, so past events keep their history."""
        today = date.today()
        q = "UPDATE events SET active=0 WHERE source=? AND last_seen<? AND (year>? OR (year=? AND (m>? OR (m=? AND d>=?))))"
        params: list = [source, seen, today.year, today.year, today.month, today.month, today.day]
        if view:
            q += " AND view=?"
            params.append(view)
        with self.tx() as c:
            cur = c.execute(q, params)
            return cur.rowcount

    def deactivate(self, view: str, cat: str, source: str) -> int:
        """Retire rows of one category and source in a view, used when a computed layer supersedes seed rows."""
        with self.tx() as c:
            return c.execute("UPDATE events SET active=0 WHERE view=? AND cat=? AND source=?", (view, cat, source)).rowcount

    def counts(self) -> dict:
        rows = self.conn.execute("SELECT view, source, COUNT(*) n FROM events WHERE active=1 GROUP BY view, source").fetchall()
        return {f"{r['view']}/{r['source']}": r["n"] for r in rows}
