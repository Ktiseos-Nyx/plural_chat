"""
Audit logging system for security events
Tracks authentication, security changes, and administrative actions
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
import json
import logging

from . import models

logger = logging.getLogger(__name__)


class AuditLogger:
    """Security audit logger"""

    # Event types
    EVENT_LOGIN_SUCCESS = "login_success"
    EVENT_LOGIN_FAILED = "login_failed"
    EVENT_LOGOUT = "logout"
    EVENT_2FA_ENABLED = "2fa_enabled"
    EVENT_2FA_DISABLED = "2fa_disabled"
    EVENT_2FA_VERIFIED = "2fa_verified"
    EVENT_2FA_FAILED = "2fa_failed"
    EVENT_BACKUP_CODE_USED = "backup_code_used"
    EVENT_PASSWORD_CHANGED = "password_changed"
    EVENT_PASSWORD_RESET = "password_reset"
    EVENT_EMAIL_CHANGED = "email_changed"
    EVENT_EMAIL_VERIFIED = "email_verified"
    EVENT_ACCOUNT_CREATED = "account_created"
    EVENT_ACCOUNT_DELETED = "account_deleted"
    EVENT_OAUTH_LINKED = "oauth_linked"
    EVENT_SESSION_INVALIDATED = "session_invalidated"
    EVENT_SUSPICIOUS_ACTIVITY = "suspicious_activity"
    EVENT_RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

    # Event categories
    CATEGORY_AUTH = "auth"
    CATEGORY_SECURITY = "security"
    CATEGORY_PROFILE = "profile"
    CATEGORY_ADMIN = "admin"

    @staticmethod
    def log(
        db: Session,
        event_type: str,
        category: str,
        user_id: Optional[int] = None,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log security event

        Args:
            db: Database session
            event_type: Type of event (use EVENT_* constants)
            category: Category (use CATEGORY_* constants)
            user_id: User ID (optional for unauthenticated events)
            description: Human-readable description
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether the action was successful
            metadata: Additional JSON metadata
        """
        try:
            audit_log = models.AuditLog(
                user_id=user_id,
                event_type=event_type,
                event_category=category,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                metadata=json.dumps(metadata) if metadata else None,
                timestamp=datetime.utcnow()
            )

            db.add(audit_log)
            db.commit()

            logger.info(
                f"AUDIT: {event_type} - User: {user_id} - Success: {success} - "
                f"IP: {ip_address} - {description or ''}"
            )
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            db.rollback()

    @staticmethod
    def log_login_success(
        db: Session,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        method: str = "password"
    ):
        """Log successful login"""
        AuditLogger.log(
            db=db,
            event_type=AuditLogger.EVENT_LOGIN_SUCCESS,
            category=AuditLogger.CATEGORY_AUTH,
            user_id=user_id,
            description=f"User logged in via {method}",
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            metadata={"method": method}
        )

    @staticmethod
    def log_login_failed(
        db: Session,
        username: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        reason: str = "invalid_credentials"
    ):
        """Log failed login attempt"""
        AuditLogger.log(
            db=db,
            event_type=AuditLogger.EVENT_LOGIN_FAILED,
            category=AuditLogger.CATEGORY_AUTH,
            user_id=None,
            description=f"Failed login attempt for username: {username}",
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            metadata={"username": username, "reason": reason}
        )

    @staticmethod
    def log_2fa_enabled(
        db: Session,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log 2FA enabled"""
        AuditLogger.log(
            db=db,
            event_type=AuditLogger.EVENT_2FA_ENABLED,
            category=AuditLogger.CATEGORY_SECURITY,
            user_id=user_id,
            description="Two-factor authentication enabled",
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )

    @staticmethod
    def log_2fa_disabled(
        db: Session,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log 2FA disabled"""
        AuditLogger.log(
            db=db,
            event_type=AuditLogger.EVENT_2FA_DISABLED,
            category=AuditLogger.CATEGORY_SECURITY,
            user_id=user_id,
            description="Two-factor authentication disabled",
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )

    @staticmethod
    def log_password_changed(
        db: Session,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log password change"""
        AuditLogger.log(
            db=db,
            event_type=AuditLogger.EVENT_PASSWORD_CHANGED,
            category=AuditLogger.CATEGORY_SECURITY,
            user_id=user_id,
            description="Password changed",
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )

    @staticmethod
    def get_user_logs(
        db: Session,
        user_id: int,
        limit: int = 50,
        category: Optional[str] = None,
        days: int = 30
    ) -> list:
        """
        Get audit logs for a user

        Args:
            db: Database session
            user_id: User ID
            limit: Max number of logs to return
            category: Filter by category
            days: Only logs from last N days

        Returns:
            List of audit log dicts
        """
        query = db.query(models.AuditLog).filter(
            models.AuditLog.user_id == user_id,
            models.AuditLog.timestamp >= datetime.utcnow() - timedelta(days=days)
        )

        if category:
            query = query.filter(models.AuditLog.event_category == category)

        logs = query.order_by(desc(models.AuditLog.timestamp)).limit(limit).all()

        return [
            {
                "id": log.id,
                "event_type": log.event_type,
                "category": log.event_category,
                "description": log.description,
                "ip_address": log.ip_address,
                "success": log.success,
                "timestamp": log.timestamp.isoformat(),
                "metadata": json.loads(log.extra_data) if log.extra_data else None
            }
            for log in logs
        ]

    @staticmethod
    def get_failed_login_attempts(
        db: Session,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        minutes: int = 15
    ) -> int:
        """
        Count failed login attempts in time window

        Args:
            db: Database session
            username: Filter by username (from metadata)
            ip_address: Filter by IP address
            minutes: Time window in minutes

        Returns:
            Number of failed attempts
        """
        query = db.query(models.AuditLog).filter(
            models.AuditLog.event_type == AuditLogger.EVENT_LOGIN_FAILED,
            models.AuditLog.timestamp >= datetime.utcnow() - timedelta(minutes=minutes)
        )

        if ip_address:
            query = query.filter(models.AuditLog.ip_address == ip_address)

        if username:
            # Note: This requires parsing JSON extra_data which is slower
            # For production, consider adding a separate username column
            logs = query.all()
            count = 0
            for log in logs:
                if log.extra_data:
                    try:
                        metadata = json.loads(log.extra_data)
                        if metadata.get("username") == username:
                            count += 1
                    except:
                        pass
            return count
        else:
            return query.count()

    @staticmethod
    def cleanup_old_logs(db: Session, days: int = 90) -> int:
        """
        Delete audit logs older than specified days

        Args:
            db: Database session
            days: Delete logs older than this many days

        Returns:
            Number of logs deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        deleted = db.query(models.AuditLog).filter(
            models.AuditLog.timestamp < cutoff_date
        ).delete()

        db.commit()

        logger.info(f"Deleted {deleted} audit logs older than {days} days")

        return deleted


# Singleton instance
audit_logger = AuditLogger()
