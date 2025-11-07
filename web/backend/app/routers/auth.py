"""
Authentication router with PluralKit integration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import requests
import logging

from ..database import get_db
from .. import models, schemas
from ..auth import create_access_token, get_current_user
from ..pluralkit import PluralKitAPI

router = APIRouter()
logger = logging.getLogger(__name__)

PK_API_URL = "https://api.pluralkit.me/v2"


@router.post("/login", response_model=schemas.LoginResponse)
async def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Login with PluralKit token
    Creates or updates user and syncs system info
    """
    pk_api = PluralKitAPI(request.pk_token)

    # Verify token and get system info
    try:
        system_info = pk_api.get_system_info()
        if not system_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid PluralKit token"
            )
    except Exception as e:
        logger.error(f"PluralKit API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to verify PluralKit token"
        )

    system_id = system_info.get("id")
    system_name = system_info.get("name", "Unknown System")

    # Find or create user
    user = db.query(models.User).filter(models.User.id == system_id).first()
    if not user:
        user = models.User(
            id=system_id,
            pk_token=request.pk_token,  # TODO: Encrypt this
            system_name=system_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user: {system_id} ({system_name})")
    else:
        # Update token and name
        user.pk_token = request.pk_token
        user.system_name = system_name
        db.commit()
        logger.info(f"Updated user: {system_id} ({system_name})")

    # Create access token
    access_token = create_access_token(data={"sub": system_id})

    return {
        "user": user,
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/verify", response_model=schemas.User)
async def verify_token(current_user: models.User = Depends(get_current_user)):
    """Verify the current access token"""
    return current_user


@router.post("/sync-pluralkit")
async def sync_from_pluralkit(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync members from PluralKit
    Downloads avatars and updates member data
    """
    pk_api = PluralKitAPI(current_user.pk_token)

    try:
        # Get members from PK
        pk_members = pk_api.get_members()
        if not pk_members:
            return {"success": False, "message": "No members found"}

        added = 0
        updated = 0
        errors = []

        for pk_member in pk_members:
            try:
                pk_id = pk_member.get("id")
                name = pk_member.get("name", "Unknown")

                # Convert proxy tags to JSON string
                import json
                proxy_tags = json.dumps(pk_member.get("proxy_tags", []))

                # Download avatar
                avatar_path = None
                avatar_url = pk_member.get("avatar_url")
                if avatar_url:
                    avatar_path = pk_api.download_avatar(avatar_url, name)

                # Check if member exists
                existing = db.query(models.Member).filter(
                    models.Member.user_id == current_user.id,
                    models.Member.pk_id == pk_id
                ).first()

                if existing:
                    # Update existing
                    existing.pronouns = pk_member.get("pronouns")
                    existing.color = "#" + pk_member.get("color", "6c757d")
                    existing.description = pk_member.get("description")
                    existing.avatar_path = avatar_path
                    existing.proxy_tags = proxy_tags
                    updated += 1
                else:
                    # Create new
                    new_member = models.Member(
                        user_id=current_user.id,
                        name=name,
                        pronouns=pk_member.get("pronouns"),
                        color="#" + pk_member.get("color", "6c757d"),
                        description=pk_member.get("description"),
                        pk_id=pk_id,
                        avatar_path=avatar_path,
                        proxy_tags=proxy_tags
                    )
                    db.add(new_member)
                    added += 1

            except Exception as e:
                logger.error(f"Error syncing member {pk_member.get('name')}: {e}")
                errors.append(str(e))

        db.commit()

        # Update last_sync timestamp
        from datetime import datetime
        current_user.last_sync = datetime.utcnow()
        db.commit()

        return {
            "success": True,
            "added": added,
            "updated": updated,
            "errors": errors
        }

    except Exception as e:
        logger.error(f"Sync error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )


@router.post("/logout")
async def logout(current_user: models.User = Depends(get_current_user)):
    """Logout (client should remove token)"""
    return {"success": True, "message": "Logged out successfully"}
