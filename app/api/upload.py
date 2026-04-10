import secrets
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app import config

router = APIRouter()

_CHUNK = 1024 * 1024  # 1 MB per read — keeps RAM usage flat regardless of file size


def _shared_path() -> Path:
    cfg = config.load()
    folder = cfg.get("shared_folder", {})
    if isinstance(folder, str):
        return Path(folder).expanduser()
    return Path(folder.get("path", "")).expanduser()


def _max_bytes() -> int:
    """Return the byte limit, or 0 if unlimited."""
    mb = int(config.load().get("max_upload_mb", 512))
    return mb * 1024 * 1024 if mb > 0 else 0


def _unique_path(folder: Path, filename: str) -> Path:
    """Return a path that does not exist in folder.

    If filename is free, return it as-is.
    Otherwise append _YYYYMMDD_HHMMSS_<4 hex chars> before the extension so
    every upload is unique and the original name is still recognisable.
    Example: important.pdf → important_20260409_143022_a3f2.pdf
    """
    dest = folder / filename
    if not dest.exists():
        return dest

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    tag = secrets.token_hex(2)          # 4 hex chars — enough to avoid same-second collisions
    return folder / f"{stem}_{ts}_{tag}{suffix}"


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """Stream an uploaded file to the shared folder, enforcing the configured size limit."""
    max_bytes = _max_bytes()

    shared = _shared_path()
    shared.mkdir(parents=True, exist_ok=True)
    dest = _unique_path(shared, file.filename)

    written = 0
    too_large = False

    try:
        with open(dest, "wb") as out:
            while chunk := await file.read(_CHUNK):
                written += len(chunk)
                if max_bytes > 0 and written > max_bytes:
                    too_large = True
                    break
                out.write(chunk)
    finally:
        await file.close()

    if too_large:
        dest.unlink(missing_ok=True)
        max_mb = max_bytes // (1024 * 1024)
        raise HTTPException(status_code=413, detail=f"File exceeds the {max_mb} MB limit")

    return {"name": dest.name, "size": written}
