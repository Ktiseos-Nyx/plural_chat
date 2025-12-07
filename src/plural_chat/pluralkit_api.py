import requests
import json
import time
import re
from urllib.parse import urlparse
from typing import List, Dict, Optional
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler


class PluralKitAPI:
    """PluralKit API integration for member import/sync"""
    
    BASE_URL = "https://api.pluralkit.me/v2"
    
    def __init__(self, token: str = None):
        self.token = token
        self.headers = {"Authorization": token} if token else {}
        self.logger = logging.getLogger('plural_chat.pluralkit_api')
    
    def set_token(self, token: str):
        """Set or update the API token"""
        self.token = token
        self.headers = {"Authorization": token}
    
    def test_connection(self) -> tuple[bool, str]:
        """Test if the API token works"""
        if not self.token:
            return False, "No token provided"
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/systems/@me",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                system_data = response.json()
                system_name = system_data.get("name", "Unnamed System")
                return True, f"Connected to system: {system_name}"
            elif response.status_code == 401:
                return False, "Invalid token"
            elif response.status_code == 403:
                return False, "Token lacks required permissions"
            else:
                return False, f"API error: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
    
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
                return None
                
        except requests.exceptions.RequestException:
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
                return []
                
        except requests.exceptions.RequestException:
            return []
    
    def get_member_by_id(self, member_id: str) -> Optional[Dict]:
        """Get a specific member by their PK ID"""
        if not self.token:
            return None
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/members/{member_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def convert_pk_member_to_local(pk_member: Dict) -> Dict:
        """Convert PluralKit member format to our local format"""
        # Convert proxy tags to JSON string for storage
        proxy_tags = pk_member.get("proxy_tags", [])
        proxy_tags_json = json.dumps(proxy_tags) if proxy_tags else None
        
        return {
            "name": pk_member.get("name", "Unknown"),
            "pronouns": pk_member.get("pronouns"),
            "avatar_path": pk_member.get("avatar_url"),  # We'll download this later
            "color": pk_member.get("color"),
            "description": pk_member.get("description"),
            "pk_id": pk_member.get("id"),
            "proxy_tags": proxy_tags_json
        }
    
    def _validate_avatar_url(self, url: str) -> bool:
        """Validate avatar URL for security (duplicate from main.py for consistency)"""
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            
            # Only allow HTTPS (except for localhost in dev)
            if parsed.scheme not in ['https'] and not (parsed.hostname in ['localhost', '127.0.0.1']):
                return False
            
            # Whitelist trusted domains
            trusted_domains = [
                'cdn.pluralkit.me',
                'media.discordapp.net', 
                'cdn.discordapp.com',
                'i.imgur.com',
                'avatars.githubusercontent.com',
                'localhost',
                '127.0.0.1'
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
    
    def download_avatar(self, avatar_url: str, member_name: str, avatar_dir: str = "avatars") -> Optional[str]:
        """Download avatar image and return local path (WebP compressed)"""
        if not avatar_url:
            return None
        
        # 🔒 SECURITY: Validate URL before downloading
        if not self._validate_avatar_url(avatar_url):
            self.logger.warning(f"Avatar URL failed security validation: {avatar_url}")
            return None
        
        import os
        from PIL import Image
        from io import BytesIO
        
        try:
            # Create avatars directory with secure permissions
            os.makedirs(avatar_dir, exist_ok=True)
            os.chmod(avatar_dir, 0o755)
            
            # 🔒 SECURITY: Create safe filename
            safe_name = self._sanitize_filename(member_name)
            local_filename = f"{safe_name}.webp"
            local_path = os.path.join(avatar_dir, local_filename)
            
            # Skip if already exists
            if os.path.exists(local_path):
                self.logger.info(f"Avatar already exists for {member_name}")
                return local_path
            
            self.logger.info(f"Downloading avatar for {member_name}...")
            
            # Download the image with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.get(avatar_url, timeout=30)
                    if response.status_code == 200:
                        break
                    elif response.status_code == 429:  # Rate limited
                        self.logger.warning(f"Rate limited, waiting 5 seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(5)
                        continue
                    else:
                        self.logger.warning(f"HTTP {response.status_code}, retrying... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(2)
                        continue
                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"Network error: {e}, retrying... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(2)
                    continue
            else:
                self.logger.error(f"Failed to download avatar for {member_name} after {max_retries} attempts")
                return None
            
            if response.status_code == 200:
                # Open image from bytes and convert to WebP
                original_image = Image.open(BytesIO(response.content))
                self.logger.info(f"Downloaded image: {original_image.size} pixels, mode: {original_image.mode}")
                
                # Smart crop to square (center crop like PK does)
                width, height = original_image.size
                if width != height:
                    self.logger.info(f"Cropping from {width}x{height} to square...")
                    # Crop to square from center
                    min_dimension = min(width, height)
                    left = (width - min_dimension) // 2
                    top = (height - min_dimension) // 2
                    right = left + min_dimension
                    bottom = top + min_dimension
                    original_image = original_image.crop((left, top, right, bottom))
                    self.logger.info(f"Cropped to {min_dimension}x{min_dimension}")
                
                # Resize to standard avatar size (256x256 like PK)
                if original_image.size != (256, 256):
                    self.logger.info(f"Resizing from {original_image.size} to 256x256...")
                    original_image = original_image.resize((256, 256), Image.Resampling.LANCZOS)
                
                # Convert to RGB if needed (WebP doesn't support some modes)
                if original_image.mode in ('RGBA', 'LA', 'P'):
                    self.logger.info(f"Converting from {original_image.mode} to RGB...")
                    # Create white background for transparency
                    rgb_image = Image.new('RGB', original_image.size, (255, 255, 255))
                    if original_image.mode == 'P':
                        original_image = original_image.convert('RGBA')
                    if 'transparency' in original_image.info:
                        rgb_image.paste(original_image, mask=original_image.split()[-1])
                        self.logger.info(f"Applied transparency mask")
                    else:
                        rgb_image.paste(original_image)
                    original_image = rgb_image
                elif original_image.mode != 'RGB':
                    self.logger.info(f"Converting from {original_image.mode} to RGB...")
                    original_image = original_image.convert('RGB')
                
                # Save as WebP with 80% quality
                self.logger.info(f"Saving as WebP with 80% quality...")
                original_image.save(local_path, 'WEBP', quality=80, optimize=True)
                
                # Get file size info
                original_size = len(response.content)
                compressed_size = os.path.getsize(local_path)
                savings = ((original_size - compressed_size) / original_size) * 100
                self.logger.info(f"Saved avatar for {member_name} - {original_size//1024}KB → {compressed_size//1024}KB ({savings:.1f}% savings)")
                
                return local_path
            else:
                self.logger.error(f"Failed to download avatar for {member_name}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading avatar for {member_name}: {e}")
            return None


class PluralKitSync:
    """Handles syncing between PluralKit and local database"""
    
    def __init__(self, system_db, app_db):
        self.system_db = system_db
        self.app_db = app_db
        self.api = PluralKitAPI()
        self.logger = logging.getLogger('plural_chat.pluralkit_sync')
    
    def setup_token(self, token: str) -> tuple[bool, str]:
        """Set up and test PluralKit token"""
        self.api.set_token(token)
        success, message = self.api.test_connection()
        
        if success:
            self.app_db.store_api_token("pluralkit", token)
            
            # Store system info
            system_info = self.api.get_system_info()
            if system_info:
                self.system_db.set_system_info("pk_system_id", system_info.get("id", ""))
                self.system_db.set_system_info("system_name", system_info.get("name", "My System"))
                if system_info.get("description"):
                    self.system_db.set_system_info("system_description", system_info["description"])
        
        return success, message
    
    def load_saved_token(self) -> bool:
        """Load previously saved PluralKit token"""
        token = self.app_db.get_api_token("pluralkit")
        if token:
            self.api.set_token(token)
            return True
        return False
    
    def sync_members(self, download_avatars: bool = True) -> tuple[int, int, List[str]]:
        """
        Sync members from PluralKit to local database
        Returns: (new_members, updated_members, errors)
        """
        if not self.load_saved_token():
            return 0, 0, ["No PluralKit token configured"]
        
        # Test connection
        success, message = self.api.test_connection()
        if not success:
            return 0, 0, [f"PluralKit connection failed: {message}"]
        
        # Get members from PK
        pk_members = self.api.get_members()
        if not pk_members:
            return 0, 0, ["No members found or API error"]
        
        new_count = 0
        updated_count = 0
        errors = []
        
        for i, pk_member in enumerate(pk_members):
            try:
                member_name = pk_member.get("name", "Unknown")
                self.logger.info(f"Processing member {i+1}/{len(pk_members)}: {member_name}")
                
                # Add small delay between members to avoid rate limits
                if i > 0 and download_avatars:
                    time.sleep(0.5)  # 500ms delay between avatar downloads
                
                local_member_data = self.api.convert_pk_member_to_local(pk_member)
                pk_id = local_member_data["pk_id"]
                
                # Check if member already exists
                existing_members = self.system_db.get_all_members()
                existing_member = None
                for member in existing_members:
                    if member.get("pk_id") == pk_id or member.get("name") == local_member_data["name"]:
                        existing_member = member
                        break
                
                # Download avatar if requested
                if download_avatars and local_member_data["avatar_path"]:
                    local_avatar_path = self.api.download_avatar(
                        local_member_data["avatar_path"], 
                        local_member_data["name"]
                    )
                    if local_avatar_path:
                        local_member_data["avatar_path"] = local_avatar_path
                    else:
                        local_member_data["avatar_path"] = None
                
                if existing_member:
                    # Update existing member
                    self.system_db.update_member(existing_member["id"], **{
                        k: v for k, v in local_member_data.items() 
                        if k != "name" and v is not None  # Don't update name, avoid overwriting with None
                    })
                    # Update PK ID if it wasn't set
                    if not existing_member.get("pk_id") and pk_id:
                        self.system_db.update_member(existing_member["id"], pk_id=pk_id)
                    updated_count += 1
                else:
                    # Add new member
                    self.system_db.add_member(**local_member_data)
                    new_count += 1
                    
            except Exception as e:
                errors.append(f"Error processing {pk_member.get('name', 'unknown')}: {str(e)}")
        
        # Update sync timestamp
        if new_count > 0 or updated_count > 0:
            self.app_db.update_sync_time("pluralkit")
        
        return new_count, updated_count, errors
    
    def import_full_system(self, download_avatars: bool = True) -> tuple[bool, str, Dict]:
        """
        Full import of PluralKit system (replaces existing data)
        Returns: (success, message, stats)
        """
        if not self.load_saved_token():
            return False, "No PluralKit token configured", {}
        
        # Test connection and get system info
        success, message = self.api.test_connection()
        if not success:
            return False, f"PluralKit connection failed: {message}", {}
        
        system_info = self.api.get_system_info()
        pk_members = self.api.get_members()
        
        if not pk_members:
            return False, "No members found or API error", {}
        
        stats = {
            "members_imported": 0,
            "avatars_downloaded": 0,
            "errors": []
        }
        
        try:
            # Import system info
            if system_info:
                self.system_db.set_system_info("pk_system_id", system_info.get("id", ""))
                self.system_db.set_system_info("system_name", system_info.get("name", "Imported System"))
                if system_info.get("description"):
                    self.system_db.set_system_info("system_description", system_info["description"])
                if system_info.get("tag"):
                    self.system_db.set_system_info("system_tag", system_info["tag"])
            
            # Import members
            for pk_member in pk_members:
                try:
                    local_member_data = self.api.convert_pk_member_to_local(pk_member)
                    
                    # Download avatar if requested
                    if download_avatars and local_member_data["avatar_path"]:
                        local_avatar_path = self.api.download_avatar(
                            local_member_data["avatar_path"], 
                            local_member_data["name"]
                        )
                        if local_avatar_path:
                            local_member_data["avatar_path"] = local_avatar_path
                            stats["avatars_downloaded"] += 1
                        else:
                            local_member_data["avatar_path"] = None
                    
                    self.system_db.add_member(**local_member_data)
                    stats["members_imported"] += 1
                    
                except Exception as e:
                    stats["errors"].append(f"Error importing {pk_member.get('name', 'unknown')}: {str(e)}")
            
            # Update sync timestamp
            self.app_db.update_sync_time("pluralkit")
            
            return True, f"Successfully imported {stats['members_imported']} members", stats
            
        except Exception as e:
            return False, f"Import failed: {str(e)}", stats