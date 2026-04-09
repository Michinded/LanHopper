from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

import app.server as server

# Paths that never require authentication
_PUBLIC_PATHS = {"/auth/login", "/", "/web/login", "/logout"}


def _extract_token(request: Request) -> str | None:
    """Try Bearer header first, then fall back to cookie (browser sessions)."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.removeprefix("Bearer ")
    return request.cookies.get("access_token")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        token = _extract_token(request)

        if not token:
            # API clients get JSON; browser requests get redirected to login
            if _wants_html(request):
                return RedirectResponse(url="/")
            return JSONResponse(status_code=401, content={"detail": "Missing token"})

        try:
            jwt.decode(token, server.session["jwt_secret"], algorithms=["HS256"])
        except JWTError:
            if _wants_html(request):
                return RedirectResponse(url="/")
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

        return await call_next(request)


def _wants_html(request: Request) -> bool:
    return "text/html" in request.headers.get("accept", "")
