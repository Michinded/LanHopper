# LanHopper — User Guide

## First launch

1. Open **LanHopper** from your Applications folder.
2. Go to **Settings** and configure:
   - **Device name** — display name shown in the browser when other devices connect.
   - **Port** — HTTP port the server will listen on (default: `8080`).
   - **Shared folder** — the folder whose contents will be available for download.
   - **QR token validity** — how long the QR code stays valid before rotating (minutes).
   - **Session duration** — how long a browser session stays active after login (minutes).
3. Press **Save**.

## Starting the server

1. Go to the **Server** screen.
2. Press **Start Server**.
3. The screen will show:
   - The local URL (e.g. `http://192.168.1.10:8080`)
   - A one-time session password
   - A QR code for quick access

## Connecting from another device

**Via QR code (recommended):**
- Scan the QR code with your phone or tablet — it opens the browser and logs you in automatically.
- The QR code rotates on the configured interval. Scan it before it expires.

**Via URL:**
- Open the URL shown in the Server screen on any browser on the same network.
- Enter the session password when prompted.

## Downloading files

- Once logged in, browse the shared folder in the browser.
- Click any file to download it.

## Stopping the server

- Press **Stop Server** on the Server screen.
- All active sessions are immediately invalidated.
- A new password and QR code are generated on the next start.

## Security notes

- The password is randomly generated on every server start and never stored.
- The QR code is single-use and rotates automatically — do not share screenshots of it.
- Sessions do not survive a server restart.
- Only devices on the same local network can connect.

## Settings reference

| Setting | Default | Description |
|---|---|---|
| Device name | `LanHopper` | Display name shown in the browser |
| Port | `8080` | HTTP server port |
| Shared folder | — | Local or network folder to share |
| QR token validity | `5 min` | How often the QR code rotates |
| Session duration | `60 min` | Browser session timeout |
| Max upload size | `512 MB` | Maximum file size per upload (or unlimited) |
| Language | `English` | UI language (English / Spanish) |
| Theme | `Dark` | App appearance |
