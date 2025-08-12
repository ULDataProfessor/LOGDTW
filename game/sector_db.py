"""
SQLite-backed repository for procedural sectors, shared by the Python version.

Schema (table: sectors):
  id INTEGER PRIMARY KEY
  name TEXT
  faction TEXT
  region TEXT        -- 'Federation', 'Nebula', etc.
  danger_level INTEGER
  has_market INTEGER
  has_outpost INTEGER
  has_station INTEGER
  has_research INTEGER
  has_mining INTEGER
  connections TEXT    -- JSON list of ints
  explored INTEGER    -- 0/1
  charted INTEGER     -- 0/1
"""

from __future__ import annotations

import os
import json
import sqlite3
from typing import Dict, List, Optional


class SectorRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sectors (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    faction TEXT,
                    region TEXT,
                    danger_level INTEGER,
                    has_market INTEGER,
                    has_outpost INTEGER,
                    has_station INTEGER,
                    has_research INTEGER,
                    has_mining INTEGER,
                    connections TEXT,
                    explored INTEGER DEFAULT 0,
                    charted INTEGER DEFAULT 0
                )
                """
            )
            conn.commit()

    def upsert_sector(self, record: Dict) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sectors (
                    id, name, faction, region, danger_level,
                    has_market, has_outpost, has_station, has_research, has_mining,
                    connections, explored, charted
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    faction=excluded.faction,
                    region=excluded.region,
                    danger_level=excluded.danger_level,
                    has_market=excluded.has_market,
                    has_outpost=excluded.has_outpost,
                    has_station=excluded.has_station,
                    has_research=excluded.has_research,
                    has_mining=excluded.has_mining,
                    connections=excluded.connections
                """,
                (
                    record['id'], record['name'], record['faction'], record['region'], record['danger_level'],
                    int(record.get('has_market', 0)), int(record.get('has_outpost', 0)), int(record.get('has_station', 0)),
                    int(record.get('has_research', 0)), int(record.get('has_mining', 0)),
                    json.dumps(record.get('connections', [])), int(record.get('explored', 0)), int(record.get('charted', 0))
                ),
            )
            conn.commit()

    def get_sector(self, sector_id: int) -> Optional[Dict]:
        with self._connect() as conn:
            cur = conn.execute("SELECT * FROM sectors WHERE id=?", (sector_id,))
            row = cur.fetchone()
            if not row:
                return None
            columns = [col[0] for col in cur.description]
            rec = dict(zip(columns, row))
            rec['connections'] = json.loads(rec['connections'] or '[]')
            return rec

    def mark_explored(self, sector_id: int) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE sectors SET explored=1 WHERE id=?", (sector_id,))
            conn.commit()

    def mark_charted(self, sector_id: int) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE sectors SET charted=1 WHERE id=?", (sector_id,))
            conn.commit()

    def add_bidirectional_connection(self, a: int, b: int) -> None:
        if a == b:
            return
        with self._connect() as conn:
            for x, y in [(a, b), (b, a)]:
                cur = conn.execute("SELECT connections FROM sectors WHERE id=?", (x,))
                row = cur.fetchone()
                if row:
                    existing = json.loads(row[0] or '[]')
                    if y not in existing:
                        existing.append(y)
                        conn.execute("UPDATE sectors SET connections=? WHERE id=?", (json.dumps(existing), x))
            conn.commit()

    def get_total_count(self) -> int:
        with self._connect() as conn:
            cur = conn.execute("SELECT COUNT(*) FROM sectors")
            return int(cur.fetchone()[0] or 0)


