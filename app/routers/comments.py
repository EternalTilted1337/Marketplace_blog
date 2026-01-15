from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db import get_db
from app.models import Users, Articles, Comments
from app.schemas import CommentRead, CommentCreate

router = APIRouter(prefix="/articles/{article_id}/comments", tags=["Comments"])


@router.post(
    "/",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать комментарий",
)
async def create_comment(
    article_id: int,
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    article = await db.get(Articles, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    new_comment = Comments(
        content=comment_data.content, article_id=article_id, author_id=current_user.id
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


@router.get(
    "/", response_model=list[CommentRead], summary="Получение всех комментариев"
)
async def get_comments(
    article_id: int,
    db: AsyncSession = Depends(get_db),
):
    query = select(Comments).where(Comments.article_id == article_id)
    result = await db.execute(query)
    return result.scalars().all()
