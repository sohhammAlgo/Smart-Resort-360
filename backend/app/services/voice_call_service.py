"""AI Voice Call escalation channel, behind a provider adapter interface.

BLOCKER (see AGENT_CONTEXT.md): a real telephony provider (e.g. Twilio Voice)
requires live account credentials which are not available in this environment.
The mock provider implements the same interface so the workflow, Kafka events,
and failure-handling paths are fully exercised and testable end-to-end.
"""

import logging
from app.core.config import settings
from app.kafka.producer import publish
from app.kafka.topics import (
    TOPIC_AMENITY_EVENTS,
    EVENT_VOICE_CALL_INITIATED,
    EVENT_VOICE_CALL_COMPLETED,
)

logger = logging.getLogger("voice_call_service")


class VoiceProvider:
    def call(self, guest_id: str, reason: str) -> dict:
        raise NotImplementedError


class MockVoiceProvider(VoiceProvider):
    def call(self, guest_id: str, reason: str) -> dict:
        logger.info("MOCK VOICE CALL -> guest=%s reason=%s", guest_id, reason)
        return {"status": "COMPLETED", "provider": "mock"}


class TwilioVoiceProvider(
    VoiceProvider
):  # pragma: no cover - requires live credentials
    def __init__(self):
        if not settings.VOICE_PROVIDER_SID or not settings.VOICE_PROVIDER_TOKEN:
            raise RuntimeError("Voice provider credentials not configured")
        from twilio.rest import Client

        self._client = Client(
            settings.VOICE_PROVIDER_SID, settings.VOICE_PROVIDER_TOKEN
        )

    def call(self, guest_id: str, reason: str) -> dict:
        # Real dial logic would resolve guest_id -> phone number via booking records.
        raise NotImplementedError(
            "Twilio dial flow not wired without live phone-number data"
        )


def get_provider() -> VoiceProvider:
    if settings.VOICE_PROVIDER == "twilio":
        return TwilioVoiceProvider()
    return MockVoiceProvider()


def initiate_voice_call(guest_id: str, reason: str) -> dict:
    publish(
        TOPIC_AMENITY_EVENTS,
        EVENT_VOICE_CALL_INITIATED,
        {"guest_id": guest_id, "reason": reason},
    )
    result = get_provider().call(guest_id, reason)
    publish(
        TOPIC_AMENITY_EVENTS,
        EVENT_VOICE_CALL_COMPLETED,
        {"guest_id": guest_id, "result": result},
    )
    return result
