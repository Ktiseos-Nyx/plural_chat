"""
Database configuration and models
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

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


# Database Models
class User(Base):
    """User/System from PluralKit"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # PK system ID
    pk_token = Column(String, nullable=False)  # Encrypted
    system_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_sync = Column(DateTime, nullable=True)

    # Relationships
    members = relationship("Member", back_populates="user", cascade="all, delete-orphan")


class Member(Base):
    """System member"""
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    pronouns = Column(String, nullable=True)
    color = Column(String, nullable=True)
    avatar_path = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    pk_id = Column(String, unique=True, nullable=True, index=True)
    proxy_tags = Column(Text, nullable=True)  # JSON string
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

    # Relationships
    member = relationship("Member", back_populates="messages")


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
