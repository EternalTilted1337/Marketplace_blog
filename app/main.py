from fastapi import FastAPI, Request
from app.core.middleware import AuthCookieMiddleware
from app.routers.auth import router as auth_router
from app.routers.articles import router as articles_router
from app.routers.comments import router as comments_router
from app.routers.categories import router as categories_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Marketplace Blog")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],# мб лучше allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware('http')
async def extrace_token_from_cookie(request:Request, call_next):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        token = request.cookies.get("access_token")
        if token:
            request.scope["headers"].append((b"authorization", f"Bearer {token}".encode("ascii")))
    response = await call_next(request)
    return response

app.add_middleware(AuthCookieMiddleware)
app.include_router(auth_router)
app.include_router(articles_router)
app.include_router(comments_router)
app.include_router(categories_router)


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to Marketplace blog"}

