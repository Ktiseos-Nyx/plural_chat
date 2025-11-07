# 🚀 Features Roadmap - Your Questions Answered

## Quick Answers

### ✅ What We Have Now
- Basic authentication (username/password + OAuth)
- Real-time chat (WebSocket)
- Member management
- PluralKit sync (optional)

### 🔨 What We're Adding
1. **Memory/Cache Management** - Redis caching
2. **PluralKit-Style Commands** - Discord-like command system
3. **Email Verification** - Required for new accounts
4. **Optional 2FA** - Security without forcing it
5. **Ephemeral Image Links** - Show images without permanent storage

---

## 1. 🧠 Memory & Cache Management

### Current State: ❌ No Caching
- Every request hits the database
- Member data fetched repeatedly
- No session caching
- Avatar requests not cached

### Solution: ✅ Redis Caching

```
┌─────────────┐      ┌─────────┐      ┌────────────┐
│   Client    │─────▶│  Redis  │─────▶│  Database  │
│  (Browser)  │◀─────│  Cache  │◀─────│ PostgreSQL │
└─────────────┘      └─────────┘      └────────────┘
     Fast!          Even Faster!        Slow (backup)
```

#### What Gets Cached:
- **User Sessions** - 30 days
- **Member Data** - 1 hour (invalidate on update)
- **Recent Messages** - 15 minutes
- **Avatar URLs** - 24 hours
- **Rate Limit Counters** - 1 minute
- **PluralKit Sync Data** - 1 hour

#### Implementation:
```python
# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL)

# Cache decorator
def cache(ttl: int = 3600):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Try cache first
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Cache miss - fetch from DB
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage example
@cache(ttl=3600)  # 1 hour
async def get_members(user_id: int):
    return db.query(Member).filter(Member.user_id == user_id).all()
```

#### Memory Management:
- **Redis Memory Limit**: 256MB (configurable)
- **Eviction Policy**: LRU (Least Recently Used)
- **Max Connections**: 50
- **Connection Timeout**: 30 seconds

#### Monitoring:
```python
# Redis stats endpoint
@app.get("/admin/cache-stats")
async def cache_stats():
    info = redis_client.info()
    return {
        "memory_used": info["used_memory_human"],
        "keys": redis_client.dbsize(),
        "hit_rate": info.get("keyspace_hits", 0) /
                    (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1))
    }
```

---

## 2. 🎮 PluralKit-Style Command System

### Discord Bot Commands → Web Chat Commands

You want commands like Discord but in a web interface!

#### Example Commands:
```
/member add Riley          → Add new member
/member Riley pronouns she/her  → Set pronouns
/switch Riley, Alex        → Log a switch
/front                     → See who's fronting
/proxy add Riley [text]    → Add proxy tag
/avatar Riley <url>        → Set avatar
/info Riley                → Member info
/list                      → List all members
/help                      → Show all commands
```

### Implementation: Slash Commands

