"""
Ephemeral media storage system
Images cached for 24 hours, then auto-deleted
Perfect for GPU rental sessions and temporary image sharing
"""
import hashlib
import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
from urllib.parse import urlparse
import httpx
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

# Media cache directory
MEDIA_DIR = Path(os.getenv("MEDIA_CACHE_DIR", "media_cache"))
MEDIA_DIR.mkdir(exist_ok=True)

# Cache TTL (24 hours)
MEDIA_TTL_SECONDS = 24 * 60 * 60

# Size limits
MAX_FILE_SIZE = int(os.getenv("MAX_MEDIA_SIZE", 10 * 1024 * 1024))  # 10MB
MAX_IMAGE_DIMENSION = 2048

# Allowed domains for URL fetching (whitelist)
ALLOWED_DOMAINS = [
    "imgur.com",
    "i.imgur.com",
    "cdn.discordapp.com",
    "media.discordapp.net",
    "cdn.pluralkit.me",
    "tenor.com",
    "giphy.com",
    "i.redd.it",
    "preview.redd.it",
]


class MediaCache:
    """Ephemeral media cache manager"""

    def __init__(self):
        """Initialize and cleanup old files"""
        self.cleanup_old_files()
        logger.info(f"📁 Media cache initialized: {MEDIA_DIR}")

    def cleanup_old_files(self) -> int:
        """Remove files older than TTL"""
        now = datetime.now()
        deleted = 0

        for file in MEDIA_DIR.glob("*"):
            if file.is_file() and file.suffix != ".gitkeep":
                try:
                    mtime = datetime.fromtimestamp(file.stat().st_mtime)
                    if (now - mtime).total_seconds() > MEDIA_TTL_SECONDS:
                        file.unlink()
                        deleted += 1
                        logger.debug(f"🗑️  Deleted expired media: {file.name}")
                except Exception as e:
                    logger.error(f"Error deleting {file}: {e}")

        if deleted > 0:
            logger.info(f"🗑️  Cleaned up {deleted} expired media files")

        return deleted

    def _generate_id(self, url: str) -> str:
        """Generate unique ID for URL"""
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def _is_valid_image_url(self, url: str) -> bool:
        """Validate image URL for security"""
        try:
            parsed = urlparse(url)

            # Only HTTPS
            if parsed.scheme != "https":
                return False

            # Check domain whitelist (optional)
            # Comment out to allow all domains
            # if parsed.hostname not in ALLOWED_DOMAINS:
            #     return False

            # Check file extension
            path = parsed.path.lower()
            allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]
            if not any(path.endswith(ext) for ext in allowed_extensions):
                return False

            return True
        except Exception:
            return False

    async def fetch_and_cache(self, url: str) -> Optional[str]:
        """
        Fetch external image and cache it
        Returns media_id on success, None on failure
        """
        # Validate URL
        if not self._is_valid_image_url(url):
            logger.warning(f"Invalid image URL: {url}")
            return None

        # Generate ID
        media_id = self._generate_id(url)

        # Check if already cached
        cached_files = list(MEDIA_DIR.glob(f"{media_id}.*"))
        if cached_files:
            logger.debug(f"✅ Cache hit: {media_id}")
            return media_id

        # Fetch image
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                # Check content type
                content_type = response.headers.get("content-type", "")
                if not content_type.startswith("image/"):
                    logger.warning(f"URL is not an image: {url}")
                    return None

                # Check size
                content_length = len(response.content)
                if content_length > MAX_FILE_SIZE:
                    logger.warning(f"Image too large: {content_length} bytes")
                    return None

                # Process image
                img = Image.open(BytesIO(response.content))

                # Resize if too large
                if img.width > MAX_IMAGE_DIMENSION or img.height > MAX_IMAGE_DIMENSION:
                    img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
                    logger.debug(f"Resized image to {img.width}x{img.height}")

                # Convert to WebP for efficiency
                output_path = MEDIA_DIR / f"{media_id}.webp"
                img.save(output_path, "WEBP", quality=85, optimize=True)

                logger.info(f"✅ Cached media: {media_id} ({content_length} bytes)")
                return media_id

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
        except Exception as e:
            logger.error(f"Error caching {url}: {e}")

        return None

    def get_file(self, media_id: str) -> Optional[Path]:
        """Get cached file by ID"""
        # Find file (any extension)
        files = list(MEDIA_DIR.glob(f"{media_id}.*"))
        if not files:
            return None

        file = files[0]

        # Check if expired
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        if (datetime.now() - mtime).total_seconds() > MEDIA_TTL_SECONDS:
            file.unlink()
            logger.debug(f"🗑️  Expired media: {media_id}")
            return None

        return file

    def delete_file(self, media_id: str) -> bool:
        """Delete cached file"""
        files = list(MEDIA_DIR.glob(f"{media_id}.*"))
        for file in files:
            try:
                file.unlink()
                logger.info(f"🗑️  Deleted media: {media_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting {media_id}: {e}")
        return False

    def save_uploaded_file(self, file_data: bytes, filename: str) -> Optional[str]:
        """
        Save uploaded file (for AI generated images)
        Returns media_id on success
        """
        try:
            # Generate ID from content
            media_id = hashlib.sha256(file_data).hexdigest()[:16]

            # Check if already exists
            cached_files = list(MEDIA_DIR.glob(f"{media_id}.*"))
            if cached_files:
                return media_id

            # Validate and process image
            img = Image.open(BytesIO(file_data))

            # Resize if too large
            if img.width > MAX_IMAGE_DIMENSION or img.height > MAX_IMAGE_DIMENSION:
                img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)

            # Save as WebP
            output_path = MEDIA_DIR / f"{media_id}.webp"
            img.save(output_path, "WEBP", quality=85, optimize=True)

            logger.info(f"✅ Saved uploaded media: {media_id}")
            return media_id

        except Exception as e:
            logger.error(f"Error saving uploaded file: {e}")
            return None

    def get_stats(self) -> dict:
        """Get cache statistics"""
        files = list(MEDIA_DIR.glob("*"))
        files = [f for f in files if f.is_file() and f.suffix != ".gitkeep"]

        total_size = sum(f.stat().st_size for f in files)

        return {
            "total_files": len(files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(MEDIA_DIR),
            "ttl_hours": MEDIA_TTL_SECONDS / 3600,
            "max_size_mb": MAX_FILE_SIZE / (1024 * 1024),
        }

    def extract_urls_from_message(self, content: str) -> List[str]:
        """Extract image URLs from message content"""
        # URL regex
        url_pattern = r"https?://[^\s<>\"{}|\\^`\[\]]+"
        urls = re.findall(url_pattern, content)

        # Filter for image URLs
        image_urls = []
        for url in urls:
            if self._is_valid_image_url(url):
                image_urls.append(url)

        return image_urls


# Global instance
media_cache = MediaCache()


# Cleanup task (run periodically)
async def cleanup_expired_media():
    """Periodic cleanup task"""
    deleted = media_cache.cleanup_old_files()
    if deleted > 0:
        logger.info(f"🗑️  Periodic cleanup: removed {deleted} expired files")
