import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import webbrowser
try:
    from tkinter import html
except ImportError:
    html = None
import logging
from logging.handlers import RotatingFileHandler

class HelpDialog:
    def __init__(self, parent):
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title("Plural Chat - Help")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.logger = logging.getLogger('plural_chat.help_dialog')
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"800x600+{x}+{y}")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Plural Chat Help", 
                               font=("Arial", 16, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Create notebook for different help sections
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Getting Started tab
        self.create_getting_started_tab(notebook)
        
        # Proxy Detection tab
        self.create_proxy_tab(notebook)
        
        # PluralKit Integration tab
        self.create_pluralkit_tab(notebook)
        
        # Avatar Management tab
        self.create_avatar_tab(notebook)
        
        # Troubleshooting tab
        self.create_troubleshooting_tab(notebook)
        
        # Close button
        close_frame = ttk.Frame(main_frame)
        close_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(close_frame, text="Close", 
                  command=self.dialog.destroy,
                  bootstyle="primary").pack(side=tk.RIGHT)
    
    def create_getting_started_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Getting Started")
        
        # Scrollable text
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = ttk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, 
                       font=("Arial", 11))
        text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text.yview)
        
        help_content = """
Welcome to Plural Chat! 🎉

Plural Chat is a desktop application designed for plural systems to communicate internally without cluttering external Discord servers or overwhelming partners.

QUICK START:
1. Add Members: Use Settings → Members tab to add system members
2. Import from PluralKit: Use "PluralKit Sync" to import your existing system
3. Start Chatting: Select a member and start typing!

KEY FEATURES:
• Member Management: Add, edit, and organize your system members
• Proxy Detection: Type with proxy tags to auto-switch members
• Avatar Downloads: Avatars are downloaded and compressed automatically
• PluralKit Integration: Import members and sync with your PK system
• Database Storage: All data is stored locally in SQLite databases

MEMBER ICONS:
🖼️ = Member has a downloaded avatar (appears after first message)

KEYBOARD SHORTCUTS:
• Enter = Send message
• Ctrl+Enter = Also sends message (alternative)

STATUS BAR:
The bottom status bar shows what's happening:
• "Ready" = App is idle
• "Checking avatar..." = Looking for member avatar
• "Downloading avatar..." = Fetching and compressing avatar
• "Avatar downloaded (XX% savings)" = Successfully saved avatar

Your data is stored locally in two databases:
• app.db = Settings, themes, API tokens
• system.db = Members, messages, system info
        """
        
        text.insert(tk.END, help_content)
        text.config(state=tk.DISABLED)
    
    def create_proxy_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Proxy Detection")
        
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = ttk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                       font=("Arial", 11))
        text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text.yview)
        
        proxy_content = """
PROXY DETECTION 🔍

Proxy detection allows you to type with special tags that automatically switch to the correct member.

HOW IT WORKS:
When you import from PluralKit or set up proxy tags manually, you can type messages like:

Alice: Hello world!
→ Automatically switches to Alice and sends "Hello world!"

[Bob] How's everyone doing?
→ Automatically switches to Bob and sends "How's everyone doing?"

VISUAL FEEDBACK:
• Message box turns light green when proxy is detected
• "🔍 Proxy detected" appears below the message box
• Member selector automatically updates

SETTING UP PROXY TAGS:
1. Import from PluralKit (easiest - tags come automatically)
2. Or manually add them in Settings → Members

COMMON PROXY FORMATS:
• name: text
• [name] text
• text -name
• name> text
• And many more!

TROUBLESHOOTING:
• Make sure proxy tags are set for your members
• Check that you're typing the exact prefix/suffix
• Proxy detection is case-sensitive
• Empty tags (no prefix AND no suffix) are ignored

The proxy system is designed to be just like PluralKit but for local use!
        """
        
        text.insert(tk.END, proxy_content)
        text.config(state=tk.DISABLED)
    
    def create_pluralkit_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="PluralKit Integration")
        
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = ttk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                       font=("Arial", 11))
        text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text.yview)
        
        pk_content = """
PLURALKIT INTEGRATION 🔗

Connect with your existing PluralKit system to import members and data.

GETTING YOUR TOKEN:
1. Go to PluralKit's dashboard: https://dash.pluralkit.me/
2. Log in with your Discord account
3. Go to Settings → API
4. Generate a new token
5. Copy the token (it starts with "pk.")

IMPORTING DATA:
1. Click "PluralKit Sync" in the main app
2. Paste your token and click "Save Token"
3. Check "Download Avatars" if you want images (recommended)
4. Click "Sync Members"

WHAT GETS IMPORTED:
• Member names and display names
• Pronouns and descriptions
• Colors and birthdays
• Proxy tags (for auto-switching)
• Avatar URLs (downloaded and compressed to WebP)

AVATAR DOWNLOADING:
• Avatars are downloaded during sync if enabled
• Images are converted to WebP format at 80% quality
• Typically saves 90%+ storage space
• Rectangular images are center-cropped to squares
• All avatars are standardized to 256x256 pixels

SYNC FEATURES:
• Rate limiting to avoid hitting PK's API limits
• Retry logic for failed downloads
• Progress tracking with member count
• Duplicate name handling (adds numbers if needed)
• Preserves existing local data

TROUBLESHOOTING:
• Token invalid: Generate a new one from PK dashboard
• Sync stops: May be rate limited, wait and try again
• No members found: Check that your PK system has members
• Avatar download fails: Network issues or broken image URLs

Your PK token is stored securely and only used for API calls.
        """
        
        text.insert(tk.END, pk_content)
        text.config(state=tk.DISABLED)
    
    def create_avatar_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Avatar Management")
        
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = ttk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                       font=("Arial", 11))
        text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text.yview)
        
        avatar_content = """
AVATAR MANAGEMENT 🖼️

Plural Chat efficiently manages member avatars with smart compression and lazy loading.

AVATAR DOWNLOADING:
There are two ways avatars get downloaded:

1. LAZY LOADING (Automatic):
   • When a member sends their first message
   • Only downloads when needed
   • Happens in the background

2. BULK IMPORT (PluralKit Sync):
   • Downloads all avatars during sync
   • Good for getting everything at once
   • Can be enabled/disabled in sync dialog

SMART COMPRESSION:
• Original: 4MB PNG → Compressed: 200KB WebP (95% savings!)
• Center-cropped to square (no smooshing!)
• Resized to 256x256 pixels (PluralKit standard)
• 80% quality WebP compression
• Transparency handled with white background

PROCESSING STEPS:
1. Download original image
2. Center crop to square if needed
3. Resize to 256x256 using high-quality scaling
4. Convert to RGB (remove transparency)
5. Save as WebP with 80% quality
6. Update database to point to local file

VISUAL INDICATORS:
• 🖼️ icon appears next to members with downloaded avatars
• Status bar shows download progress
• Debug messages in console show file sizes

STORAGE LOCATION:
• Avatars saved in "avatars/" folder
• Named as "member_[id].webp"
• Database stores path to local file

TROUBLESHOOTING:
• "Failed to download": Check internet connection
• "Rate limited": PluralKit is throttling requests
• "Avatar not found": Original URL may be broken
• Large file sizes: Compression should reduce by 90%+

The system is designed to be storage-efficient while maintaining good image quality!
        """
        
        text.insert(tk.END, avatar_content)
        text.config(state=tk.DISABLED)
    
    def create_troubleshooting_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Troubleshooting")
        
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = ttk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                       font=("Arial", 11))
        text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text.yview)
        
        troubleshooting_content = """
TROUBLESHOOTING 🔧

Common issues and solutions:

DATABASE ERRORS:
• "UNIQUE constraint failed": Trying to add duplicate member
  → Solution: Use different name or import will auto-number
• "No such column": Database schema mismatch
  → Solution: App auto-migrates on startup, restart if needed

PROXY DETECTION ISSUES:
• "TypeError: endswith first arg must be str": Broken proxy tags
  → Solution: Fixed in recent update, restart app
• Proxy not detecting: Check exact prefix/suffix spelling
• Message not sending: Enter key should work, try clicking Send

PLURALKIT SYNC PROBLEMS:
• "No token configured": Need to save PK token first
• "Connection failed": Check internet and token validity
• Sync stops partway: Rate limiting, wait and retry
• "No members found": Your PK system might be empty

AVATAR DOWNLOAD ISSUES:
• "Failed to download": Network issue or broken URL
• Images too large: Compression should handle this
• "Rate limited": Too many requests, automatic retry
• Missing avatars: May not have been set in PluralKit

PERFORMANCE ISSUES:
• App slow to start: Database migration on first run
• Large avatar files: Should compress to <100KB each
• Memory usage: Restart app if it gets sluggish

UI PROBLEMS:
• Themes not working: Try switching themes in Settings
• Window size issues: Use Settings → General to adjust
• Missing buttons: Window might be too small

FILE LOCATIONS:
• app.db: App settings and preferences
• system.db: Member and message data
• avatars/: Downloaded avatar images
• All files in app directory

GETTING HELP:
• Check debug messages in console
• Look at status bar for current activity
• Most operations show progress feedback
• Enable debug mode for more detailed logs

If problems persist, check for updates or restart the application.
        """
        
        text.insert(tk.END, troubleshooting_content)
        text.config(state=tk.DISABLED)