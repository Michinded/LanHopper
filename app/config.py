import json
import sys
from pathlib import Path


def _exe_dir() -> Path:
    """Root directory of the executable (dev or PyInstaller bundle)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


def _default_shared_dir() -> str:
    return str(_exe_dir() / "shared")


_DEFAULTS = {
    "device_name": "LanHopper",
    "port": 8080,
    "shared_folder": {
        "type": "local",
        "path": _default_shared_dir(),
    },
    "language": "en",
    "qr_token_minutes": 5,
    "session_minutes": 60,
    "max_upload_mb": 512,
}


def _data_dir() -> Path:
    """Resolve data/ relative to the executable (works for both dev and PyInstaller)."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent
    return base / "data"


def load() -> dict:
    path = _data_dir() / "user_config.json"
    if not path.exists():
        save(_DEFAULTS.copy())
        return _DEFAULTS.copy()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(config: dict) -> None:
    path = _data_dir() / "user_config.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
