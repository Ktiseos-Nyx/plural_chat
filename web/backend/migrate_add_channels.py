"""
Database migration: Add Channels feature

This script:
1. Creates the channels table (if not exists)
2. Adds channel_id column to messages table (if not exists)
3. Creates a default #general channel for each existing user
4. Assigns all existing messages to their user's default channel
"""
import sys
import os
from sqlalchemy import inspect, text

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, User, Channel, Message, SessionLocal
from datetime import datetime


def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def check_column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def run_migration():
    """Run the channels migration"""
    print("=" * 60)
    print("CHANNELS FEATURE MIGRATION")
    print("=" * 60)
    print()

    # Create all tables (will create channels table if it doesn't exist)
    print("Step 1: Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created/verified")
    print()

    # Create a database session
    db = SessionLocal()

    try:
        # Check if channel_id column exists in messages table
        print("Step 2: Checking messages table structure...")
        if check_table_exists('messages'):
            if not check_column_exists('messages', 'channel_id'):
                print("⚠  channel_id column not found in messages table")
                print("   Adding channel_id column...")
                # SQLite doesn't support ALTER TABLE ADD COLUMN with constraints easily
                # But SQLAlchemy should have created it with create_all above
                db.execute(text("ALTER TABLE messages ADD COLUMN channel_id INTEGER"))
                db.commit()
                print("✓ channel_id column added")
            else:
                print("✓ channel_id column already exists")
        print()

        # Step 3: Create default channels for existing users
        print("Step 3: Creating default channels for users...")
        users = db.query(User).all()

        channels_created = 0
        for user in users:
            # Check if user already has a default channel
            existing_default = db.query(Channel).filter(
                Channel.user_id == user.id,
                Channel.is_default == True
            ).first()

            if not existing_default:
                # Create default #general channel
                default_channel = Channel(
                    user_id=user.id,
                    name="general",
                    description="General chat",
                    color="#6366f1",
                    emoji="💬",
                    is_default=True,
                    is_archived=False,
                    position=0,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(default_channel)
                channels_created += 1
                print(f"  ✓ Created default channel for user {user.id} ({user.username if hasattr(user, 'username') else user.id})")

        db.commit()
        print(f"✓ Created {channels_created} default channels")
        print()

        # Step 4: Assign existing messages to default channels
        print("Step 4: Assigning existing messages to default channels...")
        messages_updated = 0

        # Get all messages without a channel_id
        orphan_messages = db.query(Message).filter(
            Message.channel_id == None
        ).all()

        for message in orphan_messages:
            # Get the message's member to find the user
            from app.database import Member
            member = db.query(Member).filter(Member.id == message.member_id).first()

            if member:
                # Find the user's default channel
                default_channel = db.query(Channel).filter(
                    Channel.user_id == member.user_id,
                    Channel.is_default == True
                ).first()

                if default_channel:
                    message.channel_id = default_channel.id
                    messages_updated += 1

        db.commit()
        print(f"✓ Assigned {messages_updated} messages to default channels")
        print()

        # Summary
        print("=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)
        print(f"Users found: {len(users)}")
        print(f"Default channels created: {channels_created}")
        print(f"Messages updated: {messages_updated}")
        print()
        print("You can now:")
        print("  1. Create additional channels via the API")
        print("  2. Filter messages by channel")
        print("  3. Move messages between channels")
        print()

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print()
    response = input("This will modify your database. Continue? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        run_migration()
    else:
        print("Migration cancelled.")
