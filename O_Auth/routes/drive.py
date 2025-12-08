import json
import httpx
from starlette.responses import JSONResponse
from starlette.requests import Request

from config import GOOGLE_DRIVE_UPLOAD_URL
from token_manager import get_valid_access_token


async def upload_to_drive(request: Request):
    """Upload file to Google Drive with auto token refresh"""
    # Get valid access token (auto-refresh if needed)
    access_token = await get_valid_access_token()

    if not access_token:
        return JSONResponse(
            {"error": "Please login first via /auth/google"}, 
            status_code=401
        )

    # Parse request body
    body = await request.json()
    file_content = body.get("content", "Hello from Starlette!")
    file_name = body.get("filename", "example.txt")

    # Prepare multipart upload
    metadata = {"name": file_name}

    files = {
        "metadata": ("metadata.json", json.dumps(metadata), "application/json"),
        "file": (file_name, file_content.encode(), "text/plain")
    }

    # Upload to Google Drive
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_DRIVE_UPLOAD_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            files=files
        )

    result = response.json()
    
    if response.status_code == 200:
        return JSONResponse({
            "success": True,
            "file_id": result.get("id"),
            "file_name": result.get("name"),
            "message": "File uploaded successfully"
        })
    else:
        return JSONResponse({
            "success": False,
            "error": result
        }, status_code=response.status_code)