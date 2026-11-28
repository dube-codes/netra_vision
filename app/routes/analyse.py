from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
import uuid

try:
    from ..services.image import validate_image, resize_image_if_needed, save_image
    from ..services.vision import analyse_image as vision_analyse_image
except ImportError:
    from services.image import validate_image, resize_image_if_needed, save_image
    from services.vision import analyse_image as vision_analyse_image

router = APIRouter(
    prefix="/analyse",
    tags=["Analyse"]
)

async def process_single_image(file: UploadFile):
    """Process a single image for disease detection."""

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type for {file.filename}. Please upload a valid image.",
        )

    content = await file.read()

    validation = validate_image(content, file.content_type)
    if not validation["is_valid"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=validation["message"])

    processed = resize_image_if_needed(content)

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    save_image(processed, "uploads", unique_name)

    try:
        result = await vision_analyse_image(processed, file.content_type)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The Gemini analysis service is unavailable.",
        ) from exc

    return result


@router.post("/")
async def analyse_image(file: UploadFile = File(...)):
    """Endpoint to upload an image for disease detection.!"""

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid file type. Please upload an image.!")

    result = await process_single_image(file)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "Image received and processed for disease detection.",
        "analysis": result,
    }


@router.post("/batch")
async def analyse_images(files: List[UploadFile] = File(...)):
    """Endpoint to upload multiple images for batch disease detection."""

    results = []

    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid file type for {file.filename}. Please upload valid image.!")

        result = await process_single_image(file)
        results.append({
            "filename": file.filename,
            "result": result,
            "content_type": file.content_type
        })

    return {
        "message": "Batch image processing completed.",
        "results": results
    }