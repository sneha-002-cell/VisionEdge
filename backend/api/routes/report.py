from fastapi import APIRouter
from fastapi.responses import FileResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from sqlalchemy.orm import Session

from backend.database.database import SessionLocal
from backend.database.models import AnalyticsRecord

router = APIRouter()


@router.get("/report")
def generate_report():

    db: Session = SessionLocal()

    records = db.query(AnalyticsRecord).all()

    db.close()

    filename = "visionedge_report.pdf"

    doc = SimpleDocTemplate(filename)

    data = [[
        "Time",
        "People",
        "Cars",
        "Buses",
        "Motorcycles",
        "FPS"
    ]]

    for r in records:
        data.append([
            str(r.created_at),
            r.people,
            r.cars,
            r.buses,
            r.motorcycles,
            round(r.fps, 2),
        ])

    table = Table(data)

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ])
    )

    doc.build([table])

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename=filename,
    )