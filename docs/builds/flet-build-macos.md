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

## Build

```bash
.venv/bin/flet build macos
```

Output: `build/macos/LanHopper.app`

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

## Notes

- `flet build` does not include `tkinter` — use `ft.FilePicker()` for file/folder dialogs.
- The `.app` bundle uses the Flutter runtime and embeds Python via `serious_python`.
- Built on macOS only — cross-compilation is not supported.
- The `releases/` directory is gitignored; upload artifacts manually to GitHub Releases.
