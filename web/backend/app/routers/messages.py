"""
Messages management router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional, Tuple
from datetime import datetime
import json
import csv
import io
import re

from ..database import get_db
from .. import models, schemas
from ..auth_enhanced import get_current_user
from ..websocket import broadcast_to_user, broadcast_to_all

router = APIRouter()


def parse_proxy_tags(content: str, members: List[models.Member]) -> Tuple[Optional[int], str]:
    """
    Parse message content for proxy tags and return (member_id, stripped_content).

    PluralKit-style proxy tag format:
    - Stored as JSON array: [{"prefix": "text:", "suffix": ""}, {"prefix": "[", "suffix": "]"}]
    - Message format: "prefix content suffix"

    Returns:
        Tuple of (member_id or None, content with tags stripped)
    """
    for member in members:
        if not member.proxy_tags:
            continue

        try:
            proxy_tags_list = json.loads(member.proxy_tags)
            if not isinstance(proxy_tags_list, list):
                continue

            for tag_set in proxy_tags_list:
                if not isinstance(tag_set, dict):
                    continue

                prefix = tag_set.get("prefix", "")
                suffix = tag_set.get("suffix", "")

                # Skip empty tag sets
                if not prefix and not suffix:
                    continue

                # Check if message matches this proxy tag pattern
                matches = False
                stripped_content = content

                if prefix and suffix:
                    # Both prefix and suffix - e.g., "[text]"
                    if content.startswith(prefix) and content.endswith(suffix):
                        stripped_content = content[len(prefix):-len(suffix)].strip()
                        matches = True
                elif prefix:
                    # Only prefix - e.g., "text: message"
                    if content.startswith(prefix):
                        stripped_content = content[len(prefix):].strip()
                        matches = True
                elif suffix:
                    # Only suffix - e.g., "message -text"
                    if content.endswith(suffix):
                        stripped_content = content[:-len(suffix)].strip()
                        matches = True

                # If we found a match and there's content left, return this member
                if matches and stripped_content:
                    return (member.id, stripped_content)

        except (json.JSONDecodeError, AttributeError):
            # Skip malformed proxy_tags
            continue

    # No proxy tags matched - return original content
    return (None, content)


@router.get("/", response_model=List[schemas.Message])
async def get_messages(
    limit: int = Query(50, ge=1, le=500),
    channel_id: Optional[int] = Query(None, description="Filter by channel ID"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent messages from the chat, optionally filtered by channel

    Returns messages from all users in the channel (multi-user chat).
    """
    # Build query - no user_id filter for multi-user chat
    query = db.query(models.Message)

    # Filter by channel if specified
    if channel_id is not None:
        query = query.filter(models.Message.channel_id == channel_id)

    messages = query.order_by(desc(models.Message.timestamp)).limit(limit).all()

    # Reverse to get chronological order
    return list(reversed(messages))


