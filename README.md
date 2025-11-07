# 🌐 Plural Chat - Web Edition

A modern web-based chat application with multi-persona support, AI image generation, and real-time communication. **Perfect for plural systems, roleplayers, writers, or anyone who wants a personal chat space!**

> **Note:** This branch contains the web edition. The desktop versions have been moved to separate branches.

## 👥 Who Is This For?

- **Plural Systems** - Manage system members with optional PluralKit sync
- **Roleplayers** - Create and chat as different characters
- **Writers** - Develop characters through conversation
- **Solo Users** - Just want a private, customizable chat app
- **Anyone** - No plural system required! Works great for everyone!

## 🚀 Quick Start

The Plural Chat web edition is located in the `web/` directory. Please see the comprehensive documentation there:

**📖 [Web Edition Documentation](web/README.md)**

## ✨ Key Features

### 🎭 Character/Persona System ⭐ MAIN FEATURE!
- **Create unlimited characters** - No external service needed!
- **Full character profiles** - Name, pronouns, avatar, color, bio, proxy tags
- **Easy management** - Create, edit, delete via API or commands
- **Quick switching** - `/switch CharacterName` or auto-switch with proxy tags
- **100% independent** - No PluralKit or external service required!
- **Perfect for:**
  - 🎭 Roleplayers with multiple characters
  - ✍️ Writers developing character voices
  - 👥 Plural systems managing members
  - 🎮 Gamers with different personas
  - 🎨 Anyone wanting multiple chat profiles!

**📖 [Complete Character System Guide →](CHARACTER_SYSTEM.md)**

### Chat & Communication
- **Real-time messaging**: WebSocket-based instant messaging
- **Character-based chat**: Message as any of your created characters
- **Discord-style commands**: `/switch`, `/member`, `/generate`, `/help`, and more
- **Proxy tag auto-switching**: Type `luna: hello!` → auto-switches to Luna
- **Export chat logs**: Download conversations in JSON, CSV, or TXT

### 🤖 AI Characters (NEW!)
- **Add AI-powered characters** - Chat with LLM-powered bots!
- **Multiple providers**: Google Gemini (FREE!), OpenAI, Claude, Ollama (local)
- **Custom personalities**: Create assistants, roleplay partners, writing helpers
- **Automatic responses**: Mention @BotName and they respond
- **Perfect for:**
  - 💬 Personal assistants
  - 🎭 Roleplay NPCs
  - ✍️ Writing partners
  - 🔍 Q&A helpers

**[📖 AI Characters Guide →](AI_CHARACTERS_GUIDE.md)**

### Authentication & Security
- **Multiple login methods**: Username/password, OAuth (Discord, Google, GitHub)
- **Email verification**: Secure account creation
- **Optional 2FA**: Two-factor authentication for enhanced security
- **Encrypted storage**: Fernet encryption for sensitive data

