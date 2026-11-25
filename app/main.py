from fastapi import FastAPI


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
