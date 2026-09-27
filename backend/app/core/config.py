"""Central configuration. All secrets/config come from environment variables — never hardcoded."""

import os
from functools import lru_cache


class Settings:
    APP_NAME: str = "Smart Resort 360"
    ENV: str = os.getenv("ENV", "development")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_Tz4vWyBs9eIX@ep-soft-dawn-b47pa1yr-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
    )
    KAFKA_ENABLED: bool = os.getenv("KAFKA_ENABLED", "false").lower() == "true"

    JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE_ME_IN_ENV")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    OTP_TTL_SECONDS: int = int(os.getenv("OTP_TTL_SECONDS", "300"))
    OTP_LENGTH: int = int(os.getenv("OTP_LENGTH", "4"))

    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "noreply@smartresort360.com")
    EMAIL_DEV_CONSOLE_FALLBACK: bool = (
        os.getenv("EMAIL_DEV_CONSOLE_FALLBACK", "true").lower() == "true"
    )

    # Amenity scheduling (Phase 9B)
    AMENITY_OFFER_TTL_SECONDS: int = int(os.getenv("AMENITY_OFFER_TTL_SECONDS", "90"))
    AMENITY_AGING_RATE_PER_MINUTE: float = float(
        os.getenv("AMENITY_AGING_RATE_PER_MINUTE", "1.0")
    )

    # Notification escalation
    NOTIFICATION_ACK_WINDOW_SECONDS: int = int(
        os.getenv("NOTIFICATION_ACK_WINDOW_SECONDS", "60")
    )

    # Voice provider (adapter behind interface; real credentials injected via secrets)
    VOICE_PROVIDER: str = os.getenv("VOICE_PROVIDER", "mock")
    VOICE_PROVIDER_SID: str = os.getenv("VOICE_PROVIDER_SID", "")
    VOICE_PROVIDER_TOKEN: str = os.getenv("VOICE_PROVIDER_TOKEN", "")

    # Maintenance risk (Phase 9A) — weights must sum to 1.0, transparent + configurable
    RISK_WEIGHT_SERVICE_OVERDUE: float = float(
        os.getenv("RISK_WEIGHT_SERVICE_OVERDUE", "0.30")
    )
    RISK_WEIGHT_ASSET_AGE: float = float(os.getenv("RISK_WEIGHT_ASSET_AGE", "0.20"))
    RISK_WEIGHT_USAGE: float = float(os.getenv("RISK_WEIGHT_USAGE", "0.20"))
    RISK_WEIGHT_PREVIOUS_FAILURES: float = float(
        os.getenv("RISK_WEIGHT_PREVIOUS_FAILURES", "0.20")
    )
    RISK_WEIGHT_COMPLAINTS: float = float(os.getenv("RISK_WEIGHT_COMPLAINTS", "0.10"))
    RISK_LOW_THRESHOLD: float = float(os.getenv("RISK_LOW_THRESHOLD", "0.35"))
    RISK_HIGH_THRESHOLD: float = float(os.getenv("RISK_HIGH_THRESHOLD", "0.65"))
    MAINTENANCE_EVAL_INTERVAL_MINUTES: int = int(
        os.getenv("MAINTENANCE_EVAL_INTERVAL_MINUTES", "60")
    )

    # ChromaDB / RAG
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")

    # LLM (open-weight, pluggable)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "open-weight-llm")

    # MLflow
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")

    RUN_SCHEDULER: bool = os.getenv("RUN_SCHEDULER", "false").lower() == "true"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
