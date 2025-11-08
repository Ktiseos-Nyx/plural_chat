"""
Security router for 2FA and audit logs
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import os
from pathlib import Path
import uuid

from ..database import get_db
from .. import models
from ..auth_enhanced import (
    get_current_user,
    authenticate_user,
    create_access_token,
    verify_password
)
from ..totp_2fa import totp_manager
from ..audit import audit_logger

router = APIRouter()


# Request/Response Models
class LoginRequest(BaseModel):
    """Username/password login request"""
    username: str
    password: str
    totp_code: Optional[str] = None  # Include if 2FA is enabled
    backup_code: Optional[str] = None  # Alternative to TOTP code


class LoginResponse(BaseModel):
    """Login response"""
    access_token: Optional[str] = None
    token_type: str = "bearer"
    requires_2fa: bool = False
    user_id: Optional[int] = None
    message: Optional[str] = None


class RegisterRequest(BaseModel):
    """User registration request"""
    username: str
    password: str
    email: Optional[str] = None


class RegisterResponse(BaseModel):
    """Registration response"""
    success: bool
    message: str


class TOTPSetupResponse(BaseModel):
    """2FA setup response"""
    secret: str
    qr_code: str  # Base64 data URI
    backup_codes: List[str]
    message: str


class TOTPVerifyRequest(BaseModel):
    """2FA verification request"""
    code: str


class TOTPDisableRequest(BaseModel):
    """2FA disable request (requires password or current 2FA code)"""
    password: Optional[str] = None
    totp_code: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str


class UpdateProfileRequest(BaseModel):
    """Update profile request"""
    username: Optional[str] = None
    email: Optional[str] = None
    theme_color: Optional[str] = None


class AuditLogResponse(BaseModel):
    """Audit log entry"""
    id: int
    event_type: str
    category: str
    description: Optional[str]
    ip_address: Optional[str]
    success: bool
    timestamp: str


def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    # Check for X-Forwarded-For header (behind proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Extract user agent from request"""
    return request.headers.get("User-Agent", "unknown")


# Authentication Endpoints

@router.post("/register", response_model=RegisterResponse)
async def register_user(
    register_request: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user with username and password

    Args:
        username: Unique username (3+ characters)
        password: Password (8+ characters)
        email: Optional email address
    """
    from ..auth_enhanced import get_password_hash

    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)

    # Validate username
    if len(register_request.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters long"
        )

    # Validate password
    if len(register_request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )

    # Check if username already exists
    existing_user = db.query(models.User).filter(
        models.User.username == register_request.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )

    # Check if email already exists (if provided)
    if register_request.email:
        existing_email = db.query(models.User).filter(
            models.User.email == register_request.email
        ).first()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

    # Create new user
    hashed_password = get_password_hash(register_request.password)
    new_user = models.User(
        username=register_request.username,
        hashed_password=hashed_password,
        email=register_request.email,
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Log registration
    audit_logger.log(
        db=db,
        event_type="user_registered",
        category=audit_logger.CATEGORY_AUTH,
        user_id=new_user.id,
        description=f"New user registered: {register_request.username}",
        ip_address=ip_address,
        user_agent=user_agent
    )

    return RegisterResponse(
        success=True,
        message="Account created successfully! You can now log in."
    )


@router.post("/login", response_model=LoginResponse)
async def login_with_2fa(
    login_request: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login with username/password and optional 2FA

    Flow:
    1. Send username + password (no 2FA code)
       - If 2FA disabled: Returns access token
       - If 2FA enabled: Returns requires_2fa=true
    2. Send username + password + totp_code (or backup_code)
       - Returns access token if code is valid
    """
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)

    # Authenticate with username/password
    user = authenticate_user(db, login_request.username, login_request.password)

    if not user:
        # Log failed login
        audit_logger.log_login_failed(
            db=db,
            username=login_request.username,
            ip_address=ip_address,
            user_agent=user_agent,
            reason="invalid_credentials"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Check if 2FA is enabled
    if user.totp_enabled:
        # If no 2FA code provided, inform client 2FA is required
        if not login_request.totp_code and not login_request.backup_code:
            return LoginResponse(
                requires_2fa=True,
                user_id=user.id,
                message="2FA code required"
            )

        # Verify TOTP code
        if login_request.totp_code:
            secret = user.get_totp_secret()
            if not totp_manager.verify_code(secret, login_request.totp_code):
                # Log failed 2FA attempt
                audit_logger.log(
                    db=db,
                    event_type=audit_logger.EVENT_2FA_FAILED,
                    category=audit_logger.CATEGORY_AUTH,
                    user_id=user.id,
                    description="Failed 2FA verification during login",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False
                )

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid 2FA code"
                )

            # Log successful 2FA verification
            audit_logger.log(
                db=db,
                event_type=audit_logger.EVENT_2FA_VERIFIED,
                category=audit_logger.CATEGORY_AUTH,
                user_id=user.id,
                description="2FA verified during login",
                ip_address=ip_address,
                user_agent=user_agent
            )

        # Verify backup code
        elif login_request.backup_code:
            if not totp_manager.verify_backup_code(user, login_request.backup_code, db):
                # Log failed backup code
                audit_logger.log(
                    db=db,
                    event_type=audit_logger.EVENT_2FA_FAILED,
                    category=audit_logger.CATEGORY_AUTH,
                    user_id=user.id,
                    description="Failed backup code verification during login",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False
                )

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid backup code"
                )

            # Log backup code usage
            audit_logger.log(
                db=db,
                event_type=audit_logger.EVENT_BACKUP_CODE_USED,
                category=audit_logger.CATEGORY_SECURITY,
                user_id=user.id,
                description="Backup code used during login",
                ip_address=ip_address,
                user_agent=user_agent
            )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create access token
    access_token = create_access_token(data={"sub": user.id})

    # Log successful login
    audit_logger.log_login_success(
        db=db,
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        method="password" + ("+2fa" if user.totp_enabled else "")
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        requires_2fa=False,
        message="Login successful"
    )


