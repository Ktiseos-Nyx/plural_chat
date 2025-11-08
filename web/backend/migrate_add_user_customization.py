"""
Database migration: Add theme_color and avatar_path to users table
Run this script to update your existing database without losing data
"""
import sqlite3
import os
from pathlib import Path

# Database file location (adjust if needed)
DB_FILE = "plural_chat.db"

def migrate():
    """Add new columns to users table"""

    if not os.path.exists(DB_FILE):
        print(f"❌ Database file '{DB_FILE}' not found!")
        print("If your database is elsewhere, edit this script and set DB_FILE path.")
        return False

    print(f"📁 Found database: {DB_FILE}")
    print("🔄 Starting migration...")

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        changes_made = False

        # Add theme_color column if it doesn't exist
        if 'theme_color' not in columns:
            print("   Adding theme_color column...")
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN theme_color VARCHAR DEFAULT '#6c757d'
            """)
            changes_made = True
            print("   ✅ theme_color column added")
        else:
            print("   ℹ️  theme_color column already exists")

        # Add avatar_path column if it doesn't exist
        if 'avatar_path' not in columns:
            print("   Adding avatar_path column...")
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN avatar_path VARCHAR
            """)
            changes_made = True
            print("   ✅ avatar_path column added")
        else:
            print("   ℹ️  avatar_path column already exists")

        if changes_made:
            conn.commit()
            print("\n✅ Migration completed successfully!")
            print("   New columns added: theme_color, avatar_path")
        else:
            print("\n✅ Database already up to date!")

        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add User Customization Fields")
    print("=" * 60)
    print()

    success = migrate()

    print()
    if success:
        print("You can now restart the server and use the new features!")
    else:
        print("Migration failed. Please check the errors above.")
    print("=" * 60)
