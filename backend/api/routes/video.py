from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse

from backend.api.services.video_service import (
    generate_frames,
    process_camera_frame,
)


router = APIRouter()


# ============================================================
# PRERECORDED VIDEO STREAM
# ============================================================

@router.get("/video")
def video_feed():

    return StreamingResponse(
        generate_frames(),
        media_type=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        ),
    )


# ============================================================
# LAPTOP CAMERA FRAME
# ============================================================

@router.post("/camera/frame")
async def process_camera_frame_route(
    file: UploadFile = File(...)
):

    frame_bytes = await file.read()


    if not frame_bytes:

        return {
            "success": False,
            "message": "Empty camera frame.",
        }


    try:

        processed_frame, analytics = (
            process_camera_frame(
                frame_bytes
            )
        )


        return {
            "success": True,
            "analytics": analytics,
        }


    except Exception as error:

        print(
            "[CAMERA ERROR]",
            error
        )


        return {
            "success": False,
            "message": str(error),
        }