import pytest
import io
from unittest.mock import patch
from app.main import app
from app.core.security import get_current_user
from app.models import Users
import uuid

@pytest.mark.asyncio
async def test_create_article_with_mocker(client,mocker):
    unique_name = f"Category-{uuid.uuid4().hex[:6]}"

    cat_res = await client.post('/categories/', json={'name': unique_name})
    assert cat_res.status_code == 201, f"Ошибка создания категории: {cat_res.text}"
    category_id = cat_res.json()['id']

    async def mock_user():
        return Users(id=1, email="test@test.com", is_active=True)
    app.dependency_overrides[get_current_user] = mock_user

    mock_upload = mocker.patch("app.routers.articles.upload_image_to_s3",
                               return_value="https://fake-s3.com/image.jpg")

    mock_celery = mocker.patch("app.routers.articles.process_new_article_notification.delay")

    file = io.BytesIO(b"fake image data")
    payload = {
        "title": "New Article",
        "content": "Article Content",
        "category_id": category_id,
        "is_published": "true"
    }

    response = await client.post(
        '/articles/',
        data=payload,
        files={"image": ("test.jpg", file, "image/jpeg")}
    )

    app.dependency_overrides.clear()


    assert response.status_code == 200
    assert response.json()["image_url"] == "https://fake-s3.com/image.jpg"
    mock_celery.assert_called_once()