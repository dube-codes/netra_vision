from google import genai
import base64
import json 

client = genai.Client()

CROP_ANALISIS_PROMPT = """
    You are an expert agricultural scientist specializing in crop disease detection.
    Analyze this image of a crop/plant and provide a detailed disease assessment.

    Provide you analysis as a JSON object with exactly this structure:

    {
        "crop_detected": "Name of the crop or plant visible in the image",
        "severity": "healthy" or "mild" or "moderate" or "severe" or "critical",
        "diseases": [
            {
                "name": "Disease name",
                "confidence": 0.0 to 1.0,
                "description": "Brief description of the disease and visible symptoms"
            }
        ],

        "treatments": [
            {
                "treatment_name": "Name of treatment",
                "treatment_type": "organic" or "chemical" or "preventive",
                "instructions": "Step by step treatment instructions",
                "urgency": "immediate" or "within_week" or "seasonal",
            }
        ],

        "overall_health": "One sentence summary of plant health",
        "additional_notes": "Any other observations or recommendations",
    }
"""


async def analyse_image(image_content: bytes, content_type: str):
    """Analyse the image content using Google GenAI for disease detection."""

    interaction = await client.aio.interactions.create(
        model="gemini-3.8-flash",
        input=[
            {"type": "text", "text": CROP_ANALISIS_PROMPT},
            {
                "type": "image",
                "data": base64.b64encode(image_content).decode("utf-8"),
                "mime_type": content_type,
            },
        ]
    )
    response_text = interaction.output_text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("```", 2)[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
        response_text = response_text.strip()

    return json.loads(response_text)