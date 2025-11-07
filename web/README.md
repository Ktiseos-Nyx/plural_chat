# Plural Chat - Web Edition 🌐

A modern, self-hosted web chat application with multi-persona support, AI characters, and real-time communication. **Perfect for plural systems, roleplayers, writers, small groups, or anyone who wants a personal chat space!**

![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)

## ✨ Features

### 🎭 Character System ⭐
- **Create unlimited characters** - No external service needed!
- **Full profiles** - Name, pronouns, avatar, color, bio, proxy tags
- **Easy management** - API and Discord-style commands (`/switch`, `/member`)
- **Quick switching** - Swap characters instantly or use proxy tags
- **100% independent** - No PluralKit or external service required!

### 🤖 AI Characters (NEW!)
- **LLM-powered bots** - Chat with AI characters using Gemini, OpenAI, Claude, or Ollama!
- **Custom personalities** - Create assistants, roleplay NPCs, writing helpers, Q&A bots
- **Automatic responses** - Mention `@BotName` and they respond intelligently
- **Multiple providers** - Google Gemini (FREE!), OpenAI, Claude, or Ollama (local & private)
- **[📖 AI Characters Guide](../AI_CHARACTERS_GUIDE.md)**

### 💬 Chat & Communication
- **Real-time messaging** - WebSocket-powered instant chat
- **Discord-style commands** - `/switch`, `/member`, `/ai`, `/help`, and more
- **Proxy tag auto-switching** - Type `luna: hello!` → auto-switches to Luna
- **Export chat logs** - Download conversations in JSON, CSV, or TXT

### 🔗 Optional: PluralKit Import
- **Already have a PluralKit system?** Import it with one API call!
- Imports members, avatars, proxy tags, colors, descriptions
- **Fully optional** - Create characters manually if you prefer

### 🎨 Additional Features
- **Beautiful UI** - Built with LobeHub UI components
- **Multi-User** - Multiple people can use the same instance (5-10 users recommended)
- **Self-Hosted** - Full control over your data
- **Easy Deployment** - One-click deploy to Railway or Docker
- **AI Image Generation** - Connect to Stable Diffusion (Automatic1111/Forge/ComfyUI)
- **Authentication** - Username/password, OAuth (Discord, Google, GitHub), email verification
- **Redis Caching** - 10-100x performance boost with smart caching

## 🚀 Quick Deploy

### Deploy to Railway (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/plural-chat)

1. Click the button above
2. Set your environment variables:
   - `SECRET_KEY` - Generate a random secret key
   - `DB_PASSWORD` - Set a secure database password
3. Wait for deployment to complete
4. Visit your app URL and login with your PluralKit token!

### Local Development with Docker

```bash
# Clone the repository
git clone https://github.com/Ktiseos-Nyx/plural_chat.git
cd plural_chat/web

# Start all services
docker-compose -f docker-compose.dev.yml up

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### Backend Setup

```bash
cd web/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run the server
uvicorn main:app --reload
```

#### Frontend Setup

```bash
cd web/frontend

# Install dependencies
npm install

# Set up environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_WS_URL=http://localhost:8000" >> .env.local

# Run the development server
npm run dev
```

## 📖 Usage

### First Time Setup

1. **Create an Account**
   - Open your deployed Plural Chat instance
   - Sign up with username/password or OAuth (Discord, Google, GitHub)
   - Verify your email (if enabled)

2. **Create Your Characters**

   **Option A: Create Manually** (No external service needed!)
   ```
   /member create Luna she/her
   /member Luna avatar https://example.com/luna.png
   /member Luna color #9b59b6
   /member Luna description "A wise character who loves stargazing"
   ```

   **Option B: Import from PluralKit** (Optional)
   - Get your PluralKit token from https://pluralkit.me/dash
   - Use API endpoint: `POST /api/pluralkit/import` with your token
   - All members, avatars, and proxy tags imported automatically

3. **Start Chatting!**
   - Select a character from the sidebar
   - Type your message
   - Press Enter to send
   - Or use proxy tags: `luna: hello everyone!`

4. **Add AI Characters** (Optional)
   ```
   /ai create Assistant gemini YOUR_API_KEY "You are a helpful assistant"
   @Assistant what's the capital of France?
   ```
   See the **[AI Characters Guide](../AI_CHARACTERS_GUIDE.md)** for more!

### Useful Commands

- `/switch CharacterName` - Switch active character
- `/member list` - List all your characters
- `/member create Name pronouns` - Create new character
- `/ai create Name provider key personality` - Create AI character
- `/help` - Show all available commands

### Multi-User Setup

Multiple people can use the same instance! Perfect for:
- Small friend groups (5-10 people recommended)
- Shared roleplaying spaces
- Private communities
- Discord alternative for small groups
- Collaborative creative writing

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Next.js    │────▶│   FastAPI    │────▶│  PostgreSQL  │
│   Frontend   │     │   Backend    │     │   Database   │
│              │◀────│   + WS       │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
      │                     │                     │
      └─────────────────────┴─────────────────────┘
              Docker Compose / Railway
```

### Tech Stack

