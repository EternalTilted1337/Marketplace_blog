import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport # Добавили импорт транспорта
from app.main import app

@pytest_asyncio.fixture(scope="function")
async def client():
    # Теперь передаем приложение через транспорт
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac