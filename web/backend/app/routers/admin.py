"""
Admin panel router
Simple, friendly admin interface "for numptys" 😊
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
import os

from ..database import get_db
from .. import models, schemas
from ..auth_enhanced import get_current_user

router = APIRouter()


def is_admin(user: models.User) -> bool:
    """Check if user is admin (simple check for now)"""
    # Simple admin check: username is 'admin' or email domain is specific
    # You can customize this based on your needs
    if user.username == "admin":
        return True
    # Or check environment variable for admin usernames
    admin_users = os.getenv("ADMIN_USERS", "admin").split(",")
    return user.username in admin_users


def require_admin(current_user: models.User = Depends(get_current_user)):
    """Dependency to require admin access"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ============================================================================
# Dashboard / Overview
# ============================================================================

@router.get("/dashboard")
async def get_dashboard(
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get admin dashboard overview
    All the stats you need in one place!
    """
    # User stats
    total_users = db.query(func.count(models.User.id)).scalar()
    verified_users = db.query(func.count(models.User.id)).filter(
        models.User.is_verified == True
    ).scalar()
    active_users = db.query(func.count(models.User.id)).filter(
        models.User.is_active == True
    ).scalar()

    # Recent users (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_users = db.query(func.count(models.User.id)).filter(
        models.User.created_at >= week_ago
    ).scalar()

    # Member stats
    total_members = db.query(func.count(models.Member.id)).scalar()
    active_members = db.query(func.count(models.Member.id)).filter(
        models.Member.is_active == True
    ).scalar()

    # Message stats
    total_messages = db.query(func.count(models.Message.id)).scalar()
    messages_today = db.query(func.count(models.Message.id)).filter(
        models.Message.timestamp >= datetime.utcnow().date()
    ).scalar()

    # Media cache stats
    from ..media_cache import media_cache
    media_stats = media_cache.get_stats()

    # Cache stats (if Redis available)
    cache_stats = {}
    try:
        from ..cache import Cache
        cache_stats = Cache.get_stats()
    except:
        cache_stats = {"status": "unavailable"}

    return {
        "users": {
            "total": total_users,
            "verified": verified_users,
            "active": active_users,
            "recent_signups": recent_users
        },
        "members": {
            "total": total_members,
            "active": active_members
        },
        "messages": {
            "total": total_messages,
            "today": messages_today
        },
        "media": media_stats,
        "cache": cache_stats
    }


# ============================================================================
# User Management
# ============================================================================

@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = None,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users with pagination and search
    Perfect for finding that one user who sneezed on their keyboard!
    """
    query = db.query(models.User)

    if search:
        query = query.filter(
            (models.User.username.ilike(f"%{search}%")) |
            (models.User.email.ilike(f"%{search}%"))
        )

    total = query.count()
    users = query.order_by(desc(models.User.created_at)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "oauth_provider": user.oauth_provider,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "member_count": len(user.members)
            }
            for user in users
        ]
    }


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: int,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed info about a specific user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get member info
    members = [
        {
            "id": member.id,
            "name": member.name,
            "pronouns": member.pronouns,
            "is_active": member.is_active,
            "created_at": member.created_at.isoformat()
        }
        for member in user.members
    ]

    # Get message count
    message_count = db.query(func.count(models.Message.id)).join(models.Member).filter(
        models.Member.user_id == user_id
    ).scalar()

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "oauth_provider": user.oauth_provider,
        "pk_system_id": user.pk_system_id,
        "system_name": user.system_name,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "last_sync": user.last_sync.isoformat() if user.last_sync else None,
        "members": members,
        "message_count": message_count
    }


@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update user status
    Useful for fixing accounts when users sneeze on keyboards!
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if is_active is not None:
        user.is_active = is_active
    if is_verified is not None:
        user.is_verified = is_verified

    db.commit()
    db.refresh(user)

    return {
        "message": "User updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "is_active": user.is_active,
            "is_verified": user.is_verified
        }
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user and all their data
    Use with caution! This is permanent!
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Don't allow deleting yourself
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account from admin panel"
        )

    username = user.username
    db.delete(user)
    db.commit()

    return {
        "message": f"User '{username}' and all their data deleted successfully"
    }


# ============================================================================
# System Maintenance
# ============================================================================

