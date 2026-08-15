from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)

import cv2
import numpy as np

from backend.core.tracker import detect_and_track


router = APIRouter()


# ============================================================
# IMAGE DETECTION
# ============================================================

@router.post("/detect-image")
async def detect_image(
    file: UploadFile = File(...)
):

    """
    Upload an image and run VisionEdge object detection.
    """

    try:

        # ----------------------------------------------------
        # Read uploaded image
        # ----------------------------------------------------

        contents = await file.read()


        if not contents:

            raise HTTPException(
                status_code=400,
                detail="Empty image file.",
            )


        # ----------------------------------------------------
        # Convert to NumPy
        # ----------------------------------------------------

        np_array = np.frombuffer(
            contents,
            np.uint8,
        )


        # ----------------------------------------------------
        # Decode image
        # ----------------------------------------------------

        image = cv2.imdecode(
            np_array,
            cv2.IMREAD_COLOR,
        )


        if image is None:

            raise HTTPException(
                status_code=400,
                detail="Could not decode image.",
            )


        # ----------------------------------------------------
        # VisionEdge YOLO
        # ----------------------------------------------------

        results = detect_and_track(
            image
        )


        if not results:

            return {
                "filename": file.filename,
                "total_objects": 0,
                "detections": [],
            }


        result = results[0]

        names = result.names


        # ----------------------------------------------------
        # Build detection response
        # ----------------------------------------------------

        detections = []


        for box in result.boxes:

            try:

                class_id = int(
                    box.cls[0]
                )

                confidence = float(
                    box.conf[0]
                )

                label = names[class_id]


                detections.append(
                    {
                        "class": label,
                        "confidence": round(
                            confidence,
                            3,
                        ),
                    }
                )

            except Exception:

                continue


        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return {

            "filename":
                file.filename,

            "total_objects":
                len(detections),

            "detections":
                detections,

        }


    except HTTPException:

        raise


    except Exception as e:

        print(
            "[ERROR] Image detection error:",
            e,
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )