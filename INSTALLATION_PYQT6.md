# Plural Chat - PyQt6 Version Installation Guide

This guide will help you install and run the new PyQt6 version of Plural Chat.

## Requirements

- Python 3.8 or higher
- pip (Python package manager)
- At least 100MB of free disk space

## Installation Steps

### 1. Install Python Dependencies

First, install the required Python packages:

```bash
pip install -r requirements-pyqt6.txt
```

Or install individually:

```bash
pip install PyQt6>=6.6.0
pip install PyQt6-WebEngine>=6.6.0
pip install Pillow>=10.0.0
pip install requests>=2.32.0
pip install cryptography>=41.0.0
pip install aiohttp>=3.8.0
pip install aria2p>=0.12.0
```

### 2. Run the Application

Once dependencies are installed, you can run Plural Chat:

```bash
python main_qt6.py
```

Or make it executable (Linux/macOS):

```bash
chmod +x main_qt6.py
./main_qt6.py
```

## First Run

When you first run Plural Chat PyQt6:

1. **Create Your First Member**
   - Go to File → New Member (or press Ctrl+N)
   - Fill in member details (name is required)
   - Optionally add an avatar, color, pronouns, and proxy tags
   - Click "Save"

2. **Optional: Sync from PluralKit**
   - If you have a PluralKit system, you can import it
   - Go to PluralKit → Sync with PluralKit
   - Get your API token from https://pluralkit.me/dash
   - Paste it in the dialog and click "Start Sync"
   - Your members, avatars, and proxy tags will be imported

3. **Start Chatting**
   - Select a member from the dropdown or member list
   - Type your message in the input box
   - Press Enter or click "Send"

## Features

### Chat Interface
- Clean, modern UI with rich text support
- Member avatars displayed in chat
- Color-coded member names
- Timestamps for all messages
- Smooth scrolling

### Member Management
- Add, edit, and delete members
- Custom avatars (PNG, JPG, WebP, etc.)
- Member colors for chat display
- Pronouns support
- Custom descriptions
- Proxy tag configuration

### Proxy Tags
Proxy tags allow automatic member switching:
- Set prefix/suffix for each member (e.g., `[alex:` and `]`)
- Type `[alex: hello world]` and it auto-switches to Alex
- The message "hello world" is sent without the proxy tags

### PluralKit Integration
- One-click sync with your PluralKit system
- Imports all members, avatars, and proxy tags
- Secure encrypted token storage
- Background sync with progress feedback

### Diary System
- Personal diary for each member
- Create, edit, and delete entries
- Timestamps automatically added
- Search functionality (coming soon)

### Themes
Choose from 5 built-in themes:
- **Light** - Clean white background
- **Dark** - Easy on the eyes
- **Blue** - Calming blue tones
- **Purple** - Vibrant purple palette
- **Green** - Nature-inspired greens

Go to Settings → Preferences to change themes.

### Customization
- Change font family and size
- Adjust window size (saved automatically)
- Customize member colors
- Set personalized proxy tags

## Data Storage

All your data is stored locally:

- **app.db** - Application settings and preferences
- **system.db** - Members, messages, and diary entries
- **avatars/** - Downloaded avatar images
- **.app_key** - Encryption key for API tokens

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Member |
| Ctrl+M | Manage Members |
| Ctrl+D | Open Diary |
| Ctrl+P | PluralKit Sync |
| Ctrl+Q | Quit Application |
| F1 | Help |

## Troubleshooting

### PyQt6 Installation Issues

**On Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-pyqt6
```

**On macOS with Homebrew:**
```bash
brew install pyqt6
```

**On Windows:**
PyQt6 should install fine with pip. If not, try:
```bash
python -m pip install --upgrade pip
pip install PyQt6
```

### Database Errors

If you see database errors, try:
1. Delete `app.db` and `system.db` (you'll lose data)
2. Restart the application

### Avatar Loading Issues

If avatars don't show:
1. Check the file path is correct
2. Ensure the image format is supported (PNG, JPG, WebP)
3. Try re-selecting the avatar image

### PluralKit Sync Failing

1. Check your internet connection
2. Verify your API token at https://pluralkit.me/dash
3. Make sure PluralKit is online
4. Check the logs in `plural_chat.log`

## Differences from Original Version

The PyQt6 version has several improvements over the original tkinter version:

### New Features
- ✨ Modern, polished UI with better visual design
- ✨ Rich text support in chat display
- ✨ Better avatar rendering and caching
- ✨ Smooth animations and transitions
- ✨ Threaded PluralKit sync (no UI freezing)
- ✨ Improved theme system with more options
- ✨ Better keyboard navigation

### Performance
- 🚀 Faster rendering and scrolling
- 🚀 Better memory management
- 🚀 Efficient avatar caching
- 🚀 Background operations don't block UI

### Usability
- 👍 Intuitive dialog layouts
- 👍 Better error messages
- 👍 Inline help text
- 👍 Progress feedback for long operations

## Migration from Original Version

If you're migrating from the original tkinter version:

1. Your existing `app.db` and `system.db` will work with the PyQt6 version
2. No data migration needed
3. Simply run `python main_qt6.py` instead of `python main.py`
4. All your members, messages, and settings will be preserved

## Support and Contributing

- **Issues:** https://github.com/Ktiseos-Nyx/plural_chat/issues
- **Discussions:** https://github.com/Ktiseos-Nyx/plural_chat/discussions

## License

MIT License - See LICENSE file for details

---

**Enjoy using Plural Chat! 💜**
