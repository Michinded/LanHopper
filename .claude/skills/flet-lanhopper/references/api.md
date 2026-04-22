# Flet >= 0.80 API — Complete Reference for LanHopper

All signatures verified against the installed package at:
`.venv/lib/python3.14/site-packages/flet/controls/`

---

## App entry point

```python
# Correct
ft.run(main, assets_dir="assets")

# Wrong (removed)
ft.app(target=main)
```

---

## Buttons

All button types (`FilledButton`, `ElevatedButton`, `OutlinedButton`, `TextButton`) use `content=` not `text=`.

```python
ft.FilledButton(
    content="Save",           # str or ft.Text(...)
    icon=ft.Icons.SAVE,       # optional
    on_click=handler,
    disabled=False,
)

ft.ElevatedButton(
    content="Open",
    icon=ft.Icons.OPEN_IN_NEW,
    on_click=handler,
)

ft.OutlinedButton(
    content="Cancel",
    on_click=handler,
)

ft.TextButton(
    content="Close",
    on_click=handler,
)

# IconButton — unchanged, no content= needed
ft.IconButton(
    icon=ft.Icons.COPY_OUTLINED,
    tooltip="Copy",
    on_click=handler,
)
```

---

## Icon

```python
# Correct — positional
ft.Icon(ft.Icons.HOME)
ft.Icon(ft.Icons.HOME, color=ft.Colors.GREEN_500, size=20)

# Wrong
ft.Icon(name=ft.Icons.HOME)
```

---

## Dropdown

```python
ft.Dropdown(
    label="Language",
    value="en",
    width=180,
    options=[
        ft.dropdown.Option(key="en", text="English"),
        ft.dropdown.Option(key="es", text="Español"),
    ],
    on_select=handler,   # NOT on_change
)
```

The event value is `e.control.value`.

**Exception:** `NavigationRail` still uses `on_change`, not `on_select`.

```python
ft.NavigationRail(
    selected_index=0,
    destinations=[...],
    on_change=lambda e: navigate(e.control.selected_index),
)
```

---

## Image

`src` is a required positional argument. Accepts URL, base64 string, or raw bytes. Must be non-empty — an `ft.Image("")` will fail Flet validation on mount.

```python
# Correct
ft.Image(b64_string, width=180, height=180, fit=ft.BoxFit.CONTAIN)
ft.Image("https://example.com/img.png")

# Wrong
ft.Image(src_base64=b64_string)   # src_base64 does not exist
ft.Image("")                       # fails validation
```

When the image data is not yet available, use a Container slot:

```python
self._img_slot = ft.Container(width=180, height=180)

# Later, when data arrives:
self._img_slot.content = ft.Image(b64, width=180, height=180, fit=ft.BoxFit.CONTAIN)
self._img_slot.update()
```

`ft.BoxFit` (not `ft.ImageFit`, which was removed):

```python
ft.BoxFit.CONTAIN
ft.BoxFit.COVER
ft.BoxFit.FILL
ft.BoxFit.FIT_WIDTH
ft.BoxFit.FIT_HEIGHT
ft.BoxFit.NONE
ft.BoxFit.SCALE_DOWN
```

---

## Clipboard

Both `page.set_clipboard()` and `page.clipboard =` are removed. The handler must be `async`:

```python
from flet.controls.services.clipboard import Clipboard

async def _copy_url(self, _):
    await Clipboard().set(self._url)
    self.page.show_dialog(ft.SnackBar(
        content=ft.Text("Copied"),
        bgcolor=ft.Colors.GREEN_700,
    ))
```

---

## SnackBar

Do not add to `controls[]` or manage `.open` manually. Use `page.show_dialog()`:

```python
# Success
self.page.show_dialog(ft.SnackBar(
    content=ft.Text(i18n.t("saved")),
    bgcolor=ft.Colors.GREEN_700,
))

# Error
self.page.show_dialog(ft.SnackBar(
    content=ft.Text(i18n.t("error_msg")),
    bgcolor=ft.Colors.RED_700,
))
```

---

## AlertDialog

Must live in `page.overlay`. An empty dialog fails validation — always initialize with a placeholder title:

```python
def _build(self):
    self._dialog = ft.AlertDialog(modal=True, title=ft.Text(" "))

def did_mount(self):
    self.page.overlay.append(self._dialog)
    # Do NOT call page.update() here

def will_unmount(self):
    self.page.overlay.remove(self._dialog)

def _show_dialog(self, title: str, body: str, actions: list):
    self._dialog.title = ft.Text(title)
    self._dialog.content = ft.Text(body)
    self._dialog.actions = actions
    self._dialog.open = True
    self.page.update()
```

---

## FilePicker

Two usage modes:

**One-shot (no overlay needed):** calling `get_directory_path()` or `pick_files()` directly:
```python
async def _on_browse(self, _):
    path = await ft.FilePicker().get_directory_path()
    if path:
        self._field_path.value = path
        self._field_path.update()
```

**Persistent (with `on_result` callback):** must go in `page.overlay`. Do not pass `on_result` to `__init__` — assign it after:
```python
def _build(self):
    self._picker = ft.FilePicker()
    self._picker.on_result = self._on_pick_result

def did_mount(self):
    self.page.overlay.append(self._picker)

def will_unmount(self):
    self.page.overlay.remove(self._picker)

def _on_pick_result(self, e: ft.FilePickerResultEvent):
    if e.files:
        self._handle_files(e.files)
```

---

## UrlLauncher

```python
from flet.controls.services.url_launcher import UrlLauncher

async def _open_link(_):
    await UrlLauncher().launch_url("https://example.com")
```

---

## Colors and padding

```python
# With opacity
ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE)

# Padding — use ft.Padding for asymmetric
ft.Padding(left=32, right=32, top=28, bottom=32)

# Or uniform
padding=16
```

---

## Background thread → UI update rule

Never update a control from a background thread. Use `page.run_task()` to schedule on the Flet event loop:

```python
# From a background thread
def _on_background_event(self, data):
    if self.page:
        self.page.run_task(self._apply_on_loop, data)

# Runs on Flet event loop
async def _apply_on_loop(self, data):
    self._label.value = data.text
    self.update()
```

For a background polling loop:

```python
def did_mount(self):
    self._active = True
    self.page.run_task(self._poll_loop)

def will_unmount(self):
    self._active = False

async def _poll_loop(self):
    while self._active:
        # do work
        self._label.value = compute_value()
        if self.page:
            self.page.update()
        await asyncio.sleep(1)
```

---

## did_mount / will_unmount rules

- `did_mount`: register overlays, start background tasks, subscribe to callbacks.
- `will_unmount`: stop loops, remove overlays, clear callbacks.
- **Never call `page.update()` inside `did_mount`** — it causes a nested update cycle.
- Overlays registered in `did_mount` must be removed in `will_unmount` to avoid leaks when navigating.

---

## NavigationRail pattern

```python
rail = ft.NavigationRail(
    selected_index=0,
    label_type=ft.NavigationRailLabelType.ALL,
    min_width=80,
    group_alignment=-1.0,
    destinations=[
        ft.NavigationRailDestination(
            icon=ft.Icons.HOME_OUTLINED,
            selected_icon=ft.Icons.HOME,
            label=i18n.t("home"),
        ),
    ],
    on_change=lambda e: navigate(e.control.selected_index),
)
```

Note: `on_change` (not `on_select`) for NavigationRail.
