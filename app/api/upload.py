from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def upload_file():
    # TODO: receive and save file to shared folder
    return {"status": "ok"}
