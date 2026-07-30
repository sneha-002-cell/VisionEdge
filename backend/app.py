from fastapi import FastAPI
from backend.api.routes.detection import router as detection_router
from backend.api.routes.video import router as video_router
from backend.api.routes.analytics import router as analytics_router

app = FastAPI(
    title="VisionEdge API",
    description="AI Video Analytics Backend",
    version="1.0.0"
)

app.include_router(detection_router)
app.include_router(video_router)
app.include_router(analytics_router)


@app.get("/")
def home():
    return {"message": "Welcome to VisionEdge API"}


@app.get("/health")
def health():
    return {"status": "running"}