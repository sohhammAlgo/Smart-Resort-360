"""F12 — What-If Simulator: recompute forecast/pricing/staffing under scenario overrides."""

from sqlalchemy.orm import Session

from app.ai.forecasting_model import forecast_occupancy
from app.ai.pricing_model import recommend_price
from app.ai.scheduling_model import recommend_staffing


def simulate(
    db: Session, occupancy_override_pct: float | None = None, horizon_days: int = 1
) -> dict:
    base_forecast = forecast_occupancy(db, horizon_days)
    occupancy_pct = (
        occupancy_override_pct
        if occupancy_override_pct is not None
        else (base_forecast["forecast"][-1] * 10)
    )
    pricing = recommend_price(occupancy_pct / 10)
    staffing = recommend_staffing(occupancy_pct)
    return {
        "occupancy_pct_used": occupancy_pct,
        "pricing": pricing,
        "staffing": staffing,
        "base_forecast": base_forecast,
    }
