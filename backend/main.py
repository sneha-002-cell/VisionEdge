import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.database import engine, SessionLocal
from backend.database.models import Base, User

from backend.api.routes.detection import router as detection_router
from backend.api.routes.video import router as video_router
from backend.api.routes.analytics import router as analytics_router
from backend.api.routes.history import router as history_router
from backend.api.routes.alerts import router as alert_router
from backend.api.routes.export import router as export_router
from backend.api.routes.report import router as report_router
from backend.auth.auth import router as auth_router
from backend.auth.security import hash_password


app = FastAPI(
    title="VisionEdge API",
    description="AI Video Analytics Backend",
    version="1.0.0",
)


# --------------------------------------------------
# Database initialization
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# Demo user initialization
# --------------------------------------------------

def create_demo_user():
    db = SessionLocal()

    try:
        demo_email = os.getenv(
            "DEMO_EMAIL",
            "demo@visionedge.ai"
        )

        demo_password = os.getenv(
            "DEMO_PASSWORD",
            "VisionEdgeDemo@2026"
        )

        demo_username = os.getenv(
            "DEMO_USERNAME",
            "VisionEdge Demo"
        )

        existing_user = (
            db.query(User)
            .filter(User.email == demo_email)
            .first()
        )

        if existing_user:
            # Update the demo user's password
            existing_user.password = hash_password(demo_password)
            existing_user.username = demo_username

            db.commit()

            print("========================================")
            print("VisionEdge demo user password updated")
            print(f"Email: {demo_email}")
            print("Password: [hidden]")
            print("========================================")

            return

        demo_user = User(
            username=demo_username,
            email=demo_email,
            password=hash_password(demo_password),
        )

        db.add(demo_user)
        db.commit()

        print("========================================")
        print("VisionEdge demo user created")
        print(f"Email: {demo_email}")
        print("Password: [hidden]")
        print("========================================")

    except Exception as e:
        db.rollback()
        print(f"Could not create/update demo user: {e}")

    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    create_demo_user()


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# API Routes
# --------------------------------------------------

app.include_router(detection_router)
app.include_router(video_router)
app.include_router(analytics_router)
app.include_router(history_router)
app.include_router(alert_router)
app.include_router(export_router)
app.include_router(report_router)
app.include_router(auth_router)


# --------------------------------------------------
# Basic endpoints
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to VisionEdge API"
    }


@app.get("/health")
def health():
    return {
        "status": "running"
    }