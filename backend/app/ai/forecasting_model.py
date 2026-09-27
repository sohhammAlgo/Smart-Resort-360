"""Agent 1 — Demand & Occupancy forecasting.

BLOCKER (AGENT_CONTEXT.md): Chronos-Bolt/MOIRAI checkpoints require a model
download this sandbox cannot reach. A simple moving-average-with-trend
estimator (same output contract) is used so forecasting/pricing/scheduling can
be demoed and tested end-to-end; swapping in a real foundation-model forecaster
only requires changing this module.
"""

from datetime import date, timedelta
from statistics import mean
from sqlalchemy.orm import Session

from app.models.booking import Booking


def historical_daily_occupancy(db: Session, days: int = 14) -> list[float]:
    today = date.today()
    counts = []
    for offset in range(days, 0, -1):
        day = today - timedelta(days=offset)
        active = (
            db.query(Booking)
            .filter(Booking.check_in_date <= day, Booking.check_out_date > day)
            .count()
        )
        counts.append(float(active))
    return counts or [0.0]


def forecast_occupancy(db: Session, horizon_days: int = 1) -> dict:
    history = historical_daily_occupancy(db)
    baseline = mean(history)
    trend = (
        (history[-1] - history[0]) / max(1, len(history) - 1)
        if len(history) > 1
        else 0.0
    )
    forecast = [
        round(max(0.0, baseline + trend * i), 2) for i in range(1, horizon_days + 1)
    ]
    return {
        "model": "moving-average-trend-v1",
        "history_points": len(history),
        "forecast": forecast,
    }


def forecast_demand(db: Session, horizon_days: int = 7) -> dict:
    occ = forecast_occupancy(db, horizon_days)
    return {"model": occ["model"], "demand_index": occ["forecast"]}
