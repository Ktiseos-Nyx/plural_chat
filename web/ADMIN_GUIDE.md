# 🔧 Admin Panel Guide

**"For numptys like me who just sneezed all over their keyboard"** 😊

A simple, friendly admin interface for managing your Plural Chat instance.

## 🚀 Quick Start

### Set Up Admin Access

Admin access is controlled by the `ADMIN_USERS` environment variable:

```bash
# In .env file
ADMIN_USERS=admin,your_username,another_admin
```

Or just name your account `admin` - that works too!

### Access the Admin Panel

Once logged in as an admin, access the admin API:

```
GET http://localhost:8000/admin/dashboard
```

All admin endpoints require authentication (JWT token).

## 📊 Dashboard

Get a quick overview of everything:

**Endpoint:** `GET /admin/dashboard`

**Returns:**
```json
{
  "users": {
    "total": 42,
    "verified": 38,
    "active": 40,
    "recent_signups": 5
  },
  "members": {
    "total": 156,
    "active": 150
  },
  "messages": {
    "total": 1234,
    "today": 89
  },
  "media": {
    "total_files": 23,
    "total_size_mb": 45.2,
    "cache_dir": "/path/to/media_cache",
    "ttl_hours": 24
  },
  "cache": {
    "status": "ok"
  }
}
```

## 👥 User Management

### List All Users

**Endpoint:** `GET /admin/users?skip=0&limit=50&search=username`

**Parameters:**
- `skip` - Pagination offset (default: 0)
- `limit` - Results per page (default: 50, max: 500)
- `search` - Search by username or email (optional)

**Example:**
```bash
GET /admin/users?search=alice
```

### Get User Details

**Endpoint:** `GET /admin/users/{user_id}`

**Returns:**
- Full user info
- All members
- Message count
- Recent activity

### Update User

**Endpoint:** `PATCH /admin/users/{user_id}`

**Body:**
```json
{
  "is_active": true,
  "is_verified": true
}
```

**Use cases:**
- Manually verify a user's email
- Deactivate a spammer
- Re-activate an account
- Fix accounts after "keyboard sneezing incidents" 😄

### Delete User

**Endpoint:** `DELETE /admin/users/{user_id}`

⚠️ **WARNING:** This permanently deletes:
- The user account
- All their members
- All their messages
- All their data

**You cannot delete your own account from the admin panel.**

## 🧹 System Maintenance

### Clean Up Expired Media

**Endpoint:** `POST /admin/cleanup/media`

Manually removes expired images (older than 24 hours).

**Returns:**
```json
{
  "message": "Media cleanup completed",
  "files_deleted": 12,
  "stats": {
    "total_files": 8,
    "total_size_mb": 15.2
  }
}
```

### Clear Redis Cache

**Endpoint:** `POST /admin/cleanup/cache`

Clears all Redis cache. Use this if:
- Cache gets wonky
- You suspect stale data
- You just feel like it

**Returns:**
```json
{
  "message": "Cache cleared successfully"
}
```

## 📈 Statistics

### Database Stats

**Endpoint:** `GET /admin/stats/database`

**Returns:**
```json
{
  "tables": {
    "users": 42,
    "members": 156,
    "messages": 1234,
    "sessions": 89
  },
  "active_sessions": 45,
  "recent_activity": {
    "messages_today": 89,
    "new_users_this_week": 5
  },
  "top_users": [
    {"username": "alice", "message_count": 456},
    {"username": "bob", "message_count": 234}
  ]
}
```

### Health Check

**Endpoint:** `GET /admin/health`

**Returns:**
```json
{
  "database": "ok",
  "cache": "ok",
  "media_cache": "ok",
  "timestamp": "2025-01-15T10:30:00"
}
```

Use this to verify all systems are operational.

## ⚙️ Configuration

### View Current Config

**Endpoint:** `GET /admin/config`

**Returns:**
```json
{
  "environment": {
    "database_url": "localhost/plural_chat",
    "redis_url": "redis://localhost:6379",
    "frontend_url": "http://localhost:3000"
  },
  "features": {
    "email_enabled": true,
    "oauth_discord": true,
    "oauth_google": false,
    "oauth_github": false
  },
  "limits": {
    "max_media_size_mb": 10,
    "media_ttl_hours": 24
  }
}
```

## 🔐 Security Notes

1. **Admin access is powerful** - Only grant to trusted users
2. **Use environment variables** - Don't hardcode admin usernames
3. **HTTPS in production** - Always use HTTPS for admin endpoints
4. **Audit logs** - Consider adding logging for admin actions (future feature)

## 💡 Common Tasks

### User accidentally deleted their account?

Sorry, it's permanent. No recovery possible. This is why we have warnings!

### User can't log in?

1. Check if account is active: `GET /admin/users/{id}`
2. If `is_active: false`, reactivate: `PATCH /admin/users/{id}` with `{"is_active": true}`

### Cache seems slow or stale?

```bash
POST /admin/cleanup/cache
```

### Media storage getting full?

```bash
POST /admin/cleanup/media
```

This removes expired files (24+ hours old).

### Want to see who's most active?

```bash
GET /admin/stats/database
```

Check the `top_users` field.

### System health check before deployment?

```bash
GET /admin/health
```

Make sure everything is "ok".

## 🎯 Future Features

Ideas for future admin panel improvements:

- [ ] Web UI (currently just API)
- [ ] Audit logging
- [ ] User impersonation (for support)
- [ ] Bulk user operations
- [ ] Custom role management
- [ ] Email blast to all users
- [ ] Analytics dashboard
- [ ] Backup/restore tools

## 🤔 FAQ

**Q: Can I have multiple admins?**
A: Yes! Set `ADMIN_USERS=admin,alice,bob` in your environment.

**Q: Can admins see users' PluralKit tokens?**
A: No, they're encrypted. Even admins can't see them.

**Q: Can I delete multiple users at once?**
A: Not yet. You'll need to call DELETE for each user individually.

**Q: What happens if I delete my own account?**
A: You can't! The API prevents you from shooting yourself in the foot.

**Q: Is there a web UI?**
A: Not yet! Currently just API endpoints. You can use:
- Postman
- curl
- Your own custom admin frontend
- Browser extensions

**Q: I sneezed on my keyboard and deleted 50 users. Can I undo?**
A: No. This is why we have warnings. Be careful! ⚠️

---

## 📞 Support

Need help with admin tasks?

- Check the main [README](README.md)
- Read [Security Docs](SECURITY.md)
- Ask in [GitHub Discussions](https://github.com/Ktiseos-Nyx/plural_chat/discussions)

---

*Remember: With great power comes great responsibility!* 💜

(And please don't sneeze on your keyboard during admin operations) 😄
