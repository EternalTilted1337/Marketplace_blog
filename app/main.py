from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import select
from app.models import Articles, Users
from app.schemas import ArticleCreate, ArticleRead, UserRead, UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.auth import hash_password
app = FastAPI()


@app.post('/register', response_model = UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
        user_data : UserCreate,
        db : AsyncSession = Depends(get_db)
):
    query = select(Users).where(Users.email == user_data.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code = 400, detail = "Такой пользователь уже существует")
    new_user = Users(
        email = user_data.email,
        hashed_password = hash_password(user_data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
@app.post("/articles", response_model=ArticleRead)
async def create_articles(
        article_data : ArticleCreate,
        db : AsyncSession = Depends(get_db)
):
    new_article = Articles(
        title = article_data.title,
        content = article_data.content,
        is_published = article_data.is_published,
    )
    db.add(new_article)
    await db.commit()
    await db.refresh(new_article)
    return new_article


