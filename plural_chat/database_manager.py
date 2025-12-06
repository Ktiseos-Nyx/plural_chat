import sqlite3
import json
import base64
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from cryptography.fernet import Fernet
import logging
from logging.handlers import RotatingFileHandler


class AppDatabase:
    """Manages app-level settings and preferences"""
    
    def __init__(self, db_path="app.db"):
        self.db_path = db_path
        self._encryption_key = None
        self.init_database()
        self.logger = logging.getLogger('plural_chat.app_database')
    
    def init_database(self):
        """Initialize the app database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # App settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # API tokens table (obfuscated)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_tokens (
                    service TEXT PRIMARY KEY,
                    token_data TEXT,
                    last_sync DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Window preferences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    setting_name TEXT PRIMARY KEY,
                    setting_value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def _get_encryption_key(self):
        """Get or create encryption key for secure token storage"""
        if self._encryption_key:
            return self._encryption_key
        
        # Try to get existing key from environment or generate new one
        key_file = ".app_key"
        
        if os.path.exists(key_file):
            try:
                with open(key_file, 'rb') as f:
                    self._encryption_key = f.read()
            except:
                # Generate new key if file is corrupted
                self._encryption_key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(self._encryption_key)
        else:
            # Generate new key
            self._encryption_key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self._encryption_key)
            # Make file read-only for owner
            os.chmod(key_file, 0o600)
        
        return self._encryption_key
    
    def _encrypt_token(self, token: str) -> str:
        """Encrypt token using AES encryption"""
        try:
            fernet = Fernet(self._get_encryption_key())
            encrypted = fernet.encrypt(token.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            self.logger.warning(f"Encryption failed: {e}")
            # Fallback to base64 (temporary)
            return base64.b64encode(token.encode()).decode()
    
    def _decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt token using AES encryption"""
        try:
            fernet = Fernet(self._get_encryption_key())
            encrypted_bytes = base64.b64decode(encrypted_token.encode())
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            self.logger.warning(f"Decryption failed, trying base64 fallback: {e}")
            # Fallback for old base64-only tokens
            try:
                return base64.b64decode(encrypted_token).decode()
            except:
                self.logger.warning(f"All decryption methods failed")
                return ""
    
    def get_setting(self, key: str, default=None):
        """Get an app setting"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
            result = cursor.fetchone()
            return result[0] if result else default
    
    def set_setting(self, key: str, value: str):
        """Set an app setting"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO app_settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            conn.commit()
    
    def get_all_settings(self) -> Dict[str, str]:
        """Get all app settings as a dictionary"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM app_settings")
            return dict(cursor.fetchall())
    
    def store_api_token(self, service: str, token: str):
        """Store an API token (properly encrypted)"""
        # Basic validation - just check it's not empty
        if not token or not token.strip():
            raise ValueError("Token cannot be empty")
        
        encrypted_token = self._encrypt_token(token)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO api_tokens (service, token_data, created_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (service, encrypted_token))
            conn.commit()
            self.logger.info(f"Securely stored {service} token")
    
    def get_api_token(self, service: str) -> Optional[str]:
        """Get an API token (properly decrypted)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT token_data FROM api_tokens WHERE service = ?", (service,))
            result = cursor.fetchone()
            if result:
                return self._decrypt_token(result[0])
            return None
    
    def update_sync_time(self, service: str):
        """Update the last sync time for a service"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE api_tokens SET last_sync = CURRENT_TIMESTAMP 
                WHERE service = ?
            """, (service,))
            conn.commit()


