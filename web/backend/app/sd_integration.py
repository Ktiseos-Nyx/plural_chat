"""
Stable Diffusion API Integration
Support for Automatic1111, Forge UI, and ComfyUI

Perfect for GPU rental sessions - generate and share ephemeral images!
"""
import httpx
import json
import base64
from typing import Optional, Dict, Any, List
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class SDAPIError(Exception):
    """Stable Diffusion API error"""
    pass


class Automatic1111API:
    """
    Automatic1111 / Forge UI API client
    Both use the same API endpoints
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize API client

        Args:
            base_url: API URL (e.g., http://localhost:7860)
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    async def test_connection(self) -> bool:
        """Test if API is reachable"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/sdapi/v1/sd-models",
                    headers=self.headers
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    async def get_models(self) -> List[str]:
        """Get available models"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/sdapi/v1/sd-models",
                    headers=self.headers
                )
                response.raise_for_status()
                models = response.json()
                return [model["title"] for model in models]
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            raise SDAPIError(f"Failed to get models: {e}")

    async def text_to_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 20,
        cfg_scale: float = 7.0,
        seed: int = -1,
        sampler: str = "Euler a",
    ) -> bytes:
        """
        Generate image from text prompt

        Returns: Image bytes (PNG)
        """
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "sampler_name": sampler,
            "batch_size": 1,
            "n_iter": 1,
        }

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:  # 5 min timeout
                response = await client.post(
                    f"{self.base_url}/sdapi/v1/txt2img",
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()

                result = response.json()

                # Extract image from base64
                if "images" not in result or not result["images"]:
                    raise SDAPIError("No images in response")

                image_b64 = result["images"][0]
                image_bytes = base64.b64decode(image_b64)

                logger.info(f"✅ Generated image: {width}x{height}, {steps} steps")
                return image_bytes

        except httpx.TimeoutException:
            raise SDAPIError("Generation timed out (5 minutes)")
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise SDAPIError(f"Generation failed: {e}")

    async def image_to_image(
        self,
        init_image: bytes,
        prompt: str,
        negative_prompt: str = "",
        denoising_strength: float = 0.7,
        steps: int = 20,
        cfg_scale: float = 7.0,
    ) -> bytes:
        """
        Generate image from image + prompt

        Returns: Image bytes (PNG)
        """
        # Encode init image to base64
        init_image_b64 = base64.b64encode(init_image).decode()

        payload = {
            "init_images": [init_image_b64],
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "denoising_strength": denoising_strength,
            "steps": steps,
            "cfg_scale": cfg_scale,
        }

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.base_url}/sdapi/v1/img2img",
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()

                result = response.json()
                image_b64 = result["images"][0]
                image_bytes = base64.b64decode(image_b64)

                logger.info(f"✅ Generated img2img")
                return image_bytes

        except Exception as e:
            logger.error(f"img2img failed: {e}")
            raise SDAPIError(f"img2img failed: {e}")


class ComfyUIAPI:
    """
    ComfyUI API client
    Uses different API structure than A1111
    """

    def __init__(self, base_url: str):
        """
        Initialize ComfyUI API client

        Args:
            base_url: API URL (e.g., http://localhost:8188)
        """
        self.base_url = base_url.rstrip("/")

    async def test_connection(self) -> bool:
        """Test if API is reachable"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/system_stats")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"ComfyUI connection test failed: {e}")
            return False

    async def queue_prompt(self, workflow: Dict[str, Any]) -> str:
        """
        Queue a workflow for execution

        Returns: Prompt ID
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/prompt",
                    json={"prompt": workflow}
                )
                response.raise_for_status()

                result = response.json()
                prompt_id = result["prompt_id"]

                logger.info(f"✅ Queued ComfyUI workflow: {prompt_id}")
                return prompt_id

        except Exception as e:
            logger.error(f"Failed to queue workflow: {e}")
            raise SDAPIError(f"Failed to queue workflow: {e}")

    async def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        """Get generated image"""
        try:
            params = {
                "filename": filename,
                "subfolder": subfolder,
                "type": folder_type
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/view",
                    params=params
                )
                response.raise_for_status()
                return response.content

        except Exception as e:
            logger.error(f"Failed to get image: {e}")
            raise SDAPIError(f"Failed to get image: {e}")


class SDConnectionManager:
    """Manage user's SD API connections"""

    def __init__(self):
        self.connections: Dict[int, Dict[str, Any]] = {}

    def add_connection(
        self,
        user_id: int,
        api_type: str,
        base_url: str,
        api_key: Optional[str] = None,
        name: str = "My GPU"
    ):
        """Add or update SD API connection for user"""
        if api_type not in ["automatic1111", "forge", "comfyui"]:
            raise ValueError("Invalid API type")

        self.connections[user_id] = {
            "api_type": api_type,
            "base_url": base_url,
            "api_key": api_key,
            "name": name,
        }

        logger.info(f"✅ Added SD connection for user {user_id}: {api_type}")

    def get_connection(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's SD API connection"""
        return self.connections.get(user_id)

    def remove_connection(self, user_id: int):
        """Remove user's SD API connection"""
        if user_id in self.connections:
            del self.connections[user_id]
            logger.info(f"🗑️  Removed SD connection for user {user_id}")

    async def test_connection(self, user_id: int) -> bool:
        """Test user's SD API connection"""
        conn = self.get_connection(user_id)
        if not conn:
            return False

        api_type = conn["api_type"]
        base_url = conn["base_url"]

        if api_type in ["automatic1111", "forge"]:
            api = Automatic1111API(base_url, conn.get("api_key"))
            return await api.test_connection()
        elif api_type == "comfyui":
            api = ComfyUIAPI(base_url)
            return await api.test_connection()

        return False

    async def generate_image(
        self,
        user_id: int,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 20,
    ) -> bytes:
        """
        Generate image using user's SD API

        Returns: Image bytes
        """
        conn = self.get_connection(user_id)
        if not conn:
            raise SDAPIError("No SD API connection configured. Use /sdconnect first.")

        api_type = conn["api_type"]
        base_url = conn["base_url"]

        if api_type in ["automatic1111", "forge"]:
            api = Automatic1111API(base_url, conn.get("api_key"))
            return await api.text_to_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                steps=steps,
            )
        elif api_type == "comfyui":
            # ComfyUI requires workflow - simplified example
            raise SDAPIError("ComfyUI generation not yet implemented. Use A1111/Forge for now.")

        raise SDAPIError(f"Unknown API type: {api_type}")


# Global connection manager
sd_manager = SDConnectionManager()


# Preset prompts for member portraits
MEMBER_PORTRAIT_PRESETS = {
    "realistic": {
        "negative": "ugly, deformed, noisy, blurry, distorted, out of focus, bad anatomy, extra limbs, poorly drawn face, poorly drawn hands, missing fingers",
        "cfg_scale": 7.0,
    },
    "anime": {
        "negative": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality",
        "cfg_scale": 9.0,
    },
    "artistic": {
        "negative": "ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, mutation, mutated, extra limbs",
        "cfg_scale": 8.0,
    },
}


def build_member_prompt(
    member_name: str,
    description: str,
    style: str = "realistic"
) -> tuple[str, str]:
    """
    Build prompt for generating member portrait

    Returns: (prompt, negative_prompt)
    """
    preset = MEMBER_PORTRAIT_PRESETS.get(style, MEMBER_PORTRAIT_PRESETS["realistic"])

    prompt = f"portrait of {member_name}, {description}, high quality, detailed, professional photography"

    return (prompt, preset["negative"])
