"""
Enhanced authentication with password hashing and OAuth
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import os
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError

from .database import get_db
from . import models, schemas

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token
security = HTTPBearer()

# OAuth Configuration
oauth = OAuth()

# Discord OAuth
oauth.register(
    name='discord',
    client_id=os.getenv('DISCORD_CLIENT_ID'),
    client_secret=os.getenv('DISCORD_CLIENT_SECRET'),
    authorize_url='https://discord.com/api/oauth2/authorize',
    authorize_params=None,
    access_token_url='https://discord.com/api/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    client_kwargs={'scope': 'identify email'},
)

# Google OAuth
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

# GitHub OAuth
oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    client_kwargs={'scope': 'user:email'},
)


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


# JWT Token utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    import logging
    logger = logging.getLogger(__name__)

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    logger.info(f"Creating token with data: {to_encode}, SECRET_KEY: {SECRET_KEY[:10]}...")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Created token: {encoded_jwt[:50]}...")
    return encoded_jwt


def verify_token(token: str) -> schemas.TokenData:
    """Verify and decode JWT token"""
    import logging
    logger = logging.getLogger(__name__)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.info(f"Verifying token with SECRET_KEY: {SECRET_KEY[:10]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"Token payload: {payload}")
        user_id_str: str = payload.get("sub")
        logger.info(f"Extracted user_id: {user_id_str}, type: {type(user_id_str)}")
        if user_id_str is None:
            logger.error("user_id is None")
            raise credentials_exception
        user_id = int(user_id_str)
        return schemas.TokenData(user_id=user_id)
    except JWTError as e:
        logger.error(f"JWT verification error: {e}")
        raise credentials_exception


# User authentication
def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """Authenticate user with username and password"""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return None
    if not user.hashed_password:  # OAuth-only account
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """Get current authenticated user from JWT token"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"get_current_user called with token: {credentials.credentials[:50]}...")
    token_data = verify_token(credentials.credentials)
    logger.info(f"Token verified, looking up user with id: {token_data.user_id}")
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    if user is None:
        logger.error(f"User not found with id: {token_data.user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    logger.info(f"User found: {user.username}, is_active: {user.is_active}")
    if not user.is_active:
        logger.error(f"User {user.username} is inactive")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    logger.info(f"Returning active user: {user.username}")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# OAuth user creation/retrieval
def get_or_create_oauth_user(
    db: Session,
    provider: str,
    oauth_id: str,
    email: Optional[str],
    username: str
) -> models.User:
    """Get existing OAuth user or create new one"""
    # Try to find by OAuth ID
    user = db.query(models.User).filter(
        models.User.oauth_provider == provider,
        models.User.oauth_id == oauth_id
    ).first()

    if user:
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        return user

    # Try to find by email (link accounts)
    if email:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            # Link OAuth to existing account
            user.oauth_provider = provider
            user.oauth_id = oauth_id
            user.last_login = datetime.utcnow()
            db.commit()
            return user

    # Create new user
    # Make username unique if it exists
    base_username = username
    counter = 1
    while db.query(models.User).filter(models.User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1

    new_user = models.User(
        username=username,
        email=email,
        oauth_provider=provider,
        oauth_id=oauth_id,
        is_active=True,
        is_verified=True,  # OAuth accounts are pre-verified
        last_login=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Password validation
def validate_password(password: str) -> None:
    """Validate password strength"""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    if not any(c.isdigit() for c in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one digit"
        )
    if not any(c.isalpha() for c in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one letter"
        )


# Username validation
def validate_username(username: str) -> None:
    """Validate username format"""
    if len(username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters long"
        )
    if len(username) > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at most 30 characters long"
        )
    if not username.replace('_', '').replace('-', '').isalnum():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must contain only letters, numbers, hyphens, and underscores"
        )
