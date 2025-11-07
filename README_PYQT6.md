# Plural Chat - PyQt6 Version

A modern, desktop chat application for plural systems with PluralKit integration - now rebuilt with PyQt6!

![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-red.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

## ✨ What's New in PyQt6 Version

- **Modern UI**: Polished, professional interface with smooth animations
- **Rich Text Support**: Better message formatting and display
- **Improved Performance**: Faster rendering and better memory management
- **Better Themes**: 5 beautiful themes (Light, Dark, Blue, Purple, Green)
- **Threaded Operations**: PluralKit sync runs in background without freezing
- **Enhanced Dialogs**: Better layouts with inline help and validation
- **Keyboard Navigation**: Full keyboard shortcut support

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements-pyqt6.txt

# Run the application
python main_qt6.py
```

See [INSTALLATION_PYQT6.md](INSTALLATION_PYQT6.md) for detailed instructions.

### First Steps

1. **Create a member**: File → New Member (Ctrl+N)
2. **Start chatting**: Select member and type your message
3. **Optional**: Sync from PluralKit (PluralKit → Sync)

## 🎯 Features

### 💬 Chat Interface
- Clean, modern design
- Rich text message display
- Member avatars and colors
- Automatic timestamps
- Proxy tag detection

### 👥 Member Management
- Add/edit/delete members
- Custom avatars
- Member colors
- Pronouns support
- Proxy tags for auto-switching

### 📔 Diary System
- Personal diary for each member
- Create and edit entries
- Secure local storage
- Easy navigation

### 🔗 PluralKit Integration
- One-click system import
- Automatic member sync
- Avatar downloading
- Secure token storage
- Background sync with progress

### 🎨 Themes & Customization
- 5 built-in themes
- Custom font selection
- Adjustable font sizes
- Member color customization

## 📸 Screenshots

### Light Theme
```
┌─────────────────────────────────────────────────────┐
│ File  Members  PluralKit  Settings  Help            │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────┐  ┌─────────────────────────────┐    │
│  │ Members  │  │  Chat Display               │    │
│  │          │  │                              │    │
│  │ • Alex   │  │  Alex (they/them)  2:30 PM  │    │
│  │ • Jordan │  │    Hey everyone!             │    │
│  │ • Sam    │  │                              │    │
│  │          │  │  Jordan (she/her)  2:31 PM  │    │
│  │          │  │    Hi Alex!                  │    │
│  └──────────┘  └─────────────────────────────┘    │
│                                                      │
│  Sending as: [Alex ▼]      ✓ Detected: Alex        │
│  [Type your message...        ] [ Send ]           │
└─────────────────────────────────────────────────────┘
```

## 🔧 Technical Details

### Architecture
- **Frontend**: PyQt6 (Qt 6.6+)
- **Database**: SQLite3
- **Encryption**: Fernet (AES)
- **Image Processing**: Pillow
- **HTTP**: requests + aiohttp
- **Downloads**: aria2p

### Project Structure
```
plural_chat/
├── main_qt6.py              # PyQt6 entry point
├── qt6/                     # PyQt6 implementation
│   ├── main_window.py       # Main application window
│   ├── widgets/             # Custom widgets
│   │   ├── chat_display.py  # Rich text chat display
│   │   └── member_list.py   # Member list with avatars
│   ├── dialogs/             # Dialog windows
│   │   ├── member_manager.py
│   │   ├── settings.py
│   │   ├── pluralkit_sync.py
│   │   ├── diary.py
│   │   ├── about.py
│   │   └── help.py
│   └── utils/               # Utility modules
│       ├── proxy_detector.py
│       ├── theme_manager.py
│       └── database_compat.py
├── database_manager.py      # Database layer (shared)
├── pluralkit_api.py        # PluralKit API client (shared)
└── requirements-pyqt6.txt  # PyQt6 dependencies
```

## 🆚 PyQt6 vs Original Version

| Feature | Original (tkinter) | PyQt6 |
|---------|-------------------|-------|
| UI Framework | ttkbootstrap | PyQt6 |
| Themes | 15+ bootstrap themes | 5 custom themes |
| Rich Text | Limited | Full HTML support |
| Performance | Good | Excellent |
| Threading | Basic | Advanced (QThread) |
| Animations | None | Smooth transitions |
| Dialogs | Basic | Polished & intuitive |

**Recommendation**: Use PyQt6 version for better performance and modern UI. Original version still available in `main.py`.

## 🔐 Privacy & Security

- **Local Storage**: All data stored on your computer
- **Encrypted Tokens**: API tokens encrypted with AES
- **No Telemetry**: No tracking or analytics
- **Open Source**: Full code transparency

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Member |
| `Ctrl+M` | Manage Members |
| `Ctrl+D` | Open Diary |
| `Ctrl+P` | PluralKit Sync |
| `Ctrl+,` | Settings |
| `Ctrl+Q` | Quit |
| `F1` | Help |

## 🐛 Troubleshooting

### Can't install PyQt6?
```bash
# Try updating pip first
python -m pip install --upgrade pip
pip install PyQt6
```

### PluralKit sync not working?
1. Check internet connection
2. Verify token at https://pluralkit.me/dash
3. Check `plural_chat.log` for errors

### Avatars not showing?
- Supported formats: PNG, JPG, JPEG, GIF, WebP
- Try re-selecting the image
- Check file permissions

See [INSTALLATION_PYQT6.md](INSTALLATION_PYQT6.md) for more troubleshooting tips.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Ktiseos-Nyx/plural_chat.git
cd plural_chat

# Install dependencies
pip install -r requirements-pyqt6.txt

# Run in development mode
python main_qt6.py
```

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **PluralKit Team** - For the amazing PluralKit API
- **Qt/PyQt Team** - For the excellent Qt framework
- **Plural Community** - For feedback and support

## 🔗 Links

- **GitHub**: https://github.com/Ktiseos-Nyx/plural_chat
- **PluralKit**: https://pluralkit.me
- **Issues**: https://github.com/Ktiseos-Nyx/plural_chat/issues

---

**Made with ❤️ for the plural community**

*If you find Plural Chat useful, please star the repository! ⭐*
