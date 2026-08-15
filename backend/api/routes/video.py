from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)
from fastapi.responses import StreamingResponse

import cv2
import numpy as np

from backend.api.services.video_service import (
    generate_frames,
    process_camera_frame,
)


router = APIRouter()


# ============================================================
# SERVER VIDEO STREAM
# ============================================================

@router.get("/stream")
def video_stream():

    return StreamingResponse(
        generate_frames(),
        media_type=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        ),
    )


# ============================================================
# CAMERA FRAME AI PROCESSING
# ============================================================

@router.post("/camera/frame")
async def camera_frame(
    file: UploadFile = File(...)
):

    """
    Receive one JPEG frame from the React laptop webcam
    and process it using VisionEdge AI.
    """

    try:

        contents = await file.read()

        if not contents:

            raise HTTPException(
                status_code=400,
                detail="Empty camera frame.",
            )


        # ----------------------------------------------------
        # Convert uploaded bytes to NumPy
        # ----------------------------------------------------

        np_array = np.frombuffer(
            contents,
            np.uint8,
        )


        # ----------------------------------------------------
        # Decode JPEG
        # ----------------------------------------------------

        frame = cv2.imdecode(
            np_array,
            cv2.IMREAD_COLOR,
        )


        if frame is None:

            raise HTTPException(
                status_code=400,
                detail="Could not decode camera frame.",
            )


        # ----------------------------------------------------
        # VisionEdge AI
        # ----------------------------------------------------

        result = process_camera_frame(
            frame
        )


        return result


    except HTTPException:

        raise


    except Exception as e:

        print(
            "[ERROR] /camera/frame error:",
            e,
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )