from fastapi import Depends, HTTPException, APIRouter, Form, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.s3 import upload_image_to_s3
from app.core.security import (
    get_current_user,
)
from app.db import get_db
from app.models import Articles, Users, Categories, DeleteArticles
from app.schemas import ArticleUpdate, ArticleRead
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
        print(f"S3 Error: {e}")
        raise HTTPException(status_code=500, detail="Ошибка загрузки изображения в S3")
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
    final_query = (
        select(Articles)
        .where(Articles.id == new_article.id)
        .options(selectinload(Articles.category), selectinload(Articles.owner))
    )
    final_result = await db.execute(final_query)
    article_with_relations = final_result.scalar_one()

    process_new_article_notification.delay(article_with_relations.id, article_with_relations.title)

    return article_with_relations


@router.get("/my", response_model=list[ArticleRead], summary="Получение моих статей")
async def get_my_articles(
    db: AsyncSession = Depends(get_db), current_user: Users = Depends(get_current_user)
):
    """
    Возвращает список статей, которые написал пользователь
    """
    query = (
        select(Articles)
        .where(Articles.owner_id == current_user.id)
        .options(selectinload(Articles.category), selectinload(Articles.owner))  # Добавили загрузку
    )
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
        selectinload(Articles.category), selectinload(Articles.owner)
    )
    if category_id:
        query = query.where(Articles.category_id == category_id)
    if search:
        search_query = func.plainto_tsquery("russian", search)
        query = query.where(Articles.ts_vector.op("@@")(search_query))
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
        .options(
            selectinload(Articles.owner),
            selectinload(Articles.category)  # ДОБАВЬ ЭТУ СТРОКУ
        )
    )
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return article


@router.put("/{article_id}", response_model=ArticleRead, summary="Обновление статьи")
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """
    Обновляет статью. Можно изменять любые поля. Доступно только автору.
    """
    result = await db.execute(select(Articles).where(Articles.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    if article.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Нет прав на редактирование",)
    if article_data.category_id is not None:
        cat_check = await db.execute(
            select(Categories).where(Categories.id == article_data.category_id)
        )
        if not cat_check.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Категория не найдена")

    update_data = article_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(article, key, value)

    await db.commit()
    final_query = (
        select(Articles)
        .where(Articles.id == article_id)
        .options(selectinload(Articles.category), selectinload(Articles.owner))
    )
    final_result = await db.execute(final_query)
    updated_article = final_result.scalar_one()

    return updated_article

@router.delete("/{article_id}", status_code=204, summary="Удалить статью")
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """
    Полностью удаляет статью из базы данных. Доступно только автору.
    Выполняет "фейковое" удаление статьи, перемещая её в архив.
     Доступно только автору.
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
        title=article.title,
        content=article.content,
        owner_id=article.owner_id,
        original_id=article.id,
        image_url=article.image_url
    )
    db.add(delete_log)
    await db.delete(article)
    await db.commit()
    return None
