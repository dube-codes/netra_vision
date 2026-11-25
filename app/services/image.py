from PIL import Image
import io

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png"]

def validate_image(content: bytes, content_type: str) -> dict:
    """ Validate the uploaded image content and type"""

    # Check if the content type is an image
    if not content_type.startswith("image/"):
        return {"is_valid": False, "message": "Invalid image type"}

    if content_type not in ALLOWED_IMAGE_TYPES:
        return {"is_valid": False, "message": "Image type not allowed"}

    size_mb = len(content) / (1024 * 1024)

    if size_mb > 15: # Limit to 15mb
        return {"is_valid": False, "message": "Image size exceeds 15 MB limit"}

    image = Image.open(io.BytesIO(content))
    width, height = image.size

    return {
        "is_valid": True,
        "message": "Image is valid",
        "width": width,
        "height": height,
        "size_mb": size_mb
    }


def resize_image_if_needed(content: bytes) -> bytes:
    pass