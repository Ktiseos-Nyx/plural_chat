"""Chat display widget with rich text support."""

import logging
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import QTextBrowser
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import (
    QTextCursor, QTextCharFormat, QColor, QFont,
    QTextImageFormat, QImage, QPixmap
)

logger = logging.getLogger(__name__)


class ChatDisplay(QTextBrowser):
    """Rich text chat display widget."""

    def __init__(self, system_db, parent=None):
        super().__init__(parent)
        self.system_db = system_db

        # Configure widget
        self.setReadOnly(True)
        self.setOpenExternalLinks(False)
        self.setOpenLinks(False)

        # Avatar cache
        self.avatar_cache = {}

        # Load custom stylesheet
        self._apply_style()

    def _apply_style(self):
        """Apply custom styling to the chat display."""
        self.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11pt;
            }
        """)

    def load_history(self, limit: int = 100):
        """Load chat history from database."""
        self.clear()
        messages = self.system_db.get_recent_messages(limit)

        for msg in messages:
            self.add_message(
                msg['member_id'],
                msg['message'],
                msg['timestamp'],
                scroll=False
            )

        self.scroll_to_bottom()

    def add_message(self, member_id: int, message: str, timestamp=None, scroll=True):
        """Add a message to the chat display."""
        member = self.system_db.get_member(member_id)
        if not member:
            logger.warning(f"Member {member_id} not found")
            return

        # Use current time if not provided
        if timestamp is None:
            timestamp = datetime.now()
        elif isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except ValueError:
                timestamp = datetime.now()

        # Move cursor to end
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Add spacing if not first message
        if not cursor.atStart():
            cursor.insertBlock()

        # Create message container
        self._insert_message_html(cursor, member, message, timestamp)

        if scroll:
            self.scroll_to_bottom()

    def _insert_message_html(self, cursor, member, message, timestamp):
        """Insert a formatted message using HTML."""
        # Get member color
        member_color = member.get('color', '#6c757d')
        member_name = member.get('name', 'Unknown')
        member_pronouns = member.get('pronouns', '')

        # Format timestamp
        time_str = timestamp.strftime("%I:%M %p")

        # Build HTML for message
        html = f"""
        <div style="margin-bottom: 15px;">
            <div style="margin-bottom: 5px;">
                <span style="color: {member_color}; font-weight: bold; font-size: 11pt;">
                    {member_name}
                </span>
                {f'<span style="color: #6c757d; font-size: 9pt;"> ({member_pronouns})</span>' if member_pronouns else ''}
                <span style="color: #999; font-size: 9pt; margin-left: 10px;">
                    {time_str}
                </span>
            </div>
            <div style="margin-left: 20px; color: #333; font-size: 10pt;">
                {self._format_message_text(message)}
            </div>
        </div>
        """

        cursor.insertHtml(html)

    def _format_message_text(self, text: str) -> str:
        """Format message text (escape HTML, handle links, etc.)."""
        # Escape HTML
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')

        # Convert newlines to <br>
        text = text.replace('\n', '<br>')

        # TODO: Add link detection and formatting
        # TODO: Add markdown support if desired

        return text

    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat."""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def refresh(self):
        """Refresh the chat display."""
        self.load_history()

    def clear(self):
        """Clear the chat display."""
        super().clear()
        self.avatar_cache.clear()
