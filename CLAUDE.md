# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
python main.py
```

## Installing dependencies

```bash
pip install -r requirements.txt
```

## Building the executable

```bash
pyinstaller LanHopper.spec
```

## Flet API reference

When working with Flet (UI framework), always consult the official docs for correct API usage — especially since the API changed significantly at v0.80:

- Docs: https://flet.dev/docs/
- API Reference: https://docs.flet.dev/api-reference/

Known breaking changes already applied:
- `ft.app(target=fn)` → `ft.run(fn)` (positional, not keyword)

## Architecture

The app has two parallel runtimes that must coexist:

1. **Flet desktop window** (`main.py` → `app/views/`) — runs on the main thread via `ft.run()`.
2. **FastAPI + uvicorn HTTP server** (`app/server.py`) — runs in a daemon thread started/stopped by the user from the UI.

`app/server.py` holds a module-level `session` dict (`password`, `jwt_secret`) that is populated on `start()` and cleared on `stop()`. Both values are ephemeral — generated fresh on every server start, never persisted.

## Security model

- A random 6-digit password is generated each time the server starts.
- A JWT secret is generated alongside it (in-memory only).
- `app/middleware/auth.py` intercepts every request except `POST /auth/login` and validates the `Authorization: Bearer <token>` header.
- Sessions do not survive a server restart by design.

## Config and i18n

- `app/config.py` — reads/writes `data/user_config.json`. The `data/` directory is gitignored and created automatically on first run. Path resolution uses `sys.frozen` / `sys.executable` to work correctly both in dev and as a PyInstaller bundle.
- `app/i18n.py` — exposes `t("key")`. Call `i18n.load(language)` once at startup. Language files live in `assets/lang/<lang>.json` (bundled with the app). Path resolution uses `sys._MEIPASS` when running as a bundle.

## Adding a new API endpoint

1. Add a route to an existing file in `app/api/` or create a new router file there.
2. If new file: include the router in `app/server.py` via `app.include_router(...)`.

## Adding a new screen

1. Create `app/views/<screen>.py` with a class that receives `ft.Page`.
2. Wire it from `app/views/home.py` or a navigation element.

## Language strings

All UI-visible strings must go through `i18n.t("key")`. Add new keys to both `assets/lang/en.json` and `assets/lang/es.json`.
