"""Member management dialog for adding/editing members."""

import logging
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QPushButton, QLabel,
    QFileDialog, QColorDialog, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor

logger = logging.getLogger(__name__)


class MemberManagerDialog(QDialog):
    """Dialog for creating and editing system members."""

    def __init__(self, system_db, member_id=None, parent=None):
        super().__init__(parent)
        self.system_db = system_db
        self.member_id = member_id
        self.avatar_path = None
        self.selected_color = "#6c757d"

        self.setWindowTitle("New Member" if member_id is None else "Edit Member")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

        self._setup_ui()

        if member_id is not None:
            self._load_member_data()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Basic information
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Member name")
        basic_layout.addRow("Name:", self.name_input)

        self.pronouns_input = QLineEdit()
        self.pronouns_input.setPlaceholderText("e.g., they/them")
        basic_layout.addRow("Pronouns:", self.pronouns_input)

        # Color picker
        color_layout = QHBoxLayout()
        self.color_display = QLabel("     ")
        self.color_display.setStyleSheet(f"QLabel {{ background-color: {self.selected_color}; border: 1px solid #999; }}")
        self.color_display.setFixedSize(50, 30)
        color_layout.addWidget(self.color_display)

        color_button = QPushButton("Choose Color")
        color_button.clicked.connect(self._choose_color)
        color_layout.addWidget(color_button)
        color_layout.addStretch()

        basic_layout.addRow("Color:", color_layout)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # Avatar
        avatar_group = QGroupBox("Avatar")
        avatar_layout = QVBoxLayout()

        self.avatar_label = QLabel("No avatar selected")
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setFixedSize(128, 128)
        self.avatar_label.setStyleSheet("QLabel { border: 1px solid #999; background-color: #f8f9fa; }")
        avatar_layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)

        avatar_button_layout = QHBoxLayout()
        choose_avatar_btn = QPushButton("Choose Avatar")
        choose_avatar_btn.clicked.connect(self._choose_avatar)
        avatar_button_layout.addWidget(choose_avatar_btn)

        clear_avatar_btn = QPushButton("Clear Avatar")
        clear_avatar_btn.clicked.connect(self._clear_avatar)
        avatar_button_layout.addWidget(clear_avatar_btn)

        avatar_layout.addLayout(avatar_button_layout)
        avatar_group.setLayout(avatar_layout)
        layout.addWidget(avatar_group)

        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout()

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Optional description or notes about this member")
        self.description_input.setMaximumHeight(100)
        desc_layout.addWidget(self.description_input)

        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)

        # Proxy tags
        proxy_group = QGroupBox("Proxy Tags")
        proxy_layout = QVBoxLayout()

        help_label = QLabel("Proxy tags for automatic member detection (one per line)")
        help_label.setStyleSheet("QLabel { color: #6c757d; font-size: 9pt; }")
        proxy_layout.addWidget(help_label)

        proxy_form = QFormLayout()

        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("e.g., [member:")
        proxy_form.addRow("Prefix:", self.prefix_input)

        self.suffix_input = QLineEdit()
        self.suffix_input.setPlaceholderText("e.g., ]")
        proxy_form.addRow("Suffix:", self.suffix_input)

        proxy_layout.addLayout(proxy_form)
        proxy_group.setLayout(proxy_layout)
        layout.addWidget(proxy_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self._save_member)
        save_button.setDefault(True)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        if self.member_id is not None:
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(self._delete_member)
            delete_button.setStyleSheet("QPushButton { background-color: #dc3545; color: white; }")
            button_layout.insertWidget(0, delete_button)

        layout.addLayout(button_layout)

    def _load_member_data(self):
        """Load existing member data."""
        member = self.system_db.get_member(self.member_id)
        if not member:
            return

        self.name_input.setText(member.get('name', ''))
        self.pronouns_input.setText(member.get('pronouns', ''))
        self.description_input.setPlainText(member.get('description', ''))

        # Load color
        color = member.get('color', '#6c757d')
        self.selected_color = color
        self.color_display.setStyleSheet(f"QLabel {{ background-color: {color}; border: 1px solid #999; }}")

        # Load avatar
        avatar_path = member.get('avatar_path')
        if avatar_path and Path(avatar_path).exists():
            self.avatar_path = avatar_path
            self._display_avatar(avatar_path)

        # Load proxy tags
        proxy_tags = member.get('proxy_tags')
        if proxy_tags:
            if isinstance(proxy_tags, str):
                try:
                    proxy_tags = json.loads(proxy_tags)
                except:
                    pass

            if isinstance(proxy_tags, list) and len(proxy_tags) > 0:
                tag = proxy_tags[0]
                self.prefix_input.setText(tag.get('prefix', ''))
                self.suffix_input.setText(tag.get('suffix', ''))

    def _choose_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(QColor(self.selected_color), self)
        if color.isValid():
            self.selected_color = color.name()
            self.color_display.setStyleSheet(f"QLabel {{ background-color: {self.selected_color}; border: 1px solid #999; }}")

    def _choose_avatar(self):
        """Open file dialog to choose avatar."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Avatar Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.webp)"
        )

        if file_path:
            self.avatar_path = file_path
            self._display_avatar(file_path)

    def _clear_avatar(self):
        """Clear the selected avatar."""
        self.avatar_path = None
        self.avatar_label.clear()
        self.avatar_label.setText("No avatar selected")

    def _display_avatar(self, path: str):
        """Display avatar in the preview label."""
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                128, 128,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.avatar_label.setPixmap(pixmap)

    def _save_member(self):
        """Save the member data."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a member name.")
            return

        # Build proxy tags
        prefix = self.prefix_input.text().strip()
        suffix = self.suffix_input.text().strip()
        proxy_tags = []
        if prefix or suffix:
            proxy_tags.append({'prefix': prefix, 'suffix': suffix})

        # Prepare member data
        member_data = {
            'name': name,
            'pronouns': self.pronouns_input.text().strip(),
            'color': self.selected_color,
            'description': self.description_input.toPlainText().strip(),
            'avatar_path': self.avatar_path,
            'proxy_tags': json.dumps(proxy_tags) if proxy_tags else None
        }

        try:
            if self.member_id is None:
                # Create new member
                self.system_db.add_member(**member_data)
                logger.info(f"Created new member: {name}")
            else:
                # Update existing member
                member_data['member_id'] = self.member_id
                self.system_db.update_member(**member_data)
                logger.info(f"Updated member: {name}")

            self.accept()

        except Exception as e:
            logger.error(f"Failed to save member: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save member: {str(e)}")

    def _delete_member(self):
        """Delete the current member."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this member? This will also delete all their messages.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.system_db.delete_member(self.member_id)
                logger.info(f"Deleted member: {self.member_id}")
                self.accept()
            except Exception as e:
                logger.error(f"Failed to delete member: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete member: {str(e)}")
