#!/usr/bin/env python3
"""
Aria2 Avatar Downloader - Ultra-fast bulk avatar downloading
Because downloading thousands of avatars one-by-one is for peasants 😂
"""

import os
import json
import subprocess
import tempfile
import time
from pathlib import Path
from PIL import Image
import shutil
import platformdirs


class Aria2AvatarDownloader:
    def __init__(self, logger, status_callback=None):
        self.logger = logger
        self.status_callback = status_callback
        data_dir = Path(platformdirs.user_data_dir("PluralChat", "DuskfallCrew"))
        self.download_dir = data_dir / "avatars"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def check_aria2_available(self):
        """Check if aria2c is installed"""
        try:
            result = subprocess.run(['aria2c', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def generate_download_list(self, members):
        """Generate aria2 input file with all avatar URLs that need downloading"""
        download_list = []
        members_to_update = []
        
        for member in members:
            avatar_url = member.get('avatar_path', '')
            if not avatar_url or not avatar_url.startswith(('http://', 'https://')):
                continue
                
            # Generate safe filename
            member_id = member.get('id') or member.get('pk_id', 'unknown')
            safe_id = self._sanitize_filename(str(member_id))
            local_filename = f"member_{safe_id}.tmp"  # Download as .tmp first
            local_path = self.download_dir / local_filename
            
            # Skip if already exists
            final_path = self.download_dir / f"member_{safe_id}.webp"
            if final_path.exists():
                self.logger.info(f"Avatar already exists for {member.get('name', 'unknown')}")
                continue
            
            # Add to download list
            download_list.append({
                'url': avatar_url,
                'output': str(local_path),
                'member': member,
                'final_path': final_path
            })
            members_to_update.append(member)
        
        return download_list, members_to_update
    
    def _sanitize_filename(self, member_id):
        """Sanitize filename to prevent path traversal"""
        import re
        safe_id = re.sub(r'[^\w\-_]', '_', str(member_id))
        return safe_id[:50] if safe_id else "unknown"
    
    def download_avatars_bulk(self, members, system_db):
        """Download all avatars using aria2 in one blazing fast operation"""
        if not self.check_aria2_available():
            self.logger.error("aria2c not found! Install with: brew install aria2")
            if self.status_callback:
                self.status_callback("error", "aria2c not installed")
            return False
        
        # Generate download list
        download_list, members_to_update = self.generate_download_list(members)
        
        if not download_list:
            self.logger.info("No avatars need downloading")
            if self.status_callback:
                self.status_callback("complete", "No avatars to download")
            return True
        
        self.logger.info(f"Preparing to download {len(download_list)} avatars with aria2...")
        if self.status_callback:
            self.status_callback("running", f"Downloading {len(download_list)} avatars...", 10)
        
        # Create aria2 input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            aria2_input_file = f.name
            for item in download_list:
                # aria2 format: URL followed by options
                f.write(f"{item['url']}\n")
                f.write(f"  out={Path(item['output']).name}\n")
                f.write(f"  dir={self.download_dir}\n")
        
        try:
            # Launch aria2 with aggressive parallel settings
            aria2_cmd = [
                'aria2c',
                '--input-file', aria2_input_file,
                '--max-concurrent-downloads', '16',  # 16 parallel downloads
                '--max-connection-per-server', '4',   # 4 connections per server
                '--min-split-size', '1M',             # Don't split small files
                '--split', '1',                       # 1 connection per file (avatars are small)
                '--timeout', '30',                    # 30 second timeout
                '--retry-wait', '1',                  # 1 second retry wait
                '--max-tries', '3',                   # 3 retry attempts
                '--console-log-level', 'warn',        # Less verbose output
                '--summary-interval', '1',            # Progress updates every second
                '--download-result', 'hide'           # Hide individual results
            ]
            
            self.logger.info(f"Launching aria2: {' '.join(aria2_cmd)}")
            start_time = time.time()
            
            # Run aria2 and capture output
            process = subprocess.Popen(aria2_cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.STDOUT, text=True)
            
            # Monitor progress with rate limiting
            last_update_time = time.time()
            while process.poll() is None:
                current_time = time.time()
                if current_time - last_update_time >= 1.0:  # At least 1 second between updates
                    if self.status_callback:
                        elapsed = time.time() - start_time
                        # Estimate progress based on time (aria2 is usually very fast)
                        progress = min(30 + (elapsed * 10), 80)  # Progress from 30-80%
                        self.status_callback("running", f"aria2 downloading... ({elapsed:.1f}s)", int(progress))
                    last_update_time = current_time
                time.sleep(0.1)  # Small sleep to prevent busy waiting
            
            # Get final output
            stdout, _ = process.communicate()
            download_time = time.time() - start_time
            
            if process.returncode == 0:
                self.logger.info(f"✅ aria2 completed in {download_time:.2f} seconds!")
                if self.status_callback:
                    self.status_callback("running", f"Processing {len(download_list)} images...", 85)
                
                # Process downloaded files
                success_count = self._process_downloaded_files(download_list, members_to_update, system_db)
                
                self.logger.info(f"🎉 Processed {success_count}/{len(download_list)} avatars successfully")
                if self.status_callback:
                    self.status_callback("complete", f"Downloaded {success_count} avatars in {download_time:.1f}s")
                
                return True
            else:
                self.logger.error(f"aria2 failed with return code {process.returncode}")
                self.logger.error(f"Output: {stdout}")
                if self.status_callback:
                    self.status_callback("error", f"aria2 download failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error running aria2: {e}")
            if self.status_callback:
                self.status_callback("error", f"Download error: {e}")
            return False
        finally:
            # Clean up temp file
            try:
                os.unlink(aria2_input_file)
            except:
                pass
    
    def _process_downloaded_files(self, download_list, members_to_update, system_db):
        """Convert downloaded files to WebP and update database"""
        success_count = 0
        
        for i, item in enumerate(download_list):
            try:
                temp_path = Path(item['output'])
                final_path = item['final_path']
                member = item['member']
                
                if not temp_path.exists():
                    self.logger.warning(f"Download failed for {member.get('name', 'unknown')}")
                    continue
                
                # Convert to WebP
                self._convert_to_webp(temp_path, final_path)
                
                # Update database
                system_db.update_member(member['id'], avatar_path=str(final_path))
                
                # Clean up temp file
                temp_path.unlink()
                
                success_count += 1
                
                # Update progress
                if self.status_callback and i % 10 == 0:  # Update every 10 files
                    progress = 85 + (i / len(download_list)) * 10  # 85-95%
                    self.status_callback("running", f"Processed {i+1}/{len(download_list)} images", int(progress))
                    
            except Exception as e:
                self.logger.error(f"Failed to process {member.get('name', 'unknown')}: {e}")
                # Clean up temp file on error
                try:
                    Path(item['output']).unlink()
                except:
                    pass
        
        return success_count
    
    def _convert_to_webp(self, input_path, output_path):
        """Convert image to WebP format with optimization"""
        # Open and process image
        with Image.open(input_path) as img:
            # Smart crop to square (center crop like PK does)
            width, height = img.size
            if width != height:
                min_dimension = min(width, height)
                left = (width - min_dimension) // 2
                top = (height - min_dimension) // 2
                right = left + min_dimension
                bottom = top + min_dimension
                img = img.crop((left, top, right, bottom))
            
            # Resize to standard avatar size (256x256)
            if img.size != (256, 256):
                img = img.resize((256, 256), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if 'transparency' in img.info:
                    rgb_img.paste(img, mask=img.split()[-1])
                else:
                    rgb_img.paste(img)
                img = rgb_img
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as WebP
            img.save(output_path, 'WEBP', quality=80, optimize=True)


def main():
    """Test the aria2 downloader"""
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    def status_callback(status, message, progress=0):
        print(f"[{status}] {message} ({progress}%)")
    
    downloader = Aria2AvatarDownloader(logger, status_callback)
    
    # Test with dummy data
    test_members = [
        {
            'id': 1,
            'name': 'Test Member',
            'avatar_path': 'https://httpbin.org/image/png'  # Test URL
        }
    ]
    
    # Check if aria2 is available
    if downloader.check_aria2_available():
        print("✅ aria2c found!")
    else:
        print("❌ aria2c not found. Install with: brew install aria2")


if __name__ == "__main__":
    main()