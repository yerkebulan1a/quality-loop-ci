import asyncio
import json
import os
import pytest
import httpx
from aiokafka import AIOKafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
APP_URL = os.getenv("APP_URL", "http://web:8000")
TOPIC_NAME = "orders_topic"


@pytest.mark.asyncio
async def test_create_order_publishes_event_to_kafka():
    # 1. Инициализируем Kafka Consumer
    consumer = AIOKafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",  # Читать топик с самого начала
        group_id="test_qa_group",
    )
    await consumer.start()

    try:
        # 2. Отправляем HTTP-запрос на создание заказа в FastAPI
        payload = {"order_id": 101, "item": "Mechanical Keyboard", "price": 150.00}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{APP_URL}/orders", json=payload)

        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # 3. Вычитываем сообщение из Kafka с таймаутом 10 секунд
        async def get_message():
            async for msg in consumer:
                return msg.value

        message_value = await asyncio.wait_for(get_message(), timeout=10.0)

        # 4. Проверяем содержимое сообщения из Kafka
        assert message_value["event"] == "order_created"
        assert message_value["order_id"] == 101
        assert message_value["item"] == "Mechanical Keyboard"
        assert message_value["price"] == 150.00

    finally:
        # Обязательно закрываем коннект к Kafka
        await consumer.stop()