import os
from typing import Dict

import httpx
from fastapi import HTTPException

HEYGEN_KEY = (os.getenv("HEYGEN_KEY") or "").strip()

HEADERS = {
    "Authorization": f"Bearer {HEYGEN_KEY}",
    "Content-Type": "application/json",
}


class HeyGenService:
    def __init__(self):
        self.base_url = "https://api.heygen.com"
        self.api_key = HEYGEN_KEY
        if not self.api_key:
            raise RuntimeError("HEYGEN_KEY not found in environment variables")

    async def start_video(self, image_url: str, text: str) -> Dict:
        """
        Start HeyGen talking avatar video generation.
        HeyGen uses image_url and text for video generation.
        """
        url = f"{self.base_url}/v1/video/talking"
        headers = HEADERS.copy()
        
        body = {
            "image_url": image_url,
            "text": text or "Hello there, welcome to my video!"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=body)

        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"HeyGen API error: {response.text}"
            )

        data = response.json()
        
        # HeyGen typically returns task_id in the response
        task_id = data.get("task_id") or data.get("id") or data.get("data", {}).get("task_id")
        
        return {
            "task_id": task_id,
            "status": data.get("status", "processing"),
            "provider": "heygen"
        }

    async def get_status(self, task_id: str) -> Dict:
        """Get status of HeyGen video generation task."""
        url = f"{self.base_url}/v1/video/task/{task_id}"
        headers = {"Authorization": HEADERS["Authorization"]}

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"HeyGen API error: {response.text}"
            )

        data = response.json()
        
        result = {
            "status": data.get("status", "processing"),
            "provider": "heygen"
        }
        
        # HeyGen status can be: processing, completed, failed
        if data.get("status") == "completed":
            result["result_url"] = data.get("result_url") or data.get("video_url")
        elif data.get("status") == "failed":
            result["failed_message"] = data.get("error", {}).get("message", "Unknown error") if isinstance(data.get("error"), dict) else str(data.get("error", "Unknown error"))
        
        return result

