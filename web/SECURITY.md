# 🔐 Security Documentation - Plural Chat Web Edition

## Overview

This document details all security measures implemented in Plural Chat to protect user data and ensure safe operation.

## 🛡️ Security Features

### 1. Authentication & Authorization

#### Password Security
- **Bcrypt Hashing**: All passwords hashed with bcrypt (cost factor 12)
- **Password Requirements**:
  - Minimum 8 characters
  - At least one letter
  - At least one digit
  - Case-sensitive
- **No Plain Text Storage**: Passwords never stored in plain text
- **Salting**: Each password hash uses unique salt

#### JWT Tokens
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiration**: 30 days (configurable)
- **Secret Key**: Must be set via `SECRET_KEY` environment variable
- **Token Structure**:
  ```json
  {
    "sub": user_id,
    "exp": expiration_timestamp
  }
  ```

#### OAuth 2.0 Support
- **Providers**: Discord, Google, GitHub
- **Flow**: Authorization Code Grant
- **Scopes**: Minimal required permissions
- **Account Linking**: OAuth can link to existing accounts via email

### 2. Data Encryption

#### Sensitive Data Encryption
- **Algorithm**: Fernet (AES-128 in CBC mode)
- **Key Management**: Encryption key from `ENCRYPTION_KEY` env variable
- **Encrypted Fields**:
  - PluralKit API tokens (`pk_token_encrypted`)
  - Any future sensitive fields

#### Encryption Implementation
```python
# Database model method
def set_pk_token(self, token: str):
    """Encrypt and store PluralKit token"""
    if token:
        self.pk_token_encrypted = cipher.encrypt(token.encode())

def get_pk_token(self) -> str:
    """Decrypt and return PluralKit token"""
    if self.pk_token_encrypted:
        return cipher.decrypt(self.pk_token_encrypted).decode()
    return None
```

### 3. Database Security

#### SQL Injection Prevention
- **ORM**: SQLAlchemy with parameterized queries
- **No Raw SQL**: All queries go through ORM
- **Input Validation**: Pydantic schemas validate all inputs

#### Data Validation
```python
# Example: Member creation
class MemberCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    pronouns: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
```

#### Connection Security
- **SSL/TLS**: PostgreSQL connections use SSL in production
- **Connection Pooling**: Limited connections to prevent exhaustion
- **Timeouts**: Query timeouts prevent long-running queries

### 4. API Security

#### CORS (Cross-Origin Resource Sharing)
```python
# Configured allowed origins
allow_origins=[
    "http://localhost:3000",  # Development
    "https://yourdomain.com",  # Production
]
```

#### Rate Limiting
- **Library**: SlowAPI
- **Limits**:
  - Login: 5 attempts per minute per IP
  - Registration: 3 per hour per IP
  - API calls: 100 per minute per user
  - WebSocket: 50 messages per minute per user

#### Input Sanitization
- **HTML Escaping**: React auto-escapes in frontend
- **Filename Sanitization**: Avatar filenames sanitized
  ```python
  def _sanitize_filename(self, member_name: str) -> str:
      safe_name = re.sub(r'[^\w\-_\s]', '_', str(member_name))
      safe_name = safe_name.replace(' ', '_')
      safe_name = safe_name[:50]  # Limit length
      return safe_name
  ```

### 5. Avatar Security

#### URL Validation
- **Whitelist**: Only trusted CDNs allowed
  ```python
  trusted_domains = [
      'cdn.pluralkit.me',
      'media.discordapp.net',
      'cdn.discordapp.com',
      'i.imgur.com',
      'avatars.githubusercontent.com',
  ]
  ```
- **HTTPS Only**: All avatar URLs must use HTTPS
- **Extension Check**: Only image extensions allowed

#### File Processing
- **Image Validation**: PIL validates image format
- **Size Limits**: Resized to 256x256 max
- **Format Conversion**: All converted to WebP
- **No Direct Execution**: Images processed, not executed

### 6. Session Management

#### Session Tracking
```python
class Session(Base):
    user_id: int
    token: str  # JWT token
    ip_address: str
    user_agent: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    is_valid: bool
```

#### Security Measures
- **Session Expiry**: Tokens expire after 30 days
- **IP Tracking**: Sessions track IP for fraud detection
- **User Agent Tracking**: Detect suspicious login patterns
- **Session Invalidation**: Can revoke specific sessions

### 7. WebSocket Security

#### Connection Authentication
```python
@sio_app.event
async def connect(sid, environ, auth):
    token = auth.get('token')
    if not token:
        return False

    # Verify JWT token
    token_data = verify_token(token)
    user_id = token_data.user_id
    # Store user_id in session
```

#### Message Validation
- **Rate Limiting**: Max 50 messages per minute
- **Content Length**: Max 5000 characters per message
- **Authorization**: Users can only send as their own members

## 🔒 Production Security Checklist

### Required Environment Variables

```bash
# CRITICAL - Must be set in production
SECRET_KEY=<random-64-character-string>
ENCRYPTION_KEY=<fernet-key-from-cryptography>
DATABASE_URL=postgresql://...

# OAuth (if using)
DISCORD_CLIENT_ID=<your-discord-client-id>
DISCORD_CLIENT_SECRET=<your-discord-secret>
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-secret>
GITHUB_CLIENT_ID=<your-github-client-id>
GITHUB_CLIENT_SECRET=<your-github-secret>

# Optional
CORS_ORIGINS=https://yourdomain.com
```