@router.post("/change-password")
async def change_password(
    password_request: ChangePasswordRequest,
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password (requires current password)
    """
    from ..auth_enhanced import get_password_hash

    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)

    # Verify current password
    if not current_user.hashed_password or not verify_password(
        password_request.current_password,
        current_user.hashed_password
    ):
        # Log failed attempt
        audit_logger.log(
            db=db,
            event_type="password_change_failed",
            category=audit_logger.CATEGORY_SECURITY,
            user_id=current_user.id,
            description="Failed password change - invalid current password",
            ip_address=ip_address,
            user_agent=user_agent,
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Validate new password
    if len(password_request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_request.new_password)
    db.commit()

    # Log successful password change
    audit_logger.log(
        db=db,
        event_type="password_changed",
        category=audit_logger.CATEGORY_SECURITY,
        user_id=current_user.id,
        description="Password changed successfully",
        ip_address=ip_address,
        user_agent=user_agent
    )

    return {
        "success": True,
        "message": "Password changed successfully"
    }


@router.patch("/profile")
async def update_profile(
    profile_request: UpdateProfileRequest,
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile (username and/or email)
    """
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)

    changes = []

    # Update username if provided
    if profile_request.username and profile_request.username != current_user.username:
        # Validate username length
        if len(profile_request.username) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be at least 3 characters long"
            )

        # Check if username is already taken
        existing_user = db.query(models.User).filter(
            models.User.username == profile_request.username,
            models.User.id != current_user.id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )

        current_user.username = profile_request.username
        changes.append("username")

    # Update email if provided
    if profile_request.email is not None:
        if profile_request.email != current_user.email:
            # Validate email format if not empty
            if profile_request.email and not profile_request.email.strip():
                profile_request.email = None

            if profile_request.email:
                # Check if email is already taken
                existing_email = db.query(models.User).filter(
                    models.User.email == profile_request.email,
                    models.User.id != current_user.id
                ).first()

                if existing_email:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Email already registered"
                    )

            current_user.email = profile_request.email
            changes.append("email")

    # Update theme color if provided
    if profile_request.theme_color is not None:
        if profile_request.theme_color != current_user.theme_color:
            # Validate hex color format
            if profile_request.theme_color and not profile_request.theme_color.startswith('#'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Theme color must be a hex color code (e.g., #6c757d)"
                )

            current_user.theme_color = profile_request.theme_color
            changes.append("theme_color")

    if not changes:
        return {
            "success": True,
            "message": "No changes made"
        }

    db.commit()

    # Log profile update
    audit_logger.log(
        db=db,
        event_type="profile_updated",
        category=audit_logger.CATEGORY_PROFILE,
        user_id=current_user.id,
        description=f"Updated profile: {', '.join(changes)}",
        ip_address=ip_address,
        user_agent=user_agent
    )

    return {
        "success": True,
        "message": f"Profile updated successfully ({', '.join(changes)})"
    }


@router.post("/profile/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    request: Request = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a user avatar image
    Supported formats: JPEG, PNG, GIF, WebP
    Max size: 5MB
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )

    # Validate file size (5MB max)
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    contents = await file.read()
    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB"
        )

    # Create avatars directory if it doesn't exist
    avatars_dir = Path("avatars")
    avatars_dir.mkdir(exist_ok=True)

    # Generate unique filename
    file_ext = Path(file.filename).suffix or ".png"
    filename = f"user_{current_user.id}_{uuid.uuid4().hex[:8]}{file_ext}"
    file_path = avatars_dir / filename

    # Delete old avatar if exists
    if current_user.avatar_path:
        old_path = Path(current_user.avatar_path)
        if old_path.exists():
            try:
                old_path.unlink()
            except Exception as e:
                # Log but don't fail if old avatar can't be deleted
                print(f"Warning: Could not delete old avatar: {e}")

    # Save new avatar
    with open(file_path, "wb") as f:
        f.write(contents)

    # Update user record
    current_user.avatar_path = str(file_path)
    db.commit()

    # Log avatar update
    if request:
        audit_logger.log(
            db=db,
            event_type="avatar_updated",
            category=audit_logger.CATEGORY_PROFILE,
            user_id=current_user.id,
            description="Avatar image updated",
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )

    return {
        "success": True,
        "message": "Avatar uploaded successfully",
        "avatar_path": f"/avatars/{filename}"
    }


