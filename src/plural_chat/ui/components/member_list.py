import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, VERTICAL, HORIZONTAL, DISABLED, NORMAL, END, WORD
from PIL import Image, ImageTk
import logging
import os
import requests
import re
from urllib.parse import urlparse
from io import BytesIO

class MemberList:
    def __init__(self, parent_frame, logger, avatar_cache, thumbnail_cache, selection_callback, system_db, status_bar):
        self.parent_frame = parent_frame
        self.logger = logger
        self.avatar_cache = avatar_cache
        self.thumbnail_cache = thumbnail_cache
        self.selection_callback = selection_callback
        self.system_db = system_db
        self.status_bar = status_bar
        self.members = [] # This will be populated by load_members

        self.thumbnail_references = [] # Keep references to prevent garbage collection

        self.setup_ui()

    def setup_ui(self):
        # Create Treeview for member list with thumbnail support
        self.tree = ttk.Treeview(self.parent_frame, height=20, show='tree')
        self.tree.column('#0', width=200, anchor='w')
        self.tree.pack(fill=BOTH, expand=True)

        # Bind selection event for member list
        self.tree.bind('<<TreeviewSelect>>', self.on_member_list_select)

    def load_members(self, members_list):
        """Load members into the list and update the UI."""
        self.members = members_list

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Populate with new members
        for i, member in enumerate(self.members):
            name = member['name']
            avatar_path = member.get('avatar_path', '')

            # Create list item with avatar thumbnail or placeholder
            if avatar_path and not avatar_path.startswith(('http://', 'https://')):
                # Avatar is downloaded - show thumbnail
                self.add_member_with_thumbnail(name, avatar_path, i)
            elif avatar_path and avatar_path.startswith(('http://', 'https://')):
                # Avatar URL exists but not downloaded - show emoji placeholder
                display_name = f"🖼️ {name}"
                self.tree.insert('', 'end', iid=f"member_{i}", text=display_name)
            else:
                # No avatar
                self.tree.insert('', 'end', iid=f"member_{i}", text=name)

    def add_member_with_thumbnail(self, name, avatar_path, index):
        """Add member to treeview with actual thumbnail image"""
        try:
            # Check cache first
            cache_key = f"{name}_{avatar_path}"
            if cache_key in self.thumbnail_cache:
                thumbnail = self.thumbnail_cache[cache_key]
            else:
                # Create small thumbnail (20x20) for the list
                img = Image.open(avatar_path)
                img = img.resize((20, 20), Image.Resampling.LANCZOS)
                thumbnail = ImageTk.PhotoImage(img)
                self.thumbnail_cache[cache_key] = thumbnail
                # Store reference to prevent garbage collection
                self.thumbnail_references.append(thumbnail)

            # Add to treeview with thumbnail image
            self.tree.insert('', 'end', iid=f"member_{index}",
                                  text=f"  {name}", image=thumbnail)

        except Exception as e:
            self.logger.error(f"Failed to create thumbnail for {name}: {e}")
            # Fallback to emoji placeholder
            display_name = f"🖼️ {name}"
            self.tree.insert('', 'end', iid=f"member_{index}", text=display_name)

    def update_single_member_thumbnail(self, member):
        """Update just one member's thumbnail in the list"""
        # Find the member's index
        member_index = None
        for i, m in enumerate(self.members):
            if m['name'] == member['name']:
                member_index = i
                break

        if member_index is not None:
            # Update just this member's entry
            member_iid = f"member_{member_index}"
            if self.tree.exists(member_iid):
                self.tree.delete(member_iid)

            # Re-add with thumbnail
            self.add_member_with_thumbnail(member['name'], member['avatar_path'], member_index)

    def on_member_list_select(self, event=None):
        """Handle member selection from the treeview list"""
        selection = self.tree.selection()
        if selection:
            # Extract member index from the iid
            member_iid = selection[0]
            if member_iid.startswith('member_'):
                member_index = int(member_iid.split('_')[1])
                if 0 <= member_index < len(self.members):
                    selected_member = self.members[member_index]
                    # Call the callback to notify the parent (main app)
                    if self.selection_callback:
                        self.selection_callback(selected_member)

    def get_selected_member(self):
        """Returns the currently selected member object or None"""
        selection = self.tree.selection()
        if selection:
            member_iid = selection[0]
            if member_iid.startswith('member_'):
                member_index = int(member_iid.split('_')[1])
                if 0 <= member_index < len(self.members):
                    return self.members[member_index]
        return None

    def set_selected_member(self, member_name):
        """Selects a member in the treeview by name"""
        for i, member in enumerate(self.members):
            if member['name'] == member_name:
                member_iid = f"member_{i}"
                self.tree.selection_set(member_iid)
                self.tree.see(member_iid) # Scroll to it
                return

    def _validate_avatar_url(self, url: str) -> bool:
        """Validate avatar URL for security"""
        if not url:
            return False

        try:
            parsed = urlparse(url)

            # Only allow HTTPS (except for localhost in dev)
            if parsed.scheme not in ['https'] and not (parsed.hostname in ['localhost', '127.0.0.1']):
                self.logger.warning(f"Rejected non-HTTPS URL: {url}")
                return False

            # Whitelist trusted domains
            trusted_domains = [
                'cdn.pluralkit.me',
                'media.discordapp.net',
                'cdn.discordapp.com',
                'i.imgur.com',
                'avatars.githubusercontent.com',
                'localhost',  # For development
                '127.0.0.1'   # For development
            ]

            if parsed.hostname not in trusted_domains:
                self.logger.warning(f"Rejected untrusted domain: {parsed.hostname}")
                return False

            # Check file extension
            path = parsed.path.lower()
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            if not any(path.endswith(ext) for ext in allowed_extensions):
                self.logger.warning(f"Rejected invalid file type: {path}")
                return False

            self.logger.info(f"URL validation passed: {url}")
            return True

        except Exception as e:
            self.logger.error(f"URL validation error: {e}")
            return False

    def _sanitize_filename(self, member_id: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove any path separators and special characters
        safe_id = re.sub(r'[^\w\-_]', '_', str(member_id))
        # Limit length
        safe_id = safe_id[:50]
        # Ensure it's not empty
        if not safe_id:
            safe_id = "unknown"
        return safe_id

    def ensure_avatar_downloaded(self, member):
        """Download and cache avatar if it's a URL and not already downloaded"""
        avatar_path = member.get('avatar_path', '')
        member_name = member.get('name', 'Unknown')

        self.logger.info(f"Checking avatar for {member_name}: {avatar_path[:50]}..." if len(avatar_path) > 50 else f"Checking avatar for {member_name}: {avatar_path}")

        # Check if it's a URL that needs downloading
        if avatar_path and avatar_path.startswith(('http://', 'https://')):
            self.logger.info(f"Avatar is a URL, processing...")

            # 🔒 SECURITY: Validate URL before downloading
            if not self._validate_avatar_url(avatar_path):
                self.logger.warning(f"Avatar URL failed security validation for {member_name}")
                self.status_bar.config(text=f"🚫 Blocked unsafe avatar URL for {member_name}")
                return

            # Create avatars directory if it doesn't exist with secure permissions
            avatars_dir = 'avatars'
            os.makedirs(avatars_dir, exist_ok=True)
            os.chmod(avatars_dir, 0o755)  # Secure directory permissions
            self.logger.info(f"Ensured avatars directory exists")

            # 🔒 SECURITY: Generate safe local filename
            member_id = member.get('id') or member.get('pk_id', 'unknown')
            safe_id = self._sanitize_filename(member_id)
            local_filename = f"avatars/member_{safe_id}.webp"
            self.logger.info(f"Safe local filename: {local_filename}")

            # Skip if already downloaded
            if os.path.exists(local_filename):
                self.logger.info(f"Avatar already exists locally")
                # Update database to point to local file if it's still pointing to URL
                if member['avatar_path'].startswith(('http://', 'https://')):
                    self.logger.info(f"Updating database to point to local file")
                    self.system_db.update_member(member['id'], avatar_path=local_filename)
                    member['avatar_path'] = local_filename
                return

            self.logger.info(f"Starting download...")
            self.status_bar.config(text=f"Downloading avatar for {member_name}...")

            try:
                # Download the image
                response = requests.get(avatar_path, timeout=10)
                response.raise_for_status()
                self.logger.info(f"Downloaded {len(response.content)} bytes from server")

                # Open image from bytes and convert to WebP
                original_image = Image.open(BytesIO(response.content))
                self.logger.info(f"Opened image: {original_image.size} pixels, mode: {original_image.mode}")

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
                else:
                    self.logger.info(f"Image already in RGB mode")

                # Save as WebP with 80% quality
                self.logger.info(f"Saving as WebP with 80% quality...")
                original_image.save(local_filename, 'WEBP', quality=80, optimize=True)

                # Get file size info
                original_size = len(response.content)
                compressed_size = os.path.getsize(local_filename)
                savings = ((original_size - compressed_size) / original_size) * 100
                self.logger.info(f"Compression stats: {original_size} → {compressed_size} bytes")

                # Update database to point to local file
                self.logger.info(f"Updating database with local path...")
                self.system_db.update_member(member['id'], avatar_path=local_filename)
                member['avatar_path'] = local_filename

                # Refresh avatar cache
                self.logger.info(f"Refreshing UI avatar cache...")
                if member['name'] in self.avatar_cache:
                    del self.avatar_cache[member['name']]
                try:
                    img = Image.open(local_filename).resize((30, 30), Image.Resampling.LANCZOS)
                    avatar_image = ImageTk.PhotoImage(img)
                    self.avatar_cache[member['name']] = avatar_image
                    # Ensure strong reference is kept to prevent garbage collection
                    if not hasattr(self, 'avatar_references'):
                        self.avatar_references = []
                    self.avatar_references.append(avatar_image)
                    self.logger.info(f"Avatar cache updated successfully")
                except Exception as cache_e:
                    self.logger.warning(f"Failed to update avatar cache: {cache_e}")

                self.logger.info(f"Downloaded avatar for {member['name']} - {original_size//1024}KB → {compressed_size//1024}KB ({savings:.1f}% savings)")
                self.status_bar.config(text=f"Avatar downloaded for {member['name']} ({savings:.0f}% savings)")

                # Update just this member's entry with the new thumbnail
                self.update_single_member_thumbnail(member)

            except Exception as e:
                self.logger.error(f"Failed to download avatar for {member['name']}: {e}")
                self.status_bar.config(text=f"Failed to download avatar for {member['name']}")
        else:
            self.logger.info(f"Avatar is local file or empty, skipping download")