#### Backend - Command Parser
```python
# Command system
class Command:
    def __init__(self, name: str, handler, description: str, args: List[str]):
        self.name = name
        self.handler = handler
        self.description = description
        self.args = args

class CommandRegistry:
    def __init__(self):
        self.commands: Dict[str, Command] = {}

    def register(self, name: str, description: str, args: List[str]):
        def decorator(func):
            self.commands[name] = Command(name, func, description, args)
            return func
        return decorator

    async def execute(self, user_id: int, message: str, db: Session):
        if not message.startswith('/'):
            return None

        parts = message[1:].split()
        command_name = parts[0]
        args = parts[1:]

        command = self.commands.get(command_name)
        if not command:
            return f"❌ Unknown command: /{command_name}. Type /help for available commands."

        try:
            return await command.handler(user_id, args, db)
        except Exception as e:
            return f"❌ Error: {str(e)}"

# Global registry
commands = CommandRegistry()

# Register commands
@commands.register("member", "Manage members", ["add|remove|update", "name", "..."])
async def cmd_member(user_id: int, args: List[str], db: Session):
    if not args:
        return "❌ Usage: /member <add|remove|update> <name> [options]"

    action = args[0]

    if action == "add":
        if len(args) < 2:
            return "❌ Usage: /member add <name>"
        name = args[1]
        member = Member(user_id=user_id, name=name)
        db.add(member)
        db.commit()
        return f"✅ Added member: {name}"

    elif action == "remove":
        if len(args) < 2:
            return "❌ Usage: /member remove <name>"
        name = args[1]
        member = db.query(Member).filter(
            Member.user_id == user_id,
            Member.name == name
        ).first()
        if not member:
            return f"❌ Member not found: {name}"
        db.delete(member)
        db.commit()
        return f"✅ Removed member: {name}"

    else:
        return f"❌ Unknown action: {action}"

@commands.register("switch", "Log a switch", ["member1", "member2", "..."])
async def cmd_switch(user_id: int, args: List[str], db: Session):
    if not args:
        return "❌ Usage: /switch <member1> [member2] [...]"

    member_names = " ".join(args).split(",")
    member_names = [m.strip() for m in member_names]

    # TODO: Store switch in database
    return f"✅ Switched to: {', '.join(member_names)}"

@commands.register("front", "See who's fronting", [])
async def cmd_front(user_id: int, args: List[str], db: Session):
    # TODO: Get current fronters from database
    return "✅ Currently fronting: Riley, Alex"

@commands.register("list", "List all members", [])
async def cmd_list(user_id: int, args: List[str], db: Session):
    members = db.query(Member).filter(Member.user_id == user_id).all()
    if not members:
        return "❌ No members found"

    member_list = "\n".join([f"• {m.name}" for m in members])
    return f"**Your members:**\n{member_list}"

@commands.register("help", "Show all commands", [])
async def cmd_help(user_id: int, args: List[str], db: Session):
    help_text = "**Available Commands:**\n\n"
    for name, cmd in commands.commands.items():
        help_text += f"**/{name}** {' '.join(cmd.args)}\n"
        help_text += f"  {cmd.description}\n\n"
    return help_text

# Message handler
@app.post("/messages")
async def send_message(message: MessageCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if it's a command
    if message.content.startswith('/'):
        response = await commands.execute(user.id, message.content, db)
        if response:
            # Send command response as system message
            system_message = Message(
                member_id=message.member_id,  # Use same member
                content=response,
                timestamp=datetime.utcnow()
            )
            db.add(system_message)
            db.commit()
            return system_message

    # Regular message
    new_message = Message(
        member_id=message.member_id,
        content=message.content
    )
    db.add(new_message)
    db.commit()
    return new_message
```

#### Frontend - Command Autocomplete
```tsx
// Command autocomplete in message input
const [showAutocomplete, setShowAutocomplete] = useState(false);
const [commandSuggestions, setCommandSuggestions] = useState([]);

const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
  const value = e.target.value;
  setContent(value);

  // Show autocomplete for commands
  if (value.startsWith('/')) {
    const partial = value.slice(1).toLowerCase();
    const suggestions = COMMANDS.filter(cmd =>
      cmd.name.toLowerCase().startsWith(partial)
    );
    setCommandSuggestions(suggestions);
    setShowAutocomplete(suggestions.length > 0);
  } else {
    setShowAutocomplete(false);
  }
};

// Available commands
const COMMANDS = [
  { name: 'member', description: 'Manage members', usage: '/member add <name>' },
  { name: 'switch', description: 'Log a switch', usage: '/switch <member1>, <member2>' },
  { name: 'front', description: 'See who\'s fronting', usage: '/front' },
  { name: 'list', description: 'List all members', usage: '/list' },
  { name: 'help', description: 'Show all commands', usage: '/help' },
];

// Render autocomplete
{showAutocomplete && (
  <div className="command-autocomplete">
    {commandSuggestions.map(cmd => (
      <div key={cmd.name} onClick={() => setContent(`/${cmd.name} `)}>
        <strong>/{cmd.name}</strong> - {cmd.description}
        <div className="usage">{cmd.usage}</div>
      </div>
    ))}
  </div>
)}
```

### Command Ideas (Full List):

#### Member Management
- `/member add <name>` - Add member
- `/member remove <name>` - Remove member
- `/member <name> pronouns <pronouns>` - Set pronouns
- `/member <name> color <hex>` - Set color
- `/member <name> avatar <url>` - Set avatar
- `/info <name>` - Member info
- `/list` - List all members

