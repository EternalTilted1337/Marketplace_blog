from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import (
    get_current_user,
)
from app.db import get_db
from app.models import Articles, Users
from app.schemas import ArticleCreate, ArticleRead
from sqlalchemy.orm import selectinload
router = APIRouter(
    prefix='/articles',
    tags= ["Articles"]
)
@router.post("/", response_model=ArticleRead, summary="Создать новую статью")
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


@router.get(
    "/my", response_model=list[ArticleRead], summary="Получение моих статей"
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


@router.get(
    "/",
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
        query = query.where(Articles.title.ilike(f"%{search}%"))
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/{article_id}",
    response_model=ArticleRead,
    summary="Получение статьи по id",
)
async def get_article_by_id(article_id: int, db: AsyncSession = Depends(get_db)):
    """
    Возвращает статью по её id
    """
    query = select(Articles).where(Articles.id == article_id).options(selectinload(Articles.owner))
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return article


@router.put(
    "/{article_id}", response_model=ArticleRead, summary="Обновление статьи"
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


@router.delete("/{article_id}", status_code=204, summary="Удалить статью")
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
