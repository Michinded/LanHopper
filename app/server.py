import secrets
import socket
import string
import threading
import uvicorn
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI
from jose import jwt

from app.api import auth, files, upload, web
from app.middleware.auth import AuthMiddleware

_QR_TOKEN_MINUTES = 5

# In-memory session state — reset on every server start
session: dict = {
    "password": None,
    "jwt_secret": None,
    "port": None,
    "lan_ip": None,
    "qr_token": None,
    "used_qr_tokens": set(),
}

_server_thread: threading.Thread | None = None
_uvicorn_server: uvicorn.Server | None = None
_qr_stop_event: threading.Event | None = None


def get_lan_ip() -> str:
    """Return the machine's LAN IP (not loopback). Falls back to 127.0.0.1."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def generate_qr_token() -> str:
    """Generate a single-use QR token (5 min expiry) and print the access URL."""
    jti = secrets.token_hex(8)
    payload = {
        "sub": "lanhopper-qr",
        "jti": jti,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=_QR_TOKEN_MINUTES),
    }
    token = jwt.encode(payload, session["jwt_secret"], algorithm="HS256")
    session["qr_token"] = token

    url = f"http://{session['lan_ip']}:{session['port']}/?qr={token}"
    print(f"[LanHopper] QR URL (valid {_QR_TOKEN_MINUTES} min) →\n  {url}\n")
    return token


def _qr_rotation_loop(stop_event: threading.Event) -> None:
    """Regenerate the QR token every QR_TOKEN_MINUTES minutes until stopped."""
    while not stop_event.wait(timeout=_QR_TOKEN_MINUTES * 60):
        if session["jwt_secret"]:
            generate_qr_token()


def _build_app() -> FastAPI:
    app = FastAPI(title="LanHopper", docs_url=None, redoc_url=None)
    app.add_middleware(AuthMiddleware)
    app.include_router(web.router)
    app.include_router(auth.router, prefix="/auth")
    app.include_router(files.router, prefix="/files")
    app.include_router(upload.router, prefix="/upload")
    return app


def start(port: int) -> str:
    """Generate credentials, start the server and QR rotation, return session password."""
    global _server_thread, _uvicorn_server, _qr_stop_event

    _charset = string.ascii_uppercase + string.digits
    session["password"] = "".join(secrets.choice(_charset) for _ in range(6))
    session["jwt_secret"] = secrets.token_hex(32)
    session["port"] = port
    session["lan_ip"] = get_lan_ip()
    session["used_qr_tokens"] = set()

    config = uvicorn.Config(_build_app(), host="0.0.0.0", port=port, log_level="warning")
    _uvicorn_server = uvicorn.Server(config)

    _server_thread = threading.Thread(target=_uvicorn_server.run, daemon=True)
    _server_thread.start()

    print(f"\n[LanHopper] Server started → http://{session['lan_ip']}:{port}")
    print(f"[LanHopper] Password       → {session['password']}")

    # First QR token — printed immediately
    generate_qr_token()

    # Background thread rotates QR every 5 min
    _qr_stop_event = threading.Event()
    threading.Thread(target=_qr_rotation_loop, args=(_qr_stop_event,), daemon=True).start()

    return session["password"]


def stop() -> None:
    """Stop the server, QR rotation, and clear all session state."""
    global _uvicorn_server, _qr_stop_event

    if _qr_stop_event:
        _qr_stop_event.set()
        _qr_stop_event = None

    if _uvicorn_server:
        _uvicorn_server.should_exit = True
        _uvicorn_server = None

    session["password"] = None
    session["jwt_secret"] = None
    session["port"] = None
    session["lan_ip"] = None
    session["qr_token"] = None
    session["used_qr_tokens"] = set()


def is_running() -> bool:
    return _uvicorn_server is not None and not _uvicorn_server.should_exit


def get_url() -> str | None:
    if not is_running():
        return None
    return f"http://{session['lan_ip']}:{session['port']}"
