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

app = FastAPI(title="Marketplace blog api")


@app.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает нового пользователя в базе данных, хэширует пароль и проверяет уникальность email.
    """
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


@app.post("/token", response_model=Token, summary="Получение токена для авторизации")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Проверяет учетные данные и выдает JWT токен для авторизации по эндпоинтам
    """
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


@app.post("/articles", response_model=ArticleRead, summary="Создать новую статью")
async def create_articles(
    article_data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """
    Создает новую публикацию и привязывает её к текущему пользователю.
    """
    new_article = Articles(
        title=article_data.title,
        content=article_data.content,
        is_published=article_data.is_published,
        owner_id=current_user.id,
    )
    db.add(new_article)
    await db.commit()
    await db.refresh(new_article)
    return new_article


@app.get(
    "/articles/my", response_model=list[ArticleRead], summary="Получение моих статей"
)
async def get_my_articles(
    db: AsyncSession = Depends(get_db), current_user: Users = Depends(get_current_user)
):
    """
    Возвращает список статей, которые написал пользователь
    """
    query = select(Articles).where(Articles.owner_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()



@app.get(
    "/articles",
    response_model=list[ArticleRead],
    summary="Получение всех доступных статей",
)
async def get_articles(
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0,
    search: str | None = None,
):
    """
    Возвращение всех статей
    """
    query = select(Articles)
    if search:
        query = query.where(Articles.title.icontains(search))

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()



@app.put(
    "/articles/{article_id}", response_model=ArticleRead, summary="Обновление статьи"
)
async def update_article(
    article_id: int,
    article_data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """
    Обновляет заголовок, либо контент статьи.Доступно только автору
    """
    result = await db.execute(select(Articles).where(Articles.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    if article.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Нет прав на редактирование этой статьи. Вы не автор",
        )
    article.title = article_data.title
    article.content = article_data.content
    article.is_published = article_data.is_published
    await db.commit()
    await db.refresh(article)
    return article



@app.delete("/articles/{article_id}", status_code=204, summary="Удалить статью")
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """
    Полностью удаляет статью из базы данных. Доступно только автору.
    """
    result = await db.execute(select(Articles).where(Articles.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Такой статьи нет")
    if article.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Нет прав на удаление этой статьи. Вы не автор"
        )
    await db.delete(article)
    await db.commit()
    return None
