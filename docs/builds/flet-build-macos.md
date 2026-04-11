# Flet Build — macOS

Build guide for generating a macOS `.app` bundle and `.dmg` installer using `flet build`.

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Xcode | 15+ | App Store |
| CocoaPods | 1.16+ | `brew install cocoapods` |
| Flutter | stable | [flutter.dev](https://flutter.dev/docs/get-started/install/macos) |
| create-dmg | any | `brew install create-dmg` |

Verify your environment:

```bash
flet doctor
flutter doctor
```

---

## App metadata — `pyproject.toml`

`flet build` reads bundle metadata from `pyproject.toml` at the project root. This controls the `Info.plist` values embedded in the `.app`, including the bundle identifier, version, and minimum macOS version.

```toml
[tool.flet]
app_name = "LanHopper"
product = "LanHopper"
description = "Simple LAN file transfer tool with a modern desktop UI."
company = "Michinded"
copyright = "Copyright © 2025 Michinded. MIT License."
version = "0.9.0"

[tool.flet.macos]
bundle_id = "com.michinded.lanhopper"
minimum_version = "11.0"
```

**Update `version` here before every release.** The bundle identifier follows reverse-domain notation and should remain stable across releases.

`minimum_version = "11.0"` targets macOS Big Sur and later, which covers all Apple Silicon Macs and Intel Macs from ~2015 onward.

---

## Icon requirements

Place the following files in `assets/` before building:

| File | Purpose |
|---|---|
| `assets/icon.png` | Source image (min 1024×1024 px) — auto-detected by `flet build` |
| `assets/icon.icns` | macOS bundle icon (generated from PNG) |
| `assets/icon.ico` | Windows icon (generated from PNG) |

### Regenerate icons from PNG

```bash
# .icns (macOS)
mkdir icon.iconset
sips -z 16 16     assets/icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     assets/icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     assets/icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     assets/icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   assets/icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   assets/icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   assets/icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   assets/icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   assets/icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 assets/icon.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset -o assets/icon.icns
rm -rf icon.iconset

# .ico (Windows)
python -c "
from PIL import Image
img = Image.open('assets/icon.png').convert('RGBA')
img.save('assets/icon.ico', format='ICO', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
"
```

---

## Build

```bash
.venv/bin/flet build macos
```

Output: `build/macos/LanHopper.app`

The resulting `.app` is a **universal binary** — runs natively on both Apple Silicon (arm64) and Intel (x86_64) Macs with macOS 11+.

---

## Troubleshooting — known issues

### `ModuleNotFoundError: No module named 'tkinter'`

`flet build` embeds a minimal Python runtime via `serious_python`. `tkinter` is a C extension that is not pip-installable and is never included in the bundle.

**Fix:** Replace any `tkinter` usage with Flet's native alternatives:
- Folder/file picker → `ft.FilePicker().get_directory_path()` (async)
- Clipboard → `await Clipboard().set(value)` from `flet.controls.services.clipboard`

### Build fails with codesign error on `Dav1d.framework`

On newer versions of macOS and Xcode the codesign step may fail with:

```
bundle format unrecognized, invalid, or unsuitable
In subcomponent: .../Flet.app/Contents/Frameworks/Dav1d.framework
```

**Fix:** Re-sign the Flet desktop client before building:

```bash
# Find your installed Flet client version
ls ~/.flet/client/

# Re-sign (replace 0.84.0 with your version)
codesign --force --deep --sign - ~/.flet/client/flet-desktop-full-0.84.0/Flet.app
codesign --force --sign - ~/.flet/client/flet-desktop-full-0.84.0/Flet.app/Contents/Frameworks/Dav1d.framework

# Clear PyInstaller binary cache if present
rm -rf ~/Library/Application\ Support/pyinstaller/
```

Then run `flet build macos` again.

---

## Package as DMG

```bash
create-dmg \
  --volname "LanHopper" \
  --volicon "assets/icon.icns" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 128 \
  --icon "LanHopper.app" 150 185 \
  --hide-extension "LanHopper.app" \
  --app-drop-link 450 185 \
  "releases/LanHopper-v<VERSION>-fbuild.dmg" \
  "build/macos/"
```

Replace `<VERSION>` with the current version (e.g. `0.9.0`). The naming convention `fbuild` indicates a Flet build, as opposed to `pbuild` for PyInstaller.

Output: `releases/LanHopper-v<VERSION>-fbuild.dmg`

---

## Notes

- `flet build` does not include `tkinter` — use `ft.FilePicker()` for file/folder dialogs.
- The `.app` bundle uses the Flutter runtime and embeds Python via `serious_python`.
- Built on macOS only — cross-compilation is not supported.
- The `releases/` directory is gitignored; upload artifacts manually to GitHub Releases.
- **PyInstaller is not supported** with Flet >= 0.80 on macOS. The Flet desktop bundle includes Swift/Flutter binaries (`libswift_Concurrency.dylib`, `Dav1d.framework`) that PyInstaller 6.x cannot codesign correctly. Use `flet build` exclusively.
