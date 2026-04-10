"""
File serving API — security model
==================================

All file downloads are protected against **path traversal** (CWE-22) via
`_safe_path()`, which applies two checks on every request:

  1. ``(shared / user_input).resolve()``  — collapses ``..``, follows symlinks,
     and produces a canonical absolute path.
  2. ``resolved.relative_to(shared.resolve())``  — raises ValueError (→ HTTP 400)
     if the resolved path is not a descendant of the shared root.

This blocks all known traversal vectors:
  - ``../secret.txt``            plain relative escape
  - ``..%2Fsecret.txt``          URL-encoded slash (%2F) — also rejected by
                                  uvicorn at the protocol level before reaching
                                  the application, giving a second defence layer
  - ``subdir/../../secret.txt``  multi-level escape
  - Symlinks pointing outside    ``resolve()`` follows them, caught by check 2

The shared root is the folder configured in ``data/user_config.json`` and
resolved fresh on every request so config changes take effect immediately.

------------------------------------------------------------------------
Subfolder support — implementation notes (future feature)
------------------------------------------------------------------------
When adding the ability to browse and download from subdirectories, the
following changes are required:

Route signature
  Change ``{filename}`` to ``{path:path}`` so FastAPI captures slashes:

    @router.get("/download/{path:path}")
    def download_file(path: str): ...

  The same applies to a new listing route:

    @router.get("/browse/{path:path}")
    def browse_dir(path: str): ...

_safe_path reuse
  ``_safe_path(shared, path)`` works unchanged for any depth — it already
  resolves the full path and checks containment regardless of how many
  segments ``path`` has.

Directory listing endpoint
  Return a dict with ``{"dirs": [...], "files": [...]}`` so the frontend
  can render breadcrumbs and navigate up/down.  The listing must also
  call ``_safe_path`` on the directory path itself before iterating it.

Frontend
  - Replace the flat ``FILES`` JS array with a path-aware model.
  - Add a breadcrumb bar (e.g. Shared / docs / project).
  - Clicking a folder navigates to ``/browse/<relative_path>``.
  - Clicking a file triggers ``/files/download/<relative_path>``.

Upload
  ``upload.py`` uses ``_shared_path()`` directly.  For subfolder uploads,
  pass the target directory as a form field and validate it with
  ``_safe_path`` before writing.

Security note on directory listings
  Never expose absolute paths to the client — only paths relative to the
  shared root.  The ``_safe_path`` guard must be applied to every user-
  supplied path before any filesystem operation.
"""
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app import config

router = APIRouter()


def _shared_path() -> Path:
    cfg = config.load()
    folder = cfg.get("shared_folder", {})
    if isinstance(folder, str):
        return Path(folder).expanduser()
    return Path(folder.get("path", "")).expanduser()


def _safe_path(shared: Path, user_input: str) -> Path:
    """Resolve the requested path and verify it stays inside the shared folder.

    Blocks all path traversal attempts:
      - ../ sequences
      - URL-encoded slashes (%2F decoded by the framework)
      - Symlinks pointing outside the shared root
    Raises HTTP 400 if the resolved path escapes the shared root.
    """
    resolved = (shared / user_input).resolve()
    try:
        resolved.relative_to(shared.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid path")
    return resolved


@router.get("/")
def list_files():
    path = _shared_path()
    if not path.exists():
        return {"files": []}
    files_list = [
        {"name": f.name, "size": f.stat().st_size}
        for f in sorted(path.iterdir())
        if f.is_file()
    ]
    return {"files": files_list}


@router.get("/download/{filename}")
def download_file(filename: str):
    shared = _shared_path()
    path = _safe_path(shared, filename)
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=path.name)
