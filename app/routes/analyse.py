from fastapi import APIRouter, UploadFile, File, HTTPException, status

router = APIRouter(
    prefix="/analyse",
    tags=["Analyse"]
)

async def process_single_image(file: UploadFile):
    """Process a single image for disease detection."""

    content = await file.read()

@router.post("/")
async def analyse_crops(file: UploadFile = File(...)):
    """Endpoint to upload an image for disease detection.!"""

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid file type. Please upload an image.!")


    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "Image received and processed for disease detection.!"
    }