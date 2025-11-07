"""
Enhanced database models with proper authentication and security
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

# Database URL from environment or default to SQLite for development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./plural_chat.db"
)

# PostgreSQL URL fix for SQLAlchemy 2.0
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=True  # Set to False in production
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Encryption key for sensitive data
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generate a key if not provided (for development only)
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"⚠️  WARNING: Using auto-generated encryption key. Set ENCRYPTION_KEY in production!")

cipher = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)


# Database Models
class User(Base):
    """User account with multiple auth methods"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth-only users

    # OAuth fields
    oauth_provider = Column(String, nullable=True)  # 'discord', 'google', 'github', None
    oauth_id = Column(String, nullable=True, index=True)  # Provider's user ID

    # PluralKit integration (optional)
    pk_system_id = Column(String, nullable=True, index=True)
    pk_token_encrypted = Column(LargeBinary, nullable=True)  # Encrypted PK token
    system_name = Column(String, nullable=True)

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    last_sync = Column(DateTime, nullable=True)

    # Relationships
    members = relationship("Member", back_populates="user", cascade="all, delete-orphan")

    def set_pk_token(self, token: str):
        """Encrypt and store PluralKit token"""
        if token:
            self.pk_token_encrypted = cipher.encrypt(token.encode())

    def get_pk_token(self) -> str:
        """Decrypt and return PluralKit token"""
        if self.pk_token_encrypted:
            return cipher.decrypt(self.pk_token_encrypted).decode()
        return None


class Member(Base):
    """System member"""
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    pronouns = Column(String, nullable=True)
    color = Column(String, nullable=True)
    avatar_path = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    pk_id = Column(String, nullable=True, index=True)  # Optional PK member ID
    proxy_tags = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="members")
    messages = relationship("Message", back_populates="member", cascade="all, delete-orphan")


class Message(Base):
    """Chat message"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    edited_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    member = relationship("Member", back_populates="messages")


class Session(Base):
    """User sessions for security tracking"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_valid = Column(Boolean, default=True)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def encrypt_data(data: str) -> bytes:
    """Encrypt sensitive data"""
    return cipher.encrypt(data.encode())


def decrypt_data(encrypted: bytes) -> str:
    """Decrypt sensitive data"""
    return cipher.decrypt(encrypted).decode()
