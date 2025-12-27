from sqlalchemy.ext.asyncio import create_async_engine, async_session, AsyncSession, async_sessionmaker
from . models import Base

DATABASE_URL = 'postgresql+asyncpg://postgres:postgres@db:5432/postgres'

engine = create_async_engine(DATABASE_URL)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

async def init_bd():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        

