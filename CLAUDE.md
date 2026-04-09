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
| `FilePicker(on_result=fn)` | assign `picker.on_result = fn` after init; add to `page.overlay` |
| `ft.ImageFit.CONTAIN` | `ft.BoxFit.CONTAIN` |
| `ft.Image(src_base64=x)` | `ft.Image(x)` — `src` is positional, accepts URL/base64/bytes, must be non-empty |
| `page.set_clipboard(x)` / `page.clipboard = x` | `await Clipboard().set(x)` — async, import from `flet.controls.services.clipboard` |
| `ft.SnackBar` in `controls[]` | `page.show_dialog(ft.SnackBar(...))` |
| `ft.AlertDialog` in `controls[]` | add to `page.overlay` in `did_mount()`, remove in `will_unmount()` |

**Rules:**
- When an `unexpected keyword argument` error appears, grep the installed source — do not trust docs or examples.
- `ft.AlertDialog` and `ft.FilePicker` go in `page.overlay` via `did_mount`/`will_unmount`. Do NOT call `page.update()` inside `did_mount`.
- An empty `AlertDialog` fails Flet validation even before opening — initialize with `title=ft.Text(" ")`.
- `ft.Image` with no valid src also fails validation — use a `ft.Container` as slot and assign `container.content = ft.Image(b64)` only when data is available.
- Background thread callbacks must update the UI via `page.run_task(async_fn)`, not directly.

## Architecture

The app has two parallel runtimes that must coexist:

1. **Flet desktop window** (`main.py` → `app/views/`) — runs on the main thread via `ft.run()`.
2. **FastAPI + uvicorn HTTP server** (`app/server.py`) — runs in a daemon thread started/stopped from the Server screen.

`app/server.py` holds a module-level `session` dict that is populated on `start()` and cleared on `stop()`. All session state is ephemeral — never persisted.

## Security model

- A random **6-character alphanumeric password** is generated on each server start (never stored).
- A **JWT secret** is generated alongside it (in-memory only).
- A **single-use QR token** (short-lived JWT with `jti`) is generated immediately and rotated on a background thread every `qr_token_minutes`. Scanning the QR exchanges the token for a session cookie.
- `app/middleware/auth.py` validates requests via Bearer header (API clients) or `access_token` cookie (browser). Public paths: `/`, `/web/login`, `/auth/login`, `/logout`.
- Sessions do not survive a server restart by design.

## Config and i18n

- `app/config.py` — reads/writes `data/user_config.json`. The `data/` directory is gitignored and created automatically on first run. Path resolution uses `sys.frozen` / `sys.executable` to work correctly both in dev and as a PyInstaller bundle.
- `app/i18n.py` — exposes `t("key")`. Call `i18n.load(language)` once at startup. Language files live in `assets/lang/<lang>.json` (bundled with the app). Path resolution uses `sys._MEIPASS` when running as a bundle.

## Adding a new API endpoint

1. Add a route to an existing file in `app/api/` or create a new router file there.
2. If new file: include the router in `app/server.py` via `app.include_router(...)`.
3. If the route should be public, add its path to `_PUBLIC_PATHS` in `app/middleware/auth.py`.

## Adding a new screen

1. Create `app/views/<screen>.py` as a `ft.Column` subclass.
2. Add a `NavigationRailDestination` in `home.py`.
3. Handle the new index in `HomeView._navigate()`.

## Language strings

All UI-visible strings must go through `i18n.t("key")`. Add new keys to both `assets/lang/en.json` and `assets/lang/es.json`.
