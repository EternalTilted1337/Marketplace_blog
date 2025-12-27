import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context
from dotenv import load_dotenv

# 1. Импортируем твой Base и модели
import sys
from os.path import abspath, dirname

sys.path.insert(0, dirname(dirname(abspath(__file__))))
from app.models import Base

# 2. Загружаем переменные окружения
load_dotenv()

# 3. Настройка логирования
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 4. Указываем метаданные моделей
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Оффлайн режим"""
    url = os.getenv("ALEMBIC_DATABASE_URL")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Онлайн режим (наш случай)"""

    # Берем URL напрямую из .env
    database_url = os.getenv("ALEMBIC_DATABASE_URL")

    # Создаем движок вручную, игнорируя пустую строку в alembic.ini
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


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()