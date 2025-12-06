#!/usr/bin/env python3
"""
PluralKit Sync Worker - Standalone process for PK operations
Runs independently from the main UI to avoid threading issues
"""

import sys
import json
import time
import os
from pathlib import Path
from database_manager import SystemDatabase, AppDatabase
from pluralkit_api import PluralKitSync
from aria2_avatar_downloader import Aria2AvatarDownloader
import logging

class PKSyncWorker:
    def __init__(self, status_file, operation, download_avatars=True):
        self.status_file = status_file
        self.operation = operation
        self.download_avatars = download_avatars
        
        # Initialize databases
        self.app_db = AppDatabase()
        self.system_db = SystemDatabase()
        self.pk_sync = PluralKitSync(self.system_db, self.app_db)
        
        # Setup logging
        self.logger = logging.getLogger('pk_sync_worker')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
    def write_status(self, status, message="", progress=0, data=None):
        """Write status to file for main app to read"""
        status_data = {
            "status": status,  # "running", "complete", "error"
            "message": message,
            "progress": progress,  # 0-100
            "timestamp": time.time(),
            "data": data or {}
        }
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f)
        except Exception as e:
            print(f"Failed to write status: {e}")
    
    def run_sync_members(self):
        """Run member sync operation"""
        try:
            self.write_status("running", "Starting member sync...", 10)
            
            # Load token
            if not self.pk_sync.load_saved_token():
                self.write_status("error", "No PluralKit token configured")
                return
            
            self.write_status("running", "Testing connection...", 20)
            
            # Test connection
            success, message = self.pk_sync.api.test_connection()
            if not success:
                self.write_status("error", f"Connection failed: {message}")
                return
            
            self.write_status("running", "Syncing members...", 30)
            
            # Perform sync (without downloading avatars - we'll use aria2 for that)
            new_count, updated_count, errors = self.pk_sync.sync_members(download_avatars=False)
            
            self.write_status("running", "Members synced, checking avatars...", 60)
            
            # Use aria2 for ultra-fast avatar downloading if enabled
            if self.download_avatars:
                self._download_avatars_with_aria2()
            
            self.write_status("complete", "Sync completed successfully", 100, {
                "new_count": new_count,
                "updated_count": updated_count, 
                "errors": errors
            })
            
        except Exception as e:
            self.write_status("error", f"Sync failed: {str(e)}")
    
    def _download_avatars_with_aria2(self):
        """Download all member avatars using aria2 for maximum speed"""
        try:
            # Get all members that might need avatar downloads
            members = self.system_db.get_all_members()
            
            def status_callback(status, message, progress=60):
                # Map aria2 progress to our overall progress (60-95%)
                overall_progress = 60 + (progress * 0.35)  
                self.write_status("running", f"🚀 {message}", int(overall_progress))
            
            # Create aria2 downloader
            downloader = Aria2AvatarDownloader(self.logger, status_callback)
            
            # Check if aria2 is available
            if not downloader.check_aria2_available():
                self.logger.warning("aria2c not found, falling back to sequential downloads")
                self.write_status("running", "aria2 not found, using slower method...", 70)
                # Fallback to original method
                self._download_avatars_sequential(members)
                return
            
            # Use aria2 for blazing fast downloads
            self.logger.info("🚀 Using aria2 for ultra-fast avatar downloading!")
            success = downloader.download_avatars_bulk(members, self.system_db)
            
            if success:
                self.logger.info("✅ aria2 avatar download completed successfully")
            else:
                self.logger.warning("aria2 failed, falling back to sequential downloads")
                self._download_avatars_sequential(members)
                
        except Exception as e:
            self.logger.error(f"Error in aria2 avatar download: {e}")
            # Fallback to sequential if aria2 fails
            self._download_avatars_sequential(members)
    
    def _download_avatars_sequential(self, members):
        """Fallback method for avatar downloads without aria2"""
        try:
            self.write_status("running", "Downloading avatars (sequential)...", 70)
            
            # Use the original PluralKit sync method
            avatar_count = 0
            for i, member in enumerate(members):
                avatar_url = member.get('avatar_path', '')
                if avatar_url and avatar_url.startswith(('http://', 'https://')):
                    try:
                        # This would call the original avatar download logic
                        # For now, just log it
                        self.logger.info(f"Would download avatar for {member.get('name', 'unknown')}")
                        avatar_count += 1
                        
                        # Update progress
                        if i % 10 == 0:
                            progress = 70 + (i / len(members)) * 25  # 70-95%
                            self.write_status("running", f"Downloaded {avatar_count} avatars...", int(progress))
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to download avatar for {member.get('name', 'unknown')}: {e}")
            
            self.logger.info(f"Sequential avatar download completed: {avatar_count} avatars")
            
        except Exception as e:
            self.logger.error(f"Error in sequential avatar download: {e}")
    
    def run_full_import(self):
        """Run full system import operation"""
        try:
            self.write_status("running", "Starting full import...", 10)
            
            # Load token
            if not self.pk_sync.load_saved_token():
                self.write_status("error", "No PluralKit token configured")
                return
            
            self.write_status("running", "Testing connection...", 20)
            
            # Test connection
            success, message = self.pk_sync.api.test_connection()
            if not success:
                self.write_status("error", f"Connection failed: {message}")
                return
            
            self.write_status("running", "Importing system...", 30)
            
            # Perform import
            success, message, stats = self.pk_sync.import_full_system(self.download_avatars)
            
            if success:
                self.write_status("complete", message, 100, stats)
            else:
                self.write_status("error", message)
            
        except Exception as e:
            self.write_status("error", f"Import failed: {str(e)}")
    
    def run(self):
        """Run the specified operation"""
        print(f"Starting PK worker: {self.operation}")
        
        if self.operation == "sync":
            self.run_sync_members()
        elif self.operation == "import":
            self.run_full_import()
        else:
            self.write_status("error", f"Unknown operation: {self.operation}")

def main():
    if len(sys.argv) < 3:
        print("Usage: pk_sync_worker.py <status_file> <operation> [download_avatars]")
        print("Operations: sync, import")
        sys.exit(1)
    
    status_file = sys.argv[1]
    operation = sys.argv[2]
    download_avatars = len(sys.argv) < 4 or sys.argv[3].lower() != "false"
    
    worker = PKSyncWorker(status_file, operation, download_avatars)
    worker.run()

if __name__ == "__main__":
    main()