from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.database import SessionLocal
from backend.database.models import AnalyticsRecord

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/history")
def get_history(db: Session = Depends(get_db)):
    records = (
        db.query(AnalyticsRecord)
        .order_by(AnalyticsRecord.id.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": r.id,
            "people": r.people,
            "cars": r.cars,
            "buses": r.buses,
            "motorcycles": r.motorcycles,
            "fps": r.fps,
            "line_crossings": r.line_crossings,
            "created_at": r.created_at,
        }
        for r in records
    ]