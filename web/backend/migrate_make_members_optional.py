#!/usr/bin/env python3
"""
Database migration: Make members optional for messages

This migration:
1. Adds user_id column to messages table
2. Makes member_id nullable in messages table
3. Migrates existing messages to have user_id based on their member's user_id

Run this before starting the updated application.
"""
import sqlite3
import sys

def migrate():
    """Run the migration"""
    db_path = "plural_chat.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("Starting migration: Make members optional for messages")

        # Check if user_id column exists
        cursor.execute("PRAGMA table_info(messages)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'user_id' not in columns:
            print("Adding user_id column to messages table...")

            # Create a new table with the updated schema
            cursor.execute("""
                CREATE TABLE messages_new (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    member_id INTEGER,
                    channel_id INTEGER,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    edited_at DATETIME,
                    is_deleted BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (member_id) REFERENCES members(id),
                    FOREIGN KEY (channel_id) REFERENCES channels(id)
                )
            """)

            # Migrate data from old table to new table
            # Set user_id based on the member's user_id
            print("Migrating existing messages...")
            cursor.execute("""
                INSERT INTO messages_new (id, user_id, member_id, channel_id, content, timestamp, edited_at, is_deleted)
                SELECT m.id, mem.user_id, m.member_id, m.channel_id, m.content, m.timestamp, m.edited_at, m.is_deleted
                FROM messages m
                JOIN members mem ON m.member_id = mem.id
            """)

            # Drop old table and rename new table
            print("Replacing old messages table...")
            cursor.execute("DROP TABLE messages")
            cursor.execute("ALTER TABLE messages_new RENAME TO messages")

            # Create indexes
            print("Creating indexes...")
            cursor.execute("CREATE INDEX idx_messages_user_id ON messages(user_id)")
            cursor.execute("CREATE INDEX idx_messages_timestamp ON messages(timestamp)")
            cursor.execute("CREATE INDEX idx_messages_channel_id ON messages(channel_id)")

            conn.commit()
            print("✓ Migration completed successfully!")
            print()
            print("Members are now optional!")
            print("Users can chat as themselves without creating members.")
            print("Members can still be created for plural systems, roleplay, etc.")

        else:
            print("✓ Migration already applied - user_id column exists")
            print("  Checking if member_id is nullable...")

            cursor.execute("PRAGMA table_info(messages)")
            for col in cursor.fetchall():
                if col[1] == 'member_id':
                    is_nullable = col[3] == 0  # notnull = 0 means it IS nullable
                    if is_nullable:
                        print("✓ member_id is already nullable")
                    else:
                        print("⚠ member_id is NOT nullable - manual intervention required")
                        print("  Please recreate the database or manually alter the schema")

        conn.close()

    except Exception as e:
        print(f"✗ Migration failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("Plural Chat Database Migration")
    print("Make members optional for messages")
    print("=" * 60)
    print()

    response = input("This will modify your database. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled")
        sys.exit(0)

    migrate()
