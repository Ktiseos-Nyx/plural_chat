"""
Channels API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from ..database import get_db, Channel, Message, User
from ..schemas import Channel as ChannelSchema, ChannelCreate, ChannelUpdate
from ..auth_enhanced import get_current_user
from ..websocket import broadcast_to_user

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("/", response_model=List[ChannelSchema])
async def list_channels(
    include_archived: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all channels (shared across all users).
    Returns channels ordered by position.
    """
    query = db.query(Channel)

    if not include_archived:
        query = query.filter(Channel.is_archived == False)

    channels = query.order_by(Channel.position, Channel.created_at).all()

    # Add message count to each channel
    result = []
    for channel in channels:
        channel_dict = {
            "id": channel.id,
            "user_id": channel.user_id,
            "name": channel.name,
            "description": channel.description,
            "color": channel.color,
            "emoji": channel.emoji,
            "is_default": channel.is_default,
            "is_archived": channel.is_archived,
            "position": channel.position,
            "created_at": channel.created_at,
            "updated_at": channel.updated_at,
            "message_count": db.query(func.count(Message.id)).filter(
                Message.channel_id == channel.id
            ).scalar()
        }
        result.append(channel_dict)

    return result


@router.get("/{channel_id}", response_model=ChannelSchema)
async def get_channel(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific channel by ID."""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )

    # Add message count
    channel_dict = {
        "id": channel.id,
        "user_id": channel.user_id,
        "name": channel.name,
        "description": channel.description,
        "color": channel.color,
        "emoji": channel.emoji,
        "is_default": channel.is_default,
        "is_archived": channel.is_archived,
        "position": channel.position,
        "created_at": channel.created_at,
        "updated_at": channel.updated_at,
        "message_count": db.query(func.count(Message.id)).filter(
            Message.channel_id == channel.id
        ).scalar()
    }

    return channel_dict


@router.post("/", response_model=ChannelSchema, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: ChannelCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new channel.
    Channel names must be globally unique.
    """
    # Check if channel name already exists globally
    existing = db.query(Channel).filter(
        Channel.name == channel_data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Channel '{channel_data.name}' already exists"
        )

    # Get the highest position to place new channel at the end
    max_position = db.query(func.max(Channel.position)).scalar() or -1

    # Create channel
    new_channel = Channel(
        user_id=current_user.id,
        name=channel_data.name,
        description=channel_data.description,
        color=channel_data.color,
        emoji=channel_data.emoji,
        is_default=False,
        is_archived=False,
        position=max_position + 1
    )

    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)

    # Prepare response
    response = {
        "id": new_channel.id,
        "user_id": new_channel.user_id,
        "name": new_channel.name,
        "description": new_channel.description,
        "color": new_channel.color,
        "emoji": new_channel.emoji,
        "is_default": new_channel.is_default,
        "is_archived": new_channel.is_archived,
        "position": new_channel.position,
        "created_at": new_channel.created_at,
        "updated_at": new_channel.updated_at,
        "message_count": 0
    }

    # Broadcast channel creation via WebSocket
    background_tasks.add_task(
        broadcast_to_user,
        str(current_user.id),
        "channel_created",
        response
    )

    return response


