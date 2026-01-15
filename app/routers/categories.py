from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import Categories
from app.schemas import CategoryRead, CategoryCreate

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Получить список всех категорий",
)
async def create_category(
    category_data: CategoryCreate, db: AsyncSession = Depends(get_db)
):
    # 1. Проверяем, существует ли уже такая категория
    stmt = select(Categories).where(Categories.name == category_data.name)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категория с таким именем уже существует",
        )

    new_category = Categories(name=category_data.name)
    db.add(new_category)

    await db.commit()
    await db.refresh(new_category)
    return new_category


@router.get(
    "/",
    response_model=List[CategoryRead],
    status_code=status.HTTP_200_OK,
    summary="Создать новую категорию",
)
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Categories))
    return result.scalars().all()