# 2FA Endpoints

@router.post("/2fa/setup", response_model=TOTPSetupResponse)
async def setup_2fa(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Setup 2FA for the current user
    Returns QR code and backup codes
    """
    # Check if already enabled
    if current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled. Disable it first to re-setup."
        )

    # Generate secret, backup codes, and QR code
    secret, backup_codes, qr_code = totp_manager.setup_2fa(current_user, db)

    # Log the setup initiation
    audit_logger.log(
        db=db,
        event_type="2fa_setup_initiated",
        category=audit_logger.CATEGORY_SECURITY,
        user_id=current_user.id,
        description="2FA setup initiated (not yet enabled)",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return {
        "secret": secret,
        "qr_code": qr_code,
        "backup_codes": backup_codes,
        "message": "Scan the QR code with your authenticator app, then verify with a code to enable 2FA"
    }


@router.post("/2fa/enable")
async def enable_2fa(
    verify_request: TOTPVerifyRequest,
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enable 2FA after verifying the initial code
    Must be called after /2fa/setup
    """
    if current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )

    # Verify code and enable
    if totp_manager.enable_2fa(current_user, verify_request.code, db):
        # Log successful 2FA enable
        audit_logger.log_2fa_enabled(
            db=db,
            user_id=current_user.id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )

        return {
            "success": True,
            "message": "2FA has been enabled successfully"
        }
    else:
        # Log failed attempt
        audit_logger.log(
            db=db,
            event_type=audit_logger.EVENT_2FA_FAILED,
            category=audit_logger.CATEGORY_SECURITY,
            user_id=current_user.id,
            description="Failed to enable 2FA - invalid code",
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            success=False
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )


@router.post("/2fa/disable")
async def disable_2fa(
    disable_request: TOTPDisableRequest,
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disable 2FA for the current user
    Requires either current password OR valid 2FA code
    """
    if not current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )

    verified = False

    # Verify with password
    if disable_request.password:
        from ..auth_enhanced import verify_password
        if current_user.hashed_password and verify_password(
            disable_request.password,
            current_user.hashed_password
        ):
            verified = True

    # Verify with TOTP code
    elif disable_request.totp_code:
        secret = current_user.get_totp_secret()
        if totp_manager.verify_code(secret, disable_request.totp_code):
            verified = True

    if verified:
        totp_manager.disable_2fa(current_user, db)

        # Log 2FA disabled
        audit_logger.log_2fa_disabled(
            db=db,
            user_id=current_user.id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )

        return {
            "success": True,
            "message": "2FA has been disabled"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password or 2FA code"
        )


@router.get("/2fa/status")
async def get_2fa_status(
    current_user: models.User = Depends(get_current_user)
):
    """
    Get 2FA status for current user
    """
    backup_codes_count = 0
    if current_user.totp_enabled:
        backup_codes = current_user.get_backup_codes()
        backup_codes_count = len(backup_codes)

    return {
        "enabled": current_user.totp_enabled,
        "backup_codes_remaining": backup_codes_count
    }


@router.post("/2fa/backup-codes/regenerate")
async def regenerate_backup_codes(
    verify_request: TOTPVerifyRequest,
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate backup codes (requires 2FA verification)
    Invalidates all previous backup codes
    """
    if not current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )

    # Verify current 2FA code
    secret = current_user.get_totp_secret()
    if not totp_manager.verify_code(secret, verify_request.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA code"
        )

    # Regenerate codes
    new_codes = totp_manager.regenerate_backup_codes(current_user, db)

    # Log the regeneration
    audit_logger.log(
        db=db,
        event_type="backup_codes_regenerated",
        category=audit_logger.CATEGORY_SECURITY,
        user_id=current_user.id,
        description="Backup codes regenerated",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return {
        "success": True,
        "backup_codes": new_codes,
        "message": "New backup codes generated. Save these securely!"
    }


# Audit Log Endpoints

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    limit: int = 50,
    category: Optional[str] = None,
    days: int = 30,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for current user

    Args:
        limit: Maximum number of logs to return (default 50, max 200)
        category: Filter by category (auth, security, profile, admin)
        days: Only logs from last N days (default 30, max 90)
    """
    # Validate limits
    limit = min(limit, 200)
    days = min(days, 90)

    logs = audit_logger.get_user_logs(
        db=db,
        user_id=current_user.id,
        limit=limit,
        category=category,
        days=days
    )

    return logs


@router.get("/audit-logs/security", response_model=List[AuditLogResponse])
async def get_security_logs(
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get security-related audit logs (2FA, password changes, etc.)
    """
    logs = audit_logger.get_user_logs(
        db=db,
        user_id=current_user.id,
        limit=limit,
        category=audit_logger.CATEGORY_SECURITY,
        days=90
    )

    return logs
