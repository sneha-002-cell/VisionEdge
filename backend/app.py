from fastapi import FastAPI
from backend.api.routes.detection import router as detection_router
from backend.api.routes.video import router as video_router
from backend.api.routes.analytics import router as analytics_router
from fastapi.middleware.cors import CORSMiddleware
from backend.database.database import engine
from backend.database.models import Base
from backend.api.routes.history import router as history_router
from backend.api.routes.alerts import router as alert_router
from backend.api.routes.export import router as export_router
from backend.api.routes.report import router as report_router
from backend.auth.auth import router as auth_router

app = FastAPI(
    title="VisionEdge API",
    description="AI Video Analytics Backend",
    version="1.0.0"
)
Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detection_router)
app.include_router(video_router)
app.include_router(analytics_router)
app.include_router(history_router)
app.include_router(alert_router)
app.include_router(export_router)
app.include_router(report_router)
app.include_router(auth_router)

@app.get("/")
def home():
    return {"message": "Welcome to VisionEdge API"}


@app.get("/health")
def health():
    return {"status": "running"}