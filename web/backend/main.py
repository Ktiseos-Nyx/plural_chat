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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
