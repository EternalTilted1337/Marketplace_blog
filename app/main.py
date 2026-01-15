from fastapi import FastAPI, Request
from app.routers import auth, articles, comments, categories

app = FastAPI(title="Marketplace Blog")

@app.middleware("http")
async def extract_token_from_cookie(request: Request, call_next):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        token = request.cookies.get('access_token')
        if token:
            request.scope['headers'].append(
                (b'authorization', token.encode('ascii')))
    response = await call_next(request)
    return response

app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(comments.router)
app.include_router(categories.router)




@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to Marketplace blog"}

