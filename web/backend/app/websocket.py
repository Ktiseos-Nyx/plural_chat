"""
WebSocket handling for real-time chat
"""
import socketio
from typing import Dict, Set
import logging

from . import models

logger = logging.getLogger(__name__)

# Create Socket.IO server
sio_app = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['http://localhost:3000', 'http://localhost:8000'],
    logger=True,
    engineio_logger=True
)


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, Set[str]] = {}  # user_id -> set of session IDs

    def connect(self, sid: str, user_id: str):
        """Register a new connection"""
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(sid)
        logger.info(f"User {user_id} connected (sid: {sid})")

    def disconnect(self, sid: str, user_id: str):
        """Remove a connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(sid)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected (sid: {sid})")

    def get_user_sessions(self, user_id: str) -> Set[str]:
        """Get all session IDs for a user"""
        return self.active_connections.get(user_id, set())


connection_manager = ConnectionManager()


@sio_app.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    try:
        # Get token from auth
        token = auth.get('token') if auth else None
        if not token:
            logger.warning(f"Connection {sid} rejected: No token")
            return False

        # Verify token and get user_id
        from .auth_enhanced import verify_token
        try:
            token_data = verify_token(token)
            user_id = str(token_data.user_id)
            connection_manager.connect(sid, user_id)

            # Store user_id in session
            async with sio_app.session(sid) as session:
                session['user_id'] = user_id

            await sio_app.emit('connected', {'status': 'connected'}, room=sid)
            logger.info(f"Client {sid} connected as user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Auth error for {sid}: {e}")
            return False

    except Exception as e:
        logger.error(f"Connection error: {e}")
        return False


@sio_app.event
async def disconnect(sid):
    """Handle client disconnection"""
    try:
        async with sio_app.session(sid) as session:
            user_id = session.get('user_id')
            if user_id:
                connection_manager.disconnect(sid, user_id)
        logger.info(f"Client {sid} disconnected")
    except Exception as e:
        logger.error(f"Disconnect error: {e}")


@sio_app.event
async def send_message(sid, data):
    """Handle incoming message from client"""
    try:
        async with sio_app.session(sid) as session:
            user_id = session.get('user_id')
            if not user_id:
                return {'success': False, 'error': 'Not authenticated'}

        content = data.get('content')
        member_id = data.get('member_id')

        if not content or not member_id:
            return {'success': False, 'error': 'Missing content or member_id'}

        # Check if it's a command (starts with /)
        if content.startswith('/'):
            from .commands import registry
            from .database import SessionLocal

            db = SessionLocal()
            try:
                result = await registry.execute(int(user_id), content, db)

                # Send command result back to user
                if result:
                    command_response = {
                        'id': 0,
                        'member_id': member_id,
                        'content': result,
                        'timestamp': None,
                        'is_system': True,  # Mark as system message
                        'member': {'name': 'System', 'color': '#888888'}
                    }

                    # Send to all user's sessions
                    sessions = connection_manager.get_user_sessions(user_id)
                    for session_id in sessions:
                        await sio_app.emit('message', command_response, room=session_id)

                return {'success': True, 'is_command': True}
            finally:
                db.close()

        # Regular message handling - Save to database
        from .database import SessionLocal
        from datetime import datetime

        db = SessionLocal()
        try:
            # Get the member to include in response
            member = db.query(models.Member).filter(
                models.Member.id == member_id,
                models.Member.user_id == int(user_id)
            ).first()

            if not member:
                return {'success': False, 'error': 'Member not found or unauthorized'}

            # Get channel_id from data if provided
            channel_id = data.get('channel_id')

            # Create and save message
            new_message = models.Message(
                member_id=member_id,
                channel_id=channel_id,
                content=content,
                timestamp=datetime.utcnow()
            )
            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            # Prepare message data for broadcast
            message_data = {
                'id': new_message.id,
                'member_id': member_id,
                'channel_id': channel_id,
                'content': content,
                'timestamp': new_message.timestamp.isoformat(),
                'member': {
                    'id': member.id,
                    'name': member.name,
                    'color': member.color,
                    'avatar_path': member.avatar_path
                }
            }
        finally:
            db.close()

        # Broadcast to all connected sessions of this user
        sessions = connection_manager.get_user_sessions(user_id)
        for session_id in sessions:
            await sio_app.emit('message', message_data, room=session_id)

        # Check if message mentions an AI character
        from .ai_characters import ai_manager
        import re

        # Reopen database for AI character check
        db2 = SessionLocal()
        try:
            # Find AI characters mentioned in message (@Name or just Name at start)
            # Get all AI characters for this user
            ai_characters = db2.query(models.Member).filter(
                models.Member.user_id == int(user_id),
                models.Member.is_ai == True,
                models.Member.ai_enabled == True
            ).all()

            mentioned_ai = None
            for ai_char in ai_characters:
                # Check for @Name or Name: at start
                if (f"@{ai_char.name}" in content or
                    content.lower().startswith(ai_char.name.lower() + ":") or
                    content.lower().startswith(ai_char.name.lower() + " ")):
                    mentioned_ai = ai_char
                    break

            if mentioned_ai:
                # Get recent conversation history
                recent_messages = db2.query(models.Message).join(models.Member).filter(
                    models.Member.user_id == int(user_id)
                ).order_by(models.Message.timestamp.desc()).limit(10).all()

                # Get AI response
                ai_response = await ai_manager.get_response(
                    member=mentioned_ai,
                    message=content,
                    conversation_history=list(reversed(recent_messages)),
                    db=db2
                )

                if ai_response:
                    # Send AI response as that character
                    ai_message = {
                        'id': 0,
                        'member_id': mentioned_ai.id,
                        'content': ai_response,
                        'timestamp': None,
                        'member': {
                            'id': mentioned_ai.id,
                            'name': mentioned_ai.name,
                            'color': mentioned_ai.color or '#4285F4'
                        }
                    }

                    # Broadcast AI response
                    for session_id in sessions:
                        await sio_app.emit('message', ai_message, room=session_id)
        finally:
            db2.close()

        return {'success': True}

    except Exception as e:
        logger.error(f"Send message error: {e}")
        return {'success': False, 'error': str(e)}


@sio_app.event
async def member_update(sid, data):
    """Handle member update notification"""
    try:
        async with sio_app.session(sid) as session:
            user_id = session.get('user_id')
            if not user_id:
                return

        # Broadcast to all sessions of this user
        sessions = connection_manager.get_user_sessions(user_id)
        for session_id in sessions:
            await sio_app.emit('member_update', data, room=session_id)

    except Exception as e:
        logger.error(f"Member update error: {e}")


# Helper function to broadcast to user's sessions
async def broadcast_to_user(user_id: str, event: str, data: dict):
    """Broadcast an event to all sessions of a user"""
    sessions = connection_manager.get_user_sessions(user_id)
    for session_id in sessions:
        await sio_app.emit(event, data, room=session_id)
    logger.info(f"Broadcasted {event} to {len(sessions)} sessions of user {user_id}")


async def broadcast_to_all(event: str, data: dict):
    """Broadcast an event to all connected users (multi-user chat)"""
    total_sessions = 0
    for user_id, sessions in connection_manager.active_connections.items():
        for session_id in sessions:
            await sio_app.emit(event, data, room=session_id)
            total_sessions += 1
    logger.info(f"Broadcasted {event} to {total_sessions} sessions across all users")

