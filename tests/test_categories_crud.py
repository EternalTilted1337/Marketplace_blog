import pytest
import uuid

@pytest.mark.asyncio
async def test_category_crud_cycle(client):
    # 1. Создание (Create)
    unique_name = f"CRUD-Cat-{uuid.uuid4().hex[:4]}"
    create_res = await client.post('/categories/', json={"name": unique_name})
    assert create_res.status_code == 201
    category_id = create_res.json()['id']

    # 2. Чтение списка (Read All)
    list_res = await client.get('/categories/') # Добавили .get
    assert list_res.status_code == 200
    assert any(c["id"] == category_id for c in list_res.json())

    # 3. Чтение одной (Read One)
    detail_res = await client.get(f'/categories/{category_id}')
    assert detail_res.status_code == 200
    assert detail_res.json()['name'] == unique_name

    # 4. Обновление (Update)
    new_name = f"Updated-{uuid.uuid4().hex[:4]}"
    update_res = await client.patch(f'/categories/{category_id}', json={"name": new_name})
    # Если у тебя роутер patch готов, будет 200
    assert update_res.status_code == 200
    assert update_res.json()['name'] == new_name

    #5. Удаление (Delete)
    delete_res = await client.delete(f"/categories/{category_id}")
    assert delete_res.status_code in [200, 204]

    # 6. Проверка, что реально удалено
    check_deleted = await client.get(f"/categories/{category_id}")
    assert check_deleted.status_code == 404