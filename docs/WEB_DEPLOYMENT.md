# Web Deployment

This project now exposes a small Flask service for the browser client located in
`web/`.  The service replaces the previous PHP backend and handles all game
state using Flask sessions.

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Service

From the repository root run:

```bash
python web/app.py
```

The service starts on `http://localhost:5000` and serves JSON endpoints under
`/api`:

- `GET /api/get_status`
- `POST /api/travel`
- `POST /api/trade`

The front-end JavaScript located in `web/js` communicates with these endpoints
via `fetch`.

Static assets (`web/index.html`, `web/js`, `web/css`) can be served by any web
server or by the Flask development server.