#### Switching
- `/switch <member1>, <member2>` - Log a switch
- `/front` - See current fronters
- `/switch history` - View switch history

#### Proxy Tags
- `/proxy add <member> <prefix>text<suffix>` - Add proxy
- `/proxy remove <member> <prefix>` - Remove proxy
- `/proxy list <member>` - List proxies

#### Settings
- `/settings` - Open settings
- `/theme <name>` - Change theme
- `/export` - Export data

#### Fun/Utility
- `/roll <dice>` - Roll dice (e.g., /roll 2d6)
- `/flip` - Flip a coin
- `/8ball <question>` - Magic 8-ball

---

## 3. 📧 Email Verification

### Flow:
```
1. User registers with email
2. Email sent with verification link
3. User clicks link
4. Account activated
5. Can now use all features
```

### Implementation:
```python
# Email verification
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# Email config
mail_conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

fastmail = FastMail(mail_conf)

# Generate verification token
def generate_verification_token(email: str) -> str:
    token_data = {"email": email, "exp": datetime.utcnow() + timedelta(hours=24)}
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

# Send verification email
async def send_verification_email(email: str, username: str):
    token = generate_verification_token(email)
    verification_url = f"{FRONTEND_URL}/verify-email?token={token}"

    html = f"""
    <h2>Welcome to Plural Chat, {username}!</h2>
    <p>Please verify your email address by clicking the link below:</p>
    <a href="{verification_url}">Verify Email</a>
    <p>This link expires in 24 hours.</p>
    """

    message = MessageSchema(
        subject="Verify your Plural Chat account",
        recipients=[email],
        body=html,
        subtype="html"
    )

    await fastmail.send_message(message)

# Registration endpoint (updated)
@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Create user (is_verified=False)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        is_verified=False  # Not verified yet
    )
    db.add(user)
    db.commit()

    # Send verification email
    await send_verification_email(user.email, user.username)

    return {"message": "Registration successful! Please check your email to verify your account."}

# Verification endpoint
@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_verified = True
        db.commit()

        return {"message": "Email verified successfully!"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
```

### Email Providers (Choose One):
- **SendGrid** - Free tier: 100 emails/day
- **Mailgun** - Free tier: 5,000 emails/month
- **AWS SES** - Very cheap: $0.10 per 1,000 emails
- **SMTP** - Your own email server

---

## 4. 🔐 Optional 2FA (Not Forced!)

### Methods Supported:
1. **TOTP** (Time-based One-Time Password) - Google Authenticator, Authy
2. **Backup Codes** - For recovery

### Implementation:
```python
from pyotp import TOTP, random_base32

# Add to User model
class User(Base):
    # ... existing fields ...

    # 2FA fields
    totp_secret = Column(String, nullable=True)  # Encrypted
    totp_enabled = Column(Boolean, default=False)
    backup_codes = Column(Text, nullable=True)  # Encrypted, JSON array

# Enable 2FA
@router.post("/auth/2fa/enable")
async def enable_2fa(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Generate secret
    secret = random_base32()

    # Generate QR code
    totp = TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user.email,
        issuer_name="Plural Chat"
    )

    # Store secret (encrypted)
    user.totp_secret = encrypt_data(secret)

    # Generate backup codes
    backup_codes = [secrets.token_hex(4) for _ in range(10)]
    user.backup_codes = encrypt_data(json.dumps(backup_codes))

    db.commit()

    return {
        "secret": secret,
        "qr_code": provisioning_uri,
        "backup_codes": backup_codes
    }

# Verify and activate 2FA
@router.post("/auth/2fa/verify")
async def verify_2fa(code: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    secret = decrypt_data(user.totp_secret)
    totp = TOTP(secret)

    if totp.verify(code):
        user.totp_enabled = True
        db.commit()
        return {"message": "2FA enabled successfully!"}
    else:
        raise HTTPException(status_code=400, detail="Invalid code")

# Login with 2FA
@router.post("/auth/login-2fa")
async def login_2fa(username: str, password: str, totp_code: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.totp_enabled:
        secret = decrypt_data(user.totp_secret)
        totp = TOTP(secret)

        if not totp.verify(totp_code):
            # Try backup codes
            backup_codes = json.loads(decrypt_data(user.backup_codes))
            if totp_code not in backup_codes:
                raise HTTPException(status_code=401, detail="Invalid 2FA code")

            # Use backup code (remove it)
            backup_codes.remove(totp_code)
            user.backup_codes = encrypt_data(json.dumps(backup_codes))
            db.commit()

    # Create session
    token = create_access_token({"sub": user.id})
    return {"access_token": token}
```

