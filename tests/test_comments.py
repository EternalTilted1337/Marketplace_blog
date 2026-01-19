import pytest
import uuid
import io
from app.main import app
from app.core.security import get_current_user
from app.models import Users


@pytest.mark.asyncio
async def test_get_comments_list(client, mocker):
    cat_res = await client.post('/categories/', json={'name': f"Cat-{uuid.uuid4().hex[:4]}"})
    category_id = cat_res.json()['id']

    async def mock_user():
        return Users(id=1, email="tester@test.com", is_active=True)

    app.dependency_overrides[get_current_user] = mock_user

    mocker.patch("app.routers.articles.upload_image_to_s3", return_value="https://fake.jpg")
    mocker.patch("app.routers.articles.process_new_article_notification.delay")

    art_res = await client.post(
        '/articles/',
        data={"title": "List Test", "content": "Content", "category_id": category_id},
        files={"image": ("img.jpg", io.BytesIO(b"data"), "image/jpeg")}
    )
    article_id = art_res.json()['id']

    comment_texts = ["АДЫН", "ТВА"]
    for text in comment_texts:
        await client.post(f"/articles/{article_id}/comments/", json={"content": text})


    response = await client.get(f"/articles/{article_id}/comments/")

    app.dependency_overrides.clear()


    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2


    received_texts = [comment["content"] for comment in data]
    for original_text in comment_texts:
        assert original_text in received_texts