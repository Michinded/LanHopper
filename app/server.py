import random
import secrets
import socket
import threading
import uvicorn
from fastapi import FastAPI

from app.api import auth, files, upload
from app.middleware.auth import AuthMiddleware

# In-memory session state — reset on every server start
session: dict = {
    "password": None,
    "jwt_secret": None,
    "port": None,
    "lan_ip": None,
}

_server_thread: threading.Thread | None = None
_uvicorn_server: uvicorn.Server | None = None


def get_lan_ip() -> str:
    """Return the machine's LAN IP (not loopback). Falls back to 127.0.0.1."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def _build_app() -> FastAPI:
    app = FastAPI(title="LanHopper", docs_url=None, redoc_url=None)
    app.add_middleware(AuthMiddleware)
    app.include_router(auth.router, prefix="/auth")
    app.include_router(files.router, prefix="/files")
    app.include_router(upload.router, prefix="/upload")
    return app


def start(port: int) -> str:
    """Generate credentials, start the server, and return the session password."""
    global _server_thread, _uvicorn_server

    session["password"] = str(random.randint(0, 999999)).zfill(6)
    session["jwt_secret"] = secrets.token_hex(32)
    session["port"] = port
    session["lan_ip"] = get_lan_ip()

    config = uvicorn.Config(_build_app(), host="0.0.0.0", port=port, log_level="warning")
    _uvicorn_server = uvicorn.Server(config)

    _server_thread = threading.Thread(target=_uvicorn_server.run, daemon=True)
    _server_thread.start()

    return session["password"]


def stop() -> None:
    """Stop the server and clear session credentials."""
    global _uvicorn_server
    if _uvicorn_server:
        _uvicorn_server.should_exit = True
        _uvicorn_server = None
    session["password"] = None
    session["jwt_secret"] = None
    session["port"] = None
    session["lan_ip"] = None


def is_running() -> bool:
    return _uvicorn_server is not None and not _uvicorn_server.should_exit


def get_url() -> str | None:
    if not is_running():
        return None
    return f"http://{session['lan_ip']}:{session['port']}"
