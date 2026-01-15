
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import get_current_user
from app.models import Users


@pytest_asyncio.fixture(scope='function')
async def client():

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def override_get_current_user():
    return Users(id=1, email="test@test.com", is_active=True)

# Применяем подмену
app.dependency_overrides[get_current_user] = override_get_current_user