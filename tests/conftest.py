import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import get_current_user, create_access_token  # Добавил импорт создания токена
from app.models import Users
from datetime import timedelta


@pytest_asyncio.fixture(scope='function')
async def mock_user():

    return Users(id=1, email="test@test.com", is_active=True)


@pytest_asyncio.fixture(scope='function')
async def client(mock_user):

    access_token = create_access_token(
        data={"sub": str(mock_user.email)},
        expires_delta=timedelta(minutes=15)
    )


    async def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.cookies.set("access_token", access_token)  # Теперь тут реальный JWT
        yield ac

    app.dependency_overrides.clear()