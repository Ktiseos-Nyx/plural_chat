"""PluralKit sync dialog with progress feedback."""

import logging
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QTextEdit,
    QProgressBar, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from pluralkit_api import PluralKitAPI

logger = logging.getLogger(__name__)


class SyncWorker(QThread):
    """Worker thread for PluralKit sync operations."""

    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, api_token, system_db):
        super().__init__()
        self.api_token = api_token
        self.system_db = system_db

    def run(self):
        """Run the sync operation."""
        try:
            self.progress.emit("Connecting to PluralKit...")
            api = PluralKitAPI(self.api_token)

            # Test connection
            success, message = api.test_connection()
            if not success:
                self.finished.emit(False, f"Failed to connect to PluralKit API: {message}")
                return

            self.progress.emit("Fetching system information...")
            system_info = api.get_system_info()
            if not system_info:
                self.finished.emit(False, "Failed to fetch system information")
                return

            # Save system name
            system_name = system_info.get('name', 'Unknown System')
            self.system_db.set_system_info('name', system_name)

            self.progress.emit("Fetching members...")
            members = api.get_members()
            if members is None:
                self.finished.emit(False, "Failed to fetch members")
                return

            if len(members) == 0:
                self.progress.emit("No members found in PluralKit system")
                self.finished.emit(True, "No members to import")
                return

            self.progress.emit(f"Found {len(members)} members from PluralKit:")
            self.progress.emit("")

            # Log and display member names for debugging
            logger.info(f"PluralKit returned {len(members)} members:")
            for member in members:
                name = member.get('name', 'Unknown')
                pk_id = member.get('id', 'no-id')
                logger.info(f"  - {name} (ID: {pk_id})")
                self.progress.emit(f"  • {name}")

            self.progress.emit("")
            self.progress.emit("Starting import...")

            # Track counts
            added_count = 0
            updated_count = 0
            avatar_count = 0

            # Import each member
            for i, member in enumerate(members):
                member_name = member.get('name', 'Unknown')
                self.progress.emit(f"Importing {i+1}/{len(members)}: {member_name}")

                # Prepare member data
                proxy_tags = member.get('proxy_tags', [])
                proxy_tags_json = json.dumps(proxy_tags) if proxy_tags else None

                # Download avatar if available
                avatar_path = None
                avatar_url = member.get('avatar_url')
                if avatar_url:
                    self.progress.emit(f"  Downloading avatar for {member_name}...")
                    avatar_path = api.download_avatar(avatar_url, member_name)
                    if avatar_path:
                        self.progress.emit(f"  ✓ Avatar downloaded")
                        avatar_count += 1
                    else:
                        self.progress.emit(f"  ⚠ Avatar download failed")

                member_data = {
                    'name': member.get('name'),
                    'pronouns': member.get('pronouns'),
                    'color': '#' + member.get('color', '6c757d') if member.get('color') else '#6c757d',
                    'description': member.get('description'),
                    'pk_id': member.get('id'),
                    'avatar_path': avatar_path,
                    'proxy_tags': proxy_tags_json
                }

                # Check if member already exists (by PK ID or name)
                existing = self.system_db.get_member_by_pk_id(member_data['pk_id'])
                if not existing:
                    # Also check by name
                    existing = self.system_db.get_member_by_name(member_data['name'])

                if existing:
                    # Update existing member (remove 'name' to avoid unique constraint)
                    update_data = {k: v for k, v in member_data.items() if k != 'name'}
                    self.system_db.update_member(existing['id'], **update_data)
                    self.progress.emit(f"  ✓ Updated: {member_name}")
                    updated_count += 1
                else:
                    # Add new member
                    self.system_db.add_member(**member_data)
                    self.progress.emit(f"  ✓ Added: {member_name}")
                    added_count += 1

            self.progress.emit("")
            self.progress.emit("=" * 50)
            self.progress.emit("Sync completed successfully!")
            self.progress.emit(f"Added: {added_count} members")
            self.progress.emit(f"Updated: {updated_count} members")
            self.progress.emit(f"Avatars downloaded: {avatar_count}")
            self.progress.emit("=" * 50)

            summary = f"Sync complete! Added {added_count}, Updated {updated_count}, Avatars {avatar_count}"
            self.finished.emit(True, summary)

        except Exception as e:
            logger.error(f"Sync error: {e}")
            self.finished.emit(False, str(e))


class PluralKitSyncDialog(QDialog):
    """Dialog for syncing with PluralKit."""

    def __init__(self, app_db, system_db, parent=None):
        super().__init__(parent)
        self.app_db = app_db
        self.system_db = system_db
        self.worker = None

        self.setWindowTitle("PluralKit Sync")
        self.setMinimumWidth(600)
        self.setMinimumHeight(450)

        self._setup_ui()
        self._load_saved_token()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Info
        info_group = QGroupBox("PluralKit Integration")
        info_layout = QVBoxLayout()

        info_text = QLabel(
            "Sync your system members from PluralKit. You'll need your PluralKit API token.\n\n"
            "To get your token:\n"
            "1. Go to https://pluralkit.me/dash\n"
            "2. Click 'Get API Token'\n"
            "3. Copy and paste it below"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Token input
        token_group = QGroupBox("API Token")
        token_layout = QFormLayout()

        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setPlaceholderText("Enter your PluralKit API token")
        token_layout.addRow("Token:", self.token_input)

        show_token_button = QPushButton("Show/Hide Token")
        show_token_button.clicked.connect(self._toggle_token_visibility)
        token_layout.addRow("", show_token_button)

        token_group.setLayout(token_layout)
        layout.addWidget(token_group)

        # Progress
        progress_group = QGroupBox("Sync Progress")
        progress_layout = QVBoxLayout()

        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setMaximumHeight(150)
        progress_layout.addWidget(self.progress_text)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.sync_button = QPushButton("Start Sync")
        self.sync_button.clicked.connect(self._start_sync)
        self.sync_button.setDefault(True)
        button_layout.addWidget(self.sync_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _load_saved_token(self):
        """Load saved API token."""
        token = self.app_db.get_encrypted_setting('pk_token')
        if token:
            self.token_input.setText(token)

    def _toggle_token_visibility(self):
        """Toggle token visibility."""
        if self.token_input.echoMode() == QLineEdit.EchoMode.Password:
            self.token_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.token_input.setEchoMode(QLineEdit.EchoMode.Password)

    def _start_sync(self):
        """Start the sync process."""
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "Validation Error", "Please enter your PluralKit API token.")
            return

        # Save token
        self.app_db.set_encrypted_setting('pk_token', token)

        # Disable button
        self.sync_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_text.clear()

        # Start worker thread
        self.worker = SyncWorker(token, self.system_db)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, message: str):
        """Handle progress updates."""
        self.progress_text.append(message)
        # Scroll to bottom
        scrollbar = self.progress_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_finished(self, success: bool, message: str):
        """Handle sync completion."""
        self.progress_bar.setVisible(False)
        self.sync_button.setEnabled(True)

        if success:
            QMessageBox.information(self, "Sync Complete", message)
            self.accept()
        else:
            QMessageBox.critical(self, "Sync Failed", message)
