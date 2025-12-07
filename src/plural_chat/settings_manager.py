
import tkinter as tk
from tkinter import messagebox, font
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .member_manager import MemberManager
from .ui.themes.manager import ThemeManager

class SettingsManager(ttk.Toplevel):
    def __init__(self, parent_window, parent_app):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.parent = parent_app

        self.title("Settings")
        self.geometry("600x450")
        self.transient(parent_window) # Keep this window on top of the main window

        # Create a Notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Create tabs
        self.general_tab = ttk.Frame(self.notebook)
        self.members_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.general_tab, text="General")
        self.notebook.add(self.members_tab, text="Members")

        # General Tab Content
        general_frame = ttk.Frame(self.general_tab, padding=10)
        general_frame.pack(fill=tk.BOTH, expand=True)

        # Theme Management
        ttk.Label(general_frame, text="Select Theme:").pack(anchor=tk.W, pady=(0, 5))
        self.theme_selector = ttk.Combobox(general_frame, state="readonly")
        
        # Get all available themes from the ThemeManager
        all_themes = self.parent.theme_manager.get_available_themes()
        self.theme_selector['values'] = all_themes
        
        self.theme_selector.set(self.parent.get_theme_name())
        self.theme_selector.pack(fill=tk.X, pady=(0, 5))
        self.theme_selector.bind("<<ComboboxSelected>>", self.on_theme_selected)
        
        # Theme description label
        self.theme_description = ttk.Label(general_frame, text="", font=("Arial", 9), bootstyle="secondary")
        self.theme_description.pack(fill=tk.X, pady=(0, 15))
        
        # Update initial theme description
        self.update_theme_description()

        # Font Selection
        ttk.Label(general_frame, text="Font Settings:").pack(anchor=tk.W, pady=(15, 5))
        
        font_frame = ttk.Frame(general_frame)
        font_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Font family
        ttk.Label(font_frame, text="Font:").pack(side=tk.LEFT, padx=(0, 5))
        self.font_family_var = tk.StringVar()
        self.font_family_combo = ttk.Combobox(font_frame, textvariable=self.font_family_var, 
                                            state="readonly", width=15)
        
        # Get available fonts
        available_fonts = sorted([f for f in font.families() if not f.startswith('@')])
        # Add some common monospace fonts at the top
        priority_fonts = ['Consolas', 'Monaco', 'Courier New', 'Courier', 'monospace']
        font_list = []
        for pf in priority_fonts:
            if pf in available_fonts:
                font_list.append(pf)
                available_fonts.remove(pf)
        font_list.extend(available_fonts)
        
        self.font_family_combo['values'] = font_list
        current_font = self.parent.app_db.get_setting('font_family', 'Consolas')
        self.font_family_combo.set(current_font)
        self.font_family_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Font size
        ttk.Label(font_frame, text="Size:").pack(side=tk.LEFT, padx=(0, 5))
        self.font_size_var = tk.StringVar()
        self.font_size_combo = ttk.Combobox(font_frame, textvariable=self.font_size_var, 
                                          state="readonly", width=5)
        self.font_size_combo['values'] = ['8', '9', '10', '11', '12', '13', '14', '16', '18', '20', '24']
        current_size = self.parent.app_db.get_setting('font_size', '10')
        self.font_size_combo.set(current_size)
        self.font_size_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Apply font button
        apply_font_button = ttk.Button(font_frame, text="Apply Font", command=self.apply_font)
        apply_font_button.pack(side=tk.LEFT)
        
        # Window Sizing
        ttk.Label(general_frame, text="Window Size (WxH):").pack(anchor=tk.W, pady=(15, 5))
        size_frame = ttk.Frame(general_frame)
        size_frame.pack(fill=tk.X, pady=(0, 10))

        self.width_entry = ttk.Entry(size_frame, width=8)
        self.width_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(size_frame, text="x").pack(side=tk.LEFT)
        self.height_entry = ttk.Entry(size_frame, width=8)
        self.height_entry.pack(side=tk.LEFT, padx=(5, 0))

        apply_size_button = ttk.Button(general_frame, text="Apply Size", command=self.apply_size)
        apply_size_button.pack(anchor=tk.W)

        # Set current size
        current_geometry = self.parent_window.geometry().split('+')[0] # e.g., "800x600"
        width, height = current_geometry.split('x')
        self.width_entry.insert(0, width)
        self.height_entry.insert(0, height)

        # Personalized Greeting Settings
        ttk.Label(general_frame, text="Status Bar:").pack(anchor=tk.W, pady=(15, 5))
        greeting_frame = ttk.Frame(general_frame)
        greeting_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.personalized_greeting_var = tk.BooleanVar()
        current_greeting_setting = self.parent.app_db.get_setting('personalized_greeting', True)
        self.personalized_greeting_var.set(current_greeting_setting)
        
        greeting_checkbox = ttk.Checkbutton(
            greeting_frame, 
            text="Show personalized greeting (e.g., 'Hello System Name! Having a nice afternoon?')",
            variable=self.personalized_greeting_var,
            command=self.apply_greeting_setting
        )
        greeting_checkbox.pack(anchor=tk.W)
        
        # Add a small description
        greeting_desc = ttk.Label(
            greeting_frame, 
            text="When enabled, shows your system name and time-based greeting in the status bar",
            font=("Arial", 9), 
            bootstyle="secondary"
        )
        greeting_desc.pack(anchor=tk.W, pady=(2, 0))

        # Lazy load MemberManager
        self.member_manager_frame = None
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_tab_change(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Members" and self.member_manager_frame is None:
            self.member_manager_frame = MemberManager(self.members_tab, self.parent)
            self.member_manager_frame.pack(expand=True, fill=tk.BOTH)

    def on_theme_selected(self, event=None):
        """Handle theme selection and update description"""
        self.update_theme_description()
        self.apply_theme()
    
    def update_theme_description(self):
        """Update the theme description label"""
        selected_theme = self.theme_selector.get()
        if selected_theme:
            self.theme_description.config(text=f"🎨 Current theme: {selected_theme}")
        else:
            self.theme_description.config(text="")
    
    def apply_theme(self, event=None):
        selected_theme = self.theme_selector.get()
        self.parent.change_theme(selected_theme)
    
    def apply_font(self):
        """Apply font settings to the application"""
        font_family = self.font_family_var.get()
        font_size = self.font_size_var.get()
        
        if not font_family or not font_size:
            messagebox.showerror("Error", "Please select both font family and size.", parent=self)
            return
        
        try:
            font_size = int(font_size)
            
            # Save to database
            self.parent.app_db.set_setting('font_family', font_family)
            self.parent.app_db.set_setting('font_size', str(font_size))
            
            # Apply to current UI
            self.parent.apply_font_settings(font_family, font_size)
            
            # Show success message
            try:
                from ttkbootstrap.toast import ToastNotification
                toast = ToastNotification(
                    title="Font Applied!",
                    message=f"Font changed to {font_family} {font_size}pt",
                    duration=3000,
                    bootstyle="success"
                )
                toast.show_toast()
            except ImportError:
                messagebox.showinfo("Success", f"Font changed to {font_family} {font_size}pt", parent=self)
                
        except ValueError:
            messagebox.showerror("Error", "Invalid font size. Please enter a number.", parent=self)

    def apply_size(self):
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            self.parent_window.geometry(f"{width}x{height}")
        except ValueError:
            messagebox.showerror("Error", "Invalid size. Please enter numbers for width and height.", parent=self)

    def apply_greeting_setting(self):
        """Apply the personalized greeting setting"""
        try:
            enabled = self.personalized_greeting_var.get()
            self.parent.app_db.set_setting('personalized_greeting', enabled)
            
            # Update the status bar immediately
            self.parent.update_status_greeting()
            
            status_text = "enabled" if enabled else "disabled"
            messagebox.showinfo("Success", f"Personalized greeting {status_text}", parent=self)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update greeting setting: {str(e)}", parent=self)

    def on_closing(self):
        # Call the save method of the embedded MemberManager if it was created
        if self.member_manager_frame:
            self.member_manager_frame.on_save_and_close()
        self.destroy()

