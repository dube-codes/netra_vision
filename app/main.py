from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv

load_dotenv()

try:
    from .routes.analyse import router as analysis_router
except ImportError:
    from routes.analyse import router as analysis_router


app = FastAPI(
    title="Netra Vision API",
    description="AI-powered crop disease detection using Gemini Vision. Upload plant photos, get disease diagnosis and treatment plans.!",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "app": "netra-vision",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyse": "Upload an image for disease detection",
            "POST /analyse/batch": "Upload multiple images for batch disease detection",
            "GET /analysis": "Retrieve a list of all analysis performed",
            "GET /analysis/{analysis_id}": "Retrieve details of a specific analysis by Id"
        }
    }


app.include_router(analysis_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    request_schema = openapi_schema["paths"]["/analyse/batch"]["post"]["requestBody"]["content"]["multipart/form-data"]["schema"]
    schema_ref = request_schema.get("$ref")
    if schema_ref:
        component_name = schema_ref.rsplit("/", 1)[-1]
        file_items = openapi_schema["components"]["schemas"][component_name]["properties"]["files"]["items"]
        file_items.clear()
        file_items.update({"type": "string", "format": "binary"})

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
