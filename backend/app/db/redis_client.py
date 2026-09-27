"""Redis: cache, temporary state, TTL-based data, Sorted Sets for priority queues.
PostgreSQL remains authoritative for durable state.
"""

import fakeredis
import redis

from app.core.config import settings

_client = None


def get_redis():
    global _client
    if _client is not None:
        return _client
    if settings.ENV == "test" or settings.REDIS_URL.startswith("fake://"):
        _client = fakeredis.FakeStrictRedis(decode_responses=True)
    else:
        try:
            client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            client.ping()
            _client = client
        except Exception:
            # Fallback so the app remains demoable / testable without a live Redis instance.
            _client = fakeredis.FakeStrictRedis(decode_responses=True)
    return _client
