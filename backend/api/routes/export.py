from fastapi import APIRouter
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import pandas as pd

from backend.database.database import SessionLocal
from backend.database.models import AnalyticsRecord

router = APIRouter()


@router.get("/export/csv")
def export_csv():

    db: Session = SessionLocal()

    records = db.query(AnalyticsRecord).all()

    db.close()

    data = []

    for r in records:
        data.append({
            "Time": r.created_at,
            "People": r.people,
            "Cars": r.cars,
            "Buses": r.buses,
            "Motorcycles": r.motorcycles,
            "FPS": r.fps,
            "LineCrossings": r.line_crossings,
        })

    df = pd.DataFrame(data)

    filename = "visionedge_report.csv"

    df.to_csv(filename, index=False)

    return FileResponse(
        path=filename,
        media_type="text/csv",
        filename=filename,
    )