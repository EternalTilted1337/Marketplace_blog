import pytest

# Эта метка говорит pytest, что все функции в файле асинхронные
pytestmark = pytest.mark.asyncio

async def test_root_endpoint(client):
    """Простейший тест для проверки, что API вообще дышит"""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Marketplace blog"}

async def test_create_article_unauthorized(client):
    """Проверяем, что Middleware защищает создание статьи без токена"""
    response = await client.post("/articles/", data={"title": "Test"})
    # Если Middleware работает, он вернет 401
    assert response.status_code == 401