from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
import os


class AuthCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Список путей, которые не требуют токена
        exempt_paths = ["/docs", "/openapi.json", "/auth/login", "/auth/register"]

        if request.url.path in exempt_paths or request.method == "GET":
            return await call_next(request)

        token = request.cookies.get("access_token")
        if not token:
            return JSONResponse(status_code=401, content={"detail": "Missing token"})

        try:
            # Просто проверка на валидность (секрет из env)
            jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        except jwt.PyJWTError:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        return await call_next(request)
