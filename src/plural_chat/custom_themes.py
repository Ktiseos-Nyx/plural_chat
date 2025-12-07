"""
Custom themes for Plural Chat
Add your custom ttkbootstrap themes here
"""

import ttkbootstrap as ttk
from ttkbootstrap import Style

# Custom themes dictionary - DISABLED cyberpunk_plural (causes errors)
CUSTOM_THEMES = {
    # CYBERPUNK_PLURAL THEME DISABLED DUE TO StyleBuilderTTK ERRORS
    # "cyberpunk_plural": {
    #     "type": "dark", 
    #     "colors": {
    #         "primary": "#7745d1",
    #         "secondary": "#ba1ca1",
    #         "success": "#3a8e7f",
    #         "info": "#1687cb", 
    #         "warning": "#c99504",
    #         "danger": "#bb0700",
    #         "light": "#37b5c4",
    #         "dark": "#2c0352",
    #         "bg": "#000811",
    #         "fg": "#00fbea",
    #         "selectbg": "#5c22ba",
    #         "selectfg": "#ffffff",
    #         "border": "#060606",
    #         "inputfg": "#bfb6cd",
    #         "inputbg": "#30115e",
    #         "active": "#17082E"
    #     }
    # }
}

def register_custom_themes():
    """Register all custom themes with ttkbootstrap"""
    try:
        # Load the proper theme definition file
        import os
        import sys
        
        # No sys.path manipulation needed in a package structure.
        
        # Try to import and register the theme
        try:
            # TEMPORARILY DISABLED - causes StyleBuilderTTK error
            # from cyberpunk_plural_theme import theme
            pass
            
            # Register the theme with ttkbootstrap
            style = Style()
            
            # Check if we can register it
            if hasattr(style, 'register_theme'):
                style.register_theme(theme)
                print(f"✅ Registered theme: {theme.name}")
            else:
                # Fallback - try to use the theme definition directly
                if hasattr(style, 'theme_create'):
                    style.theme_create(theme.name, theme)
                    print(f"✅ Created theme: {theme.name}")
                else:
                    print(f"⚠️  Theme registration not available, using manual styling")
                    
        except ImportError as e:
            print(f"⚠️  Could not import theme definition: {e}")
        except Exception as e:
            print(f"⚠️  Theme registration failed: {e}")
            print("   Theme will be available in settings but may use manual styling")
                
    except Exception as e:
        print(f"❌ Error in theme registration: {e}")
        # Continue anyway - themes will still be in the list

def get_custom_theme_names():
    """Get list of custom theme names"""
    return list(CUSTOM_THEMES.keys())

def is_custom_theme(theme_name):
    """Check if a theme is a custom theme"""
    return theme_name in CUSTOM_THEMES

