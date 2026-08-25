import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aiokafka import AIOKafkaProducer


# Временная база данных в памяти
items_db = {}

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC_NAME = "orders_topic"

producer: AIOKafkaProducer = None

class Item(BaseModel):
    id: int
    name: str
    price: float

class OrderSchema(BaseModel):
    order_id: int
    item: str
    price: float

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Старт Producer при запуске приложения
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    await producer.start()
    yield
    # Остановка Producer при завершении работы
    await producer.stop()


app = FastAPI(title="Quality Loop API",lifespan=lifespan)
# Healthcheck — эндпоинт проверки здоровья сервиса (нужен для Docker и CI)
# @app.get("/healthz", tags=["health"])
# async def healthz():
#     # Optionally check DB / cache readiness here and return 503 if not ready
#     return {"status": "ok"}
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

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/orders")
async def create_order(order: OrderSchema):
    event_payload = {
        "event": "order_created",
        "order_id": order.order_id,
        "item": order.item,
        "price": order.price,
    }
    try:
        # Отправляем сообщение в Kafka
        await producer.send_and_wait(TOPIC_NAME, value=event_payload)
        return {"status": "success", "message": "Order event sent to Kafka", "data": order}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish to Kafka: {str(e)}")