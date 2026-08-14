def test_healthcheck(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_item(client):
    payload = {"id": 1, "name": "Laptop", "price": 999.99}

    # 1. Создание товара (ожидаем 201 Created)
    create_res = client.post("/items", json=payload)
    assert create_res.status_code == 201
    assert create_res.json() == payload

    # 2. Получение товара (ожидаем 200 OK)
    get_res = client.get("/items/1")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Laptop"


def test_get_nonexistent_item(client):
    # Запрос несуществующего ID (ожидаем 404 Not Found)
    response = client.get("/items/999")
    assert response.status_code == 404