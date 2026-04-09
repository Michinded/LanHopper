import json
import sys
from pathlib import Path

_strings: dict = {}


def _lang_dir() -> Path:
    """Resolve assets/lang/ — works in dev and as a PyInstaller bundle."""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent.parent
    return base / "assets" / "lang"


def load(language: str) -> None:
    """Load the language file for the given language code (e.g. 'en', 'es')."""
    global _strings
    path = _lang_dir() / f"{language}.json"
    if not path.exists():
        path = _lang_dir() / "en.json"
    with open(path, "r", encoding="utf-8") as f:
        _strings = json.load(f)


def t(key: str) -> str:
    """Return the translated string for key, or the key itself as fallback."""
    return _strings.get(key, key)
