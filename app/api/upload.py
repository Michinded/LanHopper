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
    return int(config.load().get("max_upload_mb", 512)) * 1024 * 1024


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """Stream an uploaded file to the shared folder, enforcing the configured size limit."""
    max_bytes = _max_bytes()

    shared = _shared_path()
    shared.mkdir(parents=True, exist_ok=True)
    dest = shared / file.filename

    written = 0
    too_large = False

    try:
        with open(dest, "wb") as out:
            while chunk := await file.read(_CHUNK):
                written += len(chunk)
                if written > max_bytes:
                    too_large = True
                    break
                out.write(chunk)
    finally:
        await file.close()

    if too_large:
        dest.unlink(missing_ok=True)
        max_mb = max_bytes // (1024 * 1024)
        raise HTTPException(status_code=413, detail=f"File exceeds the {max_mb} MB limit")

    return {"name": file.filename, "size": written}
