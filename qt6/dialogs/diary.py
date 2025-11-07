"""Diary dialog for personal member entries."""

import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QTextEdit, QLineEdit, QPushButton,
    QLabel, QSplitter, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)


class DiaryDialog(QDialog):
    """Dialog for viewing and editing diary entries."""

    def __init__(self, system_db, member_id, parent=None):
        super().__init__(parent)
        self.system_db = system_db
        self.member_id = member_id
        self.current_entry_id = None

        # Get member name
        member = self.system_db.get_member(member_id)
        member_name = member['name'] if member else "Unknown"

        self.setWindowTitle(f"Diary - {member_name}")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self._setup_ui()
        self._load_entries()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - Entry list
        left_widget = self._create_entry_list()
        splitter.addWidget(left_widget)

        # Right side - Entry editor
        right_widget = self._create_entry_editor()
        splitter.addWidget(right_widget)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def _create_entry_list(self):
        """Create the entry list widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Entries")
        header_label.setStyleSheet("QLabel { font-weight: bold; font-size: 12pt; }")
        header_layout.addWidget(header_label)

        new_button = QPushButton("New Entry")
        new_button.clicked.connect(self._new_entry)
        header_layout.addWidget(new_button)

        layout.addLayout(header_layout)

        # Entry list
        self.entry_list = QListWidget()
        self.entry_list.itemClicked.connect(self._on_entry_selected)
        layout.addWidget(self.entry_list)

        return widget

    def _create_entry_editor(self):
        """Create the entry editor widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title_layout = QHBoxLayout()
        title_label = QLabel("Title:")
        title_layout.addWidget(title_label)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Entry title")
        title_layout.addWidget(self.title_input)

        layout.addLayout(title_layout)

        # Content
        content_label = QLabel("Content:")
        layout.addWidget(content_label)

        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Write your diary entry here...")
        layout.addWidget(self.content_edit)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_button = QPushButton("Save Entry")
        save_button.clicked.connect(self._save_entry)
        button_layout.addWidget(save_button)

        delete_button = QPushButton("Delete Entry")
        delete_button.clicked.connect(self._delete_entry)
        delete_button.setStyleSheet("QPushButton { background-color: #dc3545; color: white; }")
        button_layout.addWidget(delete_button)

        layout.addLayout(button_layout)

        return widget

    def _load_entries(self):
        """Load diary entries from database."""
        self.entry_list.clear()
        entries = self.system_db.get_diary_entries(self.member_id)

        for entry in entries:
            item = QListWidgetItem(entry['title'] or "Untitled")
            item.setData(Qt.ItemDataRole.UserRole, entry['id'])
            self.entry_list.addItem(item)

    def _on_entry_selected(self, item: QListWidgetItem):
        """Handle entry selection."""
        entry_id = item.data(Qt.ItemDataRole.UserRole)
        self._load_entry(entry_id)

    def _load_entry(self, entry_id: int):
        """Load an entry into the editor."""
        entry = self.system_db.get_diary_entry(entry_id)
        if not entry:
            return

        self.current_entry_id = entry_id
        self.title_input.setText(entry['title'] or '')
        self.content_edit.setPlainText(entry['content'] or '')

    def _new_entry(self):
        """Create a new diary entry."""
        self.current_entry_id = None
        self.title_input.clear()
        self.content_edit.clear()
        self.title_input.setFocus()

    def _save_entry(self):
        """Save the current entry."""
        title = self.title_input.text().strip()
        content = self.content_edit.toPlainText().strip()

        if not title and not content:
            QMessageBox.warning(self, "Validation Error", "Please enter a title or content.")
            return

        try:
            if self.current_entry_id is None:
                # Create new entry
                self.system_db.add_diary_entry(self.member_id, title, content)
                logger.info("Created new diary entry")
            else:
                # Update existing entry
                self.system_db.update_diary_entry(self.current_entry_id, title, content)
                logger.info("Updated diary entry")

            self._load_entries()

            # Select the saved entry
            if self.current_entry_id is not None:
                for i in range(self.entry_list.count()):
                    item = self.entry_list.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == self.current_entry_id:
                        self.entry_list.setCurrentItem(item)
                        break

        except Exception as e:
            logger.error(f"Failed to save diary entry: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save entry: {str(e)}")

    def _delete_entry(self):
        """Delete the current entry."""
        if self.current_entry_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this diary entry?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.system_db.delete_diary_entry(self.current_entry_id)
                logger.info("Deleted diary entry")

                self.current_entry_id = None
                self.title_input.clear()
                self.content_edit.clear()
                self._load_entries()

            except Exception as e:
                logger.error(f"Failed to delete diary entry: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete entry: {str(e)}")
