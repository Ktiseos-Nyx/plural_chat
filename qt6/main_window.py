"""Main window for Plural Chat PyQt6."""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTextEdit, QLineEdit, QPushButton, QComboBox, QLabel,
    QMenuBar, QMenu, QToolBar, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QTextCursor, QFont

from qt6.utils.database_compat import AppDatabase, SystemDatabase
from qt6.widgets.chat_display import ChatDisplay
from qt6.widgets.member_list import MemberListWidget
from qt6.dialogs.member_manager import MemberManagerDialog
from qt6.dialogs.settings import SettingsDialog
from qt6.dialogs.pluralkit_sync import PluralKitSyncDialog
from qt6.dialogs.diary import DiaryDialog
from qt6.dialogs.about import AboutDialog
from qt6.dialogs.help import HelpDialog
from qt6.utils.proxy_detector import ProxyDetector
from qt6.utils.theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Plural Chat")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize databases
        self.app_db = AppDatabase()
        self.system_db = SystemDatabase()

        # Initialize utilities
        self.theme_manager = ThemeManager(self, self.app_db)
        self.proxy_detector = ProxyDetector(self.system_db)

        # Current member selection
        self.current_member_id = None

        # Setup UI
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_status_bar()
        self._load_settings()
        self._load_members()
        self._load_chat_history()

        logger.info("MainWindow initialized")

    def _setup_ui(self):
        """Set up the main user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Member list
        self.member_list = MemberListWidget(self.system_db)
        self.member_list.member_selected.connect(self._on_member_selected)
        self.member_list.member_double_clicked.connect(self._on_member_edit)

        # Right panel - Chat area
        chat_widget = self._create_chat_widget()

        # Add to splitter
        splitter.addWidget(self.member_list)
        splitter.addWidget(chat_widget)
        splitter.setStretchFactor(0, 1)  # Member list
        splitter.setStretchFactor(1, 3)  # Chat area

        main_layout.addWidget(splitter)

    def _create_chat_widget(self):
        """Create the chat area widget."""
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(10, 10, 10, 10)
        chat_layout.setSpacing(10)

        # Chat display
        self.chat_display = ChatDisplay(self.system_db)
        chat_layout.addWidget(self.chat_display, stretch=1)

        # Input area
        input_container = self._create_input_area()
        chat_layout.addWidget(input_container)

        return chat_widget

    def _create_input_area(self):
        """Create the message input area."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Member selector row
        selector_layout = QHBoxLayout()
        selector_layout.setSpacing(10)

        selector_label = QLabel("Sending as:")
        selector_layout.addWidget(selector_label)

        self.member_selector = QComboBox()
        self.member_selector.setMinimumWidth(200)
        self.member_selector.currentIndexChanged.connect(self._on_member_selector_changed)
        selector_layout.addWidget(self.member_selector, stretch=1)

        # Proxy detection indicator
        self.proxy_indicator = QLabel("")
        self.proxy_indicator.setStyleSheet("QLabel { color: #28a745; font-weight: bold; }")
        selector_layout.addWidget(self.proxy_indicator)

        layout.addLayout(selector_layout)

        # Message input row
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self._send_message)
        self.message_input.textChanged.connect(self._on_message_text_changed)
        input_layout.addWidget(self.message_input, stretch=1)

        self.send_button = QPushButton("Send")
        self.send_button.setMinimumWidth(100)
        self.send_button.clicked.connect(self._send_message)
        self.send_button.setDefault(True)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        return container

    def _setup_menu_bar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_member_action = QAction("&New Member", self)
        new_member_action.setShortcut(QKeySequence.StandardKey.New)
        new_member_action.triggered.connect(self._show_new_member_dialog)
        file_menu.addAction(new_member_action)

        file_menu.addSeparator()

        export_action = QAction("&Export System Data", self)
        export_action.triggered.connect(self._export_system_data)
        file_menu.addAction(export_action)

        import_action = QAction("&Import System Data", self)
        import_action.triggered.connect(self._import_system_data)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Members menu
        members_menu = menubar.addMenu("&Members")

        manage_members_action = QAction("&Manage Members", self)
        manage_members_action.setShortcut("Ctrl+M")
        manage_members_action.triggered.connect(self._show_member_manager)
        members_menu.addAction(manage_members_action)

        members_menu.addSeparator()

        diary_action = QAction("&Diary", self)
        diary_action.setShortcut("Ctrl+D")
        diary_action.triggered.connect(self._show_diary)
        members_menu.addAction(diary_action)

        # PluralKit menu
        pk_menu = menubar.addMenu("&PluralKit")

        sync_action = QAction("&Sync with PluralKit", self)
        sync_action.setShortcut("Ctrl+P")
        sync_action.triggered.connect(self._show_pluralkit_sync)
        pk_menu.addAction(sync_action)

        # Settings menu
        settings_menu = menubar.addMenu("&Settings")

        preferences_action = QAction("&Preferences", self)
        preferences_action.setShortcut(QKeySequence.StandardKey.Preferences)
        preferences_action.triggered.connect(self._show_settings)
        settings_menu.addAction(preferences_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        help_action = QAction("&Help", self)
        help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        help_action.triggered.connect(self._show_help)
        help_menu.addAction(help_action)

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self):
        """Set up the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # New member
        new_member_action = QAction("New Member", self)
        new_member_action.triggered.connect(self._show_new_member_dialog)
        toolbar.addAction(new_member_action)

        toolbar.addSeparator()

        # PluralKit sync
        pk_sync_action = QAction("PluralKit Sync", self)
        pk_sync_action.triggered.connect(self._show_pluralkit_sync)
        toolbar.addAction(pk_sync_action)

        toolbar.addSeparator()

        # Diary
        diary_action = QAction("Diary", self)
        diary_action.triggered.connect(self._show_diary)
        toolbar.addAction(diary_action)

        toolbar.addSeparator()

        # Settings
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self._show_settings)
        toolbar.addAction(settings_action)

    def _setup_status_bar(self):
        """Set up the status bar."""
        self.statusBar().showMessage("Ready")

    def _load_settings(self):
        """Load application settings."""
        # Load window geometry
        geometry = self.app_db.get_setting("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # Apply theme
        self.theme_manager.apply_saved_theme()

        # Load font settings
        # Use system default font family if not set
        default_font = QFont()  # Get system default
        font_family = self.app_db.get_setting("font_family", default_font.family())

        # Ensure font_size is an integer
        font_size_setting = self.app_db.get_setting("font_size", "10")
        try:
            font_size = int(font_size_setting)
        except (ValueError, TypeError):
            font_size = 10

        font = QFont(font_family, font_size)
        self.setFont(font)

    def _load_members(self):
        """Load members into the member selector and list."""
        members = self.system_db.get_all_members()

        # Update member list widget
        self.member_list.load_members()

        # Update member selector
        self.member_selector.clear()
        for member in members:
            self.member_selector.addItem(member['name'], member['id'])

        # Select first member if available
        if members:
            self.member_selector.setCurrentIndex(0)
            self.current_member_id = members[0]['id']

    def _load_chat_history(self):
        """Load chat history."""
        self.chat_display.load_history()

    def _on_member_selected(self, member_id: int):
        """Handle member selection from the list."""
        self.current_member_id = member_id

        # Update selector to match
        for i in range(self.member_selector.count()):
            if self.member_selector.itemData(i) == member_id:
                self.member_selector.setCurrentIndex(i)
                break

        self.statusBar().showMessage(f"Selected member: {self._get_member_name(member_id)}")

    def _on_member_selector_changed(self, index: int):
        """Handle member selector change."""
        if index >= 0:
            self.current_member_id = self.member_selector.itemData(index)

    def _on_member_edit(self, member_id: int):
        """Handle double-click on member to edit."""
        self._show_member_manager(member_id)

    def _on_message_text_changed(self, text: str):
        """Handle message text changes for proxy detection."""
        if not text:
            self.proxy_indicator.setText("")
            return

        # Detect proxy
        detected = self.proxy_detector.detect_proxy(text)

        if detected:
            member_name = self._get_member_name(detected['member_id'])
            self.proxy_indicator.setText(f"✓ Detected: {member_name}")

            # Auto-switch member
            for i in range(self.member_selector.count()):
                if self.member_selector.itemData(i) == detected['member_id']:
                    self.member_selector.setCurrentIndex(i)
                    break
        else:
            self.proxy_indicator.setText("")

    def _send_message(self):
        """Send a message."""
        text = self.message_input.text().strip()
        if not text:
            return

        if self.current_member_id is None:
            QMessageBox.warning(self, "No Member Selected", "Please select a member to send as.")
            return

        # Remove proxy tags if detected
        detected = self.proxy_detector.detect_proxy(text)
        if detected:
            text = detected['message']

        # Save message to database
        self.system_db.add_message(self.current_member_id, text)

        # Display message in chat
        self.chat_display.add_message(self.current_member_id, text)

        # Clear input
        self.message_input.clear()
        self.proxy_indicator.setText("")

        # Scroll to bottom
        self.chat_display.scroll_to_bottom()

    def _get_member_name(self, member_id: int) -> str:
        """Get member name by ID."""
        member = self.system_db.get_member(member_id)
        return member['name'] if member else "Unknown"

    def _show_new_member_dialog(self):
        """Show dialog to create a new member."""
        dialog = MemberManagerDialog(self.system_db, parent=self)
        if dialog.exec():
            self._load_members()
            self.statusBar().showMessage("New member created")

    def _show_member_manager(self, member_id: int = None):
        """Show member management dialog."""
        dialog = MemberManagerDialog(self.system_db, member_id, parent=self)
        if dialog.exec():
            self._load_members()
            self.chat_display.refresh()
            self.statusBar().showMessage("Members updated")

    def _show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.app_db, self.theme_manager, parent=self)
        if dialog.exec():
            self._load_settings()
            self.statusBar().showMessage("Settings saved")

    def _show_pluralkit_sync(self):
        """Show PluralKit sync dialog."""
        dialog = PluralKitSyncDialog(self.app_db, self.system_db, parent=self)
        if dialog.exec():
            self._load_members()
            self.statusBar().showMessage("PluralKit sync completed")

    def _show_diary(self):
        """Show diary dialog."""
        if self.current_member_id is None:
            QMessageBox.warning(self, "No Member Selected", "Please select a member to view their diary.")
            return

        dialog = DiaryDialog(self.system_db, self.current_member_id, parent=self)
        dialog.exec()

    def _show_help(self):
        """Show help dialog."""
        dialog = HelpDialog(parent=self)
        dialog.exec()

    def _show_about(self):
        """Show about dialog."""
        dialog = AboutDialog(parent=self)
        dialog.exec()

    def _export_system_data(self):
        """Export system data to JSON."""
        # TODO: Implement export functionality
        QMessageBox.information(self, "Export", "Export functionality coming soon!")

    def _import_system_data(self):
        """Import system data from JSON."""
        # TODO: Implement import functionality
        QMessageBox.information(self, "Import", "Import functionality coming soon!")

    def closeEvent(self, event):
        """Handle window close event."""
        # Save window geometry
        self.app_db.set_setting("window_geometry", self.saveGeometry())

        logger.info("MainWindow closed")
        event.accept()
