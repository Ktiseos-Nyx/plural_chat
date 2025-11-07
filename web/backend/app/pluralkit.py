"""
PluralKit API client for backend
"""
import requests
import json
import time
import re
import os
from urllib.parse import urlparse
from typing import List, Dict, Optional
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class PluralKitAPI:
    """PluralKit API integration"""

    BASE_URL = "https://api.pluralkit.me/v2"

    def __init__(self, token: str = None):
        self.token = token
        self.headers = {"Authorization": token} if token else {}

    def get_system_info(self) -> Optional[Dict]:
        """Get basic system information"""
        if not self.token:
            return None

        try:
            response = requests.get(
                f"{self.BASE_URL}/systems/@me",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"PK API error: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"PK API connection error: {e}")
            return None

    def get_members(self) -> List[Dict]:
        """Get all members from PluralKit"""
        if not self.token:
            return []

        try:
            response = requests.get(
                f"{self.BASE_URL}/systems/@me/members",
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"PK API error: {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"PK API connection error: {e}")
            return []

    def _validate_avatar_url(self, url: str) -> bool:
        """Validate avatar URL for security"""
        if not url:
            return False

        try:
            parsed = urlparse(url)

            # Only allow HTTPS
            if parsed.scheme != 'https':
                return False

            # Whitelist trusted domains
            trusted_domains = [
                'cdn.pluralkit.me',
                'media.discordapp.net',
                'cdn.discordapp.com',
                'i.imgur.com',
                'avatars.githubusercontent.com',
            ]

            if parsed.hostname not in trusted_domains:
                return False

            # Check file extension
            path = parsed.path.lower()
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            if not any(path.endswith(ext) for ext in allowed_extensions):
                return False

            return True

        except Exception:
            return False

    def _sanitize_filename(self, member_name: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove any path separators and special characters
        safe_name = re.sub(r'[^\w\-_\s]', '_', str(member_name))
        # Replace spaces with underscores
        safe_name = safe_name.replace(' ', '_')
        # Limit length
        safe_name = safe_name[:50]
        # Ensure it's not empty
        if not safe_name:
            safe_name = "unknown"
        return safe_name

    def download_avatar(
        self,
        avatar_url: str,
        member_name: str,
        avatar_dir: str = "avatars"
    ) -> Optional[str]:
        """Download avatar image and return local path (WebP compressed)"""
        if not avatar_url:
            return None

        # Validate URL
        if not self._validate_avatar_url(avatar_url):
            logger.warning(f"Avatar URL failed security validation: {avatar_url}")
            return None

        try:
            # Create avatars directory
            os.makedirs(avatar_dir, exist_ok=True)
            os.chmod(avatar_dir, 0o755)

            # Create safe filename
            safe_name = self._sanitize_filename(member_name)
            local_filename = f"{safe_name}.webp"
            local_path = os.path.join(avatar_dir, local_filename)

            # Skip if already exists
            if os.path.exists(local_path):
                logger.info(f"Avatar already exists for {member_name}")
                return local_path

            logger.info(f"Downloading avatar for {member_name}...")

            # Download with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.get(avatar_url, timeout=30)
                    if response.status_code == 200:
                        break
                    elif response.status_code == 429:  # Rate limited
                        logger.warning(f"Rate limited, waiting 5 seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(5)
                        continue
                    else:
                        logger.warning(f"HTTP {response.status_code}, retrying... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(2)
                        continue
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Network error: {e}, retrying... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(2)
                    continue
            else:
                logger.error(f"Failed to download avatar for {member_name} after {max_retries} attempts")
                return None

            if response.status_code == 200:
                # Open image and convert to WebP
                original_image = Image.open(BytesIO(response.content))

                # Smart crop to square
                width, height = original_image.size
                if width != height:
                    min_dimension = min(width, height)
                    left = (width - min_dimension) // 2
                    top = (height - min_dimension) // 2
                    right = left + min_dimension
                    bottom = top + min_dimension
                    original_image = original_image.crop((left, top, right, bottom))

                # Resize to 256x256
                if original_image.size != (256, 256):
                    original_image = original_image.resize((256, 256), Image.Resampling.LANCZOS)

                # Convert to RGB if needed
                if original_image.mode in ('RGBA', 'LA', 'P'):
                    rgb_image = Image.new('RGB', original_image.size, (255, 255, 255))
                    if original_image.mode == 'P':
                        original_image = original_image.convert('RGBA')
                    if 'transparency' in original_image.info:
                        rgb_image.paste(original_image, mask=original_image.split()[-1])
                    else:
                        rgb_image.paste(original_image)
                    original_image = rgb_image
                elif original_image.mode != 'RGB':
                    original_image = original_image.convert('RGB')

                # Save as WebP
                original_image.save(local_path, 'WEBP', quality=80, optimize=True)

                logger.info(f"Saved avatar for {member_name}")
                return local_path
            else:
                logger.error(f"Failed to download avatar for {member_name}: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error downloading avatar for {member_name}: {e}")
            return None