@router.patch("/{channel_id}", response_model=ChannelSchema)
async def update_channel(
    channel_id: int,
    channel_data: ChannelUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a channel's properties."""
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.user_id == current_user.id
    ).first()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )

    # Check if new name conflicts with existing channel
    if channel_data.name and channel_data.name != channel.name:
        existing = db.query(Channel).filter(
            Channel.user_id == current_user.id,
            Channel.name == channel_data.name
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Channel '{channel_data.name}' already exists"
            )

    # Update fields
    update_data = channel_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(channel, field, value)

    channel.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(channel)

    # Prepare response
    response = {
        "id": channel.id,
        "user_id": channel.user_id,
        "name": channel.name,
        "description": channel.description,
        "color": channel.color,
        "emoji": channel.emoji,
        "is_default": channel.is_default,
        "is_archived": channel.is_archived,
        "position": channel.position,
        "created_at": channel.created_at,
        "updated_at": channel.updated_at,
        "message_count": db.query(func.count(Message.id)).filter(
            Message.channel_id == channel.id
        ).scalar()
    }

    # Broadcast channel update via WebSocket
    background_tasks.add_task(
        broadcast_to_user,
        str(current_user.id),
        "channel_updated",
        response
    )

    return response


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    channel_id: int,
    delete_messages: bool = False,
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a channel.
    Cannot delete the default channel.

    - delete_messages=true: Delete all messages in the channel
    - delete_messages=false (default): Set message channel_id to NULL
    """
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.user_id == current_user.id
    ).first()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )

    if channel.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the default channel"
        )

    # Handle messages
    if delete_messages:
        # Delete all messages in the channel
        db.query(Message).filter(Message.channel_id == channel_id).delete()
    else:
        # Set channel_id to NULL for all messages
        db.query(Message).filter(Message.channel_id == channel_id).update(
            {"channel_id": None}
        )

    # Delete the channel
    db.delete(channel)
    db.commit()

    # Broadcast channel deletion via WebSocket
    if background_tasks:
        background_tasks.add_task(
            broadcast_to_user,
            str(current_user.id),
            "channel_deleted",
            {"id": channel_id}
        )

    return None


@router.post("/{channel_id}/archive", response_model=ChannelSchema)
async def archive_channel(
    channel_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive a channel (hide from main list but keep messages)."""
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.user_id == current_user.id
    ).first()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )

    channel.is_archived = True
    channel.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(channel)

    response = {
        "id": channel.id,
        "user_id": channel.user_id,
        "name": channel.name,
        "description": channel.description,
        "color": channel.color,
        "emoji": channel.emoji,
        "is_default": channel.is_default,
        "is_archived": channel.is_archived,
        "position": channel.position,
        "created_at": channel.created_at,
        "updated_at": channel.updated_at,
        "message_count": db.query(func.count(Message.id)).filter(
            Message.channel_id == channel.id
        ).scalar()
    }

    # Broadcast channel archive via WebSocket
    background_tasks.add_task(
        broadcast_to_user,
        str(current_user.id),
        "channel_updated",
        response
    )

    return response


@router.post("/{channel_id}/unarchive", response_model=ChannelSchema)
async def unarchive_channel(
    channel_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unarchive a channel (make visible again)."""
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.user_id == current_user.id
    ).first()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )

    channel.is_archived = False
    channel.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(channel)

    response = {
        "id": channel.id,
        "user_id": channel.user_id,
        "name": channel.name,
        "description": channel.description,
        "color": channel.color,
        "emoji": channel.emoji,
        "is_default": channel.is_default,
        "is_archived": channel.is_archived,
        "position": channel.position,
        "created_at": channel.created_at,
        "updated_at": channel.updated_at,
        "message_count": db.query(func.count(Message.id)).filter(
            Message.channel_id == channel.id
        ).scalar()
    }

    # Broadcast channel unarchive via WebSocket
    background_tasks.add_task(
        broadcast_to_user,
        str(current_user.id),
        "channel_updated",
        response
    )

    return response


@router.post("/reorder", response_model=List[ChannelSchema])
async def reorder_channels(
    channel_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reorder channels by providing a list of channel IDs in the desired order.
    Only updates channels that belong to the current user.
    """
    # Verify all channels belong to the user
    channels = db.query(Channel).filter(
        Channel.id.in_(channel_ids),
        Channel.user_id == current_user.id
    ).all()

    if len(channels) != len(channel_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some channels not found or don't belong to you"
        )

    # Update positions
    channel_map = {c.id: c for c in channels}
    for position, channel_id in enumerate(channel_ids):
        channel_map[channel_id].position = position
        channel_map[channel_id].updated_at = datetime.utcnow()

    db.commit()

    # Return updated channels
    result = []
    for channel in sorted(channels, key=lambda c: c.position):
        result.append({
            "id": channel.id,
            "user_id": channel.user_id,
            "name": channel.name,
            "description": channel.description,
            "color": channel.color,
            "emoji": channel.emoji,
            "is_default": channel.is_default,
            "is_archived": channel.is_archived,
            "position": channel.position,
            "created_at": channel.created_at,
            "updated_at": channel.updated_at,
            "message_count": db.query(func.count(Message.id)).filter(
                Message.channel_id == channel.id
            ).scalar()
        })

    return result
