# LanHopper

A simple LAN file transfer tool with a modern desktop UI.

## Features

- Transfer files between devices on the same network
- 6-character alphanumeric password auto-generated on each server start
- Single-use QR code that rotates automatically (configurable interval)
- QR code grants direct browser access without typing the password
- JWT-secured REST API and browser sessions (cookie-based)
- Configurable port, shared folder, device name, QR validity, and session duration
- Local and network (UNC / mount) shared folder support
- Multi-language support (English / Spanish)

---

## For users

Download the latest release for your platform from the [Releases page](https://github.com/Michinded/LanHopper/releases).

| Platform | File |
|---|---|
| macOS | `LanHopper-vX.X.X-fbuild.dmg` |

1. Open the `.dmg` and drag **LanHopper** to your Applications folder.
2. Launch the app.

See the [User Guide](docs/user-guide.md) for full usage instructions.

---

## For developers

### Requirements

- Python 3.10+
- Flutter (stable) — required for `flet build`
- Xcode 15+ and CocoaPods 1.16+ (macOS builds)

### Setup

```bash
pip install -r requirements.txt
python main.py
```

### Building

LanHopper uses `flet build` to produce native desktop bundles. PyInstaller is not supported with Flet >= 0.80.

```bash
flet build macos
```

See [`docs/builds/flet-build-macos.md`](docs/builds/flet-build-macos.md) for the full build and DMG packaging guide.

---

## Security and disclaimer

LanHopper is designed for **private local networks only**. Traffic is unencrypted HTTP — do not use it on public or untrusted Wi-Fi.

This is an open-source, non-commercial project provided **as is** with no warranties. The authors are not liable for any damages resulting from its use. Bug reports and feedback are welcome via [GitHub Issues](https://github.com/Michinded/LanHopper/issues).

See the [User Guide](docs/user-guide.md#security-notes-and-best-practices) for the full security notes and recommended practices.

---

## Configuration (`data/user_config.json`)

Created automatically on first launch. Editable via the Settings screen.

| Key | Default | Description |
|---|---|---|
| `device_name` | `LanHopper` | Display name shown in the browser |
| `port` | `8080` | HTTP server port |
| `shared_folder` | `./shared` | Folder to share (local or network) |
| `language` | `en` | UI language (`en` / `es`) |
| `qr_token_minutes` | `5` | QR code validity in minutes |
| `session_minutes` | `60` | Browser session duration in minutes |
