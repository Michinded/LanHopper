---
name: flet-lanhopper
description: |
  Working guide for Flet >= 0.80 UI code in the LanHopper project. Use this skill whenever you are: adding a new screen or view, modifying existing views, debugging a Flet control error (unexpected keyword argument, overlay issues, update cycle errors), writing background-to-UI callbacks, or structuring new UI features. The Flet API changed substantially at 0.80 — many parameter names were renamed or made positional — so consult this skill for any Flet control constructor. Also use it when separating logic from views, deciding what goes in a view vs a module, or when unsure how to structure a new feature following the project's KISS pattern.
---

# Flet >= 0.80 in LanHopper

The project uses Flet >= 0.80, which introduced breaking API changes from what most online examples and docs show. The installed source is the authoritative reference: `.venv/lib/python3.14/site-packages/flet/controls/`.

## API quick-reference

Most common traps — see `references/api.md` for the complete cheatsheet:

| Use this | Not this |
|---|---|
| `ft.run(main)` | `ft.app(target=main)` |
| `ft.Icon(ft.Icons.HOME)` | `ft.Icon(name=ft.Icons.HOME)` |
| `FilledButton(content="Label", icon=..., on_click=fn)` | `FilledButton(text="Label")` |
| `ElevatedButton(content="Label")` | `ElevatedButton(text="Label")` |
| `OutlinedButton(content="Label")` | `OutlinedButton(text="Label")` |
| `Dropdown(on_select=fn)` | `Dropdown(on_change=fn)` |
| `ft.BoxFit.CONTAIN` | `ft.ImageFit.CONTAIN` |
| `ft.Image(src)` — positional, must be non-empty | `ft.Image(src_base64=b64)` |
| `await Clipboard().set(value)` — async handler | `page.set_clipboard(value)` |
| `page.show_dialog(ft.SnackBar(...))` | Adding SnackBar to `controls[]` |

When an `unexpected keyword argument` error appears, grep the installed source rather than trusting examples:
```bash
grep -n "def __init__" .venv/lib/python3.14/site-packages/flet/controls/<ControlName>.py
```

---

## View pattern (KISS)

Every screen is a `ft.Column` subclass in `app/views/<name>.py`. The goal is that views are thin renderers: they display state and forward user actions. Business logic lives in modules (`app/server`, `app/config`, `app/utils/`).

### View anatomy

```python
class MyView(ft.Column):
    def __init__(self):
        super().__init__(expand=True, spacing=20,
                         alignment=ft.MainAxisAlignment.CENTER)
        # Capture initial state from modules, not derived logic
        self._state = module.get_initial_state()
        self._build()

    # ── Construction ──────────────────────────────────────────────
    def _build(self):
        """Pure widget construction. No I/O, no module calls beyond
        reading the initial display value. Store refs to anything
        that will change as self._widget_name."""
        self._label = ft.Text(self._state.display_text)
        self._action_btn = ft.FilledButton(
            content=i18n.t("action_label"),
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._on_action,
        )
        # Assign self.controls once at the end
        self.controls = [self._label, self._action_btn]

    # ── Lifecycle ─────────────────────────────────────────────────
    def did_mount(self):
        """Start background tasks and register overlays here.
        Do NOT call page.update() inside did_mount."""
        self.page.overlay.append(self._dialog)   # if any
        self.page.run_task(self._background_loop)

    def will_unmount(self):
        """Stop loops and deregister overlays."""
        self._running = False
        if self._dialog in self.page.overlay:
            self.page.overlay.remove(self._dialog)

    # ── State → UI ────────────────────────────────────────────────
    def _refresh(self, running: bool):
        """Single place where state drives the UI.
        Funneling all updates here prevents forgetting .update()
        and makes the rendering logic easy to follow."""
        self._label.value = i18n.t("running") if running else i18n.t("stopped")
        self._action_btn.disabled = not module.can_act()
        self.update()

    # ── Event handlers ────────────────────────────────────────────
    def _on_action(self, _):
        """Thin: validate → call module → refresh."""
        result = module.do_something()
        self._refresh(result.running)

    def _on_error(self, message: str):
        self.page.show_dialog(ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_700,
        ))
```

### The rules behind the pattern

**`_build()` is pure widget construction.** It sets up the tree and stores mutable-control refs. No network calls, no file reads, no logic. The only module call here is reading the initial display value already held in `self._state`.

