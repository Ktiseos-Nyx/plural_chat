# 🚀 Easy Deployment Guide

Deploy Plural Chat to the cloud in minutes! This guide covers multiple platforms.

## 📋 Table of Contents

- [Quick Deploy Options](#quick-deploy-options)
- [Railway (Recommended)](#railway-recommended)
- [Vercel + Railway Hybrid](#vercel--railway-hybrid)
- [Docker Anywhere](#docker-anywhere)
- [VPS Manual Setup](#vps-manual-setup)
- [Firebase? (Answered)](#firebase-answered)
- [Environment Variables](#environment-variables)

---

## ⚡ Quick Deploy Options

| Platform | Difficulty | Cost | Best For |
|----------|-----------|------|----------|
| **Railway** | ⭐ Easy | $5-20/mo | All-in-one solution |
| **Vercel + Railway** | ⭐⭐ Moderate | $0-15/mo | Free frontend |
| **Docker (Any VPS)** | ⭐⭐⭐ Advanced | $5-10/mo | Full control |
| **Cloudflare Tunnel** | ⭐⭐ Moderate | $0-10/mo | Home server |

---

## 🚂 Railway (Recommended)

**Why Railway?** One-click deploy, automatic SSL, PostgreSQL included, perfect for beginners!

### Method 1: One-Click Deploy (Easiest)

1. **Click Deploy Button:**
   - *(Coming soon: We'll add a Railway button to the repo)*
   - For now, follow Method 2

### Method 2: Manual Railway Deploy

#### 1. Create Railway Account
- Go to [Railway.app](https://railway.app)
- Sign up with GitHub (free $5 credit)

#### 2. Create New Project
```
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your fork of plural_chat
4. Railway auto-detects Docker configuration!
```

#### 3. Add PostgreSQL Database
```
1. In your project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway auto-creates DATABASE_URL
```

#### 4. Add Redis Cache
```
1. Click "New" → "Database" → "Redis"
2. Railway auto-creates REDIS_URL
```

#### 5. Configure Environment Variables

Click on your service → "Variables" → Add these:

**Required:**
```bash
# Database (auto-provided by Railway)
DATABASE_URL=${POSTGRES_URL}
REDIS_URL=${REDIS_URL}

# App Settings
SECRET_KEY=<generate-random-string-here>
ENCRYPTION_KEY=<generate-random-string-here>
FRONTEND_URL=https://your-app.railway.app

# Admin Users
ADMIN_USERS=admin,your_username
```

**Optional (for OAuth):**
```bash
# Discord OAuth
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

**Optional (for Email):**
```bash
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=noreply@yourdomain.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
```

#### 6. Deploy!
```
1. Railway automatically deploys on push
2. Wait 2-5 minutes for build
3. Click "Generate Domain" to get your URL
4. Done! Visit https://your-app.railway.app
```

#### 7. Generate Secret Keys

On your local machine:
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add these to Railway Variables.

### Railway Cost Estimate
- **Free tier**: $5 credit (500 hours)
- **Hobby Plan**: $5/month gets you:
  - Backend service ($5-10/mo)
  - PostgreSQL ($0-5/mo)
  - Redis ($0-2/mo)
  - **Total: ~$5-20/month** depending on usage

---

## 🔥 Vercel + Railway Hybrid

**Why?** Vercel's free tier for frontend + Railway for backend = Cost savings!

### 1. Deploy Backend to Railway
Follow the Railway steps above for backend + database only.

### 2. Deploy Frontend to Vercel

```bash
cd web/frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow prompts:
# - Project name: plural-chat-frontend
# - Framework: Next.js (auto-detected)
# - Build command: npm run build
```

### 3. Configure Frontend Environment Variables

In Vercel dashboard → Settings → Environment Variables:

```bash
NEXT_PUBLIC_API_URL=https://your-railway-backend.railway.app
NEXT_PUBLIC_WS_URL=wss://your-railway-backend.railway.app
```

### 4. Configure Backend CORS

In Railway, add to environment variables:

```bash
FRONTEND_URL=https://your-vercel-app.vercel.app
```

**Cost:** $0-5/month (Vercel free + Railway backend only)

---

## 🐳 Docker Anywhere

Deploy to **any VPS** with Docker (DigitalOcean, Linode, Hetzner, etc.)

### 1. Rent a VPS
- **DigitalOcean**: $6/month (1GB RAM)
- **Hetzner**: $4/month (2GB RAM) - cheapest!
- **Linode**: $5/month (1GB RAM)

### 2. SSH into Server
```bash
ssh root@your-server-ip
```

### 3. Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### 4. Install Docker Compose
```bash
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 5. Clone Repository
```bash
git clone https://github.com/Ktiseos-Nyx/plural_chat.git
cd plural_chat/web
```

### 6. Create Environment File
```bash
nano .env
```

Add your configuration (see [Environment Variables](#environment-variables) section below).

### 7. Deploy with Docker Compose
```bash
docker-compose up -d
```

### 8. Configure Nginx (Optional but Recommended)

Install Nginx:
```bash
apt update && apt install nginx certbot python3-certbot-nginx -y
```

Create Nginx config:
```bash
nano /etc/nginx/sites-available/plural-chat
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /socket.io {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/plural-chat /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

Get SSL certificate:
```bash
certbot --nginx -d your-domain.com
```

**Cost:** $4-6/month + domain (~$12/year)

---

## ☁️ Cloudflare Tunnel (Home Server / No Port Forwarding)

Perfect if you want to run on your own hardware without opening ports!

### 1. Install Cloudflared
```bash
# On your server (Linux)
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

### 2. Authenticate
```bash
cloudflared tunnel login
```

### 3. Create Tunnel
```bash
cloudflared tunnel create plural-chat
```

### 4. Configure Tunnel
Create config file:
```bash
nano ~/.cloudflared/config.yml
```

Add:
```yaml
url: http://localhost:3000
tunnel: <tunnel-id-from-step-3>
credentials-file: /home/youruser/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: chat.yourdomain.com
    service: http://localhost:3000
  - hostname: api.chat.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

### 5. Route DNS
```bash
cloudflared tunnel route dns plural-chat chat.yourdomain.com
cloudflared tunnel route dns plural-chat api.chat.yourdomain.com
```

### 6. Run Tunnel
```bash
cloudflared tunnel run plural-chat
```

### 7. Make It Auto-Start
```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

**Cost:** $0 (Cloudflare free) + hardware you own

---

## 🔥 Firebase? (Answered)

**Q: Should we use Firebase?**

**A: Not for this app, but here's why:**

### What Firebase Is:
Firebase is Google's platform that provides:
- **Firestore**: NoSQL database
- **Realtime Database**: Real-time sync
- **Authentication**: OAuth, email/password
- **Cloud Storage**: File storage
- **Hosting**: Static site hosting
- **Cloud Functions**: Serverless functions

### Why We're NOT Using Firebase:

❌ **No Python Support**
- Firebase Cloud Functions only support JavaScript/TypeScript
- Our FastAPI backend is Python

❌ **Cold Starts**
- Cloud Functions have 1-3 second cold starts
- Bad for real-time chat

❌ **Cost**
- Firestore charges per read/write
- Chat apps = LOTS of reads/writes
- Can get expensive fast ($50-200/month)

❌ **WebSocket Limitations**
- Firebase Realtime Database is different from WebSockets
- Our Socket.IO setup won't work

### What We COULD Use Firebase For:

✅ **Alternative Storage for Images**
- Firebase Storage instead of local filesystem
- Good for permanent image storage
- $0.026/GB/month

✅ **Firebase Auth (Optional)**
- Could integrate Firebase OAuth
- But we already have Authlib working

✅ **Hosting Frontend Only**
- Firebase Hosting for Next.js
- But Vercel is better for Next.js

### Recommendation:

**Stick with current stack:**
- Backend: Railway / VPS (Python FastAPI)
- Database: PostgreSQL (better for relational data)
- Cache: Redis (perfect for chat)
- Frontend: Vercel / Railway
- Storage: Local filesystem / S3 / Cloudflare R2

**Only use Firebase if:**
- You want to replace PostgreSQL with Firestore (not recommended)
- You want Firebase Storage for permanent images (optional)

---

## 🔐 Environment Variables

Here's a complete list of all environment variables:

### Required

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/plural_chat
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Admin Users (comma-separated)
ADMIN_USERS=admin,your_username
```

### Optional - OAuth

```bash
# Discord
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_secret

# Google
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_secret

# GitHub
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_secret
```

### Optional - Email

```bash
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=noreply@yourdomain.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_TLS=True
MAIL_SSL=False
```

### Optional - Features

```bash
# Media Storage
MAX_MEDIA_SIZE=10485760  # 10MB in bytes
MEDIA_TTL_HOURS=24

# Cache
REDIS_MAX_MEMORY=256mb
```

---

## 🎯 Platform Comparison

| Feature | Railway | Vercel+Railway | Docker VPS | Cloudflare Tunnel |
|---------|---------|----------------|------------|-------------------|
| **Setup Time** | 5 minutes | 10 minutes | 30 minutes | 20 minutes |
| **Difficulty** | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Cost/month** | $5-20 | $0-15 | $4-10 | $0 |
| **Auto SSL** | ✅ Yes | ✅ Yes | Manual | ✅ Yes |
| **Auto Deploy** | ✅ Yes | ✅ Yes | Manual | Manual |
| **Scaling** | ✅ Easy | ✅ Easy | Manual | ❌ No |
| **Best For** | Beginners | Budget-conscious | Advanced | Home servers |

---

## 🆘 Troubleshooting

### "Cannot connect to database"
- Check `DATABASE_URL` is set correctly
- Ensure PostgreSQL is running
- On Railway, make sure Postgres service is linked

### "CORS error"
- Update `FRONTEND_URL` to match your actual frontend URL
- Check FastAPI CORS middleware in `main.py`

### "WebSocket not connecting"
- Ensure `/socket.io` path is proxied correctly
- Check Nginx config if using reverse proxy
- Verify Socket.IO CORS origins

### "Commands not working"
- Commands were just integrated in latest version
- Make sure you're on latest branch: `claude/web-edition-011CUtGhPmjDv5gQkW1cdKYD`
- Type `/help` to see available commands

### "Images not loading"
- Check `MEDIA_DIR` exists and has write permissions
- Verify ephemeral storage is working: `docker exec -it backend ls /app/media_cache`

---

## 📞 Need Help?

- 📖 Check the [main README](../README.md)
- 🔐 Read [Security Docs](../web/SECURITY.md)
- 🎨 See [AI Generation Guide](../AI_GENERATION_GUIDE.md)
- 💬 Ask in [GitHub Discussions](https://github.com/Ktiseos-Nyx/plural_chat/discussions)

---

*Made with 💜 for the plural community (and everyone else!)*
