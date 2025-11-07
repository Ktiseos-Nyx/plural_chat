# Plural Chat - Web Edition 🌐

A modern, self-hosted web application for plural systems to chat with PluralKit integration. Deploy your own instance for your private group!

![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)

## ✨ Features

- **Real-time Chat** - WebSocket-powered instant messaging
- **PluralKit Sync** - One-click import of your system members
- **Beautiful UI** - Built with LobeHub UI components
- **Multi-User** - Multiple systems can connect to the same instance
- **Self-Hosted** - Full control over your data
- **Easy Deployment** - One-click deploy to Railway or Docker

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

1. **Get Your PluralKit Token**
   - Visit https://pluralkit.me/dash
   - Click "Get API Token"
   - Copy your token

2. **Login**
   - Open your deployed Plural Chat instance
   - Paste your PluralKit token
   - Click "Connect to PluralKit"

3. **Sync Your Members**
   - Click the "Sync" button in the sidebar
   - Your members and avatars will be imported automatically

4. **Start Chatting!**
   - Select a member from the sidebar
   - Type your message
   - Press Enter to send

### Multi-User Setup

Each user can login with their own PluralKit token. All messages are visible to everyone connected to the same instance, making it perfect for:
- Systems communicating with each other
- Shared headspaces
- Private plural communities
- Collaborative system management

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
- Socket.IO (WebSockets)
- Python-JOSE (JWT Auth)
- PluralKit API Integration

**Deployment:**
- Docker & Docker Compose
- Railway (One-click deploy)
- Vercel (Frontend alternative)

## 🔐 Security Features

- **JWT Authentication** - Secure token-based auth
- **PluralKit Token Encryption** - Tokens stored securely
- **CORS Protection** - Configurable allowed origins
- **SQL Injection Prevention** - SQLAlchemy parameterized queries
- **XSS Protection** - React auto-escaping
- **Avatar Validation** - Whitelist of trusted CDNs
- **Path Traversal Prevention** - Filename sanitization

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
├── backend/               # FastAPI application
│   ├── app/              # Application code
│   │   ├── routers/     # API routes
│   │   ├── database.py  # DB models
│   │   ├── schemas.py   # Pydantic schemas
│   │   ├── auth.py      # JWT auth
│   │   ├── pluralkit.py # PK API client
│   │   └── websocket.py # Socket.IO handlers
│   └── main.py          # FastAPI entry point
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

### Database Migrations

```bash
cd web/backend

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

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
