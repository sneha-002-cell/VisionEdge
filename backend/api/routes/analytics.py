from fastapi import APIRouter, Depends

from backend.api.services.analytics_service import (
    get_analytics,
)

from backend.auth.security import verify_token


router = APIRouter()


@router.get("/analytics")
def analytics(
    user=Depends(verify_token),
):

    return get_analytics()