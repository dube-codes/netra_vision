# Netra Vision

Netra Vision is a personal learning project for uploading plant photos and getting crop disease assessments from the Google Gemini API. It is a small FastAPI backend; it does not include a frontend or a database.

## Features

- Accepts one image or a batch of images through multipart form uploads.
- Validates JPEG and PNG image uploads, with a 15 MB per-image limit.
- Resizes images so neither dimension exceeds 2048 pixels.
- Sends each image to Gemini for a crop health and disease assessment.
- Saves processed images in an `uploads/` folder created at runtime.

## Tech stack

- Python. The current workspace `venv` uses Python 3.13.13; the project does not declare a supported Python version.
- FastAPI and Uvicorn for the API.
- Pillow for image validation and resizing.
- Google GenAI SDK for image analysis.
- `python-dotenv` for loading the root `.env` file.
- `python-multipart` for file uploads.

## Project structure

```text
netra_vision/
|-- app/
|   |-- main.py
|   |-- routes/
|   |   `-- analyse.py
|   `-- services/
|       |-- image.py
|       `-- vision.py
|-- requirements.txt
|-- README.md
`-- .gitignore
```

The application creates `uploads/` in its current working directory when it saves an image. The `.env` file is local configuration and is excluded by `.gitignore`.

## Installation and setup

Clone the repository and move into its folder:

```text
git clone https://github.com/dube-codes/netra_vision.git
cd netra_vision
```

Create and activate the `venv` environment, then install the pinned dependencies.

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation scripts, run this in the current PowerShell process and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```bat
python -m venv venv
venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

### macOS or Linux

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Environment variables

Create a `.env` file in the project root and add your own Gemini API key:

```env
GEMINI_API_KEY=your_api_key
```

Do not commit a real API key. The application loads `.env` when `app.main` is imported, and the Google GenAI client reads the key from the environment.

## How to run

From the project root, with the environment activated and `.env` configured, start the development server:

```text
python -m uvicorn app.main:app --reload
```

The API listens at `http://127.0.0.1:8000` by default. Open `http://127.0.0.1:8000/docs` to confirm it is running.

## API endpoints

No authentication is configured.

| Method | Path             | Parameters and behavior                                                                       | Status codes               |
| ------ | ---------------- | --------------------------------------------------------------------------------------------- | -------------------------- |
| `GET`  | `/`              | No parameters. Returns the API name, version, and endpoint descriptions.                      | `200`                      |
| `POST` | `/analyse/`      | Multipart form field `file`: one JPEG or PNG image. Returns its analysis.                     | `200`, `400`, `422`, `502` |
| `POST` | `/analyse/batch` | Multipart form field `files`: repeat this field once per image. Returns one result per image. | `200`, `400`, `422`, `502` |

Images must have an accepted image content type (`image/jpeg`, `image/jpg`, or `image/png`) and be no larger than 15 MB each. Each image is analyzed in sequence. If an image is invalid or Gemini analysis fails, the batch request stops with an error.

`400` is raised for an unsupported or invalid image, `422` for a missing or invalid request field, and `502` when the Gemini analysis call or its response parsing fails. The `400` and `502` error responses are raised in the code but are not currently listed in the generated OpenAPI response documentation.

## Request and response example

This PowerShell example sends two images to the batch endpoint. Replace the paths with your own files:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/analyse/batch" `
  -F "files=@C:\path\to\plant-one.jpg;type=image/jpeg" `
  -F "files=@C:\path\to\plant-two.png;type=image/png"
```

The request is `multipart/form-data`; use the field name `files` for every image. A successful response has this shape. The assessment text and values come from Gemini and can vary:

```json
{
  "message": "Batch image processing completed.",
  "results": [
    {
      "filename": "plant-one.jpg",
      "result": {
        "crop_detected": "Tomato",
        "severity": "mild",
        "diseases": [
          {
            "name": "Example leaf spot",
            "confidence": 0.82,
            "description": "Small spots are visible on several leaves."
          }
        ],
        "treatments": [
          {
            "treatment_name": "Remove affected leaves",
            "treatment_type": "preventive",
            "instructions": "Remove affected leaves and avoid wetting foliage.",
            "urgency": "within_week"
          }
        ],
        "overall_health": "The plant shows mild symptoms.",
        "additional_notes": "Monitor new growth for changes."
      },
      "content_type": "image/jpeg"
    }
  ]
}
```

The single-image endpoint returns the analysis under the `analysis` field; the batch endpoint uses `result` for each image.

## Swagger and OpenAPI docs

FastAPI provides the interactive docs at `/docs`, the alternative docs at `/redoc`, and the OpenAPI schema at `/openapi.json`. The batch upload schema is adjusted in `app/main.py` so Swagger UI treats each `files` item as a binary upload.

## What I learned

I practiced building async FastAPI routes, accepting multipart file uploads, validating and resizing images with Pillow, loading local environment variables, and calling an external image-analysis API. I also used OpenAPI metadata to make the batch file-upload field usable in Swagger UI.

## Known limitations

- There is no database or saved analysis history. The root response advertises `GET /analysis` and `GET /analysis/{analysis_id}`, but neither route is implemented.
- Uploaded images are saved under `uploads/` before Gemini analysis and are not cleaned up if analysis fails.
- The 15 MB check happens after the uploaded file has been read into memory.
- Batch processing is sequential and fails the whole request on the first invalid image or analysis failure.
- Gemini output is parsed as JSON but is not checked against a response model. The prompt's example currently contains trailing commas, which can lead to invalid JSON.
- The analysis endpoints do not require authentication. Do not expose this service publicly without adding appropriate access controls.
- The API does not declare a required Python version. The version noted above is from this workspace's virtual environment only.

## Potential improvements

- Correct the JSON example in the Gemini prompt and validate the model response with a response schema.
- Enforce upload and batch-size limits while reading files, and remove saved files when processing fails.
- Add tests for image validation, resizing, single uploads, batch uploads, and Gemini failures.
- Decide whether batch requests should return per-image errors instead of failing as a whole.
- Either implement the analysis-history routes with persistence or remove them from the root response.
- Document error responses in OpenAPI and consider authentication before deploying beyond local development.
