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
            # Indexes for query performance
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_sectors_explored ON sectors(explored)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_sectors_charted ON sectors(charted)"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sectors_id ON sectors(id)")
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
                    record["id"],
                    record["name"],
                    record["faction"],
                    record["region"],
                    record["danger_level"],
                    int(record.get("has_market", 0)),
                    int(record.get("has_outpost", 0)),
                    int(record.get("has_station", 0)),
                    int(record.get("has_research", 0)),
                    int(record.get("has_mining", 0)),
                    json.dumps(record.get("connections", [])),
                    int(record.get("explored", 0)),
                    int(record.get("charted", 0)),
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
            rec["connections"] = json.loads(rec["connections"] or "[]")
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
                    existing = json.loads(row[0] or "[]")
                    if y not in existing:
                        existing.append(y)
                        conn.execute(
                            "UPDATE sectors SET connections=? WHERE id=?", (json.dumps(existing), x)
                        )
            conn.commit()

    def get_total_count(self) -> int:
        with self._connect() as conn:
            cur = conn.execute("SELECT COUNT(*) FROM sectors")
            return int(cur.fetchone()[0] or 0)

    # ----------------------------
    # Integrity and maintenance
    # ----------------------------
    def check_and_fix_bidirectional(self) -> int:
        """Ensure all connections are bidirectional. Returns number of fixes made."""
        fixes = 0
        with self._connect() as conn:
            cur = conn.execute("SELECT id, connections FROM sectors")
            rows = cur.fetchall()
            id_to_conns = {}
            for sid, conns_json in rows:
                try:
                    id_to_conns[sid] = set(json.loads(conns_json or "[]"))
                except Exception:
                    id_to_conns[sid] = set()

            # Fix missing reverse links
            for a, conns in id_to_conns.items():
                for b in list(conns):
                    if b == a:
                        continue
                    if b not in id_to_conns:
                        # Skip dangling reference
                        continue
                    if a not in id_to_conns[b]:
                        id_to_conns[b].add(a)
                        fixes += 1

            # Persist normalized connections (unique, sorted)
            for sid, conns in id_to_conns.items():
                norm = sorted(set(int(x) for x in conns if isinstance(x, int) or str(x).isdigit()))
                conn.execute(
                    "UPDATE sectors SET connections=? WHERE id=?",
                    (json.dumps(norm), sid),
                )
            conn.commit()
        return fixes

    def export_graph_json(self, file_path: str) -> None:
        """Export sectors and edges to a JSON file for debugging/visualization."""
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT id, name, faction, region, danger_level, has_market, has_outpost, has_station, has_research, has_mining, connections, explored, charted FROM sectors"
            )
            nodes = []
            edges = set()
            for row in cur.fetchall():
                (sid, name, faction, region, danger, mkt, outp, stat, res, mino, conns_json, explored, charted) = row
                nodes.append(
                    {
                        "id": sid,
                        "name": name,
                        "faction": faction,
                        "region": region,
                        "danger_level": danger,
                        "has_market": mkt,
                        "has_outpost": outp,
                        "has_station": stat,
                        "has_research": res,
                        "has_mining": mino,
                        "explored": explored,
                        "charted": charted,
                    }
                )
                try:
                    conns = json.loads(conns_json or "[]")
                except Exception:
                    conns = []
                for b in conns:
                    a, b2 = int(sid), int(b)
                    if a == b2:
                        continue
                    edge = (a, b2) if a < b2 else (b2, a)
                    edges.add(edge)

            data = {"nodes": nodes, "edges": sorted(list(edges))}
            os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
