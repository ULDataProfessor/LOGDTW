# LOGDTW Web API

This service exposes a small REST API used by the web front end.

## Endpoints

### `GET /status`
Returns the current player and world status.

**Response**
```json
{
  "success": true,
  "player": {"name": "Captain", ...},
  "world": {"current_location": "Alpha Station", ...}
}
```

### `POST /travel`
Move the player to a new sector.

**Request body**
```json
{"sector": 2}
```

**Response**
```json
{"success": true, "message": "Jumped to Sector 2", "player": {...}}
```

### `POST /trade`
Buy or sell goods in the market.

**Request body**
```json
{"item": "Food", "quantity": 1, "trade_action": "buy"}
```

**Response**
```json
{"success": true, "message": "Bought 1 Food for 50 credits", "credits": 950}
```

All responses include a boolean `success` flag and error messages when the action cannot be completed.
