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

When working with Flet, always consult the installed source at `.venv/lib/python3.14/site-packages/flet/controls/` to verify parameter names before using them. The API changed significantly at v0.80 and many online examples are outdated.

- Docs: https://flet.dev/docs/
- API Reference: https://docs.flet.dev/api-reference/

**Verified breaking changes in this project's installed version:**

| Old (pre-0.80 / outdated examples) | Correct |
|---|---|
| `ft.app(target=fn)` | `ft.run(fn)` — positional |
| `ft.Icon(name=x)` | `ft.Icon(x)` — positional |
| `FilledButton(text=x, icon=y)` | `FilledButton(content=x, icon=y)` |
| `ElevatedButton(text=x)` | `ElevatedButton(content=x)` |
| `OutlinedButton(text=x)` | `OutlinedButton(content=x)` |
| `Dropdown(on_change=fn)` | `Dropdown(on_select=fn)` |
| `FilePicker(on_result=fn)` | `picker = ft.FilePicker(); picker.on_result = fn` — assign after init, add to `page.overlay` |

**Rule:** when an `unexpected keyword argument` error appears on a Flet control, grep the installed source for the `__init__` or `@control` dataclass fields — do not trust docs or examples without verifying.

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
