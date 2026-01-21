# Local Mode with SQLite Fallback

## Overview

The application now supports a local mode that automatically falls back to a local SQLite database when the primary database connection is unavailable. All changes made in local mode are tracked and can be synced back to the primary database when the connection is restored.

## Features

- **Automatic Fallback**: When the primary database connection fails, the system automatically queues all database operations for later sync
- **Change Tracking**: All database operations (insert, update, delete) are tracked in a local SQLite queue
- **Automatic Sync**: When the primary database connection is restored, pending changes are automatically synced
- **Manual Sync**: API endpoints allow manual triggering of sync operations
- **Status Monitoring**: API endpoints provide real-time status of database connectivity and sync queue

## How It Works

### Database Adapter

The `DatabaseAdapter` class (`web/db_adapter.py`) manages:
- Connection status monitoring
- Automatic fallback to local SQLite
- Change queueing for sync
- Sync operations when connection is restored

### Local Database

The `LocalDatabase` class maintains a local SQLite database (`local_backup.db`) that stores:
- A sync queue of all pending database operations
- Metadata about each change (table, operation, record data, timestamp)

### Integration

The system is integrated into the existing database models:
- `get_or_create_player()` automatically queues changes when in local mode
- All database operations check connection status
- Failed operations are queued for later sync

## API Endpoints

### Check Database Status
```
GET /api/db/status
```
Returns the current database connection status and sync queue information.

**Response:**
```json
{
  "success": true,
  "primary_connected": true,
  "local_mode": false,
  "sync_queue": {
    "total_changes": 0,
    "pending_sync": 0,
    "synced": 0
  },
  "connection_status": {
    "connected": true,
    "last_check": "2024-01-01T12:00:00"
  }
}
```

### Check Database Connectivity
```
GET /api/db/check
```
Tests the database connection and attempts to sync if reconnected.

**Response:**
```json
{
  "success": true,
  "connected": true,
  "message": "Database connection OK"
}
```

### Manual Sync
```
POST /api/db/sync
```
Manually triggers synchronization of pending changes from local to primary database.

**Response:**
```json
{
  "success": true,
  "message": "Synced 5 of 5 changes",
  "synced": 5,
  "total": 5,
  "errors": []
}
```

## Configuration

The local mode is enabled by default when initializing the database:

```python
init_database(app, enable_local_fallback=True)
```

The local backup database is stored at:
```
web/local_backup.db
```

## Usage Scenarios

### Scenario 1: Network Outage
1. User is playing the game
2. Network connection to primary database is lost
3. System automatically detects the disconnection
4. All database operations are queued in local SQLite
5. User continues playing normally
6. When connection is restored, changes are automatically synced

### Scenario 2: Manual Sync
1. User notices database is disconnected (via status endpoint)
2. User continues playing (changes are queued locally)
3. User manually triggers sync via `/api/db/sync`
4. All pending changes are applied to primary database

### Scenario 3: Connection Monitoring
1. Application periodically checks connection status
2. When connection is restored, automatic sync is triggered
3. User is notified of sync status

## Technical Details

### Change Tracking

Each database operation is tracked with:
- `table_name`: The database table affected
- `operation`: Type of operation (insert, update, delete)
- `record_id`: ID of the affected record (if available)
- `record_data`: Full record data as JSON
- `timestamp`: When the change occurred
- `synced`: Whether the change has been synced

### Sync Process

When syncing:
1. Retrieve all pending changes from local queue
2. For each change:
   - Apply to primary database using SQLAlchemy models
   - Handle conflicts (e.g., record already exists)
   - Mark as synced on success
3. Report sync results

### Error Handling

- Connection failures are caught and logged
- Sync errors don't prevent application from running
- Failed syncs can be retried
- Old synced records are cleaned up automatically (after 7 days)

## Limitations

1. **Read Operations**: In local mode, read operations still attempt to use the primary database. If it fails, the operation will fail (future enhancement: cache reads locally)

2. **Complex Relationships**: Complex database relationships may not sync perfectly if foreign keys are involved

3. **Conflict Resolution**: If the same record is modified both locally and on the primary database, the sync will use the local version (last write wins)

4. **Performance**: Large numbers of queued changes may slow down sync operations

## Future Enhancements

- Local caching of read operations
- Conflict resolution strategies
- Batch sync operations
- Sync progress indicators
- Web UI for sync status