def apply_custom_theme(theme_name, style_obj):
    """Apply a custom theme manually by configuring styles"""
    if theme_name not in CUSTOM_THEMES:
        return False
    
    try:
        theme_data = CUSTOM_THEMES[theme_name]
        colors = theme_data['colors']
        
        # Configure ALL ttkbootstrap widget styles with our custom colors
        
        # Basic widgets
        style_obj.configure('TFrame', background=colors['bg'])
        style_obj.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        style_obj.configure('TLabelFrame', background=colors['bg'], foreground=colors['fg'])
        style_obj.configure('TLabelFrame.Label', background=colors['bg'], foreground=colors['fg'])
        
        # Buttons with different styles
        style_obj.configure('TButton', 
                          background=colors['primary'],
                          foreground=colors['selectfg'],
                          borderwidth=1,
                          focuscolor=colors['selectbg'])
        
        # Styled buttons
        style_obj.configure('success.TButton', background=colors['success'], foreground=colors['selectfg'])
        style_obj.configure('info.TButton', background=colors['info'], foreground=colors['selectfg'])
        style_obj.configure('warning.TButton', background=colors['warning'], foreground=colors['selectfg'])
        style_obj.configure('danger.TButton', background=colors['danger'], foreground=colors['selectfg'])
        style_obj.configure('secondary.TButton', background=colors['secondary'], foreground=colors['selectfg'])
        style_obj.configure('light.TButton', background=colors['light'], foreground=colors['dark'])
        style_obj.configure('dark.TButton', background=colors['dark'], foreground=colors['fg'])
        
        # Outline buttons
        style_obj.configure('primary-outline.TButton', background=colors['bg'], foreground=colors['primary'], bordercolor=colors['primary'])
        style_obj.configure('success-outline.TButton', background=colors['bg'], foreground=colors['success'], bordercolor=colors['success'])
        style_obj.configure('info-outline.TButton', background=colors['bg'], foreground=colors['info'], bordercolor=colors['info'])
        style_obj.configure('warning-outline.TButton', background=colors['bg'], foreground=colors['warning'], bordercolor=colors['warning'])
        style_obj.configure('danger-outline.TButton', background=colors['bg'], foreground=colors['danger'], bordercolor=colors['danger'])
        style_obj.configure('secondary-outline.TButton', background=colors['bg'], foreground=colors['secondary'], bordercolor=colors['secondary'])
        
        # Input widgets
        style_obj.configure('TEntry',
                          fieldbackground=colors['inputbg'],
                          foreground=colors['inputfg'],
                          bordercolor=colors['border'],
                          insertcolor=colors['fg'])
        
        style_obj.configure('TCombobox',
                          fieldbackground=colors['inputbg'],
                          foreground=colors['inputfg'],
                          bordercolor=colors['border'],
                          selectbackground=colors['selectbg'],
                          selectforeground=colors['selectfg'])
        
        # Text widget (for chat)
        style_obj.configure('TText',
                          background=colors['bg'],
                          foreground=colors['fg'],
                          selectbackground=colors['selectbg'],
                          selectforeground=colors['selectfg'],
                          insertbackground=colors['fg'])
        
        # Treeview (for member list)
        style_obj.configure('Treeview',
                          background=colors['bg'],
                          foreground=colors['fg'],
                          fieldbackground=colors['bg'],
                          selectbackground=colors['selectbg'],
                          selectforeground=colors['selectfg'],
                          bordercolor=colors['border'])
        
        style_obj.configure('Treeview.Heading',
                          background=colors['dark'],
                          foreground=colors['fg'],
                          bordercolor=colors['border'])
        
        # Notebook (for settings tabs)
        style_obj.configure('TNotebook',
                          background=colors['bg'],
                          bordercolor=colors['border'])
        
        style_obj.configure('TNotebook.Tab',
                          background=colors['dark'],
                          foreground=colors['fg'],
                          padding=[20, 10],
                          bordercolor=colors['border'])
        
        # Scrollbars
        style_obj.configure('TScrollbar',
                          background=colors['dark'],
                          troughcolor=colors['bg'],
                          bordercolor=colors['border'],
                          arrowcolor=colors['fg'])
        
        # Paned window
        style_obj.configure('TPanedwindow', background=colors['bg'])
        
        # Menu (if any)
        style_obj.configure('TMenubutton',
                          background=colors['primary'],
                          foreground=colors['selectfg'],
                          bordercolor=colors['border'])
        
        print(f"✅ Applied comprehensive custom theme: {theme_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error applying custom theme {theme_name}: {e}")
        return False

def get_theme_info(theme_name):
    """Get information about a custom theme"""
    if theme_name in CUSTOM_THEMES:
        return CUSTOM_THEMES[theme_name]
    return None

# Theme descriptions for the UI
THEME_DESCRIPTIONS = {
    "cyberpunk_plural": {
        "name": "Cyberpunk Plural",
        "description": "🌃 Deep space cyberpunk theme with purple/magenta/cyan colors",
        "style": "Dark",
        "accent": "Purple/Cyan",
        "vibe": "Synthwave Cyberpunk"
    }
}

def get_theme_description(theme_name):
    """Get description for a theme"""
    if theme_name in THEME_DESCRIPTIONS:
        return THEME_DESCRIPTIONS[theme_name]
    return {
        "name": theme_name.replace('_', ' ').title(),
        "description": "Custom theme",
        "style": "Unknown",
        "accent": "Various",
        "vibe": "Custom"
    }

if __name__ == "__main__":
    # Test the custom themes
    print("🎨 Testing Custom Themes...")
    register_custom_themes()
    
    style = Style()
    print(f"📋 Available themes: {sorted(style.theme_names())}")
    
    for theme_name in get_custom_theme_names():
        info = get_theme_description(theme_name)
        print(f"🎯 {info['name']}: {info['description']}")