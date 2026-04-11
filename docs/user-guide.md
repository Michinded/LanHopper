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

## Security notes and best practices

### How LanHopper protects your session

- The password is randomly generated on every server start and never stored on disk.
- The QR code is single-use and rotates automatically — scanning it a second time will not grant access.
- Sessions are invalidated immediately when the server is stopped.
- All file access is restricted to the configured shared folder — no other part of your system is reachable.

### Recommended practices

- **Only share what you need.** Point the shared folder to a dedicated transfer folder, not your entire home directory or Documents.
- **Stop the server when you're done.** Don't leave it running unattended, even on a trusted network.
- **Don't share QR screenshots.** The QR encodes a one-time token — treat it like a password.
- **Use short QR and session timeouts.** The defaults (5 min QR / 60 min session) are a reasonable balance; lower them if you're in a less trusted environment.
- **Trusted networks only.** LanHopper is designed for private home or office networks. Avoid using it on public Wi-Fi or shared hotspots.
- **No HTTPS.** Traffic between devices is unencrypted HTTP. This is acceptable on a private LAN but means data could be intercepted on untrusted networks.

## Disclaimer

LanHopper is an open-source project provided **as is**, free of charge, with no warranties of any kind — express or implied.

- The authors are not responsible for any data loss, unauthorized access, security breaches, or any other damages resulting from the use or misuse of this software.
- By using LanHopper, you accept full responsibility for how and where you run it.
- This is a non-commercial project maintained on a best-effort basis. There are no guaranteed response times or obligations to fix reported issues, though feedback and bug reports are always welcome via [GitHub Issues](https://github.com/Michinded/LanHopper/issues).

If you discover a security vulnerability, please report it through GitHub Issues and we will review it as soon as possible.

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
