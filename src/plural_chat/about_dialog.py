import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import webbrowser
import logging
from logging.handlers import RotatingFileHandler
import os
from PIL import Image, ImageTk


class AboutDialog:
    """About dialog showing project information, credits, and links"""
    
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
        self.logger = logging.getLogger('plural_chat.about_dialog')
        
    def show(self):
        """Show the About dialog"""
        self.dialog = ttk.Toplevel(self.parent)
        self.dialog.title("About Plural Chat")
        self.dialog.geometry("600x650")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (650 // 2)
        self.dialog.geometry(f"600x650+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the About dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding=30)
        main_frame.pack(fill=BOTH, expand=True)
        
        # App icon/title section
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="🗨️ Plural Chat", 
                               font=("Arial", 24, "bold"))
        title_label.pack()
        
        version_label = ttk.Label(title_frame, text="Version 0.1.0", 
                                 font=("Arial", 12), bootstyle="secondary")
        version_label.pack(pady=(5, 0))
        
        # Description
        desc_text = """A desktop chat application designed specifically for plural systems.
        
Features include:
• Local chat with member switching
• PluralKit integration and sync
• Proxy detection and auto-switching
• Personal diary system for private thoughts
• SQLite database for performance
• Modern themes via ttkbootstrap
• Export/import system data"""
        
        desc_label = ttk.Label(main_frame, text=desc_text, 
                              font=("Arial", 11), justify=LEFT)
        desc_label.pack(fill=X, pady=(0, 20))
        
        # Technology section
        tech_frame = ttk.LabelFrame(main_frame, text="Built With", padding=15)
        tech_frame.pack(fill=X, pady=(0, 20))
        
        tech_text = """• Python 3.8+ 🐍
• ttkbootstrap - Modern UI themes with full customization
• SQLite - Lightning-fast local database
• Pillow - Advanced image processing & WebP compression
• Requests - PluralKit API integration
• Aria2 - Ultra-fast parallel avatar downloading
• Modular UI architecture - Clean component separation
• Subprocess workers - Non-blocking background operations
• Advanced theme management - OS-independent styling"""
        
        tech_label = ttk.Label(tech_frame, text=tech_text, 
                              font=("Arial", 10), justify=LEFT)
        tech_label.pack(anchor=W)
        
        # Credits section
        credits_frame = ttk.LabelFrame(main_frame, text="Credits", padding=15)
        credits_frame.pack(fill=X, pady=(0, 20))
        
        credits_text = """Created by: Duskfallcrew aka The Duskfall Portal Crew, of Ktiseos Nyx
        
Special thanks to:
• PluralKit team for the amazing API
• ttkbootstrap developers for beautiful themes
• Vecteezy for the default avatar
• The Plural Community for its support"""
        
        credits_label = ttk.Label(credits_frame, text=credits_text, 
                                 font=("Arial", 10), justify=LEFT)
        credits_label.pack(anchor=W)
        
        # Links section
        links_frame = ttk.Frame(main_frame)
        links_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Button(links_frame, text="🌐 PluralKit", 
                  command=lambda: self.open_url("https://pluralkit.me"), 
                  bootstyle="info-outline").pack(side=LEFT, padx=(0, 10))
        
        ttk.Button(links_frame, text="📖 GitHub", 
                  command=lambda: self.open_url("https://github.com/your-repo/plural-chat"), 
                  bootstyle="secondary-outline").pack(side=LEFT, padx=(0, 10))
        
        # Ko-fi button with logo
        self.create_kofi_button(links_frame)

        ttk.Button(links_frame, text="Default Avatar Attribution", 
                  command=lambda: self.open_url("https://www.vecteezy.com/free-png/default-avatar"), 
                  bootstyle="link").pack(side=LEFT, padx=(10, 0))
        
        # License section
        license_frame = ttk.Frame(main_frame)
        license_frame.pack(fill=X, pady=(0, 20))
        
        license_text = """Released under the MIT License
Copyright © 2025 Duskfallcrew aka The Duskfall Portal Crew, of Ktiseos Nyx"""
        
        license_label = ttk.Label(license_frame, text=license_text, 
                                 font=("Arial", 9), bootstyle="secondary")
        license_label.pack()
        
        # Close button
        close_frame = ttk.Frame(main_frame)
        close_frame.pack(fill=X)
        
        ttk.Button(close_frame, text="Close", command=self.close_dialog, 
                  bootstyle="primary").pack(pady=(10, 0))
        
    def create_kofi_button(self, parent_frame):
        """Create Ko-fi support button with logo"""
        try:
            from importlib import resources
            # Load Ko-fi logo using importlib.resources for package data
            with resources.path('plural_chat', 'kofi_logo.webp') as kofi_logo_path:
                kofi_image = Image.open(kofi_logo_path)
                
                # Resize to button-appropriate size
                kofi_image = kofi_image.resize((80, 26), Image.Resampling.LANCZOS)
                kofi_photo = ImageTk.PhotoImage(kofi_image)
                
                # Create button with logo
                kofi_button = ttk.Button(
                    parent_frame, 
                    image=kofi_photo,
                    text="  Support on Ko-fi",
                    compound=LEFT,
                    command=lambda: self.open_url("https://ko-fi.com/duskfallcrew/"),
                    bootstyle="warning"
                )
                kofi_button.pack(side=LEFT, padx=(0, 10))
                
                # Keep reference to prevent garbage collection
                kofi_button.image = kofi_photo
                
        except (ImportError, FileNotFoundError, Exception) as e:
            self.logger.error(f"Error creating Ko-fi button with logo: {e}")
            # Fallback to text-only button
            ttk.Button(parent_frame, text="☕ Support on Ko-fi", 
                      command=lambda: self.open_url("https://ko-fi.com/duskfallcrew/"), 
                      bootstyle="warning-outline").pack(side=LEFT, padx=(0, 10))
        
    def open_url(self, url):
        """Open URL in default browser"""
        try:
            webbrowser.open(url)
        except Exception as e:
            self.logger.error(f"Could not open URL: {e}")
            messagebox.showerror("Error", f"Could not open URL: {e}")
    
    def close_dialog(self):
        """Close the About dialog"""
        if self.dialog:
            self.dialog.destroy()