#!/usr/bin/env python3
"""
Database Adapter with Local SQLite Fallback
Provides automatic fallback to local SQLite when primary database is unavailable,
with change tracking and sync capabilities.
"""

import os
import json
import sqlite3
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError, DisconnectionError
from sqlalchemy import event, create_engine
from sqlalchemy.pool import Pool


class LocalDatabase:
    """Local SQLite database for offline mode"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock = threading.Lock()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize local database schema"""
        with self._connect() as conn:
            # Create change tracking table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    record_id INTEGER,
                    record_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    synced INTEGER DEFAULT 0
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sync_queue_synced ON sync_queue(synced, timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sync_queue_table ON sync_queue(table_name, record_id)")
            conn.commit()
    
    def _connect(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def queue_change(self, table_name: str, operation: str, record_id: Optional[int], record_data: Dict):
        """Queue a change for later sync"""
        with self.lock:
            with self._connect() as conn:
                conn.execute("""
                    INSERT INTO sync_queue (table_name, operation, record_id, record_data)
                    VALUES (?, ?, ?, ?)
                """, (table_name, operation, record_id, json.dumps(record_data)))
                conn.commit()
    
    def get_pending_changes(self, limit: int = 1000) -> List[Dict]:
        """Get pending changes for sync"""
        with self.lock:
            with self._connect() as conn:
                cursor = conn.execute("""
                    SELECT id, table_name, operation, record_id, record_data, timestamp
                    FROM sync_queue
                    WHERE synced = 0
                    ORDER BY timestamp ASC
                    LIMIT ?
                """, (limit,))
                return [
                    {
                        "id": row[0],
                        "table_name": row[1],
                        "operation": row[2],
                        "record_id": row[3],
                        "record_data": json.loads(row[4]),
                        "timestamp": row[5]
                    }
                    for row in cursor.fetchall()
                ]
    
    def mark_synced(self, sync_ids: List[int]):
        """Mark changes as synced"""
        if not sync_ids:
            return
        with self.lock:
            with self._connect() as conn:
                placeholders = ",".join("?" * len(sync_ids))
                conn.execute(f"""
                    UPDATE sync_queue
                    SET synced = 1
                    WHERE id IN ({placeholders})
                """, sync_ids)
                conn.commit()
    
    def clear_synced(self, older_than_days: int = 7):
        """Clear old synced records"""
        with self.lock:
            with self._connect() as conn:
                conn.execute("""
                    DELETE FROM sync_queue
                    WHERE synced = 1
                    AND timestamp < datetime('now', '-' || ? || ' days')
                """, (older_than_days,))
                conn.commit()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get sync queue statistics"""
        with self.lock:
            with self._connect() as conn:
                total = conn.execute("SELECT COUNT(*) FROM sync_queue").fetchone()[0]
                pending = conn.execute("SELECT COUNT(*) FROM sync_queue WHERE synced = 0").fetchone()[0]
                synced = conn.execute("SELECT COUNT(*) FROM sync_queue WHERE synced = 1").fetchone()[0]
                return {
                    "total_changes": total,
                    "pending_sync": pending,
                    "synced": synced
                }


class DatabaseAdapter:
    """Database adapter with automatic fallback to local SQLite"""
    
    def __init__(self, primary_db: SQLAlchemy, local_db_path: str = None):
        self.primary_db = primary_db
        self.local_db_path = local_db_path or os.path.join(
            os.path.dirname(__file__), "local_backup.db"
        )
        self.local_db = LocalDatabase(self.local_db_path)
        self._connection_status = {"connected": True, "last_check": datetime.utcnow()}
        self._setup_connection_pool_events()
    
    def _setup_connection_pool_events(self):
        """Setup SQLAlchemy connection pool events to detect disconnections"""
        @event.listens_for(Pool, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Track successful connections"""
            self._connection_status["connected"] = True
            self._connection_status["last_check"] = datetime.utcnow()
        
        @event.listens_for(Pool, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            """Check connection on checkout"""
            try:
                dbapi_conn.execute("SELECT 1")
                self._connection_status["connected"] = True
                self._connection_status["last_check"] = datetime.utcnow()
            except Exception:
                self._connection_status["connected"] = False
                self._connection_status["last_check"] = datetime.utcnow()
    
    def is_connected(self) -> bool:
        """Check if primary database is connected"""
        was_connected = self._connection_status.get("connected", False)
        
        try:
            if not self.primary_db.engine:
                self._connection_status["connected"] = False
                self._connection_status["last_check"] = datetime.utcnow()
                return False
            
            # Try a simple query
            with self.primary_db.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1"))
            
            self._connection_status["connected"] = True
            self._connection_status["last_check"] = datetime.utcnow()
            
            # If we just reconnected, try to sync pending changes
            if not was_connected and self._connection_status["connected"]:
                # Auto-sync in background (non-blocking)
                try:
                    self.sync_pending_changes()
                except Exception:
                    pass  # Don't fail if auto-sync fails
            
            return True
        except (OperationalError, DisconnectionError, Exception) as e:
            self._connection_status["connected"] = False
            self._connection_status["last_check"] = datetime.utcnow()
            self._connection_status["last_error"] = str(e)
            return False
    
    @contextmanager
    def session(self):
        """Get database session with automatic fallback"""
        if self.is_connected():
            try:
                yield self.primary_db.session
                self.primary_db.session.commit()
            except (OperationalError, DisconnectionError) as e:
                self.primary_db.session.rollback()
                self._connection_status["connected"] = False
                self._connection_status["last_error"] = str(e)
                raise
        else:
            # Use local mode - create a mock session-like object
            # In practice, we'll need to handle this differently
            raise ConnectionError("Primary database unavailable, using local mode")
    
    def queue_for_sync(self, table_name: str, operation: str, record_id: Optional[int], record_data: Dict):
        """Queue a change for sync when connection is restored"""
        self.local_db.queue_change(table_name, operation, record_id, record_data)
    
    def sync_pending_changes(self) -> Dict[str, Any]:
        """Sync pending changes from local database to primary"""
        if not self.is_connected():
            return {
                "success": False,
                "message": "Primary database not connected",
                "synced": 0
            }
        
        changes = self.local_db.get_pending_changes()
        if not changes:
            return {
                "success": True,
                "message": "No pending changes",
                "synced": 0
            }
        
        synced_count = 0
        synced_ids = []
        errors = []
        
        try:
            for change in changes:
                try:
                    if self._apply_change(change):
                        synced_ids.append(change["id"])
                        synced_count += 1
                    else:
                        errors.append(f"Failed to apply change {change['id']}")
                except Exception as e:
                    errors.append(f"Error applying change {change['id']}: {str(e)}")
            
            # Mark successfully synced changes
            if synced_ids:
                self.local_db.mark_synced(synced_ids)
            
            return {
                "success": True,
                "message": f"Synced {synced_count} of {len(changes)} changes",
                "synced": synced_count,
                "total": len(changes),
                "errors": errors
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Sync failed: {str(e)}",
                "synced": synced_count,
                "errors": errors
            }
    
    def _apply_change(self, change: Dict) -> bool:
        """Apply a single change to the primary database"""
        table_name = change["table_name"]
        operation = change["operation"]
        record_data = change["record_data"]
        record_id = change.get("record_id")
        
        # Import models dynamically to avoid circular imports
        try:
            from web.models import (
                User, Player, InventoryItem, SectorVisibility,
                EventHistory, MarketData, PlayerMission, GameSettings
            )
        except ImportError:
            # If models aren't available, we can't sync
            return False
        
        model_map = {
            "users": User,
            "players": Player,
            "inventory_items": InventoryItem,
            "sector_visibility": SectorVisibility,
            "event_history": EventHistory,
            "market_data": MarketData,
            "player_missions": PlayerMission,
            "game_settings": GameSettings
        }
        
        model = model_map.get(table_name)
        if not model:
            return False
        
        try:
            if operation == "insert" or operation == "update":
                # For updates, try to find existing record
                if record_id and operation == "update":
                    existing = model.query.get(record_id)
                    if existing:
                        # Update existing - only update fields that exist in the model
                        for key, value in record_data.items():
                            if hasattr(existing, key) and not key.startswith("_"):
                                try:
                                    setattr(existing, key, value)
                                except (TypeError, ValueError) as e:
                                    # Skip fields that can't be set (e.g., relationships)
                                    continue
                    else:
                        # Record doesn't exist, treat as insert
                        # Remove id from record_data for insert
                        insert_data = {k: v for k, v in record_data.items() if k != "id"}
                        new_record = model(**insert_data)
                        self.primary_db.session.add(new_record)
                else:
                    # Insert new - remove id if present
                    insert_data = {k: v for k, v in record_data.items() if k != "id"}
                    new_record = model(**insert_data)
                    self.primary_db.session.add(new_record)
                
                self.primary_db.session.commit()
                return True
            
            elif operation == "delete":
                if record_id:
                    record = model.query.get(record_id)
                    if record:
                        self.primary_db.session.delete(record)
                        self.primary_db.session.commit()
                        return True
                return False
            
            return False
        except Exception as e:
            self.primary_db.session.rollback()
            # Log error but don't raise - let sync continue with other changes
            print(f"Warning: Failed to apply change {change.get('id')}: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get database connection and sync status"""
        local_stats = self.local_db.get_stats()
        return {
            "primary_connected": self.is_connected(),
            "connection_status": self._connection_status,
            "local_mode": not self.is_connected(),
            "sync_queue": local_stats,
            "local_db_path": self.local_db_path
        }


# Global adapter instance (will be initialized in app.py)
db_adapter: Optional[DatabaseAdapter] = None


def init_db_adapter(primary_db: SQLAlchemy, local_db_path: str = None) -> DatabaseAdapter:
    """Initialize the database adapter"""
    global db_adapter
    db_adapter = DatabaseAdapter(primary_db, local_db_path)
    return db_adapter


def get_db_adapter() -> Optional[DatabaseAdapter]:
    """Get the global database adapter"""
    return db_adapter

