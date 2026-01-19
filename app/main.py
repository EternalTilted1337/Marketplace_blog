from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router
from app.routers.articles import router as articles_router
from app.routers.comments import router as comments_router
from app.routers.categories import router as categories_router
from app.core.middleware import AuthCookieMiddleware
from app.db import engine
from app.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Marketplace Blog", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware('http')
async def extract_token_from_cookie(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        token = request.cookies.get("access_token")
        if token:
            request.scope["headers"].append((b"authorization", f"Bearer {token}".encode("ascii")))
    return await call_next(request) # Просто возвращаем результат

app.add_middleware(AuthCookieMiddleware)
app.include_router(auth_router)
app.include_router(articles_router)
app.include_router(comments_router)
app.include_router(categories_router)

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to Marketplace blog"}