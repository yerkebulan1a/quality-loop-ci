import os
import pytest
import httpx

APP_URL = os.getenv("APP_URL", "http://web:8000")


@pytest.mark.asyncio
async def test_healthcheck():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{APP_URL}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_create_and_get_item():
    payload = {"id": 1, "name": "Laptop", "price": 999.99}

    async with httpx.AsyncClient() as client:
        # 1. Создание товара (201 Created)
        create_res = await client.post(f"{APP_URL}/items", json=payload)
        assert create_res.status_code == 201
        assert create_res.json() == payload

        # 2. Получение товара (200 OK)
        get_res = await client.get(f"{APP_URL}/items/1")
        assert get_res.status_code == 200
        assert get_res.json()["name"] == "Laptop"


@pytest.mark.asyncio
async def test_get_nonexistent_item():
    async with httpx.AsyncClient() as client:
        # 3. Запрос несуществующего ID (404 Not Found)
        response = await client.get(f"{APP_URL}/items/999")
        assert response.status_code == 404