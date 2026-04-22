---
name: flet-guide
description: |
  Portable guide for building Flet >= 0.80 desktop applications. Use this skill whenever you are writing or modifying Flet UI code: adding a new view, using any Flet control constructor (FilledButton, Dropdown, Image, AlertDialog, FilePicker, etc.), handling background-to-UI callbacks, managing overlays, or structuring views following the KISS pattern. The Flet API changed substantially at 0.80 — many parameter names were renamed or made positional — so use this skill even for small control changes to avoid keyword argument errors. Works in any Flet project, not tied to any specific codebase.
---

# Flet >= 0.80 Guide

Flet 0.80 rewrote large parts of the control API. Most online examples and the official docs still show old signatures. When an `unexpected keyword argument` error appears, grep the installed source — do not trust examples:

```bash
grep -n "def __init__" .venv/lib/python3.14/site-packages/flet/controls/<ControlName>.py
```

See `references/api.md` for the complete verified API cheatsheet.

## Quick-reference: most common traps

| Use this | Not this |
|---|---|
| `ft.run(main)` | `ft.app(target=main)` |
| `ft.Icon(ft.Icons.HOME)` | `ft.Icon(name=ft.Icons.HOME)` |
| `FilledButton(content="Label", icon=..., on_click=fn)` | `FilledButton(text="Label")` |
| `ElevatedButton(content="Label")` | `ElevatedButton(text="Label")` |
| `OutlinedButton(content="Label")` | `OutlinedButton(text="Label")` |
| `TextButton(content="Label")` | `TextButton(text="Label")` |
| `Dropdown(on_select=fn)` | `Dropdown(on_change=fn)` |
| `NavigationRail(on_change=fn)` | `NavigationRail(on_select=fn)` ← exception |
| `ft.BoxFit.CONTAIN` | `ft.ImageFit.CONTAIN` |
| `ft.Image(src)` — positional, non-empty | `ft.Image(src_base64=b64)` |
| `await Clipboard().set(value)` — async | `page.set_clipboard(value)` |
| `page.show_dialog(ft.SnackBar(...))` | Adding SnackBar to `controls[]` |

---

## View pattern

Every screen is a `ft.Column` subclass. The pattern separates three concerns: **construction** (`_build`), **lifecycle** (`did_mount`/`will_unmount`), and **state → UI** (`_refresh`).

### Anatomy

```python
class MyView(ft.Column):
    def __init__(self):
        super().__init__(expand=True, spacing=20)
        self._active = False
        self._build()

    # ── Construction ──────────────────────────────────────────────
    def _build(self):
        """Pure widget tree. No I/O. Store refs to mutable controls."""
        self._label = ft.Text("initial value")
        self._btn = ft.FilledButton(
            content="Do it",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._on_action,
        )
        # One assignment at the end
        self.controls = [self._label, self._btn]

    # ── Lifecycle ─────────────────────────────────────────────────
    def did_mount(self):
        """Register overlays. Start background tasks.
        Do NOT call page.update() here."""
        self._active = True
        self.page.overlay.append(self._dialog)
        self.page.run_task(self._background_loop)

    def will_unmount(self):
        """Stop loops. Remove overlays."""
        self._active = False
        if self._dialog in self.page.overlay:
            self.page.overlay.remove(self._dialog)

    # ── State → UI ────────────────────────────────────────────────
    def _refresh(self, running: bool):
        """All state changes come through here. One place, predictable."""
        self._label.value = "Running" if running else "Stopped"
        self._btn.disabled = running
        self.update()

    # ── Event handlers ────────────────────────────────────────────
    def _on_action(self, _):
        """Thin: validate → call service → refresh."""
        result = my_service.do_something()
        self._refresh(result.running)
```

### Why this works

- **`_build()` is pure.** No network calls, no file reads. Only widget construction. This makes the view testable and the tree predictable.
- **`_refresh()` is the single update path.** Funneling all state changes here means you never forget `self.update()` and the rendering logic stays in one readable place.
- **`did_mount` / `will_unmount` are paired.** Everything started in `did_mount` is stopped in `will_unmount`. Missing `will_unmount` cleanup causes memory leaks and ghost tasks when navigating between screens.
- **Event handlers delegate.** If a handler contains business logic rather than just calling a service, that logic belongs in a service or logic module.