### Optional: PluralKit Import
- **Already have a PluralKit system?** Import it with one API call!
- Imports: members, avatars, proxy tags, colors, descriptions
- **Fully optional** - Create characters manually if you prefer
- **One-way or sync** - Your choice!
- [Learn more about PK sync →](web/FEATURES_ROADMAP.md#pluralkit-integration)

### AI Image Generation
- **Stable Diffusion integration**: Connect to Automatic1111, Forge UI, or ComfyUI
- **GPU rental support**: Perfect for RunPod and Vast.ai sessions
- **Ephemeral storage**: Generated images auto-delete after 24 hours
- **Share in chat**: AI generations posted directly to conversations

### Performance & Caching
- **Redis caching**: 10-100x performance improvement
- **Smart TTLs**: Sessions (30 days), members (1 hour), messages (15 minutes)
- **Rate limiting**: Protection against abuse
- **WebP compression**: Efficient image storage

## 📁 Repository Structure

```
plural_chat/
├── web/                          # Web edition (main application)
│   ├── backend/                  # FastAPI backend
│   │   ├── app/
│   │   │   ├── auth_enhanced.py  # Authentication system
│   │   │   ├── commands.py       # Discord-style commands
│   │   │   ├── sd_integration.py # Stable Diffusion API
│   │   │   ├── media_cache.py    # Ephemeral image storage
│   │   │   └── ...
│   │   └── requirements.txt
│   ├── frontend/                 # Next.js frontend (Lobe UI)
│   ├── docker-compose.yml
│   └── README.md                 # ← START HERE
│
├── AI_GENERATION_GUIDE.md        # SD integration guide
├── AUTH_SECURITY_SUMMARY.md      # Security overview
├── NEW_FEATURES_SUMMARY.md       # Feature summary
├── WEB_EDITION_COMPLETE.md       # Completion notes
└── ...

```

## 🎨 AI Image Generation

One of the standout features! Connect your temporary GPU rental to Plural Chat:

```bash
/sdconnect a1111 https://your-runpod-url.proxy.runpod.net
/generate portrait of Riley, purple hair, digital art
```

**Perfect for:**
- 🎨 Generating system member portraits
- 💸 GPU rental sessions (pay per hour)
- 🗑️ No permanent storage bloat (24hr auto-delete)
- 👥 Multiple systems sharing one GPU instance

**[Full AI Generation Guide](AI_GENERATION_GUIDE.md)**

## 📖 Documentation

**Start Here:**
- **[Character System Guide](CHARACTER_SYSTEM.md)** ⭐ - Create and manage characters
- **[AI Characters Guide](AI_CHARACTERS_GUIDE.md)** 🤖 - Add LLM-powered bots!
- **[Deployment Guide](DEPLOYMENT.md)** - Railway, Docker, VPS, Cloudflare Tunnel
- **[Web Edition Docs](web/README.md)** - Main documentation

**Guides:**
- **[AI Image Generation](AI_GENERATION_GUIDE.md)** - Stable Diffusion + GPU rentals
- **[Getting Started](web/GETTING_STARTED.md)** - First-time setup
- **[Admin Guide](web/ADMIN_GUIDE.md)** - Admin panel "for numptys"

**Technical:**
- **[Authentication Design](web/AUTHENTICATION_REDESIGN.md)** - Auth system overview
- **[Security Documentation](web/SECURITY.md)** - Security best practices
- **[Features Roadmap](web/FEATURES_ROADMAP.md)** - All features documented

## 🔧 Technology Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **Socket.IO** - Real-time WebSocket communication
- **SQLAlchemy** - ORM for database
- **Redis** - Caching and session storage
- **Bcrypt** - Password hashing
- **JWT** - Token-based authentication

### Frontend
- **Next.js 14** - React framework
- **Lobe UI** - Modern chat interface components
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first styling

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **PostgreSQL** - Production database
- **Nginx** - Reverse proxy

## 🚀 Deployment

### Quick Deploy

```bash
cd web
docker-compose up -d
```

Visit `http://localhost:3000`

### Production Deployment

See **[Deployment Guide](web/DEPLOYMENT.md)** for:
- Railway deployment (one-click)
- VPS deployment (Docker)
- Environment configuration
- SSL/HTTPS setup
- Database migrations

## 🤝 Contributing

We welcome contributions from the plural community!

- 🐛 **Bug reports** - [GitHub Issues](https://github.com/Ktiseos-Nyx/plural_chat/issues)
- 💡 **Feature requests** - [GitHub Discussions](https://github.com/Ktiseos-Nyx/plural_chat/discussions)
- 🔧 **Code contributions** - See [Contributing Guide](CONTRIBUTING.md)
- 📖 **Documentation** - Help improve our docs

Please read our **[Code of Conduct](CODE_OF_CONDUCT.md)** before contributing.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

For third-party components and attributions, see [NOTICES.md](NOTICES.md).

## 💝 Credits

- **Created by:** Duskfall Portal Crew
- **Inspired by:** The amazing plural community
- **Thanks to:** PluralKit team for the fantastic API
- **UI Framework:** Lobe Chat UI team

## 🔗 Links

- **[GitHub Repository](https://github.com/Ktiseos-Nyx/plural_chat)** - Source code
- **[GitHub Issues](https://github.com/Ktiseos-Nyx/plural_chat/issues)** - Bug reports
- **[GitHub Discussions](https://github.com/Ktiseos-Nyx/plural_chat/discussions)** - Community Q&A
- **[PluralKit](https://pluralkit.me)** - The bot that inspired this project
- **[Support us on Ko-fi](https://ko-fi.com/duskfallcrew)** - Help keep development going
- **[Ktiseos Nyx Discord](https://discord.gg/HhBSvM9gBY)** - Development & AI Discord
- **[Earth & Dusk Media Discord](https://discord.gg/5t2kYxt7An)** - Twitch & Media Discord

## ⚡ What Makes This Special?

### 🎭 It's Like Geocities for Your Chat Personas!

Remember when you could customize everything? That energy, but for chat:

- **Create as many characters as you want** - No limits, no external services
- **Customize everything** - Colors, avatars, bios, pronouns
- **Switch instantly** - Be whoever you want, whenever
- **No gatekeeping** - Not just for plural systems!
- **Your data, your server** - Self-hostable, open source

**It's MSN Messenger meets forum roleplay meets personal expression!**

### "Hold Your Virtual Beer" Moment 🍺

The ephemeral AI image generation feature is **perfect** for GPU rental sessions:

1. 🎮 Rent a GPU for 1 hour ($0.20-0.50)
2. 🔗 Connect to Plural Chat
3. 🎨 Generate character portraits, scenes, anything!
4. 💬 Share generations in chat
5. 🗑️ Everything auto-deletes after 24 hours
6. 💸 Stop the GPU rental when done

**No permanent storage bloat. No wasted space. Just pure creative fun!**

### Security First

- Bcrypt password hashing (cost factor 12)
- Fernet encryption for sensitive tokens
- JWT with proper expiry
- Rate limiting against brute force
- Email verification
- Optional 2FA
- Session tracking
- HTTPS-only in production

**[Full Security Documentation](web/SECURITY.md)**

---

## 🎯 Get Started

Ready to dive in?

1. **[Read the Web Edition Docs](web/README.md)**
2. **[Follow the Getting Started Guide](web/GETTING_STARTED.md)**
3. **[Deploy with Docker Compose](web/DEPLOYMENT.md)**

---

*Made with 💜 by and for the plural community*
