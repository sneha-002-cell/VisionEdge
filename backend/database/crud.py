from sqlalchemy.orm import Session
from backend.database.models import AnalyticsRecord


def save_record(db: Session, data):
    record = AnalyticsRecord(
        people=data["people"],
        cars=data["cars"],
        buses=data["buses"],
        motorcycles=data["motorcycles"],
        fps=data["fps"],
        line_crossings=data["line_crossings"],
    )

    db.add(record)
    db.commit()