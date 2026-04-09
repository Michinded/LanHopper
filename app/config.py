import json
import os
import sys
from pathlib import Path

_DEFAULTS = {
    "device_name": "LanHopper",
    "port": 8080,
    "shared_folder": str(Path.home() / "LanHopper" / "shared"),
    "language": "en",
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
