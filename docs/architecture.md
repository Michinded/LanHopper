# LanHopper — Architecture

## Directory Structure

```
LanHopper/
├── main.py                    # Entry point — launches Flet app via ft.run()
├── app/
│   ├── config.py              # Loads/saves data/user_config.json, resolves paths for dev+bundle
│   ├── i18n.py                # Loads assets/lang/<lang>.json via t("key")
│   ├── server.py              # Starts/stops FastAPI+uvicorn, QR rotation, session state
│   │
│   ├── api/                   # HTTP layer — FastAPI routers
│   │   ├── auth.py            # POST /auth/login → JSON JWT (API clients)
│   │   ├── files.py           # GET /files, GET /files/download/{filename}
│   │   ├── upload.py          # POST /upload
│   │   └── web.py             # GET /, POST /web/login, GET /browse, GET /logout
│   │
│   ├── middleware/
│   │   └── auth.py            # Validates Bearer header or access_token cookie
│   │
│   ├── utils/
│   │   ├── network.py         # check_port(), kill_process() — psutil-based
│   │   └── paths.py           # normalize_path(), pick_folder() — cross-platform
│   │
│   └── views/                 # Flet screens (ft.Column subclasses)
│       ├── home.py            # Layout shell: NavigationRail + content switcher + status badge
│       ├── server.py          # Server screen: start/stop, URL, password, QR image
│       └── settings.py        # Settings: port, folder, language, security timings
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
| UI | Flet ≥ 0.80 | Desktop window, screens, user interaction |
| HTTP Server | FastAPI + uvicorn | File transfer API + browser UI, daemon thread |
| Auth | python-jose (JWT) | Session tokens and single-use QR tokens |
| Config | JSON (stdlib) | Persist user preferences across launches |
| i18n | JSON + stdlib | Load UI strings from language file |
| Path utils | pathlib + tkinter | Cross-platform path normalization and native folder picker |
| Network utils | psutil + socket | Port availability check and process termination |
| QR | qrcode + Pillow | Generate QR PNG as base64, shown in ServerView |
| Build | PyInstaller | Package into a single executable |

## UI Layout

```
┌─────────────────────────────────────┐
│  NavigationRail  │  Content area    │
│                  │                  │
│  🏠 Home         │  Active screen   │
│  ⚡ Server       │                  │
│  ⚙  Settings    │                  │
└─────────────────────────────────────┘
```

`home.py` owns the shell (rail + content `Column`). `_navigate(index)` clears and replaces the content area. Each screen is a self-contained `ft.Column` subclass.

## Security Model

- On each server start a **random 6-char alphanumeric password** is generated (never stored).
- A **JWT secret** is generated alongside it (in-memory only). All tokens are invalidated when the server stops.
- The middleware checks `Authorization: Bearer` header first, then falls back to the `access_token` cookie (browser sessions). Public paths: `/`, `/web/login`, `/auth/login`, `/logout`.
- A **single-use QR token** (JWT with unique `jti`) is generated immediately on start and rotated on a background thread. Used `jti` values are tracked in `session["used_qr_tokens"]`. Scanning the QR exchanges the token for a full session cookie.
- Two background threads manage the server: one runs uvicorn, one rotates the QR. Both are daemon threads stopped via `threading.Event` on `server.stop()`.

## Web Routes

| Route | Auth | Description |
|---|---|---|
| `GET /` | Public | Login page. Handles `?qr=<token>` redemption and existing session redirect |
| `POST /web/login` | Public | Form login → sets `access_token` cookie → redirect to `/browse` |
| `GET /browse` | Cookie | HTML file listing with download links and logout button |
| `GET /logout` | Public | Deletes `access_token` cookie → redirect to `/` |
| `POST /auth/login` | Public | JSON login for API clients → returns Bearer JWT |
| `GET /files/` | Bearer/Cookie | JSON file list |
| `GET /files/download/{f}` | Bearer/Cookie | File download |
| `POST /upload` | Bearer/Cookie | File upload (stub) |

## Config File (`data/user_config.json`)

```json
{
  "device_name": "LanHopper",
  "port": 8080,
  "shared_folder": {
    "type": "local",
    "path": "/path/to/executable/shared"
  },
  "language": "en",
  "qr_token_minutes": 5,
  "session_minutes": 60
}
```

- Created automatically with defaults on first launch.
- `shared_folder.type` is `"local"` or `"network"`. Old string format is migrated automatically.
- `qr_token_minutes` and `session_minutes` are read at runtime — changing them takes effect on the next token issuance without restarting the server.

## Shared Folder Types

| Type | Behavior | Path input |
|---|---|---|
| `local` | `Path.expanduser()` normalization | Read-only field + native folder picker (tkinter, daemon thread) |
| `network` | Stored as-is | Editable text field (UNC on Windows, mount path on macOS/Linux) |

## QR Rotation

1. `server.start()` calls `generate_qr_token()` immediately and spawns `_qr_rotation_loop`.
2. The loop uses `reset_event.wait(timeout=qr_minutes*60)`. On natural timeout it regenerates. On manual regenerate (`server.regenerate_qr()`), it generates first then sets `reset_event` to restart the countdown.
3. `generate_qr_token()` invokes `_on_qr_rotated` callback if registered. `ServerView` registers via `server.set_qr_callback()` in `did_mount` and clears it in `will_unmount`. The callback uses `page.run_task()` to update the UI safely from the background thread.

## i18n

`app/i18n.py` exposes a single function:

```python
t("start_server")  # → "Start Server"
```

Language is determined by `config["language"]`. Files live in `assets/lang/`.
When running as a PyInstaller bundle, paths are resolved via `sys._MEIPASS`.

## Flet API Notes (≥ 0.80)

See `CLAUDE.md` for the full breaking-changes table. Key patterns used in this project:

- `AlertDialog` and `FilePicker` → `page.overlay` via `did_mount`/`will_unmount`
- `SnackBar` → `page.show_dialog(ft.SnackBar(...))`
- `ft.Image(b64_string)` — src is positional and required; use a `ft.Container` as slot when src is not yet available
- Background thread → UI updates via `page.run_task(async_fn)`

## Adding a New Screen

1. Create `app/views/my_screen.py` as a `ft.Column` subclass.
2. Add a `NavigationRailDestination` in `home.py`.
3. Handle the new index in `HomeView._navigate()`.

## Adding a New API Endpoint

1. Create or edit a file in `app/api/`.
2. Define a FastAPI `APIRouter` and include it in `app/server.py`.
3. If public: add the path to `_PUBLIC_PATHS` in `app/middleware/auth.py`.
