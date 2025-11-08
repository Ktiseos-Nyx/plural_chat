"""
Messages management router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime
import json
import csv
import io

from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user
from ..websocket import broadcast_to_user

router = APIRouter()


@router.get("/", response_model=List[schemas.Message])
async def get_messages(
    limit: int = Query(50, ge=1, le=500),
    channel_id: Optional[int] = Query(None, description="Filter by channel ID"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent messages from the chat, optionally filtered by channel"""
    # Get messages from all members of this user's system
    query = db.query(models.Message).join(models.Member).filter(
        models.Member.user_id == current_user.id
    )

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
        member_id=message.member_id,
        channel_id=message.channel_id,
        content=message.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    # Load member relationship for response
    db.refresh(new_message, ['member'])

    # Broadcast message to all user's sessions via WebSocket
    background_tasks.add_task(
        broadcast_to_user,
        str(current_user.id),
        "message",
        {
            "id": new_message.id,
            "member_id": new_message.member_id,
            "channel_id": new_message.channel_id,
            "content": new_message.content,
            "timestamp": new_message.timestamp.isoformat(),
            "member": {
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
        }
    )

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

    # Build query
    query = db.query(models.Message).join(models.Member).filter(
        models.Member.user_id == current_user.id,
        models.Message.is_deleted == False
    )

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
                "member": {
                    "id": msg.member.id,
                    "name": msg.member.name,
                    "pronouns": msg.member.pronouns,
                    "color": msg.member.color
                },
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
    writer.writerow(["Timestamp", "Member", "Pronouns", "Message", "Edited"])

    # Data
    for msg in messages:
        writer.writerow([
            msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            msg.member.name,
            msg.member.pronouns or "",
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
        member_info = f"{msg.member.name}"
        if msg.member.pronouns:
            member_info += f" ({msg.member.pronouns})"

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
