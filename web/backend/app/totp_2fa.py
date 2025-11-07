"""
Two-Factor Authentication (2FA) using TOTP
Authenticator app-based 2FA (Google Authenticator, Authy, etc.)
"""
import pyotp
import qrcode
import io
import base64
import secrets
from typing import Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from . import models

logger = logging.getLogger(__name__)


class TOTP2FA:
    """TOTP-based Two-Factor Authentication Manager"""

    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret (base32)"""
        return pyotp.random_base32()

    @staticmethod
    def generate_backup_codes(count: int = 8) -> list:
        """
        Generate backup codes for account recovery
        Returns list of 8-digit codes
        """
        codes = []
        for _ in range(count):
            # Generate 8-digit code
            code = ''.join([str(secrets.randbelow(10)) for _ in range(8)])
            codes.append(code)
        return codes

    @staticmethod
    def get_provisioning_uri(user: models.User, secret: str, issuer: str = "Plural Chat") -> str:
        """
        Get provisioning URI for QR code
        Format: otpauth://totp/Plural Chat:username?secret=SECRET&issuer=Plural%20Chat
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user.username,
            issuer_name=issuer
        )

    @staticmethod
    def generate_qr_code(provisioning_uri: str) -> str:
        """
        Generate QR code image as base64 data URI
        Returns: data:image/png;base64,... URI
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_base64}"

    @staticmethod
    def verify_code(secret: str, code: str, window: int = 1) -> bool:
        """
        Verify TOTP code

        Args:
            secret: TOTP secret
            code: 6-digit code from authenticator app
            window: Time window for validation (1 = ±30 seconds)

        Returns:
            True if code is valid
        """
        if not code or not secret:
            return False

        try:
            totp = pyotp.TOTP(secret)
            # Remove spaces/dashes from code
            code = code.replace(' ', '').replace('-', '')
            return totp.verify(code, valid_window=window)
        except Exception as e:
            logger.error(f"TOTP verification error: {e}")
            return False

    @staticmethod
    def verify_backup_code(user: models.User, code: str, db: Session) -> bool:
        """
        Verify and consume a backup code

        Args:
            user: User model
            code: 8-digit backup code
            db: Database session

        Returns:
            True if backup code is valid and unused
        """
        if not code or not user.backup_codes_encrypted:
            return False

        try:
            # Get backup codes
            backup_codes = user.get_backup_codes()

            # Remove spaces/dashes
            code = code.replace(' ', '').replace('-', '')

            # Check if code exists
            if code in backup_codes:
                # Remove used code
                backup_codes.remove(code)
                user.set_backup_codes(backup_codes)
                db.commit()

                logger.info(f"Backup code used for user {user.id}. {len(backup_codes)} remaining.")
                return True

            return False
        except Exception as e:
            logger.error(f"Backup code verification error: {e}")
            return False

    @staticmethod
    def setup_2fa(user: models.User, db: Session) -> Tuple[str, list, str]:
        """
        Setup 2FA for user

        Args:
            user: User model
            db: Database session

        Returns:
            Tuple of (secret, backup_codes, qr_code_data_uri)
        """
        # Generate secret and backup codes
        secret = TOTP2FA.generate_secret()
        backup_codes = TOTP2FA.generate_backup_codes()

        # Generate QR code
        provisioning_uri = TOTP2FA.get_provisioning_uri(user, secret)
        qr_code = TOTP2FA.generate_qr_code(provisioning_uri)

        # Store encrypted secret and backup codes (but don't enable yet!)
        user.set_totp_secret(secret)
        user.set_backup_codes(backup_codes)
        user.totp_enabled = False  # Not enabled until verified

        db.commit()

        logger.info(f"2FA setup initiated for user {user.id}")

        return secret, backup_codes, qr_code

    @staticmethod
    def enable_2fa(user: models.User, verification_code: str, db: Session) -> bool:
        """
        Enable 2FA after verifying initial code

        Args:
            user: User model
            verification_code: 6-digit code from authenticator
            db: Database session

        Returns:
            True if code is valid and 2FA is enabled
        """
        secret = user.get_totp_secret()
        if not secret:
            logger.warning(f"No TOTP secret found for user {user.id}")
            return False

        # Verify code
        if TOTP2FA.verify_code(secret, verification_code):
            user.totp_enabled = True
            db.commit()
            logger.info(f"2FA enabled for user {user.id}")
            return True

        logger.warning(f"Invalid verification code for user {user.id}")
        return False

    @staticmethod
    def disable_2fa(user: models.User, db: Session):
        """
        Disable 2FA for user

        Args:
            user: User model
            db: Database session
        """
        user.totp_enabled = False
        user.totp_secret_encrypted = None
        user.backup_codes_encrypted = None
        db.commit()

        logger.info(f"2FA disabled for user {user.id}")

    @staticmethod
    def regenerate_backup_codes(user: models.User, db: Session) -> list:
        """
        Generate new backup codes (invalidates old ones)

        Args:
            user: User model
            db: Database session

        Returns:
            List of new backup codes
        """
        backup_codes = TOTP2FA.generate_backup_codes()
        user.set_backup_codes(backup_codes)
        db.commit()

        logger.info(f"Backup codes regenerated for user {user.id}")

        return backup_codes


# Singleton instance
totp_manager = TOTP2FA()
