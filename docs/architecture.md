# LanHopper — Architecture

## Directory Structure

```
LanHopper/
├── main.py                    # Entry point — launches Flet app
├── app/
│   ├── config.py              # Loads/saves data/user_config.json
│   ├── i18n.py                # Loads assets/lang/<lang>.json via t("key")
│   ├── server.py              # Starts/stops FastAPI+uvicorn in a background thread
│   │
│   ├── api/                   # HTTP layer — FastAPI routers
│   │   ├── auth.py            # POST /auth/login → returns JWT
│   │   ├── files.py           # GET /files, GET /download/{filename}
│   │   └── upload.py          # POST /upload
│   │
│   ├── middleware/            # FastAPI middleware
│   │   └── auth.py            # Validates Bearer JWT on all routes except /auth/login
│   │
│   └── views/                 # Flet screens
│       ├── home.py            # Main screen: start/stop, QR code, file list
│       └── settings.py        # Settings screen: port, folder, language, device name
│
├── assets/                    # Bundled read-only resources (packed by PyInstaller)
│   ├── icon.png
│   └── lang/
│       ├── en.json
│       └── es.json
│
├── data/                      # Runtime data — gitignored, created on first launch
│   └── user_config.json
│
├── requirements.txt
└── LanHopper.spec             # PyInstaller build config
```

## Layers

| Layer | Technology | Responsibility |
|---|---|---|
| UI | Flet | Desktop window, screens, user interaction |
| HTTP Server | FastAPI + uvicorn | File transfer REST API, runs in background thread |
| Auth | python-jose (JWT) | Session tokens signed with an in-memory secret |
| Config | JSON (stdlib) | Persist user preferences across launches |
| i18n | JSON + stdlib | Load UI strings from language file |
| QR | qrcode + Pillow | Generate connection QR shown on home screen |
| Build | PyInstaller | Package into a single executable |

## Security Model

- On each server start, a **random 6-digit password** is generated (never stored).
- A **JWT secret** is also generated fresh each start (in-memory only).
- The client posts the password to `POST /auth/login` and receives a short-lived JWT.
- Every subsequent request must include `Authorization: Bearer <token>`.
- The JWT middleware rejects all unauthenticated requests except `/auth/login`.
- Sessions do not survive a server restart by design.

## Config File (`data/user_config.json`)

```json
{
  "device_name": "My PC",
  "port": 8080,
  "shared_folder": "~/LanHopper/shared",
  "language": "en"
}
```

Created automatically with defaults on first launch if it does not exist.

## i18n

`app/i18n.py` exposes a single function:

```python
t("start_server")  # → "Start Server"
```

Language is determined by `config["language"]`. Files live in `assets/lang/`.
When running as a PyInstaller bundle, paths are resolved via `sys._MEIPASS`.

## Adding a New Screen

1. Create `app/views/my_screen.py` with a Flet `Control` subclass.
2. Import and render it from `app/views/home.py` or wire it to a nav element.

## Adding a New API Endpoint

1. Create or edit a file in `app/api/`.
2. Define a FastAPI `APIRouter`.
3. Include the router in `app/server.py`.
