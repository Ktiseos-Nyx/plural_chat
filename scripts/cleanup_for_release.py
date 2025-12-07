#!/usr/bin/env python3
"""
Cleanup script to sanitize Plural Chat for GitHub release
Removes personal data while keeping the app structure intact
"""

import os
import sqlite3
import shutil
import glob
import platformdirs
from pathlib import Path
from datetime import datetime

def cleanup_databases():
    """Delete databases from the user data directory and project root."""
    print("🗄️ Deleting databases for fresh start...")
    
    data_dir = Path(platformdirs.user_data_dir("PluralChat", "DuskfallCrew"))
    db_files = [data_dir / "app.db", data_dir / "system.db"]
    
    for db_file in db_files:
        if db_file.exists():
            db_file.unlink()
            print(f"  ✅ {db_file.name} deleted from user data directory")
        else:
            print(f"  ℹ️ No {db_file.name} found in user data directory")

    # Also clean up old root directory databases
    if os.path.exists('app.db'):
        os.remove('app.db')
        print("  ✅ Old root app.db deleted")
    if os.path.exists('system.db'):
        os.remove('system.db')
        print("  ✅ Old root system.db deleted")

def cleanup_avatars():
    """Remove personal avatar images from the user data directory."""
    print("🖼️ Cleaning avatars...")

    data_dir = Path(platformdirs.user_data_dir("PluralChat", "DuskfallCrew"))
    avatars_dir = data_dir / "avatars"
    
    if avatars_dir.exists():
        removed_count = 0
        for avatar_file in avatars_dir.glob('*'):
            if avatar_file.is_file():
                avatar_file.unlink()
                removed_count += 1
        if removed_count > 0:
            print(f"  ✅ Removed {removed_count} personal avatar files from user data directory")
        else:
            print("  ℹ️ No personal avatar files to remove from user data directory")
    else:
        print("  ℹ️ No avatars directory found in user data directory")
    
    # Also cleanup old root dir
    if os.path.exists('avatars'):
        print("  🗑️ Removing obsolete root 'avatars' directory...")
        shutil.rmtree('avatars')

def cleanup_logs():
    """Remove log files from the user log directory."""
    print("📝 Cleaning logs...")
    
    log_dir = Path(platformdirs.user_log_dir("PluralChat", "DuskfallCrew"))
    if log_dir.exists():
        log_files = list(log_dir.glob('*.log'))
        for log_file in log_files:
            log_file.unlink()
        
        if log_files:
            print(f"  ✅ Removed {len(log_files)} log files from user log directory")
        else:
            print("  ℹ️ No log files found in user log directory")
    else:
        print("  ℹ️ No user log directory found")
    
    # Also clean up old root dir logs
    old_log_files = glob.glob('*.log') + glob.glob('logs/*.log')
    if old_log_files:
        for log_file in old_log_files:
            if os.path.exists(log_file):
                os.remove(log_file)
        print(f"  ✅ Removed {len(old_log_files)} old log files from project root")
    if os.path.exists('logs'):
        shutil.rmtree('logs')
        print("  🗑️ Removed obsolete root 'logs' directory")


def cleanup_exports():
    """Remove any export files from the project root."""
    print("📤 Cleaning export files...")
    
    patterns = ['*.json', '*.txt']
    
    removed_files = []
    for pattern in patterns:
        files = glob.glob(pattern)
        for file_path in files:
            # Check against a list of files to keep
            if os.path.basename(file_path) not in ['pyproject.toml', 'requirements.txt']:
                os.remove(file_path)
                removed_files.append(file_path)
    
    if removed_files:
        print(f"  ✅ Removed {len(removed_files)} export/history files from project root")
    else:
        print("  ℹ️ No export or history files found in project root")

def cleanup_temp_files():
    """Remove temporary and cache files from the project."""
    print("🧹 Cleaning temporary files...")
    
    patterns = [
        '**/__pycache__',
        '**/*.pyc',
        '**/*.pyo', 
        '**/*.tmp',
        '**/.DS_Store',
    ]
    
    removed_count = 0
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=True):
            if os.path.isfile(path):
                os.remove(path)
                removed_count += 1
            elif os.path.isdir(path):
                shutil.rmtree(path)
                removed_count += 1
    
    if removed_count > 0:
        print(f"  ✅ Removed {removed_count} temporary/cache files and folders")
    else:
        print("  ℹ️ No temporary files found")

def create_sample_data():
    """Create sample members A and B for demo"""
    print("👤 Creating sample demo members...")
    
    import subprocess
    import time
    
    try:
        # Set PYTHONPATH to include src, so the module can be found
        env = os.environ.copy()
        env['PYTHONPATH'] = 'src' + os.pathsep + env.get('PYTHONPATH', '')

        # Start the app briefly to initialize databases in the correct user directory
        process = subprocess.Popen(['python', '-m', 'plural_chat.main'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 env=env)
        time.sleep(3)
        process.terminate()
        process.wait()
        
        data_dir = Path(platformdirs.user_data_dir("PluralChat", "DuskfallCrew"))
        db_path = data_dir / "system.db"
        
        if db_path.exists():
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO members (name, pronouns, color, avatar_path, description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                "Member A", "they/them", "#7745d1", "default_avatar.png",
                "This is a sample member for demonstration. You can edit or delete this member and add your own!"
            ))
            member_a_id = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO members (name, pronouns, color, avatar_path, description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                "Member B", "she/her", "#ba1ca1", "default_avatar.png",
                "Another sample member for demonstration. Feel free to customize or replace with your own members!"
            ))
            member_b_id = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO messages (member_id, message, timestamp)
                VALUES (?, ?, ?)
            """, (member_a_id, "Hi! Welcome to Plural Chat! This is a sample message from Member A.", datetime.now().strftime("%H:%M")))
            
            cursor.execute("""
                INSERT INTO messages (member_id, message, timestamp) 
                VALUES (?, ?, ?)
            """, (member_b_id, "Hello there! I'm Member B. You can delete us and add your own system members through Settings > Members.", datetime.now().strftime("%H:%M")))
            
            conn.commit()
            conn.close()
            print("  ✅ Added sample members A & B with welcome messages")
        else:
            print(f"  ⚠️ Could not create sample data - database not found at {db_path}")
            
    except Exception as e:
        print(f"  ⚠️ Could not create sample data: {e}")

def main():
    """Main cleanup function"""
    print("🧼 Starting Plural Chat cleanup for GitHub release...")
    print("=" * 50)
    
    # Make sure we're in the right directory
    if not os.path.exists('src/plural_chat/main.py'):
        print("❌ Error: Please run this script from the Plural Chat project root directory")
        return
    
    # Perform cleanup steps
    cleanup_databases()
    cleanup_avatars() 
    cleanup_logs()
    cleanup_exports()
    cleanup_temp_files()
    create_sample_data()
    
    print("=" * 50)
    print("✅ Cleanup complete! Your Plural Chat is now ready for GitHub.")
    print("📋 What was cleaned:")
    print("   • User-specific databases (app.db, system.db)")
    print("   • User-specific downloaded avatars")
    print("   • User-specific log files")
    print("   • Old files from the project root (logs, dbs, exports)")
    print("   • Temporary and cache files (__pycache__)")
    print("🎉 Fresh sample data created in the user's data directory.")
    print("\n💡 Tip: Test the app once more before committing to GitHub!")

if __name__ == "__main__":
    main()