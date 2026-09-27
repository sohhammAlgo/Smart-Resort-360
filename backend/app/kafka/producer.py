"""Kafka producer abstraction.

Falls back to an in-memory/log-based no-op producer when KAFKA_ENABLED is false
or the broker is unreachable, so the application, tests and demo remain fully
functional without a live Kafka cluster. This keeps Kafka strictly an
application event bus (never a required synchronous dependency for business logic).
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.core.config import settings

logger = logging.getLogger("kafka.producer")

# In-memory event log, primarily used by tests/demo to assert events were published.
EVENT_LOG: List[Dict[str, Any]] = []


class _NoOpProducer:
    def send(self, topic: str, event_type: str, payload: Dict[str, Any]):
        record = {
            "topic": topic,
            "event_type": event_type,
            "payload": payload,
            "published_at": datetime.now(timezone.utc).isoformat(),
        }
        EVENT_LOG.append(record)
        logger.info("kafka_event(no-op) %s", json.dumps(record, default=str))
        return record


class _RealProducer:
    def __init__(self):
        from kafka import KafkaProducer  # kafka-python, optional dependency

        self._producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        )

    def send(self, topic: str, event_type: str, payload: Dict[str, Any]):
        record = {
            "event_type": event_type,
            "payload": payload,
            "published_at": datetime.now(timezone.utc).isoformat(),
        }
        self._producer.send(topic, record)
        self._producer.flush()
        EVENT_LOG.append({"topic": topic, **record})
        return record


_producer_instance = None


def get_producer():
    global _producer_instance
    if _producer_instance is not None:
        return _producer_instance
    if settings.KAFKA_ENABLED:
        try:
            _producer_instance = _RealProducer()
        except Exception:
            logger.warning("Kafka broker unavailable; falling back to no-op producer")
            _producer_instance = _NoOpProducer()
    else:
        _producer_instance = _NoOpProducer()
    return _producer_instance


def publish(topic: str, event_type: str, payload: Dict[str, Any]):
    return get_producer().send(topic, event_type, payload)
