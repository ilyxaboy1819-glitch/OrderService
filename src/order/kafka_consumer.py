import asyncio
import json
import logging
import uuid

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from src.config import settings
from src.database import SessionFactory
from src.order.repository import OrderRepository
from src.order.schemas import KafkaOrderPayload, OrderCreate, OrderItemCreate

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 1.0


async def kafka_consumer() -> None:
    consumer = AIOKafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )
    dlq_producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        enable_idempotence=True,
        acks="all",
    )
    await consumer.start()
    await dlq_producer.start()
    try:
        async for msg in consumer:
            await _handle(msg, dlq_producer)
            await consumer.commit()
    finally:
        await consumer.stop()
        await dlq_producer.stop()


async def _handle(msg, dlq_producer: AIOKafkaProducer) -> None:
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            await _process(msg)
            return
        except Exception as e:
            last_error = e
            logger.warning(f"Failed to process message attempt={attempt + 1}: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))

    logger.error(f"Message failed after {MAX_RETRIES} attempts, sending to DLQ")
    dlq_value = json.dumps({
        "original_message": msg.value.decode(),
        "error_reason": str(last_error),
        "retry_count": MAX_RETRIES,
        "topic": msg.topic,
        "partition": msg.partition,
        "offset": msg.offset,
    }).encode()
    await dlq_producer.send_and_wait(
        settings.kafka_dlq_topic,
        value=dlq_value,
        key=msg.key,
    )


async def _process(msg) -> None:
    payload = KafkaOrderPayload.model_validate_json(msg.value.decode())

    async with SessionFactory() as session:
        repo = OrderRepository(session)

        existing = await repo.get_by_idempotency_key(payload.idempotency_key)
        if existing:
            logger.info(f"Duplicate message, idempotency_key={payload.idempotency_key}")
            return

        data = OrderCreate(
            user_id=uuid.UUID(payload.user_id),
            user_email=payload.user_email,
            user_name=payload.user_name,
            idempotency_key=payload.idempotency_key,
            items=[
                OrderItemCreate(
                    application_id=item.application_id,
                    quantity=item.quantity,
                    price=item.price,
                    application_name=item.application_name,
                    application_category=item.application_category,
                )
                for item in payload.items
            ],
        )
        model = data.to_model()
        await repo.create(model)
        await session.commit()
        logger.info(f"Order created from Kafka, idempotency_key={payload.idempotency_key}")
