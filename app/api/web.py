from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from jose import jwt

import app.server as server
from app import config

router = APIRouter()

_TOKEN_EXPIRE_MINUTES = 60

# ------------------------------------------------------------------- helpers

def _make_token() -> str:
    payload = {
        "sub": "lanhopper-client",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, server.session["jwt_secret"], algorithm="HS256")


def _shared_path() -> Path:
    cfg = config.load()
    folder = cfg.get("shared_folder", {})
    if isinstance(folder, str):
        return Path(folder).expanduser()
    return Path(folder.get("path", "")).expanduser()


# ----------------------------------------------------------------- routes

@router.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    """Public login page. Redirect to /browse if already authenticated."""
    token = request.cookies.get("access_token")
    if token:
        try:
            jwt.decode(token, server.session["jwt_secret"], algorithms=["HS256"])
            return RedirectResponse(url="/browse")
        except Exception:
            pass
    return HTMLResponse(_login_html(error=False))


@router.post("/web/login")
async def web_login(request: Request, password: str = Form(...)):
    """Form-based login. Sets JWT cookie and redirects to /browse."""
    if password != server.session.get("password"):
        return HTMLResponse(_login_html(error=True), status_code=401)

    token = _make_token()
    response = RedirectResponse(url="/browse", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=_TOKEN_EXPIRE_MINUTES * 60,
        samesite="strict",
    )
    return response


@router.get("/browse", response_class=HTMLResponse)
def browse_page():
    """File listing page — protected by AuthMiddleware via cookie."""
    path = _shared_path()
    files = []
    if path.exists():
        files = sorted(
            [f for f in path.iterdir() if f.is_file()],
            key=lambda f: f.name.lower(),
        )
    cfg = config.load()
    device_name = cfg.get("device_name", "LanHopper")
    return HTMLResponse(_browse_html(files, device_name))


# ----------------------------------------------------------------- html

def _login_html(error: bool) -> str:
    error_block = (
        '<p class="error">Incorrect password. Try again.</p>' if error else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LanHopper — Login</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: system-ui, sans-serif;
      background: #f5f5f5;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }}
    .card {{
      background: white;
      border-radius: 16px;
      padding: 40px 36px;
      width: 100%;
      max-width: 360px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.08);
      text-align: center;
    }}
    h1 {{ font-size: 1.6rem; margin-bottom: 6px; }}
    .subtitle {{ color: #888; font-size: 0.9rem; margin-bottom: 28px; }}
    input[type=password] {{
      width: 100%;
      padding: 12px 14px;
      border: 1px solid #ddd;
      border-radius: 8px;
      font-size: 1.1rem;
      letter-spacing: 0.2em;
      text-align: center;
      margin-bottom: 14px;
      outline: none;
    }}
    input[type=password]:focus {{ border-color: #6750A4; }}
    button {{
      width: 100%;
      padding: 12px;
      background: #6750A4;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 1rem;
      cursor: pointer;
    }}
    button:hover {{ background: #7965AF; }}
    .error {{ color: #c62828; font-size: 0.85rem; margin-bottom: 12px; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>LanHopper</h1>
    <p class="subtitle">Enter the session password</p>
    {error_block}
    <form method="post" action="/web/login">
      <input type="password" name="password" autofocus autocomplete="off" placeholder="••••••">
      <button type="submit">Connect</button>
    </form>
  </div>
</body>
</html>"""


def _browse_html(files: list[Path], device_name: str) -> str:
    if files:
        rows = "".join(
            f'<tr>'
            f'<td><a href="/files/download/{f.name}">{f.name}</a></td>'
            f'<td class="size">{_fmt_size(f.stat().st_size)}</td>'
            f'</tr>'
            for f in files
        )
        table = f"""
        <table>
          <thead><tr><th>File</th><th>Size</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>"""
    else:
        table = '<p class="empty">No files in the shared folder yet.</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LanHopper — {device_name}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: system-ui, sans-serif; background: #f5f5f5; color: #1c1c1e; }}
    header {{
      background: #6750A4;
      color: white;
      padding: 16px 24px;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    header h1 {{ font-size: 1.2rem; font-weight: 600; }}
    header span {{ font-size: 0.85rem; opacity: 0.8; }}
    main {{ max-width: 760px; margin: 32px auto; padding: 0 16px; }}
    table {{ width: 100%; border-collapse: collapse; background: white;
             border-radius: 12px; overflow: hidden;
             box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}
    th {{ background: #f0ecf8; padding: 12px 16px; text-align: left;
          font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }}
    td {{ padding: 12px 16px; border-top: 1px solid #f0f0f0; }}
    td a {{ color: #6750A4; text-decoration: none; font-weight: 500; }}
    td a:hover {{ text-decoration: underline; }}
    td.size {{ color: #888; font-size: 0.85rem; width: 90px; }}
    .empty {{ text-align: center; padding: 48px; color: #aaa; background: white;
              border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}
  </style>
</head>
<body>
  <header>
    <h1>LanHopper</h1>
    <span>{device_name}</span>
  </header>
  <main>{table}</main>
</body>
</html>"""


def _fmt_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.0f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
