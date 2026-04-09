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

## Requirements

- Python 3.10+
- See `requirements.txt`

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Build executable

```bash
pyinstaller LanHopper.spec
```

## Usage

1. Launch the app
2. Go to **Settings** — configure shared folder, port, and security timings
3. Go to **Server** — press **Start Server**
4. The terminal shows the LAN URL, password, and QR URL
5. On another device: scan the QR for instant access, or open the URL and enter the password
6. Browse and download files from the shared folder
7. Press **Log out** in the browser when done, or let the session expire

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
