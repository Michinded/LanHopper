# LanHopper — Architecture

## Directory Structure

```
LanHopper/
├── main.py                    # Entry point — launches Flet app via ft.run()
├── app/
│   ├── config.py              # Loads/saves data/user_config.json, resolves paths for dev+bundle
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
│   ├── utils/
│   │   └── paths.py           # Cross-platform path helpers: normalize_path, pick_folder, is_unc
│   │
│   └── views/                 # Flet screens
│       ├── home.py            # Layout shell: NavigationRail + content switcher
│       └── settings.py        # Settings screen: port, folder type/path, language, device name
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
| HTTP Server | FastAPI + uvicorn | File transfer REST API, runs in background thread |
| Auth | python-jose (JWT) | Session tokens signed with an in-memory secret |
| Config | JSON (stdlib) | Persist user preferences across launches |
| i18n | JSON + stdlib | Load UI strings from language file |
| Path utils | pathlib + tkinter | Cross-platform path normalization and native folder picker |
| QR | qrcode + Pillow | Generate connection QR shown on home screen |
| Build | PyInstaller | Package into a single executable |

## UI Layout

```
┌─────────────────────────────────────┐
│  NavigationRail  │  Content area    │
│                  │                  │
│  🏠 Home         │  Active screen   │
│  ⚙  Settings    │                  │
└─────────────────────────────────────┘
```

`home.py` owns the shell (rail + content `Column`). `_navigate(index)` clears and replaces the content area. Each screen is a self-contained `ft.Column` subclass.

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
  "device_name": "LanHopper",
  "port": 8080,
  "shared_folder": {
    "type": "local",
    "path": "/path/to/executable/shared"
  },
  "language": "en"
}
```

- Created automatically with defaults on first launch if it does not exist.
- Default `shared_folder.path` is `./shared` relative to the executable (works in dev and bundle).
- Old string format for `shared_folder` is migrated automatically to the dict format on load.

## Shared Folder Types

| Type | Behavior | Path input |
|---|---|---|
| `local` | `Path.expanduser()` normalization | Read-only field + native folder picker (tkinter) |
| `network` | Stored as-is | Editable text field (UNC on Windows, mount path on macOS/Linux) |

The folder picker (`pick_folder()` in `app/utils/paths.py`) runs in a daemon thread to avoid blocking the Flet UI thread.

## i18n

`app/i18n.py` exposes a single function:

```python
t("start_server")  # → "Start Server"
```

Language is determined by `config["language"]`. Files live in `assets/lang/`.
When running as a PyInstaller bundle, paths are resolved via `sys._MEIPASS`.

## Flet API Notes (≥ 0.80)

This version introduced breaking changes from older Flet examples:

| Old | New |
|---|---|
| `ft.app(target=fn)` | `ft.run(fn)` |
| `ft.Icon(name=x)` | `ft.Icon(x)` — positional |
| `FilledButton(text=x)` | `FilledButton(content=x)` |
| `Dropdown(on_change=fn)` | `Dropdown(on_select=fn)` |
| `FilePicker(on_result=fn)` | assign `picker.on_result = fn` after init; add to `page.overlay` |

## Adding a New Screen

1. Create `app/views/my_screen.py` as a `ft.Column` subclass.
2. Add a `NavigationRailDestination` in `home.py`.
3. Handle the new index in `HomeView._navigate()`.

## Adding a New API Endpoint

1. Create or edit a file in `app/api/`.
2. Define a FastAPI `APIRouter`.
3. Include the router in `app/server.py` via `app.include_router(...)`.