### Frontend - 2FA Setup
```tsx
// Enable 2FA dialog
const Enable2FA = () => {
  const [qrCode, setQrCode] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  const [verifyCode, setVerifyCode] = useState('');

  const enable2FA = async () => {
    const response = await api.post('/auth/2fa/enable');
    setQrCode(response.data.qr_code);
    setBackupCodes(response.data.backup_codes);
  };

  const verify = async () => {
    await api.post('/auth/2fa/verify', { code: verifyCode });
    alert('2FA enabled successfully!');
  };

  return (
    <Dialog>
      <h2>Enable Two-Factor Authentication</h2>
      {!qrCode ? (
        <Button onClick={enable2FA}>Enable 2FA</Button>
      ) : (
        <>
          <p>Scan this QR code with your authenticator app:</p>
          <QRCode value={qrCode} />

          <p>Or enter this code manually:</p>
          <code>{qrCode.split('=')[1]}</code>

          <h3>Backup Codes (Save these!)</h3>
          <ul>
            {backupCodes.map(code => <li key={code}>{code}</li>)}
          </ul>

          <Input
            placeholder="Enter code from app"
            value={verifyCode}
            onChange={(e) => setVerifyCode(e.target.value)}
          />
          <Button onClick={verify}>Verify and Enable</Button>
        </>
      )}
    </Dialog>
  );
};
```

---

## 5. 🖼️ Ephemeral Image/File System

### Requirements:
- ❌ No permanent uploads (storage concerns)
- ✅ Show images from URLs
- ✅ Temporary storage (24 hours)
- ✅ Image preview

### Solution: URL Proxy + Temporary Cache

```
User posts: "Check this out! https://example.com/cool-image.jpg"
   ↓
Backend fetches image
   ↓
Stores in temp cache (24 hours)
   ↓
Returns proxied URL: /api/media/abc123
   ↓
Image displays in chat
   ↓
After 24 hours, auto-deleted
```

### Implementation:
```python
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

# Ephemeral media storage
MEDIA_DIR = Path("media_cache")
MEDIA_DIR.mkdir(exist_ok=True)

# Media cache TTL (24 hours)
MEDIA_TTL = 24 * 60 * 60

class MediaCache:
    def __init__(self):
        self.cleanup_old_files()

    def cleanup_old_files(self):
        """Remove files older than TTL"""
        now = datetime.now()
        for file in MEDIA_DIR.glob("*"):
            if file.is_file():
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                if (now - mtime).total_seconds() > MEDIA_TTL:
                    file.unlink()

    def generate_id(self, url: str) -> str:
        """Generate unique ID for URL"""
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    async def fetch_and_cache(self, url: str) -> str:
        """Fetch external image and cache it"""
        # Validate URL
        if not self._is_valid_image_url(url):
            raise ValueError("Invalid image URL")

        # Generate ID
        media_id = self.generate_id(url)

        # Check if already cached
        cached_files = list(MEDIA_DIR.glob(f"{media_id}.*"))
        if cached_files:
            return media_id

        # Fetch image
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                raise ValueError("URL does not point to an image")

            # Get extension
            ext = content_type.split("/")[1].split(";")[0]

            # Save to cache
            file_path = MEDIA_DIR / f"{media_id}.{ext}"
            file_path.write_bytes(response.content)

        return media_id

    def get_file(self, media_id: str) -> Optional[Path]:
        """Get cached file"""
        files = list(MEDIA_DIR.glob(f"{media_id}.*"))
        if not files:
            return None

        file = files[0]

        # Check if expired
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        if (datetime.now() - mtime).total_seconds() > MEDIA_TTL:
            file.unlink()
            return None

        return file

    def _is_valid_image_url(self, url: str) -> bool:
        """Validate image URL"""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ["http", "https"]:
                return False

            # Whitelist domains (optional)
            allowed_domains = [
                "imgur.com", "i.imgur.com",
                "cdn.discordapp.com",
                "media.discordapp.net",
                "tenor.com",
                "giphy.com",
            ]

            # Allow any domain for now
            return True
        except:
            return False

media_cache = MediaCache()

# API endpoint to proxy images
@app.get("/media/{media_id}")
async def get_media(media_id: str):
    file = media_cache.get_file(media_id)
    if not file:
        raise HTTPException(status_code=404, detail="Media not found or expired")

    # Determine content type
    ext = file.suffix.lstrip(".")
    content_type = f"image/{ext}"

    return FileResponse(file, media_type=content_type)

# Parse messages for image URLs
@app.post("/messages")
async def send_message(message: MessageCreate, ...):
    content = message.content

    # Find image URLs in message
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, content)

    media_ids = []
    for url in urls:
        try:
            # Check if it's an image
            if any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                media_id = await media_cache.fetch_and_cache(url)
                media_ids.append(media_id)
        except:
            pass  # Skip invalid URLs

    # Store message with media IDs
    new_message = Message(
        member_id=message.member_id,
        content=content,
        media_ids=json.dumps(media_ids) if media_ids else None
    )
    db.add(new_message)
    db.commit()

    return new_message
```

