import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import engine, Base, get_db
from app.models import OrderModel, ItemModel
from app.schemas import (
    OrderCreateSchema,
    OrderResponseSchema,
    StatusUpdateSchema,
    ItemSchema
)
from aiokafka import AIOKafkaProducer

TOPIC_NAME = "orders_topic"
producer: AIOKafkaProducer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем все таблицы (orders и items) в PostgreSQL при старте
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Старт Kafka Producer
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    await producer.start()
    yield
    await producer.stop()


app = FastAPI(lifespan=lifespan)


# --- Healthcheck ---
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# --- Items API ---
@app.post("/items", response_model=ItemSchema, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemSchema, db: AsyncSession = Depends(get_db)):
    db_item = ItemModel(id=item.id, name=item.name, price=item.price)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


@app.get("/items/{item_id}", response_model=ItemSchema)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ItemModel).where(ItemModel.id == item_id))
    db_item = result.scalar_one_or_none()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


# --- Orders API (Kafka + Async DB) ---
@app.post("/orders", response_model=OrderResponseSchema)
async def create_order(order: OrderCreateSchema, db: AsyncSession = Depends(get_db)):
    db_order = OrderModel(order_id=order.order_id, item=order.item, price=order.price, status="pending")
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    event_payload = {
        "event": "order_created",
        "order_id": order.order_id,
        "item": order.item,
        "price": order.price,
    }
    await producer.send_and_wait(TOPIC_NAME, value=event_payload)
    return db_order


@app.get("/orders/{order_id}", response_model=OrderResponseSchema)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OrderModel).where(OrderModel.order_id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.patch("/orders/{order_id}/status", response_model=OrderResponseSchema)
async def update_order_status(order_id: int, payload: StatusUpdateSchema, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OrderModel).where(OrderModel.order_id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = payload.status
    await db.commit()
    await db.refresh(order)
    return order