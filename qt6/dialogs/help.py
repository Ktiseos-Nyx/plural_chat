"""Help dialog."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTextBrowser
from PyQt6.QtCore import Qt


class HelpDialog(QDialog):
    """Help dialog showing usage instructions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plural Chat - Help")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Help content
        help_text = QTextBrowser()
        help_text.setReadOnly(True)
        help_text.setOpenExternalLinks(True)
        help_text.setHtml("""
            <div style="padding: 20px;">
                <h2>Plural Chat - User Guide</h2>

                <h3>Getting Started</h3>
                <p>Welcome to Plural Chat! This application provides a private space for
                system members to communicate with each other.</p>

                <h3>Basic Usage</h3>

                <h4>Sending Messages</h4>
                <ol>
                    <li>Select a member from the "Sending as" dropdown</li>
                    <li>Type your message in the input box</li>
                    <li>Press Enter or click "Send"</li>
                </ol>

                <h4>Managing Members</h4>
                <ul>
                    <li><b>Add New Member:</b> File → New Member (or Ctrl+N)</li>
                    <li><b>Edit Member:</b> Double-click on a member in the list</li>
                    <li><b>Delete Member:</b> Open member editor and click "Delete"</li>
                </ul>

                <h3>Proxy Tags</h3>
                <p>Proxy tags allow automatic member detection when typing. For example,
                if you set a member's proxy as <code>[name:</code> and <code>]</code>,
                typing <code>[name: hello]</code> will automatically switch to that member
                and send "hello".</p>

                <h4>Setting Up Proxy Tags</h4>
                <ol>
                    <li>Open member editor (double-click member or Edit Member)</li>
                    <li>Enter prefix (e.g., <code>[alex:</code>)</li>
                    <li>Enter suffix (e.g., <code>]</code>)</li>
                    <li>Save the member</li>
                </ol>

                <h3>PluralKit Integration</h3>
                <p>Sync your system from PluralKit to import all your members,
                avatars, and proxy tags automatically.</p>

                <h4>Getting Your PluralKit Token</h4>
                <ol>
                    <li>Visit <a href="https://pluralkit.me/dash">pluralkit.me/dash</a></li>
                    <li>Click "Get API Token"</li>
                    <li>Copy the token</li>
                    <li>In Plural Chat: PluralKit → Sync with PluralKit</li>
                    <li>Paste your token and click "Start Sync"</li>
                </ol>

                <h3>Diary System</h3>
                <p>Each member can maintain their own private diary entries.</p>

                <h4>Using the Diary</h4>
                <ol>
                    <li>Select a member from the list</li>
                    <li>Go to Members → Diary (or Ctrl+D)</li>
                    <li>Click "New Entry" to create an entry</li>
                    <li>Enter title and content</li>
                    <li>Click "Save Entry"</li>
                </ol>

                <h3>Customization</h3>

                <h4>Themes</h4>
                <ul>
                    <li>Go to Settings → Preferences</li>
                    <li>Choose from Light, Dark, Blue, Purple, or Green themes</li>
                    <li>Click "Save" to apply</li>
                </ul>

                <h4>Fonts</h4>
                <ul>
                    <li>Go to Settings → Preferences</li>
                    <li>Select font family and size</li>
                    <li>Click "Save"</li>
                </ul>

                <h3>Member Customization</h3>
                <ul>
                    <li><b>Name:</b> Display name for the member</li>
                    <li><b>Pronouns:</b> Member's pronouns (optional)</li>
                    <li><b>Color:</b> Member's color in chat messages</li>
                    <li><b>Avatar:</b> Profile picture for the member</li>
                    <li><b>Description:</b> Notes or description about the member</li>
                    <li><b>Proxy Tags:</b> Automatic detection patterns</li>
                </ul>

                <h3>Data Storage</h3>
                <p>All your data is stored locally on your computer in SQLite databases:</p>
                <ul>
                    <li><b>app.db:</b> Application settings and preferences</li>
                    <li><b>system.db:</b> System members, messages, and diary entries</li>
                    <li><b>avatars/:</b> Downloaded avatar images</li>
                </ul>

                <h3>Privacy & Security</h3>
                <ul>
                    <li>All data is stored locally - nothing is sent to any servers
                        except PluralKit during sync</li>
                    <li>API tokens are encrypted using industry-standard encryption</li>
                    <li>No telemetry or tracking</li>
                </ul>

                <h3>Keyboard Shortcuts</h3>
                <table border="1" cellpadding="5" style="border-collapse: collapse;">
                    <tr>
                        <td><b>Ctrl+N</b></td>
                        <td>New Member</td>
                    </tr>
                    <tr>
                        <td><b>Ctrl+M</b></td>
                        <td>Manage Members</td>
                    </tr>
                    <tr>
                        <td><b>Ctrl+D</b></td>
                        <td>Open Diary</td>
                    </tr>
                    <tr>
                        <td><b>Ctrl+P</b></td>
                        <td>PluralKit Sync</td>
                    </tr>
                    <tr>
                        <td><b>Ctrl+Q</b></td>
                        <td>Quit</td>
                    </tr>
                    <tr>
                        <td><b>F1</b></td>
                        <td>Help (this window)</td>
                    </tr>
                </table>

                <h3>Troubleshooting</h3>

                <h4>Members Not Showing Up</h4>
                <ul>
                    <li>Make sure you've added members via File → New Member</li>
                    <li>Try restarting the application</li>
                </ul>

                <h4>PluralKit Sync Failing</h4>
                <ul>
                    <li>Check your internet connection</li>
                    <li>Verify your API token is correct</li>
                    <li>Make sure PluralKit is online</li>
                </ul>

                <h4>Avatars Not Displaying</h4>
                <ul>
                    <li>Check the avatar file path is correct</li>
                    <li>Supported formats: PNG, JPG, JPEG, GIF, WebP</li>
                    <li>Try re-selecting the avatar image</li>
                </ul>

                <h3>Support</h3>
                <p>For issues, bug reports, or feature requests:</p>
                <ul>
                    <li>GitHub: <a href="https://github.com/Ktiseos-Nyx/plural_chat">
                        github.com/Ktiseos-Nyx/plural_chat</a></li>
                </ul>
            </div>
        """)
        layout.addWidget(help_text)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
