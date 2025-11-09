"""
Authentication router with PluralKit integration
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import requests
import logging

from ..database import get_db
from .. import models, schemas
from ..auth_enhanced import create_access_token, get_current_user
from ..pluralkit import PluralKitAPI

router = APIRouter()
logger = logging.getLogger(__name__)

PK_API_URL = "https://api.pluralkit.me/v2"


@router.post("/set-pk-token")
async def set_pluralkit_token(
    request: schemas.LoginRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Store PluralKit token for syncing members

    NOTE: This does NOT log you in - use /security/login for authentication.
    This only saves your PK token so you can sync members from PluralKit.
    """
    pk_api = PluralKitAPI(request.pk_token)

    # Verify token is valid
    try:
        system_info = pk_api.get_system_info()
        if not system_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PluralKit token"
            )
    except Exception as e:
        logger.error(f"PluralKit API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to verify PluralKit token"
        )

    system_id = system_info.get("id")
    system_name = system_info.get("name", "Unknown System")

    # Store encrypted PK token and system info
    current_user.set_pk_token(request.pk_token)
    current_user.pk_system_id = system_id
    current_user.system_name = system_name
    db.commit()

    logger.info(f"User {current_user.username} linked PK system: {system_id} ({system_name})")

    return {
        "success": True,
        "message": "PluralKit token saved successfully",
        "system_id": system_id,
        "system_name": system_name
    }


@router.get("/verify", response_model=schemas.User)
async def verify_token(current_user: models.User = Depends(get_current_user)):
    """Verify the current access token"""
    return current_user


@router.post("/sync-pluralkit")
async def sync_from_pluralkit(
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync members from PluralKit (with real-time progress via WebSocket)
    Downloads avatars and updates member data

    Progress updates are sent via WebSocket events:
    - 'sync_progress': { current: int, total: int, status: str }
    - 'sync_complete': { added: int, updated: int, errors: [] }

    NOTE: You must set your PluralKit token first using /auth/set-pk-token
    """
    pk_token = current_user.get_pk_token()
    if not pk_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No PluralKit token set. Use /auth/set-pk-token first."
        )

    # Start sync in background and return immediately
    background_tasks.add_task(
        _sync_pluralkit_background,
        current_user.id,
        pk_token
    )

    return {
        "success": True,
        "message": "Sync started. Listen for 'sync_progress' and 'sync_complete' WebSocket events."
    }


async def _sync_pluralkit_background(user_id: int, pk_token: str):
    """Background task for PluralKit sync with progress updates"""
    from ..database import SessionLocal
    from ..websocket import broadcast_to_user

    db = SessionLocal()
    pk_api = PluralKitAPI(pk_token)

    try:
        # Get members from PK
        pk_members = pk_api.get_members()
        if not pk_members:
            await broadcast_to_user(
                str(user_id),
                "sync_complete",
                {"success": False, "message": "No members found", "added": 0, "updated": 0, "errors": []}
            )
            return

        total = len(pk_members)
        added = 0
        updated = 0
        errors = []

        # Send initial progress
        await broadcast_to_user(
            str(user_id),
            "sync_progress",
            {"current": 0, "total": total, "status": f"Starting sync of {total} members..."}
        )

        for idx, pk_member in enumerate(pk_members, 1):
            try:
                pk_id = pk_member.get("id")
                name = pk_member.get("name", "Unknown")

                # Send progress update
                await broadcast_to_user(
                    str(user_id),
                    "sync_progress",
                    {"current": idx, "total": total, "status": f"Syncing {name}... ({idx}/{total})"}
                )

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
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            user.last_sync = datetime.utcnow()
            db.commit()

        # Send completion event
        await broadcast_to_user(
            str(user_id),
            "sync_complete",
            {
                "success": True,
                "added": added,
                "updated": updated,
                "errors": errors,
                "message": f"Sync complete! Added {added}, updated {updated} members."
            }
        )

    except Exception as e:
        logger.error(f"Sync error: {e}")
        # Send error event
        await broadcast_to_user(
            str(user_id),
            "sync_complete",
            {
                "success": False,
                "added": 0,
                "updated": 0,
                "errors": [str(e)],
                "message": f"Sync failed: {str(e)}"
            }
        )
    finally:
        db.close()


@router.post("/logout")
async def logout(current_user: models.User = Depends(get_current_user)):
    """Logout (client should remove token)"""
    return {"success": True, "message": "Logged out successfully"}
