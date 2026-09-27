from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.asset import Asset
from app.models.maintenance import MaintenanceHistory, MaintenanceRisk
from app.schemas.maintenance import AssetCreate, AssetOut, MaintenanceHistoryCreate
from app.services import risk_service

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


@router.post("/assets", response_model=AssetOut)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    asset = Asset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/assets", response_model=list[AssetOut])
def list_assets(db: Session = Depends(get_db)):
    return db.query(Asset).all()


@router.post("/history")
def add_history(payload: MaintenanceHistoryCreate, db: Session = Depends(get_db)):
    record = MaintenanceHistory(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"maintenance_id": record.maintenance_id}


@router.post("/{asset_id}/evaluate")
def evaluate(asset_id: int, db: Session = Depends(get_db)):
    try:
        risk = risk_service.evaluate_asset(db, asset_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {
        "asset_id": asset_id,
        "risk_score": float(risk.risk_score),
        "risk_level": risk.risk_level,
    }


@router.get("/risk")
def list_risk(db: Session = Depends(get_db)):
    rows = (
        db.query(MaintenanceRisk)
        .order_by(MaintenanceRisk.calculated_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "asset_id": r.asset_id,
            "risk_score": float(r.risk_score),
            "risk_level": r.risk_level,
            "calculated_at": r.calculated_at,
        }
        for r in rows
    ]
