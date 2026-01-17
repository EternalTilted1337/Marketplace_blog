import os
from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context
from dotenv import load_dotenv


import sys
from os.path import abspath, dirname

sys.path.insert(0, dirname(dirname(abspath(__file__))))
from app.models import Base


load_dotenv()


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_online() -> None:
    """Онлайн режим (наш случай)"""

    database_url = os.getenv("ALEMBIC_DATABASE_URL") or os.getenv("DATABASE_URL")

    if "db:5432" in database_url:
        database_url = database_url.replace("db:5432", "localhost:5435")


    if database_url and "postgresql+asyncpg" in database_url:
        database_url = database_url.replace("postgresql+asyncpg", "postgresql+psycopg")
    elif database_url and database_url.startswith("postgresql://"):

        database_url = database_url.replace("postgresql://", "postgresql+psycopg://")

    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()