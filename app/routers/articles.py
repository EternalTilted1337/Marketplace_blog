from fastapi import Depends, HTTPException, APIRouter, status, Form, UploadFile, File
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.s3 import upload_image_to_s3
from app.core.security import (
    get_current_user,
)
from app.db import get_db
from app.models import Articles, Users, Categories, DeleteArticles
from app.schemas import ArticleCreate, ArticleRead
from sqlalchemy.orm import selectinload
from app.tasks import process_new_article_notification

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.post("/", response_model=ArticleRead, summary="Создать новую статью")
async def create_articles(
    title: str = Form(...),
    content: str = Form(...),
    category_id: int = Form(...),
    is_published: bool = Form(False),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """
    Создает новую публикацию и привязывает её к текущему пользователю.
    """
    category_stmt = select(Categories).where(Categories.id == category_id)
    result = await db.execute(category_stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Категория не найдена")
    try:
        image_url = await upload_image_to_s3(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки изображения в S3")
    new_article = Articles(
        title=title,
        content=content,
        category_id=category_id,
        image_url=image_url,
        owner_id=current_user.id,
        is_published=is_published,
    )
    db.add(new_article)
    await db.commit()
    await db.refresh(new_article)

    process_new_article_notification.delay(new_article.id, new_article.title)

    return new_article


@router.get("/my", response_model=list[ArticleRead], summary="Получение моих статей")
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
    page_number: int = 1,
    page_size: int = 10,
    search: str | None = None,
    category_id: int | None = None,
):
    """
    Возвращает список статей с полнотекстовым поиском Postgres и пагинацией по страницам.
    """
    if page_size > 100:
        page_size = 100
    offset = (page_number - 1) * page_size
    query = select(Articles).options(
        selectinload(Articles.category),
        selectinload(Articles.owner)
    )
    if category_id:
        query = query.where(Articles.category_id == category_id)
    if search:
        search_vector = func.to_tsvector('russian', Articles.title + ' ' + Articles.content)
        search_query = func.plainto_tsquery('russian', search)
        query = query.where(search_vector.op('@@')(search_query))
    query = query.order_by(Articles.created_at.desc()).limit(page_size).offset(offset)

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
    query = (
        select(Articles)
        .where(Articles.id == article_id)
        .options(selectinload(Articles.owner))
    )
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return article


@router.put("/{article_id}", response_model=ArticleRead, summary="Обновление статьи")
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
    delete_log = DeleteArticles(
        title=article.title, content=article.content, owner_id=article.owner_id
    )
    db.add(delete_log)
    await db.delete(article)
    await db.commit()
    return None
