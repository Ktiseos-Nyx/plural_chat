# Deployment Guide - Plural Chat Web Edition

This guide covers multiple deployment options for Plural Chat.

## 🚀 Quick Deploy Options

### Option 1: Railway (Easiest)

Railway offers one-click deployment with automatic HTTPS and database provisioning.

1. **Click the Deploy Button**

   [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/plural-chat)

2. **Configure Environment Variables**

   Railway will prompt you for:
   - `SECRET_KEY` - Generate with: `openssl rand -hex 32`
   - `DB_PASSWORD` - Set a strong database password

3. **Wait for Deployment**

   Railway will automatically:
   - Create a PostgreSQL database
   - Deploy the backend
   - Deploy the frontend
   - Set up HTTPS with a custom domain

4. **Access Your App**

   Visit the URL provided by Railway (e.g., `your-app.railway.app`)

### Option 2: Docker Compose (Self-Hosted)

Perfect for VPS deployment (DigitalOcean, Linode, etc.)

1. **Install Docker**

   ```bash
   # Ubuntu/Debian
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

2. **Clone Repository**

   ```bash
   git clone https://github.com/Ktiseos-Nyx/plural_chat.git
   cd plural_chat/web
   ```

3. **Configure Environment**

   ```bash
   cp backend/.env.example backend/.env
   nano backend/.env  # Edit with your settings
   ```

4. **Start Services**

   ```bash
   # Development
   docker-compose -f docker-compose.dev.yml up -d

   # Production
   docker-compose up -d
   ```

5. **Set Up Reverse Proxy (Optional)**

   Use Caddy for automatic HTTPS:

   ```bash
   # Install Caddy
   sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
   sudo apt update
   sudo apt install caddy

   # Configure Caddyfile
   sudo nano /etc/caddy/Caddyfile
   ```

   Caddyfile contents:

   ```
   your-domain.com {
       reverse_proxy localhost:3000
   }

   api.your-domain.com {
       reverse_proxy localhost:8000
   }
   ```

   ```bash
   sudo systemctl reload caddy
   ```

## 🌐 Platform-Specific Guides

### Vercel (Frontend Only)

Deploy just the Next.js frontend to Vercel:

1. **Push to GitHub**

   ```bash
   git add .
   git commit -m "Add web edition"
   git push origin web-edition
   ```

2. **Import to Vercel**

   - Go to https://vercel.com
   - Click "Import Project"
   - Select your repository
   - Set root directory to `web/frontend`

3. **Configure Environment**

   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.com
   NEXT_PUBLIC_WS_URL=https://your-backend-url.com
   ```

4. **Deploy Backend Separately**

   Use Railway, Render, or Heroku for the backend

### Render.com

1. **Create PostgreSQL Database**

   - Go to https://render.com
   - Create new PostgreSQL database
   - Note the internal database URL

2. **Deploy Backend**

   - Create new Web Service
   - Connect your repository
   - Set root directory: `web/backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment variables:
     ```
     DATABASE_URL=<your-postgres-url>
     SECRET_KEY=<random-secret-key>
     ```

3. **Deploy Frontend**

   - Create new Web Service
   - Set root directory: `web/frontend`
   - Build command: `npm install && npm run build`
   - Start command: `npm start`
   - Environment variables:
     ```
     NEXT_PUBLIC_API_URL=<backend-url>
     NEXT_PUBLIC_WS_URL=<backend-url>
     ```

### DigitalOcean App Platform

1. **Create App**

   - Go to https://cloud.digitalocean.com/apps
   - Create new app from GitHub

2. **Configure Components**

   **Database:**
   - Type: PostgreSQL
   - Plan: Dev Database ($7/month)

   **Backend:**
   - Type: Web Service
   - Source: `web/backend`
   - Build command: `pip install -r requirements.txt`
   - Run command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

   **Frontend:**
   - Type: Web Service
   - Source: `web/frontend`
   - Build command: `npm install && npm run build`
   - Run command: `npm start`

3. **Set Environment Variables** (see below)

## 🔐 Environment Variables

### Backend (.env)

```bash
# Required
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-secret-key-here

# Optional
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
HOST=0.0.0.0
PORT=8000
```

### Frontend (.env.local)

```bash
# Required
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=https://api.yourdomain.com

# Optional
NEXT_TELEMETRY_DISABLED=1
```

## 🔧 Post-Deployment

### Database Migrations

If you make database schema changes:

```bash
cd web/backend

# Create migration
alembic revision --autogenerate -m "description"

# Apply to production
alembic upgrade head
```

### Health Checks

Check if services are running:

```bash
# Backend health
curl https://api.yourdomain.com/health

# Frontend
curl https://yourdomain.com
```

### Monitoring

**Logs:**

```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f frontend

# Railway
railway logs

# Render
View in dashboard
```

**Metrics:**

- Set up Sentry for error tracking
- Use Railway/Render built-in metrics
- Configure Prometheus + Grafana for custom metrics

## 🛡️ Security Checklist

- [ ] Strong `SECRET_KEY` (32+ random characters)
- [ ] Secure `DB_PASSWORD`
- [ ] HTTPS enabled (automatic with Railway/Render)
- [ ] CORS configured with specific origins
- [ ] Regular backups enabled for database
- [ ] Rate limiting configured (if needed)
- [ ] Database connection pooling configured
- [ ] Firewall rules set up (if on VPS)

## 💾 Backup

### Automated Backups (Railway)

Railway automatically backs up PostgreSQL databases daily.

### Manual Backup (Docker)

```bash
# Backup database
docker exec plural_chat_db pg_dump -U plural_chat plural_chat > backup.sql

# Restore database
docker exec -i plural_chat_db psql -U plural_chat plural_chat < backup.sql

# Backup avatars
tar -czf avatars-backup.tar.gz web/backend/avatars/
```

## 📈 Scaling

### Horizontal Scaling

1. **Database:** Use managed PostgreSQL with connection pooling
2. **Backend:** Run multiple instances behind a load balancer
3. **Frontend:** CDN for static assets (Vercel handles this automatically)

### Vertical Scaling

Increase resources on your platform:

- Railway: Upgrade plan
- DigitalOcean: Resize droplet
- Render: Upgrade instance type

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. DATABASE_URL incorrect
# 2. Port already in use
# 3. Missing dependencies
```

### Frontend can't connect

1. Check `NEXT_PUBLIC_API_URL` is correct
2. Verify CORS settings in backend
3. Check browser console for errors
4. Ensure backend is accessible from frontend

### Database connection errors

```bash
# Test connection
docker exec -it plural_chat_db psql -U plural_chat

# Reset database (⚠️ DATA LOSS)
docker-compose down -v
docker-compose up -d
```

## 📞 Support

- **Issues:** https://github.com/Ktiseos-Nyx/plural_chat/issues
- **Discussions:** https://github.com/Ktiseos-Nyx/plural_chat/discussions
- **Email:** support@example.com (update with actual)

---

**Need help?** Join our community or open an issue on GitHub!
