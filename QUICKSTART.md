# 🚀 Quick Start Guide

Get Plural Chat running in minutes!

## Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 18+** (for frontend)
- **npm** or **yarn** (for frontend package management)

## One-Command Start (Recommended)

### On Linux/Mac:
```bash
./dev.sh
```

### On Windows:
```batch
dev.bat
```

This will automatically:
- Install all dependencies (first run only)
- Start the backend server on http://localhost:8000
- Start the frontend server on http://localhost:3000

**That's it!** Open http://localhost:3000 in your browser and you're ready to go! 🎉

---

## Manual Setup (Alternative)

If you prefer to run things manually:

### 1. Backend Setup

```bash
cd web/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template (optional - works without it)
cp .env.example .env

# Start backend
uvicorn app.main:app --reload
```

Backend will run on http://localhost:8000

### 2. Frontend Setup

```bash
cd web/frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

Frontend will run on http://localhost:3000

---

## First Time Usage

1. **Open** http://localhost:3000
2. **Click "Sign up"** to create your account
3. **Create a member** (your first headmate/character)
4. **Start chatting!**

### Optional: Sync with PluralKit

1. Go to **Settings** (after logging in)
2. Navigate to the **Profile** tab
3. Scroll to **PluralKit Integration**
4. Enter your PluralKit API token
5. Click **Sync Members**

Your PluralKit system will be automatically imported!

---

## Useful Links

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc

---

## Features

- ✅ **User Registration & Login** - Secure authentication with optional 2FA
- ✅ **Multiple Members** - Create and manage system members
- ✅ **PluralKit Sync** - Import members from PluralKit
- ✅ **Channels/Rooms** - Organize conversations
- ✅ **Real-time Chat** - WebSocket-powered messaging
- ✅ **Dark Mode** - Easy on the eyes
- ✅ **AI Characters** (Optional) - Chat with AI-powered headmates
- ✅ **Audit Logs** - Track security events

---

## Troubleshooting

### "Cannot connect to server"
Make sure the backend is running on http://localhost:8000

### "Module not found" errors
Run `pip install -r requirements.txt` in the backend directory

### Frontend won't start
1. Delete `web/frontend/.next` folder
2. Delete `web/frontend/node_modules` folder
3. Run `npm install` again

### Database errors
The app uses SQLite by default (no setup needed). If you see database errors, delete `web/backend/plural_chat.db` and restart.

---

## What's Next?

- Explore the **Settings** page to customize your profile
- Set up **2FA** for extra security
- Create **channels** to organize your thoughts
- Try out **AI characters** (requires API keys)

---

## Need Help?

- Check out the full documentation in the `web/` directory
- Report issues: https://github.com/Ktiseos-Nyx/plural_chat/issues
- Read `GETTING_STARTED.md` for more detailed information

---

**Happy chatting!** 💬✨