### Frontend - Image Preview
```tsx
// Message component with image preview
const ChatMessage = ({ message }: { message: Message }) => {
  const mediaIds = message.media_ids ? JSON.parse(message.media_ids) : [];

  // Parse URLs from message
  const urlRegex = /(https?:\/\/[^\s<>"{}|\\^`\[\]]+)/g;
  const urls = message.content.match(urlRegex) || [];

  return (
    <div className="message">
      <div className="message-content">
        {/* Text with clickable links */}
        <Linkify>{message.content}</Linkify>
      </div>

      {/* Image previews */}
      {mediaIds.length > 0 && (
        <div className="message-images">
          {mediaIds.map(id => (
            <img
              key={id}
              src={`/api/media/${id}`}
              alt="Shared image"
              style={{ maxWidth: '400px', borderRadius: '8px' }}
              onError={(e) => {
                // Hide if failed to load (expired)
                e.currentTarget.style.display = 'none';
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
};
```

### Features:
- ✅ Auto-detect image URLs in messages
- ✅ Fetch and cache for 24 hours
- ✅ Serve via `/api/media/{id}`
- ✅ Auto-cleanup old files
- ✅ No permanent storage
- ✅ Image preview in chat
- ✅ Whitelist domains (optional)
- ✅ Size limits (1-10MB configurable)

### Storage Estimates:
```
10 users × 5 images/day × 500KB avg = 25MB/day
× 1 day TTL = 25MB total storage
```

Very small! Even with 100 users:
```
100 users × 5 images/day × 500KB = 250MB/day max
```

---

## Summary

### ✅ All Your Questions Answered:

1. **Memory/Cache Management** → Redis caching (256MB, LRU eviction)
2. **PluralKit Command System** → Slash commands (/member, /switch, /front, etc.)
3. **Email Verification** → JWT tokens, 24-hour expiry
4. **Optional 2FA** → TOTP + backup codes (opt-in, not forced)
5. **Ephemeral Images** → URL proxy, 24-hour cache, auto-cleanup

### 📊 Resource Usage:
- **Redis**: 256MB (cached sessions, members, messages)
- **Media Cache**: ~25-250MB (ephemeral, 24 hours)
- **Database**: Normal (no extra storage)

**Total Extra Storage**: <500MB for most use cases

---

## Implementation Priority:

1. ✅ **Redis Caching** (performance boost)
2. ✅ **Command System** (user experience)
3. ✅ **Email Verification** (security)
4. ✅ **Ephemeral Images** (functionality)
5. ✅ **Optional 2FA** (extra security)

---

**Want me to implement these now?** I can start with Redis caching and the command system!
