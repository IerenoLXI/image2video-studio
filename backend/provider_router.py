import os
import uuid
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services.a2e_service import A2EService
from services.did_service import DIDService
from services.heygen_service import HeyGenService


class StartRequest(BaseModel):
    provider: str
    image_url: str
    text: str


class HeyGenTestRequest(BaseModel):
    image_url: str
    text: str


router = APIRouter(prefix="/api", tags=["image2video"])

# Create uploads directory if it doesn't exist (relative to backend directory)
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize services (will raise RuntimeError if API keys are missing)
# This is intentional - services should be configured before use
try:
    a2e_service = A2EService()
except RuntimeError:
    a2e_service = None

try:
    did_service = DIDService()
except RuntimeError:
    did_service = None

try:
    heygen_service = HeyGenService()
except RuntimeError:
    heygen_service = None


def get_service(provider: str):
    """Get the appropriate service based on provider name."""
    provider_lower = provider.lower()
    if provider_lower == "a2e":
        if a2e_service is None:
            raise HTTPException(
                status_code=500,
                detail="A2E service is not configured. Please set A2E_TOKEN in .env"
            )
        return a2e_service
    elif provider_lower == "did" or provider_lower == "d-id":
        if did_service is None:
            raise HTTPException(
                status_code=500,
                detail="D-ID service is not configured. Please set DID_KEY in .env"
            )
        return did_service
    elif provider_lower == "heygen":
        if heygen_service is None:
            raise HTTPException(
                status_code=500,
                detail="HeyGen service is not configured. Please set HEYGEN_KEY in .env"
            )
        return heygen_service
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider: {provider}. Supported providers: a2e, did, heygen"
        )


@router.post("/start-image2video")
async def start_image2video(request: StartRequest):
    """
    Start image to video generation with the specified provider.
    
    Body:
    - provider: "a2e", "did", or "heygen"
    - image_url: URL of the image to use
    - text: Text to speak in the video
    """
    if not request.image_url:
        raise HTTPException(status_code=400, detail="image_url is required")
    
    if not request.text:
        raise HTTPException(status_code=400, detail="text is required")
    
    try:
        service = get_service(request.provider)
        result = await service.start_video(request.image_url, request.text)
        return result
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting video: {str(e)}")


@router.post("/upload-image")
@router.post("/upload")
async def upload_image(request: Request, file: UploadFile = File(...)):
    """
    Upload an image file and get a URL to use for video generation.
    
    Returns:
    - url: HTTPS URL that can be used in /start-image2video
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    base_url = str(request.base_url).rstrip("/")
    file_url = f"{base_url}/api/uploads/{unique_filename}"
    
    return {"url": file_url, "filename": unique_filename}


@router.get("/uploads/{filename}")
async def get_uploaded_image(filename: str):
    """Serve uploaded images."""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@router.get("/status/{provider}/{task_id}")
async def get_status(provider: str, task_id: str):
    """
    Get the status of a video generation task.
    
    Path parameters:
    - provider: "a2e", "did", or "heygen"
    - task_id: The task ID returned from /start-image2video
    """
    if not task_id:
        raise HTTPException(status_code=400, detail="task_id is required")
    
    try:
        service = get_service(provider)
        result = await service.get_status(task_id)
        return result
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@router.post("/heygen/test-call")
async def heygen_test_call(payload: HeyGenTestRequest):
    """
    Diagnostic helper to verify the exact HeyGen endpoint and status code being used.
    """
    if heygen_service is None:
        raise HTTPException(
            status_code=500,
            detail="HeyGen service is not configured. Please set HEYGEN_KEY in .env",
        )

    try:
        return await heygen_service.debug_generate(payload.image_url, payload.text)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Error testing HeyGen integration: {str(exc)}"
        )

