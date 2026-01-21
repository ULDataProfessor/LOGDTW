# Offline Status Indicator

## Current Behavior

The "offline" status shown in the main screen header is **currently based on network connectivity** (PWA/Service Worker), **not database connectivity**.

### Network-Based Offline Detection

The connection status indicator in the header (`#connection-status`) shows:
- **"Connected"** (green) when `navigator.onLine` is `true`
- **"Disconnected"** (red) when `navigator.onLine` is `false`

This is handled by:
- Browser's `navigator.onLine` API
- Service Worker network detection
- PWA offline page (`/offline.html`)

### Database Connectivity

The database connection status is **separate** from network connectivity:
- The database can be offline even if the network is online (e.g., database server down)
- The network can be offline but database might still be accessible (e.g., local database)

## Local Mode Feature

With the new **Local Mode** feature, when the database connection fails:
- All operations are queued in local SQLite (`data/db/local_backup.db`)
- The game continues to function normally
- Changes are automatically synced when the database connection is restored

## Future Enhancement

To show database status in the UI:
1. Add a separate database status indicator
2. Poll `/api/db/status` endpoint periodically
3. Display database connection status separately from network status
4. Show sync queue status (pending changes count)

## API Endpoints for Database Status

- `GET /api/db/status` - Get database connection and sync status
- `GET /api/db/check` - Check database connectivity
- `POST /api/db/sync` - Manually trigger sync

## Example Response

```json
{
  "success": true,
  "primary_connected": true,
  "local_mode": false,
  "sync_queue": {
    "total_changes": 0,
    "pending_sync": 0,
    "synced": 0
  }
}
```

