from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
import os


class AuthCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Список путей, которые не требуют токена
        exempt_paths = [
            "/docs",
            "/openapi.json",
            "/auth/login",
            "/auth/register",
            "/favicon.ico",
        ]
        path = request.url.path

        if (
                path.startswith("/docs") or
                path.startswith("/redoc") or
                path == "/openapi.json" or
                path.startswith("/auth/")  # Разрешаем логин и регистрацию
        ):
            return await call_next(request)
        # 2. Получаем токен именно из COOKIES (как требует ТЗ)
        token = request.cookies.get("access_token")

        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Токен отсутствует в cookies"}
            )

        try:
            # 3. Валидация токена
            jwt.decode(
                token,
                os.getenv("SECRET_KEY"),
                algorithms=[os.getenv("ALGORITHM", "HS256")]
            )
        except jwt.PyJWTError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Невалидный или просроченный токен"}
            )

        return await call_next(request)
