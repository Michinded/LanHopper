import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import jwt

import app.server as server
from app import config

router = APIRouter()

# ------------------------------------------------------------------- templates

_templates: Jinja2Templates | None = None


def _get_templates() -> Jinja2Templates:
    global _templates
    if _templates is None:
        if getattr(sys, "frozen", False):
            tpl_dir = Path(sys._MEIPASS) / "app" / "web" / "templates"
        else:
            tpl_dir = Path(__file__).parent.parent / "web" / "templates"
        _templates = Jinja2Templates(directory=str(tpl_dir))
    return _templates


# ------------------------------------------------------------------- helpers

def _session_minutes() -> int:
    return int(config.load().get("session_minutes", 60))


def _make_token() -> str:
    payload = {
        "sub": "lanhopper-client",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=_session_minutes()),
    }
    return jwt.encode(payload, server.session["jwt_secret"], algorithm="HS256")


def _shared_path() -> Path:
    cfg = config.load()
    folder = cfg.get("shared_folder", {})
    if isinstance(folder, str):
        return Path(folder).expanduser()
    return Path(folder.get("path", "")).expanduser()


def _fmt_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.0f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


# ----------------------------------------------------------------- routes

@router.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    """Public login page. Handles QR token redemption and existing session check."""

    # 1. QR token redemption
    qr_token = request.query_params.get("qr")
    if qr_token:
        try:
            claims = jwt.decode(qr_token, server.session["jwt_secret"], algorithms=["HS256"])
            jti = claims.get("jti")
            if jti and jti not in server.session["used_qr_tokens"]:
                server.session["used_qr_tokens"].add(jti)
                response = RedirectResponse(url="/browse", status_code=303)
                response.set_cookie(
                    key="access_token",
                    value=_make_token(),
                    httponly=True,
                    max_age=_session_minutes() * 60,
                    samesite="lax",
                    path="/",
                )
                return response
        except Exception:
            pass
        return _get_templates().TemplateResponse(
            request, "login.html", {"error": False, "qr_expired": True}
        )

    # 2. Already have a valid session cookie → skip login
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        try:
            jwt.decode(cookie_token, server.session["jwt_secret"], algorithms=["HS256"])
            return RedirectResponse(url="/browse")
        except Exception:
            pass

    return _get_templates().TemplateResponse(
        request, "login.html", {"error": False, "qr_expired": False}
    )


@router.post("/web/login")
async def web_login(request: Request, password: str = Form(default="")):
    """Form-based login. Sets JWT cookie and redirects to /browse."""
    if not password or password != server.session.get("password"):
        return _get_templates().TemplateResponse(
            request, "login.html", {"error": True, "qr_expired": False},
            status_code=401,
        )

    token = _make_token()
    response = RedirectResponse(url="/browse", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=_session_minutes() * 60,
        samesite="strict",
    )
    return response


@router.get("/logout")
def logout():
    """Clear the session cookie and redirect to login."""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token", path="/")
    return response


@router.get("/browse", response_class=HTMLResponse)
def browse_page(request: Request):
    """File listing page — protected by AuthMiddleware via cookie."""
    path = _shared_path()
    files = []
    if path.exists():
        files = [
            {"name": f.name, "size": _fmt_size(f.stat().st_size)}
            for f in sorted(path.iterdir(), key=lambda f: f.name.lower())
            if f.is_file()
        ]
    cfg = config.load()
    device_name = cfg.get("device_name", "LanHopper")
    max_upload_mb = int(cfg.get("max_upload_mb", 512))
    return _get_templates().TemplateResponse(
        request, "browse.html",
        {"files": files, "device_name": device_name, "max_upload_mb": max_upload_mb},
    )
