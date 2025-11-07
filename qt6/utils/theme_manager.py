"""Theme management for PyQt6 application."""

import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages application themes and styling."""

    # Available themes
    THEMES = {
        'light': {
            'name': 'Light',
            'base': '#ffffff',
            'alternate_base': '#f8f9fa',
            'text': '#212529',
            'button': '#e9ecef',
            'button_text': '#212529',
            'highlight': '#007bff',
            'highlight_text': '#ffffff',
            'window': '#ffffff',
            'window_text': '#212529',
        },
        'dark': {
            'name': 'Dark',
            'base': '#2b2b2b',
            'alternate_base': '#353535',
            'text': '#e0e0e0',
            'button': '#3a3a3a',
            'button_text': '#e0e0e0',
            'highlight': '#0d6efd',
            'highlight_text': '#ffffff',
            'window': '#1e1e1e',
            'window_text': '#e0e0e0',
        },
        'blue': {
            'name': 'Blue',
            'base': '#e3f2fd',
            'alternate_base': '#bbdefb',
            'text': '#1565c0',
            'button': '#90caf9',
            'button_text': '#0d47a1',
            'highlight': '#2196f3',
            'highlight_text': '#ffffff',
            'window': '#e3f2fd',
            'window_text': '#1565c0',
        },
        'purple': {
            'name': 'Purple',
            'base': '#f3e5f5',
            'alternate_base': '#e1bee7',
            'text': '#6a1b9a',
            'button': '#ce93d8',
            'button_text': '#4a148c',
            'highlight': '#9c27b0',
            'highlight_text': '#ffffff',
            'window': '#f3e5f5',
            'window_text': '#6a1b9a',
        },
        'green': {
            'name': 'Green',
            'base': '#e8f5e9',
            'alternate_base': '#c8e6c9',
            'text': '#2e7d32',
            'button': '#a5d6a7',
            'button_text': '#1b5e20',
            'highlight': '#4caf50',
            'highlight_text': '#ffffff',
            'window': '#e8f5e9',
            'window_text': '#2e7d32',
        },
    }

    def __init__(self, main_window, app_db):
        self.main_window = main_window
        self.app_db = app_db
        self.current_theme = 'light'

    def get_available_themes(self):
        """Get list of available theme names."""
        return [(key, data['name']) for key, data in self.THEMES.items()]

    def apply_theme(self, theme_name: str):
        """Apply a theme to the application."""
        if theme_name not in self.THEMES:
            logger.warning(f"Theme '{theme_name}' not found, using 'light'")
            theme_name = 'light'

        theme = self.THEMES[theme_name]
        self.current_theme = theme_name

        # Create palette
        palette = QPalette()

        # Set colors
        palette.setColor(QPalette.ColorRole.Window, QColor(theme['window']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(theme['window_text']))
        palette.setColor(QPalette.ColorRole.Base, QColor(theme['base']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme['alternate_base']))
        palette.setColor(QPalette.ColorRole.Text, QColor(theme['text']))
        palette.setColor(QPalette.ColorRole.Button, QColor(theme['button']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme['button_text']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(theme['highlight']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme['highlight_text']))

        # Apply palette
        QApplication.instance().setPalette(palette)

        # Apply additional stylesheet
        self._apply_stylesheet(theme)

        # Save to database
        self.app_db.set_setting('theme', theme_name)

        logger.info(f"Applied theme: {theme_name}")

    def _apply_stylesheet(self, theme):
        """Apply additional stylesheet customizations."""
        stylesheet = f"""
            QMainWindow {{
                background-color: {theme['window']};
            }}

            QMenuBar {{
                background-color: {theme['alternate_base']};
                color: {theme['window_text']};
                border-bottom: 1px solid {theme['button']};
            }}

            QMenuBar::item:selected {{
                background-color: {theme['highlight']};
                color: {theme['highlight_text']};
            }}

            QMenu {{
                background-color: {theme['base']};
                color: {theme['text']};
                border: 1px solid {theme['button']};
            }}

            QMenu::item:selected {{
                background-color: {theme['highlight']};
                color: {theme['highlight_text']};
            }}

            QToolBar {{
                background-color: {theme['alternate_base']};
                border-bottom: 1px solid {theme['button']};
                spacing: 5px;
                padding: 5px;
            }}

            QToolButton {{
                background-color: {theme['button']};
                color: {theme['button_text']};
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }}

            QToolButton:hover {{
                background-color: {theme['highlight']};
                color: {theme['highlight_text']};
            }}

            QPushButton {{
                background-color: {theme['button']};
                color: {theme['button_text']};
                border: 1px solid {theme['button']};
                border-radius: 4px;
                padding: 6px 15px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {theme['highlight']};
                color: {theme['highlight_text']};
            }}

            QPushButton:pressed {{
                background-color: {theme['highlight']};
            }}

            QLineEdit {{
                background-color: {theme['base']};
                color: {theme['text']};
                border: 1px solid {theme['button']};
                border-radius: 4px;
                padding: 5px;
            }}

            QLineEdit:focus {{
                border: 2px solid {theme['highlight']};
            }}

            QComboBox {{
                background-color: {theme['base']};
                color: {theme['text']};
                border: 1px solid {theme['button']};
                border-radius: 4px;
                padding: 5px;
            }}

            QComboBox:hover {{
                border: 1px solid {theme['highlight']};
            }}

            QComboBox::drop-down {{
                border: none;
            }}

            QStatusBar {{
                background-color: {theme['alternate_base']};
                color: {theme['window_text']};
            }}
        """

        self.main_window.setStyleSheet(stylesheet)

    def apply_saved_theme(self):
        """Load and apply saved theme from database."""
        theme_name = self.app_db.get_setting('theme', 'light')
        self.apply_theme(theme_name)

    def get_current_theme(self):
        """Get the current theme name."""
        return self.current_theme
