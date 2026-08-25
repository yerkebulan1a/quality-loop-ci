import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
import httpx
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Worker")

TOPIC_NAME = "orders_topic"


async def process_orders():
    consumer = AIOKafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        group_id="order_processing_worker_group",
        auto_offset_reset="earliest",
    )

    await consumer.start()
    logger.info("Worker started, listening for events...")

    try:
        async for msg in consumer:
            event_data = msg.value
            if event_data.get("event") == "order_created":
                order_id = event_data["order_id"]
                await asyncio.sleep(1)

                async with httpx.AsyncClient() as client:
                    await client.patch(
                        f"{settings.APP_URL}/orders/{order_id}/status",
                        json={"status": "processed"}
                    )
                    logger.info(f"Order {order_id} marked as PROCESSED in DB.")
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(process_orders())