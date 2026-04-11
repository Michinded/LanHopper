import sys
from pathlib import Path


def normalize_path(raw: str, folder_type: str) -> str:
    """
    Normalize a path string for the current OS.

    - Local paths: resolved via pathlib (expanduser, normalize separators).
    - Network paths: kept as-is since format depends on OS and mount setup.
      Windows UNC: \\\\server\\share
      macOS/Linux: /Volumes/share or /mnt/share (already standard paths)
    """
    if folder_type == "network":
        return raw

    path = Path(raw).expanduser()
    return str(path)


def is_unc(path_str: str) -> bool:
    """Return True if the path looks like a Windows UNC path (\\\\server\\share)."""
    return path_str.startswith("\\\\") or path_str.startswith("//")


def platform_path_hint() -> str:
    """Return an OS-appropriate example for network paths."""
    if sys.platform == "win32":
        return r"\\server\share\folder"
    elif sys.platform == "darwin":
        return "/Volumes/MyShare/folder"
    else:
        return "/mnt/share/folder"
