"""Member list widget with avatars."""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon, QImage

logger = logging.getLogger(__name__)


class MemberListWidget(QWidget):
    """Widget displaying a list of system members with avatars."""

    # Signals
    member_selected = pyqtSignal(int)  # member_id
    member_double_clicked = pyqtSignal(int)  # member_id

    def __init__(self, system_db, parent=None):
        super().__init__()
        self.system_db = system_db
        self.avatar_cache = {}

        self._setup_ui()
        self.load_members()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Header
        header = QLabel("System Members")
        header.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 10px;
                font-weight: bold;
                font-size: 12pt;
                border-bottom: 2px solid #dee2e6;
            }
        """)
        layout.addWidget(header)

        # Member list
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(40, 40))
        self.list_widget.setSpacing(2)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: #f8f9fa;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #dee2e6;
            }
            QListWidget::item:hover {
                background-color: #e9ecef;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        layout.addWidget(self.list_widget)

        # Set minimum width
        self.setMinimumWidth(250)
        self.setMaximumWidth(400)

    def load_members(self):
        """Load members from database."""
        self.list_widget.clear()
        self.avatar_cache.clear()

        members = self.system_db.get_all_members()

        for member in members:
            self._add_member_item(member)

    def _add_member_item(self, member: dict):
        """Add a member item to the list."""
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, member['id'])
        item.setText(member['name'])

        # Load avatar
        avatar_path = member.get('avatar_path')
        if avatar_path and Path(avatar_path).exists():
            icon = self._load_avatar(avatar_path)
            if icon:
                item.setIcon(icon)
        else:
            # Use default avatar
            item.setIcon(self._get_default_avatar())

        self.list_widget.addItem(item)

    def _load_avatar(self, path: str) -> QIcon:
        """Load avatar image and create icon."""
        try:
            if path in self.avatar_cache:
                return self.avatar_cache[path]

            pixmap = QPixmap(path)
            if not pixmap.isNull():
                # Scale to fit icon size
                pixmap = pixmap.scaled(
                    40, 40,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )

                # Crop to square
                if pixmap.width() != pixmap.height():
                    size = min(pixmap.width(), pixmap.height())
                    x = (pixmap.width() - size) // 2
                    y = (pixmap.height() - size) // 2
                    pixmap = pixmap.copy(x, y, size, size)

                icon = QIcon(pixmap)
                self.avatar_cache[path] = icon
                return icon

        except Exception as e:
            logger.error(f"Failed to load avatar from {path}: {e}")

        return self._get_default_avatar()

    def _get_default_avatar(self) -> QIcon:
        """Get default avatar icon."""
        # Create a simple colored circle as default
        pixmap = QPixmap(40, 40)
        pixmap.fill(Qt.GlobalColor.lightGray)
        return QIcon(pixmap)

    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle item click."""
        member_id = item.data(Qt.ItemDataRole.UserRole)
        self.member_selected.emit(member_id)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handle item double click."""
        member_id = item.data(Qt.ItemDataRole.UserRole)
        self.member_double_clicked.emit(member_id)

    def select_member(self, member_id: int):
        """Select a member by ID."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == member_id:
                self.list_widget.setCurrentItem(item)
                break
