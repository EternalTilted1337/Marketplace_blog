from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from app.models import Articles, Users
from app.schemas import ArticleCreate, ArticleRead, UserRead, UserCreate, Token
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

app = FastAPI()


@app.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(Users).where(Users.email == user_data.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Такой пользователь уже существует")
    new_user = Users(
        email=user_data.email, hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@app.post("/articles", response_model=ArticleRead)
async def create_articles(
    article_data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    new_article = Articles(
        title=article_data.title,
        content=article_data.content,
        is_published=article_data.is_published,
    )
    db.add(new_article)
    await db.commit()
    await db.refresh(new_article)
    return new_article


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Users).where(Users.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
