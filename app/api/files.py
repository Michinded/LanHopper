from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_files():
    # TODO: return list of files in shared folder
    return {"files": []}


@router.get("/download/{filename}")
def download_file(filename: str):
    # TODO: stream file from shared folder
    return {"filename": filename}
