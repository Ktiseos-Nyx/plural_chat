import ttkbootstrap as ttk
from .manager import ThemeManager

def test_themes():
    # Create test window
    root = ttk.Window("Theme Test", themename="superhero")
    
    # Create theme manager
    theme_mgr = ThemeManager(root)
    
    # Test getting themes
    themes = theme_mgr.get_available_themes()
    print(f"Available themes: {themes}")
    
    # Test applying themes
    for theme in themes[:3]:  # Test first 3
        success = theme_mgr.apply_theme(theme)
        print(f"Theme {theme}: {'✅' if success else '❌'}")
        root.update()  # Refresh window
        input(f"Press Enter to try next theme...")  # Pause to see result
    
    root.destroy()

if __name__ == "__main__":
    test_themes()