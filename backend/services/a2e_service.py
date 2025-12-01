import os
from typing import Dict, Optional
import httpx
from fastapi import HTTPException


class A2EService:
    def __init__(self):
        self.base_url = "https://video.a2e.ai"
        self.token = os.getenv("A2E_TOKEN")
        if not self.token:
            raise RuntimeError("A2E_TOKEN not found in environment variables")

    async def start_video(self, image_url: str, text: str) -> Dict:
        """
        Start A2E image to video generation.
        Note: A2E uses prompt/negative_prompt, so we'll convert text to prompt.
        """
        url = f"{self.base_url}/api/v1/userImage2Video/start"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # A2E uses prompt and negative_prompt, so we'll use text as prompt
        prompt = text if text else "the person is speaking. Looking at the camera. detailed eyes, clear teeth, still background"
        negative_prompt = "low quality, static image, lowres, moving camera"
        
        body = {
            "name": "Cursor Demo",
            "image_url": image_url,
            "prompt": prompt,
            "negative_prompt": negative_prompt
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=body)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"A2E API error: {response.text}"
            )

        data = response.json()
        task = data.get("data", {})
        
        return {
            "task_id": task.get("_id"),
            "status": task.get("current_status", "processing"),
            "provider": "a2e"
        }

    async def get_status(self, task_id: str) -> Dict:
        """Get status of A2E video generation task."""
        url = f"{self.base_url}/api/v1/userImage2Video/{task_id}"
        headers = {"Authorization": f"Bearer {self.token}"}

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"A2E API error: {response.text}"
            )

        data = response.json()
        task = data.get("data", {})
        
        result = {
            "status": task.get("current_status", "processing"),
            "provider": "a2e"
        }
        
        if task.get("current_status") == "completed":
            result["result_url"] = task.get("result_url")
        elif task.get("current_status") == "failed":
            result["failed_message"] = task.get("failed_message", "Unknown error")
        
        return result

