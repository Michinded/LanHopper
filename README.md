# LanHopper

A simple LAN file transfer tool with a modern desktop UI.

## Features

- Transfer files between devices on the same network
- Password-protected sessions (auto-generated on each start)
- QR code for easy connection from other devices
- JWT-secured REST API
- Configurable port, shared folder, and device name
- Multi-language support

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
2. Configure your shared folder and port in Settings
3. Press **Start Server**
4. A 6-digit password and QR code are displayed
5. On another device, scan the QR or open the URL and enter the password
6. Transfer files freely within the session
