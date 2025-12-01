import logging
import os
from typing import Dict, Tuple

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class HeyGenService:
    """Client for the HeyGen REST API."""

    def __init__(self):
        self.base_url = "https://api.heygen.com"
        self.generate_path = "/v2/video/generate"
        self.task_path = "/v1/video/task"

        self.api_key = (os.getenv("HEYGEN_KEY") or "").strip()
        if not self.api_key:
            raise RuntimeError("HEYGEN_KEY not found in environment variables")

        # Optional defaults for avatar/voice configuration
        self.default_avatar_id = (os.getenv("HEYGEN_AVATAR_ID") or "").strip()
        self.default_voice_id = (os.getenv("HEYGEN_VOICE_ID") or "").strip()
        self.voice_language = (os.getenv("HEYGEN_LANGUAGE") or "en-US").strip()
        self.avatar_style = (os.getenv("HEYGEN_AVATAR_STYLE") or "normal").strip()
        self.voice_speed = self._safe_float(os.getenv("HEYGEN_VOICE_SPEED"), 1.0)
        self.dimension_width = self._safe_int(os.getenv("HEYGEN_DIMENSION_WIDTH"), 1280)
        self.dimension_height = self._safe_int(os.getenv("HEYGEN_DIMENSION_HEIGHT"), 720)

    @staticmethod
    def _safe_int(value: str, fallback: int) -> int:
        try:
            return int(value) if value is not None else fallback
        except (TypeError, ValueError):
            return fallback

    @staticmethod
    def _safe_float(value: str, fallback: float) -> float:
        try:
            return float(value) if value is not None else fallback
        except (TypeError, ValueError):
            return fallback

    def _json_headers(self) -> Dict[str, str]:
        return {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _auth_headers(self) -> Dict[str, str]:
        return {"X-Api-Key": self.api_key}

    def _resolve_avatar_id(self, avatar_hint: str) -> str:
        candidate = (avatar_hint or "").strip()
        if candidate:
            return candidate
        if self.default_avatar_id:
            return self.default_avatar_id
        raise HTTPException(
            status_code=400,
            detail={
                "error": "HeyGen avatar_id is required",
                "details": (
                    "Provide a HeyGen avatar_id via the image_url field or set "
                    "HEYGEN_AVATAR_ID in the environment."
                ),
            },
        )

    def _build_character_payload(self, avatar_hint: str) -> Dict:
        return {
            "type": "avatar",
            "avatar_id": self._resolve_avatar_id(avatar_hint),
            "avatar_style": self.avatar_style or "normal",
        }

    def _build_voice_payload(self, text: str) -> Dict:
        if not self.default_voice_id:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "HeyGen voice_id is not configured",
                    "details": (
                        "Set HEYGEN_VOICE_ID to a valid HeyGen voice identifier."
                    ),
                },
            )

        return {
            "type": "text",
            "input_text": (text or "Hello there, welcome to my video!").strip(),
            "voice_id": self.default_voice_id,
            "language": self.voice_language or "en-US",
            "speed": self.voice_speed,
        }

    def _build_video_body(self, image_url: str, text: str) -> Dict:
        return {
            "video_inputs": [
                {
                    "character": self._build_character_payload(image_url),
                    "voice": self._build_voice_payload(text),
                }
            ],
            "dimension": {
                "width": self.dimension_width,
                "height": self.dimension_height,
            },
        }

    async def _send_generate_request(self, payload: Dict) -> Tuple[str, httpx.Response]:
        url = f"{self.base_url}{self.generate_path}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=self._json_headers(), json=payload)
        logger.info("HeyGen POST %s returned HTTP %s", url, response.status_code)
        return url, response

    @staticmethod
    def _extract_error_detail(response: httpx.Response) -> str:
        try:
            data = response.json()
        except ValueError:
            return response.text[:200] or "Empty response"

        if isinstance(data, dict):
            return (
                data.get("message")
                or data.get("detail")
                or data.get("error", {}).get("message")
                or str(data)
            )
        return str(data)

    def _raise_api_error(self, url: str, response: httpx.Response) -> None:
        error_detail = self._extract_error_detail(response)
        logger.error(
            "HeyGen API error url=%s status=%s body=%s",
            url,
            response.status_code,
            response.text,
        )
        raise HTTPException(
            status_code=response.status_code,
            detail={
                "error": f"HeyGen API returned {response.status_code}",
                "details": error_detail,
            },
        )

    async def start_video(self, image_url: str, text: str) -> Dict:
        """
        Start HeyGen avatar video generation using the official v2 endpoint.

        The image_url parameter is treated as the HeyGen avatar_id (or falls back
        to HEYGEN_AVATAR_ID) because the /v2/video/generate API requires an avatar.
        """
        payload = self._build_video_body(image_url, text)
        url, response = await self._send_generate_request(payload)

        if response.status_code not in (200, 201):
            self._raise_api_error(url, response)

        try:
            data = response.json()
        except ValueError:
            self._raise_api_error(url, response)
        task_id = (
            data.get("task_id")
            or data.get("id")
            or data.get("data", {}).get("task_id")
        )

        return {
            "task_id": task_id,
            "status": data.get("status", "processing"),
            "provider": "heygen",
        }

    async def debug_generate(self, image_url: str, text: str) -> Dict:
        """
        Helper used by the debug route to log the request URL and status code.
        """
        payload = self._build_video_body(image_url, text)
        url, response = await self._send_generate_request(payload)
        log_level = logging.INFO if response.status_code in (200, 201) else logging.ERROR
        logger.log(
            log_level,
            "HeyGen debug call url=%s status=%s",
            url,
            response.status_code,
        )
        try:
            body = response.json()
        except ValueError:
            body = {"raw": response.text[:500]}

        return {
            "request_url": url,
            "status_code": response.status_code,
            "response": body,
        }

    async def get_status(self, task_id: str) -> Dict:
        """Get status of HeyGen video generation task."""
        url = f"{self.base_url}{self.task_path}/{task_id}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, headers=self._auth_headers())

        if response.status_code != 200:
            self._raise_api_error(url, response)

        try:
            data = response.json()
        except ValueError:
            self._raise_api_error(url, response)

        result = {
            "status": data.get("status", "processing"),
            "provider": "heygen",
        }

        if data.get("status") == "completed":
            result["result_url"] = data.get("result_url") or data.get("video_url")
        elif data.get("status") == "failed":
            error_payload = data.get("error", {})
            if isinstance(error_payload, dict):
                result["failed_message"] = error_payload.get("message", "Unknown error")
            else:
                result["failed_message"] = str(error_payload or "Unknown error")

        return result