class SystemDatabase:
    """Manages plural system data (members, messages, etc.)"""
    
    def __init__(self, db_path="system.db"):
        self.db_path = db_path
        self.init_database()
        self.logger = logging.getLogger('plural_chat.system_database')
    
    def init_database(self):
        """Initialize the system database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # System info table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_info (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Members table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    pronouns TEXT,
                    avatar_path TEXT,
                    color TEXT,
                    description TEXT,
                    pk_id TEXT UNIQUE,
                    proxy_tags TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Chat messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (member_id) REFERENCES members(id)
                )
            """)
            
            # Diary entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS diary_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (member_id) REFERENCES members(id)
                )
            """)
            
            # Database migration: Add proxy_tags column if it doesn't exist
            cursor.execute("PRAGMA table_info(members)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'proxy_tags' not in columns:
                cursor.execute("ALTER TABLE members ADD COLUMN proxy_tags TEXT")
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_member_name ON members(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_member ON messages(member_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_timestamp ON messages(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_diary_member ON diary_entries(member_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_diary_created ON diary_entries(created_at)")
            
            conn.commit()
    
    def add_member(self, name: str, pronouns: str = None, avatar_path: str = None, 
                   color: str = None, description: str = None, pk_id: str = None, 
                   proxy_tags: str = None) -> int:
        """Add a new member and return their ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO members (name, pronouns, avatar_path, color, description, pk_id, proxy_tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, pronouns, avatar_path, color, description, pk_id, proxy_tags))
            conn.commit()
            return cursor.lastrowid
    
    def get_member_by_name(self, name: str) -> Optional[Dict]:
        """Get a member by name"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members WHERE name = ?", (name,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def get_member_by_id(self, member_id: int) -> Optional[Dict]:
        """Get a member by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def get_all_members(self) -> List[Dict]:
        """Get all members"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def update_member(self, member_id: int, **kwargs):
        """Update a member's information"""
        if not kwargs:
            return
        
        set_clause = ", ".join(f"{key} = ?" for key in kwargs.keys())
        values = list(kwargs.values())
        values.append(member_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE members SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, values)
            conn.commit()
    
    def delete_member(self, member_id: int):
        """Delete a member and their messages"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE member_id = ?", (member_id,))
            cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
            conn.commit()
    
    def add_message(self, member_id: int, message: str, timestamp: str = None) -> int:
        """Add a new message and return its ID"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (member_id, message, timestamp)
                VALUES (?, ?, ?)
            """, (member_id, message, timestamp))
            conn.commit()
            return cursor.lastrowid
    
    def get_messages(self, limit: int = 100) -> List[Dict]:
        """Get recent messages with member information"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.id, m.message, m.timestamp, m.created_at,
                       mb.name as member_name, mb.avatar_path, mb.color
                FROM messages m
                JOIN members mb ON m.member_id = mb.id
                ORDER BY m.created_at DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_system_info(self, key: str, default=None):
        """Get system information"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_info WHERE key = ?", (key,))
            result = cursor.fetchone()
            return result[0] if result else default
    
    def set_system_info(self, key: str, value: str):
        """Set system information"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO system_info (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            conn.commit()
    
    def export_to_dict(self) -> Dict:
        """Export all system data to a dictionary (for JSON export)"""
        members = self.get_all_members()
        messages = self.get_messages(limit=10000)  # Get all messages
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM system_info")
            system_info = dict(cursor.fetchall())
        
        return {
            "system_info": system_info,
            "members": members,
            "messages": messages,
            "export_date": datetime.now().isoformat(),
            "version": "2.0"
        }
    
    def import_from_dict(self, data: Dict):
        """Import system data from a dictionary (from JSON import)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute("DELETE FROM messages")
            cursor.execute("DELETE FROM members")
            cursor.execute("DELETE FROM system_info")
            
            # Import system info
            if "system_info" in data:
                for key, value in data["system_info"].items():
                    cursor.execute("""
                        INSERT INTO system_info (key, value) VALUES (?, ?)
                    """, (key, value))
            
            # Import members
            member_id_map = {}  # Map old IDs to new IDs
            if "members" in data:
                for member in data["members"]:
                    # Handle duplicate names by adding suffix
                    base_name = member.get("name", "Unknown")
                    name = base_name
                    counter = 1
                    
                    while True:
                        try:
                            cursor.execute("""
                                INSERT INTO members (name, pronouns, avatar_path, color, description, pk_id, proxy_tags)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                                name,
                                member.get("pronouns"),
                                member.get("avatar_path", member.get("avatar")),  # Handle both field names
                                member.get("color"),
                                member.get("description"),
                                member.get("pk_id"),
                                member.get("proxy_tags")
                            ))
                            new_id = cursor.lastrowid
                            if "id" in member:
                                member_id_map[member["id"]] = new_id
                            break  # Success, exit the loop
                        except sqlite3.IntegrityError as e:
                            if "UNIQUE constraint failed: members.name" in str(e):
                                # Name conflict, try with suffix
                                counter += 1
                                name = f"{base_name} ({counter})"
                            else:
                                # Some other integrity error, re-raise
                                raise
            
            # Import messages
            if "messages" in data:
                for message in data["messages"]:
                    # Handle both old and new message formats
                    if "member_id" in message and message["member_id"] in member_id_map:
                        member_id = member_id_map[message["member_id"]]
                    else:
                        # Find member by name (legacy support)
                        member_name = message.get("member_name") or message.get("member")
                        cursor.execute("SELECT id FROM members WHERE name = ?", (member_name,))
                        result = cursor.fetchone()
                        if not result:
                            continue
                        member_id = result[0]
                    
                    cursor.execute("""
                        INSERT INTO messages (member_id, message, timestamp)
                        VALUES (?, ?, ?)
                    """, (
                        member_id,
                        message.get("message", ""),
                        message.get("timestamp", "")
                    ))
            
            conn.commit()
    
    def add_diary_entry(self, member_id: int, title: str, content: str) -> int:
        """Add a new diary entry and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO diary_entries (member_id, title, content)
                VALUES (?, ?, ?)
            """, (member_id, title, content))
            conn.commit()
            return cursor.lastrowid
    
    def get_diary_entries(self, member_id: int = None, limit: int = None) -> List[Dict]:
        """Get diary entries, optionally filtered by member"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if member_id:
                query = """
                    SELECT d.*, m.name as member_name
                    FROM diary_entries d
                    JOIN members m ON d.member_id = m.id
                    WHERE d.member_id = ?
                    ORDER BY d.created_at DESC
                """
                params = (member_id,)
            else:
                query = """
                    SELECT d.*, m.name as member_name
                    FROM diary_entries d
                    JOIN members m ON d.member_id = m.id
                    ORDER BY d.created_at DESC
                """
                params = ()
            
            if limit:
                query += " LIMIT ?"
                params = params + (limit,)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_diary_entry(self, entry_id: int) -> Optional[Dict]:
        """Get a specific diary entry"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.*, m.name as member_name
                FROM diary_entries d
                JOIN members m ON d.member_id = m.id
                WHERE d.id = ?
            """, (entry_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def update_diary_entry(self, entry_id: int, title: str = None, content: str = None):
        """Update a diary entry"""
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        
        if not updates:
            return
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(entry_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE diary_entries SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            conn.commit()
    
    def delete_diary_entry(self, entry_id: int):
        """Delete a diary entry"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM diary_entries WHERE id = ?", (entry_id,))
            conn.commit()
    
    def search_diary_entries(self, search_term: str, member_id: int = None) -> List[Dict]:
        """Search diary entries by content or title"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if member_id:
                cursor.execute("""
                    SELECT d.*, m.name as member_name
                    FROM diary_entries d
                    JOIN members m ON d.member_id = m.id
                    WHERE d.member_id = ? AND (d.title LIKE ? OR d.content LIKE ?)
                    ORDER BY d.created_at DESC
                """, (member_id, f"%{search_term}%", f"%{search_term}%"))
            else:
                cursor.execute("""
                    SELECT d.*, m.name as member_name
                    FROM diary_entries d
                    JOIN members m ON d.member_id = m.id
                    WHERE d.title LIKE ? OR d.content LIKE ?
                    ORDER BY d.created_at DESC
                """, (f"%{search_term}%", f"%{search_term}%"))
            
            return [dict(row) for row in cursor.fetchall()]