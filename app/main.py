from fastapi import FastAPI, Depends

from app import db
from app.models import Articles
from app.schemas import ArticleCreate, ArticleRead
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import async_session_maker, engine
from app.models import Base
app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Эта команда создаст все таблицы (articles и другие),
        # если их еще нет в базе данных.
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with async_session_maker() as session:
        yield session

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


