"""Settings dialog for application preferences."""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QComboBox, QSpinBox, QGroupBox,
    QFontComboBox, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """Dialog for application settings."""

    def __init__(self, app_db, theme_manager, parent=None):
        super().__init__(parent)
        self.app_db = app_db
        self.theme_manager = theme_manager

        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self._setup_ui()
        self._load_current_settings()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Set larger font for labels
        label_font = QFont()
        label_font.setPointSize(11)

        # Theme settings
        theme_group = QGroupBox("Appearance")
        theme_group.setFont(label_font)
        theme_layout = QFormLayout()
        theme_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(35)
        self.theme_combo.setMinimumWidth(250)
        # Make the text bigger and more readable
        combo_font = QFont()
        combo_font.setPointSize(12)
        self.theme_combo.setFont(combo_font)
        themes = self.theme_manager.get_available_themes()
        for theme_id, theme_name in themes:
            self.theme_combo.addItem(theme_name, theme_id)
        theme_layout.addRow("Theme:", self.theme_combo)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Font settings
        font_group = QGroupBox("Font")
        font_group.setFont(label_font)
        font_layout = QFormLayout()
        font_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.font_family_combo = QFontComboBox()
        self.font_family_combo.setMinimumHeight(35)
        self.font_family_combo.setMinimumWidth(250)
        self.font_family_combo.setFont(combo_font)
        font_layout.addRow("Font Family:", self.font_family_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(10)
        self.font_size_spin.setMinimumHeight(35)
        self.font_size_spin.setMinimumWidth(100)
        self.font_size_spin.setFont(combo_font)
        font_layout.addRow("Font Size:", self.font_size_spin)

        font_group.setLayout(font_layout)
        layout.addWidget(font_group)

        # System settings
        system_group = QGroupBox("System")
        system_group.setFont(label_font)
        system_layout = QFormLayout()

        info_label = QLabel("System configuration options will be added here")
        info_label.setStyleSheet("QLabel { color: #6c757d; }")
        system_layout.addRow(info_label)

        system_group.setLayout(system_layout)
        layout.addWidget(system_group)

        # Spacer
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self._save_settings)
        save_button.setDefault(True)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def _load_current_settings(self):
        """Load current settings from database."""
        # Load theme
        current_theme = self.theme_manager.get_current_theme()
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_theme:
                self.theme_combo.setCurrentIndex(i)
                break

        # Load font
        # Use system default font family if not set
        default_font = QFont()
        font_family = self.app_db.get_setting('font_family', default_font.family())
        font_size = self.app_db.get_setting('font_size', 10)

        # Set font family
        font = QFont(font_family)
        self.font_family_combo.setCurrentFont(font)

        # Set font size
        self.font_size_spin.setValue(int(font_size))

    def _save_settings(self):
        """Save settings to database."""
        try:
            # Save theme
            theme_id = self.theme_combo.currentData()
            self.theme_manager.apply_theme(theme_id)

            # Save font
            font_family = self.font_family_combo.currentFont().family()
            font_size = self.font_size_spin.value()

            self.app_db.set_setting('font_family', font_family)
            self.app_db.set_setting('font_size', font_size)

            logger.info("Settings saved successfully")
            self.accept()

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
