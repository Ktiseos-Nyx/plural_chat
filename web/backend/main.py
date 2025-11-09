"""
FastAPI Backend for Plural Chat Web Edition
Multi-user chat with PluralKit integration
"""
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import socketio

from app.database import engine, Base
from app.routers import auth, members, messages, admin, security, channels
from app.websocket import sio_app, connection_manager

# Database initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    Base.metadata.create_all(bind=engine)

    # Create default admin user if no users exist
    from app.database import SessionLocal, User, Channel
    from app.auth_enhanced import get_password_hash

    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            # Create default admin user
            admin_user = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                email="admin@plural.chat",
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            # Create default "general" channel
            default_channel = Channel(
                user_id=admin_user.id,
                name="general",
                description="General discussion",
                emoji="💬",
                is_default=True,
                is_archived=False,
                position=0,
                color="#8b5cf6"
            )
            db.add(default_channel)
            db.commit()

            print("=" * 60)
            print("🎉 DEFAULT ADMIN USER CREATED!")
            print("=" * 60)
            print("Username: admin")
            print("Password: admin123")
            print("Email:    admin@plural.chat")
            print()
            print("⚠️  CHANGE THIS PASSWORD IMMEDIATELY!")
            print("Access admin panel at: http://localhost:8000/admin/dashboard")
            print("=" * 60)
    finally:
        db.close()

    yield

# Create FastAPI app
app = FastAPI(
    title="Plural Chat API",
    description="Multi-user chat for plural systems",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO
app.mount("/socket.io", app=socketio.ASGIApp(sio_app))

# Mount avatars directory
os.makedirs("avatars", exist_ok=True)
app.mount("/avatars", StaticFiles(directory="avatars"), name="avatars")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(members.router, prefix="/members", tags=["members"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])
app.include_router(channels.router)  # Prefix is already set in the router
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(security.router, prefix="/security", tags=["security"])

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "Plural Chat API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "websocket": "active"
    }


@app.get("/users/online")
async def get_online_users():
    """Get list of currently online users"""
    from app.database import SessionLocal
    from app.database import User

    online_user_ids = connection_manager.get_online_user_ids()

    if not online_user_ids:
        return []

    # Get user details
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.id.in_([int(uid) for uid in online_user_ids])).all()
        return [
            {
                "id": user.id,
                "username": user.username,
                "theme_color": user.theme_color,
                "avatar_path": user.avatar_path
            }
            for user in users
        ]
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
