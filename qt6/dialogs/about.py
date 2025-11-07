"""About dialog."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextBrowser
from PyQt6.QtCore import Qt


class AboutDialog(QDialog):
    """About dialog showing application information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Plural Chat")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Plural Chat")
        title.setStyleSheet("QLabel { font-size: 24pt; font-weight: bold; }")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Version
        version = QLabel("Version 0.2.0 (PyQt6)")
        version.setStyleSheet("QLabel { font-size: 12pt; color: #6c757d; }")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        # Description
        description = QTextBrowser()
        description.setReadOnly(True)
        description.setOpenExternalLinks(True)
        description.setHtml("""
            <div style="padding: 20px;">
                <h3>A Desktop Chat Application for Plural Systems</h3>

                <p>Plural Chat provides a private, local environment for system members
                to communicate with each other. Built specifically for plural systems
                (people with DID, OSDD, or other forms of plurality).</p>

                <h4>Features:</h4>
                <ul>
                    <li>Private internal communication between system members</li>
                    <li>Integration with PluralKit</li>
                    <li>Offline-first design with local data storage</li>
                    <li>Personal diary system for each member</li>
                    <li>Customizable themes and appearance</li>
                    <li>Smart proxy detection for auto-switching</li>
                </ul>

                <h4>Links:</h4>
                <ul>
                    <li><a href="https://github.com/Ktiseos-Nyx/plural_chat">GitHub Repository</a></li>
                    <li><a href="https://pluralkit.me">PluralKit</a></li>
                </ul>

                <h4>License:</h4>
                <p>MIT License - Free and Open Source</p>

                <h4>Credits:</h4>
                <p>Built with PyQt6 and love for the plural community ❤️</p>
            </div>
        """)
        layout.addWidget(description)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