**`_refresh()` is the single state→UI path.** Every state change — whether from a button click, a background loop, or a module callback — funnels through `_refresh()`. This keeps updates predictable and the rendering logic in one place.

**`did_mount` / `will_unmount` manage side effects.** Background tasks and overlay registrations live here, not in `__init__`. Always pair start/stop. Never call `page.update()` inside `did_mount` — it triggers a nested update cycle.

**Event handlers delegate, never decide.** They validate user input, call a module function, then call `_refresh()`. If there's business logic building up inside a handler, it belongs in a module.

---

## Background callbacks → UI

Background threads and server callbacks cannot touch Flet controls directly. Route everything through `page.run_task()`:

```python
# Called from a background thread (e.g., a server callback)
def _on_server_event(self, data):
    if self.page:
        self.page.run_task(self._apply_event, data)

# This runs on the Flet event loop — safe to update controls
async def _apply_event(self, data):
    self._label.value = data.display_value
    self.update()
```

The pattern in this project: background callbacks are registered with `server.set_qr_callback(self._on_qr_rotated)` in `did_mount` and cleared with `server.set_qr_callback(None)` in `will_unmount`.

---

## Overlay management (AlertDialog, FilePicker)

Dialogs and file pickers must live in `page.overlay`, not in a control tree:

```python
def _build(self):
    # Initialize with a placeholder title — an empty AlertDialog
    # fails Flet validation even before it's opened
    self._confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(" "),
    )

def did_mount(self):
    self.page.overlay.append(self._confirm_dialog)
    # No page.update() here

def will_unmount(self):
    self.page.overlay.remove(self._confirm_dialog)
```

To open the dialog:
```python
def _show_confirm(self, message: str, on_confirm):
    def _close(_):
        self._confirm_dialog.open = False
        self.page.update()

    self._confirm_dialog.title = ft.Text(i18n.t("confirm"))
    self._confirm_dialog.content = ft.Text(message)
    self._confirm_dialog.actions = [
        ft.TextButton(content=i18n.t("cancel"), on_click=_close),
        ft.FilledButton(content=i18n.t("ok"), on_click=on_confirm),
    ]
    self._confirm_dialog.open = True
    self.page.update()
```

---

## KISS: what goes where

The key question is: "does this code describe *what to show*, or *how something works*?"

| Concern | Location |
|---|---|
| Widget tree, layout, visual state updates | `app/views/<name>.py` |
| Server start/stop, session state, QR logic | `app/server.py` |
| Reading and writing user config | `app/config.py` |
| Network checks, path helpers, pure functions | `app/utils/` |
| All UI-visible strings | `i18n.t("key")` — add to both lang files |
| New HTTP endpoints | `app/api/<router>.py`, included in `app/server.py` |

If a view method is doing more than: read module state → update controls → call `self.update()`, it likely belongs in a module. A view that reads `server.is_running()` and shows a green dot is good. A view that computes whether the server *should* be running is not.

---

## Adding a new screen — checklist

1. Create `app/views/<screen>.py` as a `ft.Column` subclass using the anatomy above.
2. Add a `NavigationRailDestination` in `app/views/home.py`.
3. Handle the new index in `HomeView._navigate()`.
4. Add i18n keys to `assets/lang/en.json` and `assets/lang/es.json`.
5. If the screen needs an API route, add it in `app/api/` and include the router in `app/server.py`.

---

## Common pitfalls

**Image with no src crashes on mount.** Use a `ft.Container` as a slot and assign `container.content = ft.Image(b64)` only once data is available.

**`ft.Image` has no `src_base64` kwarg.** Pass the base64 string as the first positional argument: `ft.Image(b64_string, fit=ft.BoxFit.CONTAIN)`.

**`NavigationRail` still uses `on_change`.** The rename to `on_select` applies to `Dropdown`, not `NavigationRail`.

**`ft.FilePicker` used directly in a handler** (no overlay needed for `get_directory_path()` one-shot calls): `path = await ft.FilePicker().get_directory_path()`. For persistent pickers with `on_result` callbacks, use the overlay pattern.

**`TextButton` also uses `content=`, not `text=`.** Same rule as the other button types.

---

For a full reference of every verified API signature in this project, read `references/api.md`.
