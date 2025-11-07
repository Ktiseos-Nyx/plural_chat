"""
Messages management router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[schemas.Message])
async def get_messages(
    limit: int = Query(50, ge=1, le=500),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent messages from the chat"""
    # Get messages from all members of this user's system
    messages = db.query(models.Message).join(models.Member).filter(
        models.Member.user_id == current_user.id
    ).order_by(desc(models.Message.timestamp)).limit(limit).all()

    # Reverse to get chronological order
    return list(reversed(messages))


@router.post("/", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
async def send_message(
    message: schemas.MessageCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a new message"""
    # Verify member belongs to current user
    member = db.query(models.Member).filter(
        models.Member.id == message.member_id,
        models.Member.user_id == current_user.id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Create message
    new_message = models.Message(
        member_id=message.member_id,
        content=message.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    # Load member relationship for response
    db.refresh(new_message, ['member'])

    # TODO: Broadcast via WebSocket
    return new_message


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a message"""
    message = db.query(models.Message).join(models.Member).filter(
        models.Message.id == message_id,
        models.Member.user_id == current_user.id
    ).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    db.delete(message)
    db.commit()
    return None
