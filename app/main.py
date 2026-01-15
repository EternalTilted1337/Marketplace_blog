from fastapi import FastAPI
from app.routers import auth, articles, comments

app = FastAPI(title="Marketplace Blog")

app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(comments.router)


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to Marketplace blog"}