---

## Background callbacks → UI

Background threads cannot touch Flet controls. Route all UI updates through `page.run_task()`:

```python
# Called from a background thread
def _on_server_event(self, data):
    if self.page:
        self.page.run_task(self._apply_event, data)

# Runs on the Flet event loop — safe to update controls
async def _apply_event(self, data):
    self._label.value = data.text
    self.update()
```

For a polling loop:

```python
async def _background_loop(self):
    while self._active:
        value = compute_something()
        self._label.value = value
        if self.page:
            self.page.update()
        await asyncio.sleep(1)
```

---

## Overlay management

`AlertDialog` and persistent `FilePicker` instances must live in `page.overlay`, not in a control tree.

```python
def _build(self):
    # Placeholder title is required — an empty AlertDialog fails
    # Flet's validation even before it's opened
    self._dialog = ft.AlertDialog(modal=True, title=ft.Text(" "))

def did_mount(self):
    self.page.overlay.append(self._dialog)
    # No page.update() here

def will_unmount(self):
    self.page.overlay.remove(self._dialog)

def _show_confirm(self, title: str, body: str, on_confirm):
    def _close(_):
        self._dialog.open = False
        self.page.update()

    self._dialog.title = ft.Text(title)
    self._dialog.content = ft.Text(body)
    self._dialog.actions = [
        ft.TextButton(content="Cancel", on_click=_close),
        ft.FilledButton(content="OK", on_click=on_confirm),
    ]
    self._dialog.open = True
    self.page.update()
```

---

## Image slot pattern

`ft.Image` requires a non-empty `src` — an empty string fails Flet validation on mount. When the image data isn't available yet, use a Container as a slot:

```python
def _build(self):
    self._img_slot = ft.Container(width=180, height=180)

# Later, when data arrives:
def _show_image(self, b64: str):
    self._img_slot.content = ft.Image(
        b64,
        width=180,
        height=180,
        fit=ft.BoxFit.CONTAIN,
    )
    self._img_slot.update()
```

---

## SnackBar

```python
# Success
self.page.show_dialog(ft.SnackBar(
    content=ft.Text("Saved successfully"),
    bgcolor=ft.Colors.GREEN_700,
))

# Error
self.page.show_dialog(ft.SnackBar(
    content=ft.Text("Something went wrong"),
    bgcolor=ft.Colors.RED_700,
))
```

---

## FilePicker — two modes

**One-shot (no overlay needed):**
```python
async def _on_browse(self, _):
    path = await ft.FilePicker().get_directory_path()
    if path:
        self._field.value = path
        self._field.update()
```

**Persistent with callback (overlay required):**
```python
def _build(self):
    self._picker = ft.FilePicker()
    self._picker.on_result = self._on_pick_result  # assign after init

def did_mount(self):
    self.page.overlay.append(self._picker)

def will_unmount(self):
    self.page.overlay.remove(self._picker)

def _on_pick_result(self, e: ft.FilePickerResultEvent):
    if e.files:
        self._handle_files(e.files)
```

---

## Clipboard

```python
from flet.controls.services.clipboard import Clipboard

async def _copy(self, _):
    await Clipboard().set(self._value)
    self.page.show_dialog(ft.SnackBar(
        content=ft.Text("Copied to clipboard"),
        bgcolor=ft.Colors.GREEN_700,
    ))
```

The handler must be `async`.

---

## Adding a new screen — checklist

1. Create `app/views/<screen>.py` as a `ft.Column` subclass.
2. Add a `NavigationRailDestination` in your home/shell view.
3. Handle the new index in the navigation callback.
4. If the screen needs a service, create or extend `app/services/<service>.py`.
5. Add any string literals through your i18n system — no hardcoded UI text.

For the complete API reference (every verified control signature), see `references/api.md`.
