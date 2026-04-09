from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

import app.server as server
from app import config

router = APIRouter()


def _shared_path() -> Path:
    cfg = config.load()
    folder = cfg.get("shared_folder", {})
    if isinstance(folder, str):
        return Path(folder).expanduser()
    return Path(folder.get("path", "")).expanduser()


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
    path = _shared_path() / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=filename)
