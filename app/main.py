from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Quality Loop API")

# Временная база данных в памяти
items_db = {}

class Item(BaseModel):
    id: int
    name: str
    price: float

# Healthcheck — эндпоинт проверки здоровья сервиса (нужен для Docker и CI)
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Получение товара по ID
@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

# Создание товара
@app.post("/items", response_model=Item, status_code=201)
def create_item(item: Item):
    if item.id in items_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    items_db[item.id] = item
    return item