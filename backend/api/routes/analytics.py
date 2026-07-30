from fastapi import APIRouter
from backend.api.services.analytics_service import get

router = APIRouter()


@router.get("/analytics")
def analytics():
    return get()