
import tkinter as tk
from tkinter import BOTH, X, Y, LEFT, RIGHT, VERTICAL, HORIZONTAL, DISABLED, NORMAL, END, WORD
from tkinter import ttk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
import os
import sys
import requests
import sqlite3
import re
from urllib.parse import urlparse
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import threading
import time
from pathlib import Path
import platformdirs
from functools import wraps

from .member_manager import MemberManager
from .settings_manager import SettingsManager
from PIL import Image, ImageTk
from .database_manager import AppDatabase, SystemDatabase
from .pluralkit_api import PluralKitSync
# Import dialog modules
from .pluralkit_dialog import PluralKitDialog
from .pk_export_parser import PluralKitExportParser
from .about_dialog import AboutDialog
from .help_dialog import HelpDialog
from .diary_dialog import DiaryDialog
from .ui.themes.manager import ThemeManager
from .ui.components.member_list import MemberList

# Loading screen removed - no longer needed since database operations are fast


class PluralChat:
    def __init__(self):
        self.setup_logging()
        self.logger.info("Application started.")

        # Initialize databases
        self.app_db = AppDatabase()
        self.system_db = SystemDatabase()
        self.pk_sync = PluralKitSync(self.system_db, self.app_db)



        # Migrate existing JSON data if needed
        self.migrate_json_data()

        # Get theme setting (fallback to superhero if custom theme fails)
        theme = self.app_db.get_setting('theme', 'superhero')

        # Always start with superhero as base theme for window creation
        fallback_theme = 'superhero'
        # Hide any default tkinter root window
        import tkinter as tk_root
        default_root = tk_root._default_root
        if default_root:
            default_root.withdraw()

        try:
            # Always create window with a known theme first
            self.root = ttk.Window(
                title="Plural Chat",
                themename=fallback_theme,
                size=(900, 700)
            )
        except Exception as e:
            self.logger.error(f"Error creating window: {e}")
            # Ultimate fallback
            self.root = ttk.Window(
                title="Plural Chat",
                themename='superhero',
                size=(900, 700)
            )

        # NEW: Use theme manager
        self.theme_manager = ThemeManager(self.root)

        # Apply saved theme
        saved_theme = self.app_db.get_setting('theme', 'superhero')
        self.theme_manager.apply_theme(saved_theme)
        self.logger.info(f"Using theme: {saved_theme}")
        self.logger.info("Theme manager initialized.")

        # Initialize caches with size limits to prevent memory issues
        self.avatar_cache = {}
        self.thumbnail_cache = {}
        # Get max cache size from settings, default to 100
        self.max_cache_size = int(self.app_db.get_setting('max_avatar_cache_size', '100'))

        # Set minimum size and center the window
        self.root.minsize(800, 600)
        self.root.geometry("900x700")

        # Center the window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Hide window initially while we set it up
        self.root.withdraw()

        # Add a timer for debouncing the input
        self.debounce_timer = None

        # Setup UI and load data
        self.setup_ui()
        self.load_font_settings()  # Load font settings after UI is created

        # Apply the correct theme after UI is created
        # Only apply if it's different from the fallback theme
        if theme != fallback_theme:
            self.change_theme(theme)

        self.load_members()
        self.load_chat_history()

        # Set personalized greeting in status bar
        self.update_status_greeting()

        # Show the main window
        self.root.deiconify()
        # Ensure it's focused and on top
        self.root.lift()
        self.root.focus_force()

    def setup_logging(self, level=logging.INFO):
        self.logger = logging.getLogger('plural_chat')
        log_dir = Path(platformdirs.user_log_dir("PluralChat", "DuskfallCrew"))
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "plural_chat.log"
        handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5) # 10 MB
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(level)

    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=BOTH, expand=True)

        # Top menu bar
        menu_frame = ttk.Frame(main_frame)
        menu_frame.pack(fill=X, pady=(0, 10))

        ttk.Button(menu_frame, text="Settings",
                  command=self.open_settings_manager,
                  bootstyle="info").pack(side=LEFT, padx=(0, 5))

        ttk.Button(menu_frame, text="Export System",
                  command=self.export_system_data,
                  bootstyle="success-outline").pack(side=LEFT, padx=(0, 5))

        ttk.Button(menu_frame, text="Import System",
                  command=self.import_system_data,
                  bootstyle="warning-outline").pack(side=LEFT, padx=(0, 5))

        ttk.Button(menu_frame, text="PluralKit Sync",
                  command=self.show_pluralkit_dialog,
                  bootstyle="secondary-outline").pack(side=LEFT, padx=(0, 5))

        ttk.Button(menu_frame, text="📔 Diary",
                  command=self.show_diary_dialog,
                  bootstyle="primary-outline").pack(side=LEFT, padx=(0, 15))

        # Right side buttons
        ttk.Button(menu_frame, text="About",
                  command=self.show_about_dialog,
                  bootstyle="info-outline").pack(side=RIGHT, padx=(5, 0))

        ttk.Button(menu_frame, text="Help",
                  command=self.show_help_dialog,
                  bootstyle="success-outline").pack(side=RIGHT, padx=(5, 0))

        ttk.Button(menu_frame, text="Exit",
                  command=self.exit_application,
                  bootstyle="danger-outline").pack(side=RIGHT)

        # Content area with paned window
        content_paned = ttk.Panedwindow(main_frame, orient=HORIZONTAL)
        content_paned.pack(fill=BOTH, expand=True, pady=(0, 10))

        # Status bar (needed for components)
        self.status_bar = ttk.Label(self.root, text="Ready", relief="sunken", anchor="w")
        self.status_bar.pack(side=BOTTOM, fill=X)

        # Left panel - Member list
        left_frame = ttk.LabelFrame(content_paned, text="System Members", padding=5)
        content_paned.add(left_frame, weight=1)

        # Instantiate MemberList component
        self.member_list_component = MemberList(
            parent_frame=left_frame,
            logger=self.logger,
            avatar_cache=self.avatar_cache,
            thumbnail_cache=self.thumbnail_cache,
            selection_callback=self.on_member_selected_from_list,
            system_db=self.system_db,
            status_bar=self.status_bar,
            app_db=self.app_db  # Pass database access for settings
        )

        # Right panel - Chat area
        right_frame = ttk.LabelFrame(content_paned, text="Chat History", padding=5)
        content_paned.add(right_frame, weight=3)

        self.chat_history = ttk.Text(right_frame, state=DISABLED, wrap=WORD,
                                    font=("Consolas", 10), height=20)

        # Initialize image references to prevent garbage collection
        self.chat_history.image_references = []

        # Add scrollbar to chat
        chat_scrollbar = ttk.Scrollbar(right_frame, orient=VERTICAL, command=self.chat_history.yview)
        self.chat_history.configure(yscrollcommand=chat_scrollbar.set)

        self.chat_history.pack(side=LEFT, fill=BOTH, expand=True)
        chat_scrollbar.pack(side=RIGHT, fill=Y)

        # Message input area
        input_frame = ttk.LabelFrame(main_frame, text="Send Message", padding=10)
        input_frame.pack(fill=X)

        # Member selector
        selector_header = ttk.Frame(input_frame)
        selector_header.pack(fill=X, pady=(0, 5))

        ttk.Label(selector_header, text="Speaking as:").pack(side=LEFT)

        self.proxy_indicator = ttk.Label(selector_header, text="",
                                        font=("Arial", 8), bootstyle="success")
        self.proxy_indicator.pack(side=RIGHT)

        self.member_var = tk.StringVar()
        self.member_selector = ttk.Combobox(input_frame, textvariable=self.member_var,
                                           state="readonly", width=50)
        self.member_selector.pack(fill=X, pady=(0, 10))
        self.member_selector.bind("<<ComboboxSelected>>", self.on_member_change)

        # Message entry and send button
        message_frame = ttk.Frame(input_frame)
        message_frame.pack(fill=X)

        self.message_entry = ttk.Text(message_frame, height=3, wrap=WORD, font=("Consolas", 10))
        self.message_entry.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self.send_message)  # Enter to send
        self.message_entry.bind("<Control-Return>", self.send_message)  # Ctrl+Enter also works
        self.message_entry.bind("<KeyRelease>", self.on_message_change)  # For live proxy detection

        ttk.Button(message_frame, text="Send",
                  command=self.send_message,
                  bootstyle="primary").pack(side=RIGHT, fill=Y)

    def migrate_json_data(self):
        """Migrate existing JSON data to SQLite (one-time operation)"""
        # Check if migration already done
        if self.system_db.get_system_info("migrated_from_json"):
            return

        # Migrate app settings
        try:
            with open("app_settings.json", 'r') as f:
                app_settings = json.load(f)
                for key, value in app_settings.items():
                    self.app_db.set_setting(key, str(value))
        except FileNotFoundError:
            pass

        # Migrate members
        try:
            with open("members.json", 'r') as f:
                members = json.load(f)
                for member in members:
                    try:
                        self.system_db.add_member(
                            name=member.get("name", ""),
                            pronouns=member.get("pronouns"),
                            avatar_path=member.get("avatar"),
                            description=member.get("description")
                        )
                    except sqlite3.IntegrityError:
                        # Skip duplicates during migration
                        self.logger.warning(f"Skipping duplicate member during migration: {member.get('name', 'Unknown')}")
                        pass
        except FileNotFoundError:
            pass

        # Migrate chat history
        try:
            with open("chat_history.txt", 'r') as f:
                for line in f:
                    try:
                        message_data = json.loads(line.strip())
                        member = self.system_db.get_member_by_name(message_data.get("member", ""))
                        if member:
                            self.system_db.add_message(
                                member_id=member["id"],
                                message=message_data.get("message", ""),
                                timestamp=message_data.get("timestamp", "")
                            )
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass

        # Mark migration as complete
        self.system_db.set_system_info("migrated_from_json", "true")

    def load_members(self):
        self.members = self.system_db.get_all_members()
        # Delegate UI update to the MemberList component
        self.member_list_component.load_members(self.members)
        # Pre-load all local avatars for instant chat display
        self.preload_local_avatars()

    def preload_local_avatars(self):
        """Pre-load all local avatar files into cache for instant chat display"""
        if not hasattr(self, 'avatar_references'):
            self.avatar_references = []

        for member in self.members:
            member_name = member.get('name', 'Unknown')
            avatar_path = member.get('avatar_path', '')

            # Skip if already in cache or no avatar
            if member_name in self.avatar_cache or not avatar_path:
                continue

            # Only load local files (not URLs)
            if not avatar_path.startswith(('http://', 'https://')):
                try:
                    path_to_open = Path(avatar_path)
                    if not path_to_open.is_absolute():
                        # It might be a package resource like 'default_avatar.png'
                        try:
                            from importlib import resources
                            # Use resources.files for modern importlib
                            with resources.as_file(resources.files('plural_chat').joinpath(path_to_open.name)) as p:
                                path_to_open = p
                        except (FileNotFoundError, ModuleNotFoundError):
                            # Or it might be a relative path from the old data structure, now in the user data dir
                            data_dir = Path(platformdirs.user_data_dir("PluralChat", "DuskfallCrew"))
                            path_to_open = data_dir / "avatars" / avatar_path

                    if not Path(path_to_open).exists():
                        self.logger.warning(f"Avatar file not found for {member_name} at {path_to_open}")
                        continue

                    # Load avatar into cache
                    img = Image.open(path_to_open).resize((30, 30), Image.Resampling.LANCZOS)
                    avatar_image = ImageTk.PhotoImage(img)
                    self.avatar_cache[member_name] = avatar_image

                    # Keep reference to prevent garbage collection
                    self.avatar_references.append(avatar_image)
                    
                    # Manage cache size to prevent memory issues
                    self._manage_cache_size(self.avatar_cache, self.max_cache_size)

                    self.logger.info(f"Pre-loaded avatar for {member_name}")

                except Exception as e:
                    self.logger.warning(f"Failed to pre-load avatar for {member_name}: {e}")

    def clear_image_references(self):
        """Safely clear image references to prevent memory leaks"""
        if hasattr(self.chat_history, 'image_references'):
            self.chat_history.image_references.clear()
        else:
            self.chat_history.image_references = []

    def update_status_greeting(self):
        """Update status bar with personalized greeting based on system name and time of day"""
        try:
            # Check if personalized greeting is enabled (default to True for existing users)
            greeting_enabled = self.app_db.get_setting('personalized_greeting', True)

            if not greeting_enabled:
                self.status_bar.config(text="Ready")
                return

            # Get system name from database
            system_name = self.system_db.get_system_info("system_name", "")

            # If no system name, use a generic greeting
            if not system_name or system_name.strip() == "":
                self.status_bar.config(text="Ready")
                return

            # Get current time for time-based greeting
            current_hour = datetime.now().hour

            # Determine time of day
            if 5 <= current_hour < 12:
                time_of_day = "morning"
            elif 12 <= current_hour < 17:
                time_of_day = "afternoon"
            elif 17 <= current_hour < 21:
                time_of_day = "evening"
            else:
                time_of_day = "night"

            # Create personalized greeting
            greeting = f"Hello {system_name}! Having a nice {time_of_day}?"
            self.status_bar.config(text=greeting)

            self.logger.info(f"Status greeting set: {greeting}")

        except Exception as e:
            self.logger.error(f"Error updating status greeting: {e}")
            self.status_bar.config(text="Ready")



    def on_member_change(self, event=None):
        selected_name = self.member_var.get()
        self.current_member = next((m for m in self.members if m['name'] == selected_name), None)

    def on_member_selected_from_list(self, selected_member):
        """Callback from MemberList when a member is selected."""
        self.current_member = selected_member
        self.member_selector.set(selected_member['name'])

    def detect_proxy_member(self, message_text: str) -> tuple:
        """
        Detect if message matches any member's proxy tags
        Returns: (member, cleaned_message) or (None, original_message)
        """
        if not message_text.strip():
            return None, message_text

        for member in self.members:
            proxy_tags_json = member.get('proxy_tags')
            if not proxy_tags_json:
                continue

            try:
                proxy_tags = json.loads(proxy_tags_json)

                for tag in proxy_tags:
                    prefix = tag.get('prefix') or ''
                    suffix = tag.get('suffix') or ''

                    # Debug print
                    self.logger.debug(f"Proxy detection debug: prefix='{prefix}' (type: {type(prefix)}), suffix='{suffix}' (type: {type(suffix)})")

                    # Skip empty tags
                    if not prefix and not suffix:
                        continue

                    # Check if message matches this proxy pattern
                    if (message_text.startswith(prefix) and message_text.endswith(suffix)):
                        # Extract the clean message
                        start_pos = len(prefix)
                        end_pos = len(message_text) - len(suffix) if suffix else len(message_text)

                        if start_pos <= end_pos:
                            clean_message = message_text[start_pos:end_pos].strip()
                            if clean_message:  # Don't match empty messages
                                return member, clean_message

            except json.JSONDecodeError:
                continue

        return None, message_text

    def suggest_proxy_fix(self, message_text: str) -> str:
        """Suggest possible proxy fixes when detection fails"""
        if len(message_text) < 3:  # Too short to be meaningful
            return ""

        # Check if message might be trying to proxy
        suggestions = []

        for member in self.members:
            member_name = member['name']

            # Check if message starts with member name (missing colon)
            if message_text.lower().startswith(member_name.lower()):
                # Check if they forgot the colon
                if len(message_text) > len(member_name) and message_text[len(member_name)] == ' ':
                    suggestions.append(f"💡 Did you mean '{member_name}:' instead of '{member_name}'?")
                    break
                # Check if they used semicolon instead of colon
                elif len(message_text) > len(member_name) and message_text[len(member_name)] == ';':
                    suggestions.append(f"💡 Did you mean '{member_name}:' instead of '{member_name};'?")
                    break

            # Check if they're close to a member name (typo detection)
            elif self.fuzzy_match(message_text.split()[0] if message_text.split() else "", member_name):
                first_word = message_text.split()[0]
                suggestions.append(f"💡 Did you mean '{member_name}:' instead of '{first_word}'?")
                break

        # Check for common proxy patterns that might be malformed
        if ':' in message_text and not suggestions:
            parts = message_text.split(':', 1)
            if len(parts) == 2:
                potential_name = parts[0].strip()
                # Look for members with similar names
                for member in self.members:
                    if self.fuzzy_match(potential_name, member['name']):
                        suggestions.append(f"💡 Did you mean '{member['name']}:' instead of '{potential_name}:'?")
                        break

        return suggestions[0] if suggestions else ""

    def fuzzy_match(self, word1: str, word2: str, threshold: float = 0.7) -> bool:
        """Simple fuzzy matching for typo detection"""
        if not word1 or not word2:
            return False

        # Simple Levenshtein-like distance check
        word1, word2 = word1.lower(), word2.lower()

        # Exact match
        if word1 == word2:
            return True

        # Length difference too large
        if abs(len(word1) - len(word2)) > 2:
            return False

        # Simple character overlap check
        matches = sum(1 for c in word1 if c in word2)
        overlap = matches / max(len(word1), len(word2))

        return overlap >= threshold

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

    def on_message_change(self, event=None):
        """Debounce handler for message text changes."""
        # Cancel any existing timer
        if self.debounce_timer:
            self.root.after_cancel(self.debounce_timer)

        # Start a new timer to call the proxy check after 300ms
        self.debounce_timer = self.root.after(300, self.perform_proxy_check)

    def perform_proxy_check(self):
        """Handle message text changes for live proxy detection after a debounce delay."""
        message_text = self.message_entry.get("1.0", tk.END).strip()

        # Get the default background color from the current theme to properly reset it
        try:
            style = ttk.Style()
            default_bg = style.lookup('TText', 'background')
        except tk.TclError:
            default_bg = 'white' # Fallback for when theme is not fully ready

        if not message_text:
            # Reset everything when empty
            self.proxy_indicator.config(text="")
            self.update_status_greeting()
            self.message_entry.config(bg=default_bg)
            return

        detected_member, clean_message = self.detect_proxy_member(message_text)

        if detected_member:
            # Auto-select the detected member
            self.member_selector.set(detected_member['name'])
            self.current_member = detected_member

            # Show visual feedback
            self.message_entry.config(bg="#e8f5e8")
            self.proxy_indicator.config(text="🔍 Proxy detected")
            self.status_bar.config(text=f"Proxy detected: {detected_member['name']}")
        else:
            # Reset to default
            self.message_entry.config(bg=default_bg)
            self.proxy_indicator.config(text="")

            # Smart proxy suggestions in status bar
            suggestion = self.suggest_proxy_fix(message_text)
            if suggestion:
                self.status_bar.config(text=suggestion)
            else:
                self.update_status_greeting() # Reset to the default greeting

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

            # Create avatars directory if it doesn't exist
            try:
                data_dir = Path(platformdirs.user_data_dir("PluralChat", "DuskfallCrew"))
                avatars_dir = data_dir / "avatars"
                avatars_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Ensured avatars directory exists at {avatars_dir}")
            except Exception as e:
                self.logger.error(f"Failed to create avatars directory: {e}")
                self.status_bar.config(text=f"Error creating avatars directory: {e}")
                return

            # 🔒 SECURITY: Generate safe local filename
            member_id = member.get('id') or member.get('pk_id', 'unknown')
            safe_id = self._sanitize_filename(member_id)
            local_filename = avatars_dir / f"member_{safe_id}.webp"
            self.logger.info(f"Safe local filename: {local_filename}")

            # Skip if already downloaded
            if local_filename.exists():
                self.logger.info(f"Avatar already exists locally")
                # Update database to point to local file if it's still pointing to URL
                if member['avatar_path'].startswith(('http://', 'https://')):
                    self.logger.info(f"Updating database to point to local file")
                    self.system_db.update_member(member['id'], avatar_path=str(local_filename))
                    member['avatar_path'] = str(local_filename)
                return

            self.logger.info(f"Starting download...")
            self.status_bar.config(text=f"Downloading avatar for {member_name}...")

            try:
                # Download the image with better error handling
                response = requests.get(avatar_path, timeout=30)  # Increased timeout
                response.raise_for_status()
                self.logger.info(f"Downloaded {len(response.content)} bytes from server")

                # Open image from bytes and convert to WebP
                from io import BytesIO
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
                self.system_db.update_member(member['id'], avatar_path=str(local_filename))
                member['avatar_path'] = str(local_filename)

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
                    
                    # Manage cache size to prevent memory issues
                    self._manage_cache_size(self.avatar_cache, self.max_cache_size)
                    
                    self.logger.info(f"Avatar cache updated successfully")
                except Exception as cache_e:
                    self.logger.warning(f"Failed to update avatar cache: {cache_e}")

                self.logger.info(f"Downloaded avatar for {member['name']} - {original_size//1024}KB → {compressed_size//1024}KB ({savings:.1f}% savings)")
                self.status_bar.config(text=f"Avatar downloaded for {member['name']} ({savings:.0f}% savings)")

                # Update just this member's entry with the new thumbnail
                if hasattr(self, 'member_list_component'):
                    self.member_list_component.update_single_member_thumbnail(member)

            except requests.exceptions.Timeout:
                self.logger.error(f"Timeout downloading avatar for {member['name']}: {avatar_path}")
                self.status_bar.config(text=f"Timeout downloading avatar for {member['name']}")
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Network error downloading avatar for {member['name']}: {e}")
                self.status_bar.config(text=f"Network error downloading avatar for {member['name']}")
            except IOError as e:
                self.logger.error(f"Image processing error for {member['name']}: {e}")
                self.status_bar.config(text=f"Image processing error for {member['name']}")
            except Exception as e:
                self.logger.error(f"Unexpected error downloading avatar for {member['name']}: {e}")
                self.status_bar.config(text=f"Error downloading avatar for {member['name']}")
        else:
            self.logger.info(f"Avatar is local file or empty, skipping download")
            # But we still need to load local files into the avatar cache!
            avatar_path = member.get('avatar_path', '')
            member_name = member.get('name', 'Unknown')

            if avatar_path and not avatar_path.startswith(('http://', 'https://')):
                try:
                    # Load local avatar into cache if not already there
                    if member_name not in self.avatar_cache:
                        img = Image.open(avatar_path).resize((30, 30), Image.Resampling.LANCZOS)
                        avatar_image = ImageTk.PhotoImage(img)
                        self.avatar_cache[member_name] = avatar_image

                        # Ensure strong reference is kept to prevent garbage collection
                        if not hasattr(self, 'avatar_references'):
                            self.avatar_references = []
                        self.avatar_references.append(avatar_image)
                        
                        # Manage cache size to prevent memory issues
                        self._manage_cache_size(self.avatar_cache, self.max_cache_size)

                        self.logger.info(f"Loaded local avatar for {member_name} into cache")

                        # Update the member list thumbnail too
                        if hasattr(self, 'member_list_component'):
                            self.member_list_component.update_single_member_thumbnail(member)

                except FileNotFoundError:
                    self.logger.warning(f"Avatar file not found for {member_name}: {avatar_path}")
                except IOError as e:
                    self.logger.warning(f"Error loading avatar file for {member_name}: {e}")
                except Exception as e:
                    self.logger.warning(f"Unexpected error loading avatar for {member_name}: {e}")

    def save_members(self):
        # No longer needed - database auto-saves
        pass

    def send_message(self, event=None):
        raw_message = self.message_entry.get("1.0", tk.END).strip()
        if not raw_message:
            return "break" if event else None

        # Check for proxy detection
        detected_member, clean_message = self.detect_proxy_member(raw_message)

        # Use detected member if found, otherwise use current selection
        if detected_member:
            sending_member = detected_member
            message_text = clean_message
        else:
            if not hasattr(self, 'current_member') or not self.current_member:
                messagebox.showwarning("No Member", "Please select a member to speak as.")
                return
            sending_member = self.current_member
            message_text = raw_message

        member_name = sending_member['name']
        member_id = sending_member['id']
        timestamp = datetime.now().strftime("%H:%M")

        # Download avatar if needed (lazy loading)
        self.status_bar.config(text=f"Checking avatar for {member_name}...")
        self.ensure_avatar_downloaded(sending_member)
        self.status_bar.config(text="Ready")

        # Save to database (use the cleaned message)
        self.system_db.add_message(member_id, message_text, timestamp)

        # Display the message
        self.chat_history.config(state=NORMAL)

        # Insert avatar if available
        if member_name in self.avatar_cache:
            try:
                image_to_display = self.avatar_cache[member_name]
                self.chat_history.image_create(tk.END, image=image_to_display, padx=5)
                # Explicitly store a reference on the text widget to prevent garbage collection
                if not hasattr(self.chat_history, 'image_references'):
                    self.chat_history.image_references = []
                self.chat_history.image_references.append(image_to_display)
            except Exception as e:
                self.logger.error(f"Failed to insert avatar for {member_name} in send_message: {e}")
                # Create a simple placeholder if avatar loading fails
                try:
                    placeholder = Image.new('RGB', (30, 30), color='grey')
                    placeholder_image = ImageTk.PhotoImage(placeholder)
                    self.chat_history.image_create(tk.END, image=placeholder_image, padx=5)
                    # Keep both chat and global references
                    if not hasattr(self.chat_history, 'image_references'):
                        self.chat_history.image_references = []
                    self.chat_history.image_references.append(placeholder_image)
                    if not hasattr(self, 'avatar_references'):
                        self.avatar_references = []
                    self.avatar_references.append(placeholder_image)
                except Exception as placeholder_e:
                    self.logger.error(f"Failed to create placeholder for {member_name} in send_message: {placeholder_e}")

        # Insert message with styling (use cleaned message)
        header = f" {member_name} [{timestamp}]\n"
        self.chat_history.insert(tk.END, header, "header")
        self.chat_history.insert(tk.END, f"  {message_text}\n\n")

        # Style the header
        self.chat_history.tag_configure("header", font=("Consolas", 10, "bold"))

        self.chat_history.config(state=DISABLED)
        self.chat_history.see(tk.END)

        # Clear message entry and reset background
        self.message_entry.delete("1.0", tk.END)
        # Reset any custom background - ttk.Text auto-styles with theme, no need to set bg
        # self.message_entry.config(bg='')  # This breaks with empty string!

        # Update member selector if proxy was used
        if detected_member:
            self.member_selector.set(member_name)
            self.current_member = detected_member

        return "break"

    def open_settings_manager(self):
        try:
            settings = SettingsManager(self.root, self)
            # Ensure the dialog is visible and focused
            settings.deiconify()  # Make sure it's not iconified
            settings.lift()       # Bring to front
            settings.focus_set()  # Give it focus
        except Exception as e:
            self.logger.error(f"Error opening settings: {e}")
            messagebox.showerror("Settings Error", f"Failed to open settings: {e}")

    def load_chat_history(self):
        self.chat_history.config(state=NORMAL)
        self.chat_history.delete("1.0", tk.END)

        # Clear any existing image references first
        self.clear_image_references()

        messages = self.system_db.get_messages(limit=1000)
        messages.reverse()  # Show oldest first

        for message in messages:
            self.display_loaded_message(message)

        self.chat_history.config(state=DISABLED)

    def display_loaded_message(self, message_data):
        member_name = message_data.get('member_name', 'Unknown')
        message_text = message_data.get('message', '')
        timestamp = message_data.get('timestamp', '')

        # Insert avatar if available
        if member_name in self.avatar_cache:
            try:
                image_to_display = self.avatar_cache[member_name]
                self.chat_history.image_create(tk.END, image=image_to_display, padx=5)
                # Explicitly store a reference on the text widget to prevent garbage collection
                if not hasattr(self.chat_history, 'image_references'):
                    self.chat_history.image_references = []
                self.chat_history.image_references.append(image_to_display)
                self.logger.debug(f"Inserted avatar for {member_name}")
            except Exception as e:
                self.logger.error(f"Failed to insert avatar for {member_name}: {e}")
                # Create a simple placeholder if avatar loading fails
                try:
                    placeholder = Image.new('RGB', (30, 30), color='grey')
                    placeholder_image = ImageTk.PhotoImage(placeholder)
                    self.chat_history.image_create(tk.END, image=placeholder_image, padx=5)
                    # Keep both chat and global references
                    if not hasattr(self.chat_history, 'image_references'):
                        self.chat_history.image_references = []
                    self.chat_history.image_references.append(placeholder_image)
                    if not hasattr(self, 'avatar_references'):
                        self.avatar_references = []
                    self.avatar_references.append(placeholder_image)
                except Exception as placeholder_e:
                    self.logger.error(f"Failed to create placeholder for {member_name}: {placeholder_e}")

        # Insert message
        header = f" {member_name} [{timestamp}]\n"
        self.chat_history.insert(tk.END, header, "header")
        self.chat_history.insert(tk.END, f"  {message_text}\n\n")

    def show_pluralkit_dialog(self):
        """Show PluralKit integration dialog"""
        dialog = PluralKitDialog(self.root, self.pk_sync, self.refresh_members)
        dialog.show()

    def show_about_dialog(self):
        """Show About dialog"""
        dialog = AboutDialog(self.root)
        dialog.show()

    def show_help_dialog(self):
        """Show Help dialog"""
        HelpDialog(self.root)

    def show_diary_dialog(self):
        """Show Diary dialog"""
        dialog = DiaryDialog(self.root, self.system_db, self.members, self.app_db)
        dialog.show()

    def exit_application(self):
        """Exit the application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit Plural Chat?"):
            self.root.quit()

    def refresh_members(self):
        """Refresh member list after PluralKit sync"""
        # Clear avatar cache to prevent memory buildup during refresh
        if hasattr(self, 'avatar_cache'):
            self.avatar_cache.clear()
        if hasattr(self, 'avatar_references'):
            self.avatar_references.clear()
        
        self.load_members()
        # After refreshing members, ensure the member selector is updated
        member_names = [member['name'] for member in self.members]
        self.member_selector['values'] = member_names
        if member_names and self.current_member and self.current_member['name'] in member_names:
            self.member_selector.set(self.current_member['name'])
        elif member_names:
            self.member_selector.set(member_names[0])
            self.current_member = self.members[0]
        else:
            self.member_selector.set("")
            self.current_member = None

        # Update personalized greeting with new system name
        self.update_status_greeting()

    def get_theme_name(self):
        return self.app_db.get_setting('theme', 'superhero')

    def get_theme_mode(self):
        return "N/A"  # ttkbootstrap doesn't have separate modes

    def change_theme(self, theme_name, mode=None):
        """MUCH SIMPLER now!"""
        success = self.theme_manager.apply_theme(theme_name)
        if success:
            self.app_db.set_setting('theme', theme_name)
            self.status_bar.config(text=f"✨ Theme changed to {theme_name}")
        else:
            self.status_bar.config(text=f"❌ Failed to apply theme {theme_name}")

    def force_theme_override(self):
        """Force all widgets to ignore macOS appearance and use ttkbootstrap theme only"""
        try:
            # Override common widget types that might fall back to system theme
            style = self.root.style

            # Force all text widgets to use theme colors, not system
            # This should prevent any macOS dark/light mode interference
            current_theme = style.theme_use()

            # Get theme colors
            theme_bg = style.lookup('TLabel', 'background') or '#ffffff'
            theme_fg = style.lookup('TLabel', 'foreground') or '#000000'

            # Force configure all widget types
            widget_types = ['TFrame', 'TLabel', 'TButton', 'TEntry', 'TText',
                           'TCombobox', 'TLabelFrame', 'Treeview', 'TNotebook', 'TLabelFrame.Label']

            for widget_type in widget_types:
                try:
                    style.configure(widget_type, background=theme_bg, foreground=theme_fg)
                except:
                    pass  # Some widget types might not support all options

            # NUCLEAR OPTION: Force the specific problematic widgets
            try:
                # Force the main window background
                self.root.configure(bg=theme_bg)

                # Force the member list specifically
                if hasattr(self, 'member_list'):
                    style.configure('Treeview', background=theme_bg, foreground=theme_fg, fieldbackground=theme_bg)
                    self.member_list.configure(style='Treeview')

                # Force LabelFrame backgrounds (like "System Members", "Chat History")
                style.configure('TLabelFrame', background=theme_bg, foreground=theme_fg)
                style.configure('TLabelFrame.Label', background=theme_bg, foreground=theme_fg)

            except Exception as e:
                self.logger.error(f"Nuclear option failed: {e}")

            self.logger.info(f"Forced theme override with bg={theme_bg}, fg={theme_fg}")

        except Exception as e:
            self.logger.error(f"Error forcing theme override: {e}")

    def apply_font_settings(self, font_family, font_size):
        """Apply font settings to all text components"""
        try:
            # Update chat history
            self.chat_history.config(font=(font_family, font_size))

            # Update message entry
            self.message_entry.config(font=(font_family, font_size))

            # Update status bar
            self.status_bar.config(text=f"✨ Font changed to {font_family} {font_size}pt")

            self.logger.info(f"Font changed to {font_family} {font_size}pt")

        except Exception as e:
            self.logger.error(f"Error applying font settings: {e}")
            self.status_bar.config(text="❌ Error applying font settings")

    def load_font_settings(self):
        """Load and apply saved font settings"""
        try:
            font_family = self.app_db.get_setting('font_family', 'Consolas')
            font_size = int(self.app_db.get_setting('font_size', '10'))

            # Apply to UI components
            self.apply_font_settings(font_family, font_size)

        except Exception as e:
            self.logger.error(f"Error loading font settings: {e}")
            # Use defaults
            self.apply_font_settings('Consolas', 10)

    def get_theme_name(self):
        """Get the current theme name"""
        return self.app_db.get_setting('theme', 'superhero')

    def export_system_data(self):
        # Export using the database
        export_data = self.system_db.export_to_dict()

        # Add theme settings
        export_data["theme_settings"] = {
            "theme": self.app_db.get_setting('theme', 'superhero')
        }

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export System Data"
        )

        if filename:
            try:
                with open(filename, "w", encoding='utf-8') as f:
                    json.dump(export_data, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Export Complete", f"System data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {e}")

    def import_system_data(self):
        if messagebox.askyesno("Import Warning",
                              "Importing will replace your current system data. Continue?"):
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Import System Data"
            )

            if filename:
                try:
                    # Use the smart parser to handle different formats
                    parser = PluralKitExportParser()
                    import_data = parser.parse_export_file(filename)

                    # Import system data using database
                    self.system_db.import_from_dict(import_data)

                    # Import theme settings if available
                    if "theme_settings" in import_data:
                        theme = import_data["theme_settings"].get("theme", "superhero")
                        self.app_db.set_setting('theme', theme)
                        # Apply the imported theme immediately
                        self.change_theme(theme)

                    # Refresh UI
                    self.load_members()
                    self.load_chat_history()

                    # Update personalized greeting with new system name
                    self.update_status_greeting()

                    # Force theme refresh after UI rebuild
                    current_theme = self.get_theme_name()
                    self.change_theme(current_theme)

                    # Show import stats
                    member_count = len(import_data.get("members", []))
                    message_count = len(import_data.get("messages", []))
                    source = import_data.get("system_info", {}).get("imported_from", "unknown")

                    messagebox.showinfo("Import Complete",
                                       f"Successfully imported from {source}!\n\n"
                                       f"Members: {member_count}\n"
                                       f"Messages: {message_count}")

                except Exception as e:
                    messagebox.showerror("Import Error", f"Failed to import: {e}\n\n"
                                       f"Supported formats:\n"
                                       f"- PluralKit exports\n"
                                       f"- Our own export format")

    def _manage_cache_size(self, cache_dict, max_size=None):
        """Remove oldest entries from cache if it exceeds max_size"""
        # If max_size is not provided, get from settings
        if max_size is None:
            max_size = int(self.app_db.get_setting('max_avatar_cache_size', '100'))
        
        if len(cache_dict) > max_size and max_size > 0:  # Only manage size if limit > 0
            # Remove oldest entries (first ones added) - this is approximate since dict order is insertion order
            excess = len(cache_dict) - max_size
            keys_to_remove = list(cache_dict.keys())[:excess]
            for key in keys_to_remove:
                del cache_dict[key]

    def retry_on_failure(self, max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
        """
        Retry decorator for network operations
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                current_delay = delay
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == max_retries - 1:  # Last attempt
                            self.logger.error(f"Function {func.__name__} failed after {max_retries} attempts: {e}")
                            raise e
                        self.logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                return None
            return wrapper
        return decorator

    def run(self):
        self.root.mainloop()


def main():
    app = PluralChat()
    app.run()


if __name__ == "__main__":
    main()
