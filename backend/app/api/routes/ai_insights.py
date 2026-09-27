from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.ai.forecasting_model import forecast_occupancy, forecast_demand
from app.ai.pricing_model import recommend_price
from app.ai.sentiment_model import analyze_sentiment
from app.ai.scheduling_model import recommend_staffing
from app.services.scenario_service import simulate

router = APIRouter(tags=["ai"])


@router.get("/forecast/occupancy")
def get_occupancy_forecast(horizon_days: int = 1, db: Session = Depends(get_db)):
    return forecast_occupancy(db, horizon_days)


@router.get("/forecast/demand")
def get_demand_forecast(horizon_days: int = 7, db: Session = Depends(get_db)):
    return forecast_demand(db, horizon_days)


class PricingRequest(BaseModel):
    occupancy_forecast: float


@router.post("/pricing/recommend")
def pricing_recommend(payload: PricingRequest):
    return recommend_price(payload.occupancy_forecast)


class SentimentRequest(BaseModel):
    review_text: str


@router.post("/sentiment/analyze")
def sentiment_analyze(payload: SentimentRequest):
    return analyze_sentiment(payload.review_text)


@router.get("/staff/recommendation")
def staff_recommendation(occupancy_forecast_pct: float = 70.0):
    return recommend_staffing(occupancy_forecast_pct)


class ScenarioRequest(BaseModel):
    occupancy_override_pct: float | None = None
    horizon_days: int = 1


@router.post("/scenario/simulate")
def scenario_simulate(payload: ScenarioRequest, db: Session = Depends(get_db)):
    return simulate(db, payload.occupancy_override_pct, payload.horizon_days)