### Generating Secrets

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate ENCRYPTION_KEY (Python)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Infrastructure Security

1. **HTTPS Only**
   - Use Caddy, Nginx, or Railway for automatic HTTPS
   - Redirect all HTTP to HTTPS
   - HSTS headers enabled

2. **Database**
   - Use managed PostgreSQL (Railway, DigitalOcean, AWS RDS)
   - Enable SSL/TLS connections
   - Regular automated backups
   - Restrict network access (firewall)

3. **Firewall**
   ```bash
   # Allow only necessary ports
   - 443 (HTTPS)
   - 80 (HTTP redirect)
   - PostgreSQL port (only from app server)
   ```

4. **Updates**
   - Keep dependencies updated
   - Monitor security advisories
   - Test updates in staging first

## 🚨 Potential Vulnerabilities & Mitigations

### 1. Brute Force Attacks
**Risk**: Password guessing
**Mitigation**:
- Rate limiting on login endpoint (5 attempts/minute)
- Account lockout after 10 failed attempts (future enhancement)
- CAPTCHA after 3 failed attempts (future enhancement)

### 2. Session Hijacking
**Risk**: Stolen JWT tokens
**Mitigation**:
- Short token expiry (30 days, but can be reduced)
- IP address tracking
- Session invalidation on suspicious activity
- HTTPS-only cookies (future enhancement)

### 3. XSS (Cross-Site Scripting)
**Risk**: Malicious scripts in user content
**Mitigation**:
- React auto-escapes all content
- CSP headers (future enhancement)
- No `dangerouslySetInnerHTML` usage
- Input validation on backend

### 4. CSRF (Cross-Site Request Forgery)
**Risk**: Unauthorized actions from malicious sites
**Mitigation**:
- JWT tokens in Authorization header (not cookies)
- CORS restrictions
- SameSite cookie attribute (if using cookies)

### 5. Data Exposure
**Risk**: Sensitive data leaked
**Mitigation**:
- Passwords hashed with bcrypt
- PK tokens encrypted with Fernet
- No sensitive data in logs
- Pydantic response models filter fields

### 6. DoS (Denial of Service)
**Risk**: Service overwhelmed
**Mitigation**:
- Rate limiting on all endpoints
- Connection limits on WebSocket
- Database connection pooling
- Cloudflare or similar (recommended)

## 📊 Data Privacy

### Data Collected

**User Account**:
- Username (required)
- Email (optional, required for OAuth)
- Password hash (if using password login)
- OAuth provider & ID (if using OAuth)

**System Data**:
- Member names, pronouns, colors
- PluralKit system ID (optional)
- PluralKit token (encrypted, optional)
- Avatar images

**Usage Data**:
- Chat messages
- Login timestamps
- IP addresses (session tracking)
- User agent strings

### Data Retention

- **Messages**: Indefinite (user can delete)
- **Sessions**: 30 days
- **Avatars**: Indefinite (user can delete member)
- **Accounts**: Indefinite (user can delete account)

### User Rights (GDPR Compliance)

Users can:
1. **View** their data (GET /users/me)
2. **Edit** their data (PATCH /users/me)
3. **Delete** their data (DELETE /users/me)
4. **Export** their data (future enhancement)

### Data Deletion

When a user deletes their account:
- User record deleted
- All members deleted
- All messages deleted
- All avatars deleted
- Sessions invalidated
- OAuth connections removed

## 🔍 Security Monitoring

### Logging

**What We Log**:
- Failed login attempts (with IP)
- Account creation
- Password changes
- OAuth connections
- Session creation/deletion
- API errors

**What We DON'T Log**:
- Passwords (plain or hashed)
- PK tokens
- Message content (unless error)
- Sensitive user data

### Recommended Monitoring

1. **Sentry** - Error tracking
2. **Grafana** - Metrics dashboard
3. **ELK Stack** - Log aggregation
4. **Uptime Robot** - Service monitoring

## 🛠️ Security Testing

### Manual Testing Checklist

- [ ] SQL injection attempts
- [ ] XSS payload injection
- [ ] CSRF token bypass
- [ ] Brute force password attempts
- [ ] Session hijacking
- [ ] OAuth flow manipulation
- [ ] File upload attacks
- [ ] Rate limit bypass
- [ ] WebSocket authentication bypass

### Automated Testing

```bash
# Security scan with Bandit
pip install bandit
bandit -r backend/app/

# Dependency vulnerability scan
pip install safety
safety check

# OWASP ZAP scanning
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:8000
```

## 📞 Security Contact

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email: security@example.com (update with actual)
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (optional)

## 🔄 Security Updates

This security documentation is reviewed quarterly and updated as needed.

**Last Updated**: November 2025
**Next Review**: February 2026

---

## ✅ Security Certifications

- OWASP Top 10 Compliance: ✅ Addressed
- GDPR Compliance: ✅ Partial (user rights implemented)
- SOC 2: ❌ Not certified (overkill for self-hosted)

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

**This is a living document. Contributions and improvements welcome!**
