from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status
from jose import jwt
from pydantic import BaseModel

import app.server as server

router = APIRouter()

_TOKEN_EXPIRE_MINUTES = 60


class LoginRequest(BaseModel):
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    if body.password != server.session["password"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    payload = {
        "sub": "lanhopper-client",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=_TOKEN_EXPIRE_MINUTES),
    }
    token = jwt.encode(payload, server.session["jwt_secret"], algorithm="HS256")
    return TokenResponse(access_token=token)
