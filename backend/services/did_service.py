import os
from typing import Dict
import httpx
from fastapi import HTTPException


class DIDService:
    def __init__(self):
        self.base_url = "https://api.d-id.com"
        # Strip whitespace/newlines to avoid invalid header bytes
        self.api_key = os.getenv("DID_KEY", "").strip()
        if not self.api_key:
            raise RuntimeError("DID_KEY not found in environment variables")
        self.auth_header = (
            self.api_key
            if self.api_key.lower().startswith(("basic ", "bearer "))
            else f"Basic {self.api_key}"
        )

    async def start_video(self, image_url: str, text: str) -> Dict:
        """
        Start D-ID talking avatar video generation.
        D-ID uses source_url for image and script for text.
        """
        url = f"{self.base_url}/talks"
        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json"
        }
        
        body = {
            "source_url": image_url,
            "script": {
                "type": "text",
                "input": text or "Hello there, welcome to my video!"
            }
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=body)

        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"D-ID API error: {response.text}"
            )

        data = response.json()
        
        return {
            "task_id": data.get("id"),
            "status": data.get("status", "processing"),
            "provider": "did"
        }

    async def get_status(self, task_id: str) -> Dict:
        """Get status of D-ID video generation task."""
        url = f"{self.base_url}/talks/{task_id}"
        headers = {"Authorization": self.auth_header}

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"D-ID API error: {response.text}"
            )

        data = response.json()
        
        result = {
            "status": data.get("status", "processing"),
            "provider": "did"
        }
        
        # D-ID status can be: created, processing, done, error
        if data.get("status") == "done":
            result["status"] = "completed"
            result["result_url"] = data.get("result_url")
        elif data.get("status") == "error":
            result["status"] = "failed"
            result["failed_message"] = data.get("error", {}).get("message", "Unknown error")
        
        return result

