"""
Clean theme management - no more debug hell!
"""
import ttkbootstrap as ttk

class ThemeManager:
    def __init__(self, root_window):
        self.root = root_window
        self.current_theme = "superhero"  # Safe default

    def get_available_themes(self):
        """Get all working built-in themes (no custom themes for now)"""
        try:
            # Get themes from ttkbootstrap
            all_themes = list(self.root.style.theme_names())
            # Filter out any that might be problematic (but keep Criss's awesome theme!)
            # Note: kn-bootstrap-vapor-dark is Criss's theme that somehow made it into ttkbootstrap 😂
            safe_themes = all_themes  # All themes work now, including Criss's secret theme!
            return sorted(safe_themes)
        except Exception:
            # Ultimate fallback
            return ["superhero", "darkly", "solar", "cyborg", "vapor", "pulse",
                   "flatly", "journal", "litera", "lumen", "minty", "morph"]

    def apply_theme(self, theme_name):
        """Apply theme with proper error handling - NO NUCLEAR OPTIONS"""
        try:
            # Only apply if it's different from the current theme
            if self.current_theme != theme_name:
                # Simple and clean
                self.root.style.theme_use(theme_name)
                self.current_theme = theme_name
                print(f"✅ Applied theme: {theme_name}")
            return True
        except Exception as e:
            print(f"❌ Theme failed: {e}")
            return False

    def get_current_theme(self):
        """Get the currently applied theme"""
        return self.current_theme
