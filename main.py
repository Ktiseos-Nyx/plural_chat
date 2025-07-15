
import tkinter as tk
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

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from member_manager import MemberManager
from settings_manager import SettingsManager
from PIL import Image, ImageTk
from database_manager import AppDatabase, SystemDatabase
from pluralkit_api import PluralKitSync
# Import dialog modules
from pluralkit_dialog import PluralKitDialog
from pk_export_parser import PluralKitExportParser
from about_dialog import AboutDialog
from help_dialog import HelpDialog
from diary_dialog import DiaryDialog
from custom_themes import register_custom_themes, get_custom_theme_names, is_custom_theme, apply_custom_theme


# Loading screen removed - no longer needed since database operations are fast

class PluralChat:
    def __init__(self):
        self.setup_logging()
        self.logger.info("Application started.")

        # Initialize databases
        self.app_db = AppDatabase()
        self.system_db = SystemDatabase()
        self.pk_sync = PluralKitSync(self.system_db, self.app_db)
        
        # Register custom themes BEFORE creating window
        register_custom_themes()
        
        # Migrate existing JSON data if needed
        self.migrate_json_data()
        
        # Get theme setting (fallback to superhero if custom theme fails)
        theme = self.app_db.get_setting('theme', 'superhero')
        
        # If it's a custom theme, make sure it's properly loaded
        if is_custom_theme(theme):
            print(f"🎨 Attempting to use custom theme: {theme}")
            # Try to use superhero as base if custom theme fails
            fallback_theme = 'superhero'
        else:
            fallback_theme = theme
        try:
            # Always create window with a known theme first
            self.root = ttk.Window(
                title="Plural Chat",
                themename=fallback_theme,
                size=(900, 700)
            )
        except Exception as e:
            print(f"❌ Error creating window: {e}")
            # Ultimate fallback
            self.root = ttk.Window(
                title="Plural Chat",
                themename='superhero',
                size=(900, 700)
            )
        # Hide window initially while we set it up
        self.root.withdraw()
        
        self.avatar_cache = {}
        self.avatar_references = []  # Keep references to prevent garbage collection
        self.current_member = None
        
        # Setup UI and load data
        self.setup_ui()
        self.load_font_settings()  # Load font settings after UI is created
        
        # Apply custom theme after UI is created
        if is_custom_theme(theme):
            print(f"🎨 Applying custom theme after UI setup: {theme}")
            self.change_theme(theme)
        
        self.load_members()
        self.load_chat_history()
        
        # Show the main window
        self.root.deiconify()
        # Ensure it's focused and on top
        self.root.lift()
        self.root.focus_force()

    def setup_logging(self, level=logging.INFO):
        self.logger = logging.getLogger('plural_chat')
        log_file = os.path.join(os.path.dirname(__file__), 'logs', 'plural_chat.log')
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
        content_paned = ttk.PanedWindow(main_frame, orient=HORIZONTAL)
        content_paned.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Left panel - Member list
        left_frame = ttk.LabelFrame(content_paned, text="System Members", padding=5)
        content_paned.add(left_frame, weight=1)
        
        # Create Treeview for member list with thumbnail support
        self.member_list = ttk.Treeview(left_frame, height=20, show='tree')
        self.member_list.column('#0', width=200, anchor='w')
        self.member_list.pack(fill=BOTH, expand=True)
        
        # Cache for thumbnail images - store references to prevent garbage collection
        self.thumbnail_cache = {}
        self.thumbnail_references = []  # Keep references to prevent garbage collection
        
        # Bind selection event for member list
        self.member_list.bind('<<TreeviewSelect>>', self.on_member_list_select)
        
        # Right panel - Chat area
        right_frame = ttk.LabelFrame(content_paned, text="Chat History", padding=5)
        content_paned.add(right_frame, weight=3)
        
        self.chat_history = tk.Text(right_frame, state=DISABLED, wrap=WORD, 
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
                                        font=("Arial", 8), foreground="green")
        self.proxy_indicator.pack(side=RIGHT)
        
        self.member_var = tk.StringVar()
        self.member_selector = ttk.Combobox(input_frame, textvariable=self.member_var, 
                                           state="readonly", width=50)
        self.member_selector.pack(fill=X, pady=(0, 10))
        self.member_selector.bind("<<ComboboxSelected>>", self.on_member_change)
        
        # Message entry and send button
        message_frame = ttk.Frame(input_frame)
        message_frame.pack(fill=X)
        
        self.message_entry = tk.Text(message_frame, height=3, wrap=WORD, font=("Consolas", 10))
        self.message_entry.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self.send_message)  # Enter to send
        self.message_entry.bind("<Control-Return>", self.send_message)  # Ctrl+Enter also works
        self.message_entry.bind("<KeyRelease>", self.on_message_change)  # For live proxy detection
        
        ttk.Button(message_frame, text="Send", 
                  command=self.send_message, 
                  bootstyle="primary").pack(side=RIGHT, fill=Y)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief="sunken", anchor="w")
        self.status_bar.pack(side=BOTTOM, fill=X)

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
        self.load_avatars()
        self.update_member_ui()
    
    def clear_image_references(self):
        """Safely clear image references to prevent memory leaks"""
        if hasattr(self.chat_history, 'image_references'):
            self.chat_history.image_references.clear()
        else:
            self.chat_history.image_references = []

    def load_avatars(self):
        for member in self.members:
            member_name = member['name']
            avatar_path = member.get('avatar_path', '')

            if member_name not in self.avatar_cache:
                try:
                    if avatar_path and os.path.exists(avatar_path):
                        img = Image.open(avatar_path).resize((30, 30), Image.Resampling.LANCZOS)
                        avatar_image = ImageTk.PhotoImage(img)
                        self.avatar_cache[member_name] = avatar_image
                        self.avatar_references.append(avatar_image)  # Keep reference
                        self.logger.debug(f"Loaded avatar for {member_name}")
                    else:
                        # Create a simple colored placeholder
                        self.logger.info(f"No valid avatar found for {member_name}, creating placeholder.")
                        placeholder = Image.new('RGB', (30, 30), color='grey')
                        placeholder_image = ImageTk.PhotoImage(placeholder)
                        self.avatar_cache[member_name] = placeholder_image
                        self.avatar_references.append(placeholder_image)  # Keep reference
                except (FileNotFoundError, IOError) as e:
                    self.logger.warning(f"Error loading avatar for {member_name} from {avatar_path}: {e}. Creating placeholder.")
                    # Create a simple colored placeholder as fallback
                    try:
                        placeholder = Image.new('RGB', (30, 30), color='grey')
                        placeholder_image = ImageTk.PhotoImage(placeholder)
                        self.avatar_cache[member_name] = placeholder_image
                        self.avatar_references.append(placeholder_image)  # Keep reference
                    except Exception as placeholder_e:
                        self.logger.error(f"Failed to create placeholder for {member_name}: {placeholder_e}")
                        # If even placeholder creation fails, skip this member
                        continue
                except Exception as e:
                    self.logger.error(f"Unexpected error loading avatar for {member_name}: {e}")
                    # Try to create a placeholder as last resort
                    try:
                        placeholder = Image.new('RGB', (30, 30), color='grey')
                        placeholder_image = ImageTk.PhotoImage(placeholder)
                        self.avatar_cache[member_name] = placeholder_image
                        self.avatar_references.append(placeholder_image)  # Keep reference
                    except Exception as placeholder_e:
                        self.logger.error(f"Failed to create placeholder for {member_name}: {placeholder_e}")
                        # If even placeholder creation fails, skip this member
                        continue

    def update_member_ui(self):
        # Update member treeview
        for item in self.member_list.get_children():
            self.member_list.delete(item)
        
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
                self.member_list.insert('', 'end', iid=f"member_{i}", text=display_name)
            else:
                # No avatar
                self.member_list.insert('', 'end', iid=f"member_{i}", text=name)
        
        # Update combobox (use clean names without icons)
        member_names = [member['name'] for member in self.members]
        self.member_selector['values'] = member_names
        if member_names:
            self.member_selector.set(member_names[0])
            self.current_member = self.members[0]
    
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
            self.member_list.insert('', 'end', iid=f"member_{index}", 
                                  text=f"  {name}", image=thumbnail)
            
        except Exception as e:
            self.logger.error(f"Failed to create thumbnail for {name}: {e}")
            # Fallback to emoji placeholder
            display_name = f"🖼️ {name}"
            self.member_list.insert('', 'end', iid=f"member_{index}", text=display_name)
    
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
            if self.member_list.exists(member_iid):
                self.member_list.delete(member_iid)
            
            # Re-add with thumbnail
            self.add_member_with_thumbnail(member['name'], member['avatar_path'], member_index)

    def on_member_change(self, event=None):
        selected_name = self.member_var.get()
        self.current_member = next((m for m in self.members if m['name'] == selected_name), None)
    
    def on_member_list_select(self, event=None):
        """Handle member selection from the treeview list"""
        selection = self.member_list.selection()
        if selection:
            # Extract member index from the iid
            member_iid = selection[0]
            if member_iid.startswith('member_'):
                member_index = int(member_iid.split('_')[1])
                if 0 <= member_index < len(self.members):
                    self.current_member = self.members[member_index]
                    # Update the combobox to match
                    self.member_selector.set(self.current_member['name'])

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
        """Handle message text changes for live proxy detection"""
        message_text = self.message_entry.get("1.0", tk.END).strip()
        
        if not message_text:
            # Reset everything when empty
            self.message_entry.config(bg="white")
            self.proxy_indicator.config(text="")
            self.status_bar.config(text="Ready")
            return
        
        detected_member, clean_message = self.detect_proxy_member(message_text)
        
        if detected_member:
            # Auto-select the detected member
            self.member_selector.set(detected_member['name'])
            self.current_member = detected_member
            
            # Show visual feedback
            self.message_entry.config(bg="#e8f5e8")  # Light green background
            self.proxy_indicator.config(text="🔍 Proxy detected")
            self.status_bar.config(text=f"Proxy detected: {detected_member['name']}")
        else:
            # Reset to default
            self.message_entry.config(bg="white")
            self.proxy_indicator.config(text="")
            
            # Smart proxy suggestions in status bar
            suggestion = self.suggest_proxy_fix(message_text)
            if suggestion:
                self.status_bar.config(text=suggestion)
            else:
                self.status_bar.config(text="Ready")

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
                self.system_db.update_member(member['id'], avatar_path=local_filename)
                member['avatar_path'] = local_filename
                
                # Refresh avatar cache
                self.logger.info(f"Refreshing UI avatar cache...")
                if member['name'] in self.avatar_cache:
                    del self.avatar_cache[member['name']]
                try:
                    img = Image.open(local_filename).resize((30, 30), Image.Resampling.LANCZOS)
                    self.avatar_cache[member['name']] = ImageTk.PhotoImage(img)
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
                    if not hasattr(self.chat_history, 'image_references'):
                        self.chat_history.image_references = []
                    self.chat_history.image_references.append(placeholder_image)
                except Exception as placeholder_e:
                    self.logger.error(f"Failed to create placeholder for {member_name} in send_message: {placeholder_e}")
        
        # Insert message with styling (use cleaned message)
        header = f" {member_name} [{timestamp}]\n"
        self.chat_history.insert(tk.END, header, "header")
        self.chat_history.insert(tk.END, f"  {message_text}\n\n")
        
        # Style the header
        self.chat_history.tag_configure("header", font=("Consolas", 10, "bold"), 
                                       foreground="#66d9ff")
        
        self.chat_history.config(state=DISABLED)
        self.chat_history.see(tk.END)
        
        # Clear message entry and reset background
        self.message_entry.delete("1.0", tk.END)
        self.message_entry.config(bg="white")
        
        # Update member selector if proxy was used
        if detected_member:
            self.member_selector.set(member_name)
            self.current_member = detected_member
        
        return "break"

    def open_settings_manager(self):
        SettingsManager(self.root, self)

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
                    if not hasattr(self.chat_history, 'image_references'):
                        self.chat_history.image_references = []
                    self.chat_history.image_references.append(placeholder_image)
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
        self.load_members()

    def get_theme_name(self):
        return self.app_db.get_setting('theme', 'superhero')
    
    def get_theme_mode(self):
        return "N/A"  # ttkbootstrap doesn't have separate modes
    
    def change_theme(self, theme_name, mode=None):
        """Change theme instantly without restart"""
        try:
            # Check if it's a custom theme
            if is_custom_theme(theme_name):
                # Apply custom theme manually
                success = apply_custom_theme(theme_name, self.root.style)
                if success:
                    self.status_bar.config(text=f"✨ Custom theme {theme_name} applied")
                else:
                    self.status_bar.config(text=f"⚠️  Custom theme {theme_name} partially applied")
            else:
                # Apply built-in theme
                self.root.style.theme_use(theme_name)
                self.status_bar.config(text=f"✨ Theme changed to {theme_name}")
            
            # Save the setting
            self.app_db.set_setting('theme', theme_name)
            
        except Exception as e:
            self.logger.error(f"Error changing theme: {e}")
            # Try fallback to superhero theme
            try:
                self.root.style.theme_use('superhero')
                self.status_bar.config(text=f"❌ Theme error, reverted to superhero")
            except:
                self.status_bar.config(text="❌ Error changing theme")
    
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
                    
                    # Refresh UI
                    self.load_members()
                    self.load_chat_history()
                    
                    # Show import stats
                    member_count = len(import_data.get("members", []))
                    message_count = len(import_data.get("messages", []))
                    source = import_data.get("system_info", {}).get("imported_from", "unknown")
                    
                    messagebox.showinfo("Import Complete", 
                                       f"Successfully imported from {source}!\n\n"
                                       f"Members: {member_count}\n"
                                       f"Messages: {message_count}\n\n"
                                       f"Restart the app to see theme changes.")
                    
                except Exception as e:
                    messagebox.showerror("Import Error", f"Failed to import: {e}\n\n"
                                       f"Supported formats:\n"
                                       f"- PluralKit exports\n"
                                       f"- Our own export format")

    def run(self):
        self.root.mainloop()


def main():
    app = PluralChat()
    app.run()


if __name__ == "__main__":
    main()
