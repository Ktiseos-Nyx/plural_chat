"""
Email verification system
"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

# Email configuration
mail_config = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@pluralchat.app"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

# Check if email is configured
EMAIL_ENABLED = bool(os.getenv("MAIL_USERNAME") and os.getenv("MAIL_PASSWORD"))

if EMAIL_ENABLED:
    fastmail = FastMail(mail_config)
    logger.info("✅ Email verification enabled")
else:
    fastmail = None
    logger.warning("⚠️  Email verification disabled (no MAIL_* env vars)")

# Frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# JWT secret for email tokens
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"


def generate_verification_token(email: str, user_id: int) -> str:
    """Generate email verification token"""
    token_data = {
        "email": email,
        "user_id": user_id,
        "type": "email_verification",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)


def verify_email_token(token: str) -> Optional[dict]:
    """Verify email token and return data"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check token type
        if payload.get("type") != "email_verification":
            return None

        return {
            "email": payload.get("email"),
            "user_id": payload.get("user_id")
        }
    except JWTError:
        return None


async def send_verification_email(email: str, username: str, user_id: int):
    """Send verification email"""
    if not EMAIL_ENABLED:
        logger.warning(f"Email not sent to {email} - email not configured")
        return False

    token = generate_verification_token(email, user_id)
    verification_url = f"{FRONTEND_URL}/verify-email?token={token}"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
            .button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #6c757d; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌈 Welcome to Plural Chat!</h1>
            </div>
            <div class="content">
                <h2>Hi {username}! 👋</h2>
                <p>Thank you for creating an account with Plural Chat. We're excited to have you join our community!</p>

                <p>Please verify your email address by clicking the button below:</p>

                <p style="text-align: center;">
                    <a href="{verification_url}" class="button">Verify Email Address</a>
                </p>

                <p>Or copy and paste this link into your browser:</p>
                <p style="background: white; padding: 10px; border-radius: 4px; word-break: break-all; font-size: 12px;">
                    {verification_url}
                </p>

                <p><strong>This link expires in 24 hours.</strong></p>

                <p>If you didn't create this account, you can safely ignore this email.</p>

                <div class="footer">
                    <p>Plural Chat - A safe space for plural systems 💜</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="Verify your Plural Chat account",
        recipients=[email],
        body=html,
        subtype="html"
    )

    try:
        await fastmail.send_message(message)
        logger.info(f"✅ Verification email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send email to {email}: {e}")
        return False


async def send_password_reset_email(email: str, username: str, user_id: int):
    """Send password reset email"""
    if not EMAIL_ENABLED:
        logger.warning(f"Email not sent to {email} - email not configured")
        return False

    # Generate reset token (similar to verification token)
    token_data = {
        "email": email,
        "user_id": user_id,
        "type": "password_reset",
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    reset_url = f"{FRONTEND_URL}/reset-password?token={token}"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #dc3545; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
            .button {{ display: inline-block; background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Password Reset Request</h1>
            </div>
            <div class="content">
                <h2>Hi {username},</h2>
                <p>We received a request to reset your password for your Plural Chat account.</p>

                <p>Click the button below to reset your password:</p>

                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </p>

                <div class="warning">
                    <strong>⚠️  Security Notice:</strong><br>
                    This link expires in 2 hours.<br>
                    If you didn't request this reset, please ignore this email and your password will remain unchanged.
                </div>

                <p>Or copy and paste this link:</p>
                <p style="background: white; padding: 10px; border-radius: 4px; word-break: break-all; font-size: 12px;">
                    {reset_url}
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="Reset your Plural Chat password",
        recipients=[email],
        body=html,
        subtype="html"
    )

    try:
        await fastmail.send_message(message)
        logger.info(f"✅ Password reset email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send email to {email}: {e}")
        return False


def verify_password_reset_token(token: str) -> Optional[dict]:
    """Verify password reset token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check token type
        if payload.get("type") != "password_reset":
            return None

        return {
            "email": payload.get("email"),
            "user_id": payload.get("user_id")
        }
    except JWTError:
        return None
