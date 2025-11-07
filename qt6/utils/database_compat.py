"""Database compatibility layer for PyQt6 version.

This module adds convenience methods to the existing database classes
without modifying the original database_manager.py
"""

from database_manager import AppDatabase as BaseAppDatabase, SystemDatabase as BaseSystemDatabase


class AppDatabase(BaseAppDatabase):
    """Extended AppDatabase with PyQt6 convenience methods."""

    def get_encrypted_setting(self, key: str, default=None):
        """Get an encrypted setting (alias for API token storage)."""
        token = self.get_api_token(key)
        return token if token else default

    def set_encrypted_setting(self, key: str, value: str):
        """Set an encrypted setting (alias for API token storage)."""
        self.store_api_token(key, value)


class SystemDatabase(BaseSystemDatabase):
    """Extended SystemDatabase with PyQt6 convenience methods."""

    def get_member(self, member_id: int):
        """Alias for get_member_by_id for consistency."""
        return self.get_member_by_id(member_id)

    def get_recent_messages(self, limit: int = 100):
        """Alias for get_messages for consistency."""
        messages = self.get_messages(limit)
        # Reverse to get chronological order (oldest to newest)
        return list(reversed(messages))

    def get_member_by_pk_id(self, pk_id: str):
        """Get a member by their PluralKit ID."""
        if not pk_id:
            return None

        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members WHERE pk_id = ?", (pk_id,))
            result = cursor.fetchone()
            return dict(result) if result else None

    def add_member(self, name: str, pronouns: str = None, avatar_path: str = None,
                   color: str = None, description: str = None, pk_id: str = None,
                   proxy_tags: str = None, avatar_url: str = None, **kwargs) -> int:
        """
        Extended add_member that handles avatar_url parameter.
        The avatar_url is stored for later download but not used directly.
        """
        # Call parent add_member
        return super().add_member(
            name=name,
            pronouns=pronouns,
            avatar_path=avatar_path,
            color=color,
            description=description,
            pk_id=pk_id,
            proxy_tags=proxy_tags
        )