@router.post("/", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
async def send_message(
    message: schemas.MessageCreate,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a new message

    Messages can be sent either:
    - As the user directly (member_id = None) - default for regular chat
    - As a member (member_id provided) - for plural users or roleplay
    - Via proxy tags (e.g., "text: hello") - automatically detected and parsed

    Proxy tag detection takes priority over manually provided member_id.
    """
    # Get all user's members for proxy tag parsing
    user_members = db.query(models.Member).filter(
        models.Member.user_id == current_user.id,
        models.Member.is_active == True
    ).all()

    # Parse proxy tags from content
    detected_member_id, stripped_content = parse_proxy_tags(message.content, user_members)

    # Use proxy-detected member if found, otherwise use provided member_id
    final_member_id = detected_member_id if detected_member_id is not None else message.member_id
    final_content = stripped_content

    # Verify member belongs to current user (if member_id provided or detected)
    if final_member_id is not None:
        member = db.query(models.Member).filter(
            models.Member.id == final_member_id,
            models.Member.user_id == current_user.id
        ).first()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

    # Verify channel if specified
    if message.channel_id is not None:
        channel = db.query(models.Channel).filter(
            models.Channel.id == message.channel_id,
            models.Channel.user_id == current_user.id
        ).first()

        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )

    # Create message
    new_message = models.Message(
        user_id=current_user.id,
        member_id=final_member_id,
        channel_id=message.channel_id,
        content=final_content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    # Load relationships for response
    db.refresh(new_message, ['user', 'member'])

    # Broadcast message to all user's sessions via WebSocket
    ws_payload = {
        "id": new_message.id,
        "user_id": new_message.user_id,
        "member_id": new_message.member_id,
        "channel_id": new_message.channel_id,
        "content": new_message.content,
        "timestamp": new_message.timestamp.isoformat(),
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "theme_color": current_user.theme_color,
            "avatar_path": current_user.avatar_path,
        }
    }

    # Add member data if message was sent as a member
    if new_message.member:
        ws_payload["member"] = {
            "id": new_message.member.id,
            "user_id": new_message.member.user_id,
            "name": new_message.member.name,
            "pronouns": new_message.member.pronouns,
            "color": new_message.member.color,
            "avatar_path": new_message.member.avatar_path,
            "description": new_message.member.description,
            "pk_id": new_message.member.pk_id,
            "proxy_tags": new_message.member.proxy_tags,
            "created_at": new_message.member.created_at.isoformat()
        }

    # Broadcast to ALL users (multi-user chat)
    background_tasks.add_task(
        broadcast_to_all,
        "message",
        ws_payload
    )

    return new_message


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a message"""
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.user_id == current_user.id
    ).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    db.delete(message)
    db.commit()
    return None


@router.get("/export/{format}")
async def export_messages(
    format: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export chat logs in various formats

    Supported formats:
    - json: Structured JSON with member data
    - csv: CSV format (timestamp, member, message)
    - txt: Plain text format (readable)
    """
    if format not in ["json", "csv", "txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be json, csv, or txt"
        )

    # Build query - export all messages (multi-user chat)
    query = db.query(models.Message).filter(
        models.Message.is_deleted == False
    )

    # Optional: filter by channel if needed
    # if channel_id:
    #     query = query.filter(models.Message.channel_id == channel_id)

    # Apply date filters
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(models.Message.timestamp >= start_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use YYYY-MM-DD"
            )

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(models.Message.timestamp <= end_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use YYYY-MM-DD"
            )

    # Get messages
    messages = query.order_by(models.Message.timestamp).all()

    # Generate filename
    filename_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"plural_chat_export_{filename_date}.{format}"

    # Export based on format
    if format == "json":
        return _export_json(messages, filename)
    elif format == "csv":
        return _export_csv(messages, filename)
    else:  # txt
        return _export_txt(messages, filename)


def _export_json(messages, filename):
    """Export as JSON"""
    data = {
        "export_date": datetime.now().isoformat(),
        "message_count": len(messages),
        "messages": [
            {
                "id": msg.id,
                "timestamp": msg.timestamp.isoformat(),
                "user": {
                    "id": msg.user.id,
                    "username": msg.user.username,
                },
                "member": {
                    "id": msg.member.id,
                    "name": msg.member.name,
                    "pronouns": msg.member.pronouns,
                    "color": msg.member.color
                } if msg.member else None,
                "content": msg.content,
                "edited_at": msg.edited_at.isoformat() if msg.edited_at else None
            }
            for msg in messages
        ]
    }

    json_str = json.dumps(data, indent=2, ensure_ascii=False)

    return StreamingResponse(
        io.BytesIO(json_str.encode('utf-8')),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def _export_csv(messages, filename):
    """Export as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["Timestamp", "User", "Member", "Pronouns", "Message", "Edited"])

    # Data
    for msg in messages:
        writer.writerow([
            msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            msg.user.username,
            msg.member.name if msg.member else "",
            msg.member.pronouns if msg.member else "",
            msg.content,
            "Yes" if msg.edited_at else "No"
        ])

    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def _export_txt(messages, filename):
    """Export as plain text"""
    lines = [
        "=" * 60,
        "Plural Chat Export",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Messages: {len(messages)}",
        "=" * 60,
        "",
    ]

    for msg in messages:
        timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # Show member name if message was sent as a member, otherwise show username
        if msg.member:
            member_info = f"{msg.member.name}"
            if msg.member.pronouns:
                member_info += f" ({msg.member.pronouns})"
        else:
            member_info = f"{msg.user.username}"

        lines.append(f"[{timestamp}] {member_info}:")
        lines.append(f"  {msg.content}")
        if msg.edited_at:
            lines.append(f"  (edited {msg.edited_at.strftime('%Y-%m-%d %H:%M:%S')})")
        lines.append("")

    lines.append("=" * 60)
    lines.append(f"End of export ({len(messages)} messages)")
    lines.append("=" * 60)

    content = "\n".join(lines)

    return StreamingResponse(
        io.BytesIO(content.encode('utf-8')),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