**Frontend:**
- Next.js 16 (React 19)
- TypeScript
- LobeHub UI
- Zustand (State Management)
- Socket.IO Client
- Tailwind CSS
- Ant Design

**Backend:**
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Redis (Caching & Sessions)
- Socket.IO (WebSockets)
- Python-JOSE (JWT Auth)
- httpx (LLM API Integration)
- Bcrypt (Password Hashing)
- Cryptography (Fernet Encryption)
- Optional: PluralKit API Integration

**Deployment:**
- Docker & Docker Compose
- Railway (One-click deploy)
- Vercel (Frontend alternative)

## 🔐 Security Features

### Authentication & Authorization
- **JWT Authentication** - Secure token-based auth with HS256
- **Bcrypt Password Hashing** - Industry-standard password protection
- **OAuth 2.0** - Login with Discord, Google, or GitHub
- **Email Verification** - Optional email confirmation
- **Session Management** - Track active sessions with IP/user agent logging

### 🔒 Two-Factor Authentication (Optional)
- **TOTP-based 2FA** - Authenticator app support (Google Authenticator, Authy, etc.)
- **QR Code Setup** - Easy scanning for instant setup
- **Backup Codes** - 8 one-time recovery codes
- **Optional Security** - Users can enable/disable in profile settings
- **No SMS/Email** - More secure than SMS-based 2FA

### 📊 Audit Logging
- **Security Event Tracking** - All logins, 2FA changes, password updates logged
- **Failed Attempt Monitoring** - Track suspicious login attempts
- **IP & User Agent Logging** - Full context for security events
- **User-Accessible Logs** - View your own security history via API
- **Automatic Cleanup** - Old logs auto-deleted after 90 days

### Data Protection
- **Fernet Encryption** - PluralKit tokens & AI API keys encrypted at rest
- **SQL Injection Prevention** - SQLAlchemy parameterized queries
- **CORS Protection** - Configurable allowed origins
- **XSS Protection** - React auto-escaping
- **Path Traversal Prevention** - Filename sanitization

### Media & File Security
- **Ephemeral Storage** - Images auto-deleted after 24 hours
- **File Size Limits** - Configurable max upload size (default 10MB)
- **HTTPS-Only** - Rejects non-secure image URLs
- **Image Validation** - Pillow verification of actual file format

### Rate Limiting
- **Redis-Based** - Intelligent rate limiting per endpoint
- **Login Protection** - Prevent brute force attacks
- **Configurable Limits** - Per-endpoint customization

## 🌍 Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/plural_chat

# Security
SECRET_KEY=your-secret-key-here

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=http://localhost:8000
```

## 📝 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Development

### Project Structure

```
web/
├── frontend/                # Next.js application
│   ├── app/                # Next.js app directory
│   │   ├── page.tsx       # Main chat page
│   │   └── login/         # Login page
│   ├── components/         # React components
│   │   ├── ChatList.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── MessageInput.tsx
│   │   └── MemberSidebar.tsx
│   └── lib/               # Utilities
│       ├── store.ts       # Zustand store
│       ├── api.ts         # API client
│       └── useWebSocket.ts # WS hook
├── backend/                  # FastAPI application
│   ├── app/                 # Application code
│   │   ├── routers/        # API routes
│   │   ├── database.py     # DB models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── auth_enhanced.py # Enhanced authentication
│   │   ├── commands.py     # Discord-style commands
│   │   ├── ai_characters.py # LLM integration
│   │   ├── cache.py        # Redis caching
│   │   ├── pluralkit.py    # PK API client (optional)
│   │   ├── sd_integration.py # Stable Diffusion
│   │   └── websocket.py    # Socket.IO handlers
│   └── main.py             # FastAPI entry point
└── docker/              # Docker configurations
```

### Running Tests

```bash
# Backend tests
cd web/backend
pytest

# Frontend tests
cd web/frontend
npm test
```

### Database Schema

The database schema is automatically created on first startup using SQLAlchemy's `create_all()`. When you add new features or update the code, new columns are automatically added to existing tables.

**No manual migrations needed!** Just restart the backend and the database will be updated.

## 🐛 Troubleshooting

### Backend won't start

- Check if PostgreSQL is running
- Verify DATABASE_URL in .env
- Check logs: `docker-compose logs backend`

### Frontend can't connect to backend

- Verify NEXT_PUBLIC_API_URL is correct
- Check CORS settings in backend
- Check browser console for errors

### WebSocket not connecting

- Ensure backend is running
- Check firewall settings
- Verify WebSocket URL is correct

### PluralKit sync fails

- Check internet connection
- Verify PluralKit token is valid
- Check backend logs for API errors

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## 📜 License

MIT License - See [LICENSE](../../LICENSE) for details.

## 🔗 Links

- **Main Repository**: https://github.com/Ktiseos-Nyx/plural_chat
- **PluralKit**: https://pluralkit.me
- **Issues**: https://github.com/Ktiseos-Nyx/plural_chat/issues

## 💜 Acknowledgments

- **PluralKit Team** - For the amazing API
- **LobeHub** - For the beautiful UI components
- **Plural Community** - For feedback and support

---

**Made with ❤️ for the plural community**

*Deploy your own instance today!* 🚀