@router.post("/cleanup/media")
async def cleanup_media(
    admin: models.User = Depends(require_admin)
):
    """
    Manually trigger media cache cleanup
    Removes expired images (older than 24 hours)
    """
    from ..media_cache import media_cache

    deleted = media_cache.cleanup_old_files()

    return {
        "message": "Media cleanup completed",
        "files_deleted": deleted,
        "stats": media_cache.get_stats()
    }


@router.post("/cleanup/cache")
async def cleanup_cache(
    admin: models.User = Depends(require_admin)
):
    """
    Clear Redis cache
    Use this if cache gets wonky!
    """
    try:
        from ..cache import Cache
        Cache.clear_all()
        return {
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        return {
            "message": "Cache cleanup failed",
            "error": str(e)
        }


@router.get("/stats/database")
async def get_database_stats(
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed database statistics
    All the numbers you could ever want!
    """
    # Table counts
    users_count = db.query(func.count(models.User.id)).scalar()
    members_count = db.query(func.count(models.Member.id)).scalar()
    messages_count = db.query(func.count(models.Message.id)).scalar()
    sessions_count = db.query(func.count(models.Session.id)).scalar()

    # Active sessions
    active_sessions = db.query(func.count(models.Session.id)).filter(
        models.Session.is_valid == True,
        models.Session.expires_at > datetime.utcnow()
    ).scalar()

    # Recent activity
    today = datetime.utcnow().date()
    messages_today = db.query(func.count(models.Message.id)).filter(
        models.Message.timestamp >= today
    ).scalar()

    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = db.query(func.count(models.User.id)).filter(
        models.User.created_at >= week_ago
    ).scalar()

    # Top active users (by message count)
    top_users = db.query(
        models.User.username,
        func.count(models.Message.id).label('message_count')
    ).join(models.Member).join(models.Message).group_by(
        models.User.id, models.User.username
    ).order_by(desc('message_count')).limit(10).all()

    return {
        "tables": {
            "users": users_count,
            "members": members_count,
            "messages": messages_count,
            "sessions": sessions_count
        },
        "active_sessions": active_sessions,
        "recent_activity": {
            "messages_today": messages_today,
            "new_users_this_week": new_users_week
        },
        "top_users": [
            {"username": username, "message_count": count}
            for username, count in top_users
        ]
    }


@router.get("/health")
async def health_check(
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    System health check
    Make sure everything is working!
    """
    health = {
        "database": "ok",
        "cache": "unknown",
        "media_cache": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }

    # Check database
    try:
        db.execute("SELECT 1")
        health["database"] = "ok"
    except Exception as e:
        health["database"] = f"error: {str(e)}"

    # Check Redis cache
    try:
        from ..cache import Cache
        Cache.get("health_check")
        health["cache"] = "ok"
    except Exception as e:
        health["cache"] = f"error: {str(e)}"

    # Check media cache
    try:
        from ..media_cache import MEDIA_DIR
        if MEDIA_DIR.exists():
            health["media_cache"] = "ok"
        else:
            health["media_cache"] = "directory missing"
    except Exception as e:
        health["media_cache"] = f"error: {str(e)}"

    return health


# ============================================================================
# Configuration (Read-only for now)
# ============================================================================

@router.get("/config")
async def get_config(
    admin: models.User = Depends(require_admin)
):
    """
    View current configuration
    Shows environment variables and settings
    """
    return {
        "environment": {
            "database_url": os.getenv("DATABASE_URL", "sqlite:///./app.db").split("@")[-1],  # Hide credentials
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "frontend_url": os.getenv("FRONTEND_URL", "http://localhost:3000")
        },
        "features": {
            "email_enabled": bool(os.getenv("MAIL_USERNAME")),
            "oauth_discord": bool(os.getenv("DISCORD_CLIENT_ID")),
            "oauth_google": bool(os.getenv("GOOGLE_CLIENT_ID")),
            "oauth_github": bool(os.getenv("GITHUB_CLIENT_ID"))
        },
        "limits": {
            "max_media_size_mb": int(os.getenv("MAX_MEDIA_SIZE", 10 * 1024 * 1024)) / (1024 * 1024),
            "media_ttl_hours": 24
        }
    }
