import json
from typing import Dict, List, Optional
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler


class PluralKitExportParser:
    """Parser for PluralKit export files - handles the complex nested structure"""
    
    def __init__(self):
        self.supported_versions = ["1.1", "1.0"]  # Add more as we discover them
        self.logger = logging.getLogger('plural_chat.pk_export_parser')
    
    def parse_export_file(self, filepath: str) -> Dict:
        """
        Parse a PluralKit export file and convert to our format
        Returns: {"system_info": {}, "members": [], "messages": []}
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Detect export format
            if self.is_pk_export_format(data):
                return self.parse_pk_export(data)
            elif self.is_our_export_format(data):
                return data  # Already in our format
            else:
                raise ValueError("Unsupported export format")
                
        except Exception as e:
            self.logger.error(f"Failed to parse export file: {e}")
            raise ValueError(f"Failed to parse export file: {e}")
    
    def is_pk_export_format(self, data: Dict) -> bool:
        """Check if this looks like a PluralKit export"""
        # PK exports have version, id, uuid, and members fields
        return (data.get("version") in [1, 2] and 
                "id" in data and 
                "uuid" in data and 
                "members" in data)
    
    def is_our_export_format(self, data: Dict) -> bool:
        """Check if this is our own export format"""
        return "system_info" in data and "export_date" in data.get("system_info", {})
    
    def parse_pk_export(self, data: Dict) -> Dict:
        """Parse PluralKit export format"""
        result = {
            "system_info": {},
            "members": [],
            "messages": []
        }
        
        # Parse system info
        result["system_info"] = {
            "name": data.get("name", "Imported System"),
            "pk_system_id": data.get("id", ""),
            "export_date": datetime.now().isoformat(),
            "version": "2.0",
            "imported_from": "pluralkit"
        }
        
        if data.get("description"):
            result["system_info"]["description"] = data["description"]
        if data.get("tag"):
            result["system_info"]["tag"] = data["tag"]
        if data.get("timezone"):
            result["system_info"]["timezone"] = data["timezone"]
        
        # Parse members
        members_data = data.get("members", [])
        for pk_member in members_data:
            member = self.parse_pk_member(pk_member)
            if member:
                result["members"].append(member)
        
        # Parse messages (if present)
        # PK exports might have different message formats
        messages_data = data.get("messages", [])
        for pk_message in messages_data:
            message = self.parse_pk_message(pk_message, result["members"])
            if message:
                result["messages"].append(message)
        
        return result
    
    def parse_pk_member(self, pk_member: Dict) -> Optional[Dict]:
        """Parse a PluralKit member object"""
        try:
            # Convert proxy tags to JSON string
            proxy_tags = pk_member.get("proxy_tags", [])
            proxy_tags_json = json.dumps(proxy_tags) if proxy_tags else None
            
            # Smart name selection to avoid conflicts
            display_name = pk_member.get("display_name") or ""
            base_name = pk_member.get("name") or "Unknown"
            
            # Safely strip if not None
            display_name = display_name.strip() if display_name else ""
            base_name = base_name.strip() if base_name else "Unknown"
            
            # Use display_name if it's different and not empty, otherwise use name
            if display_name and display_name != base_name:
                name = display_name
            else:
                name = base_name
            
            # Fallback if both are empty
            if not name:
                name = "Unknown Member"
            
            member = {
                "name": name,
                "pk_id": pk_member.get("id"),
                "pronouns": pk_member.get("pronouns"),
                "avatar_path": pk_member.get("avatar_url"),  # Note: field name difference
                "color": pk_member.get("color"),
                "description": pk_member.get("description"),
                "proxy_tags": proxy_tags_json
            }
            
            # Store original name in description if different
            if display_name and display_name != base_name:
                orig_desc = member.get("description", "")
                if orig_desc:
                    member["description"] = f"Original name: {base_name}\n\n{orig_desc}"
                else:
                    member["description"] = f"Original name: {base_name}"
            
            # Handle additional PK fields
            if pk_member.get("birthday"):
                member["birthday"] = pk_member["birthday"]
            
            return member
            
        except Exception as e:
            self.logger.error(f"Error parsing member {pk_member.get('name', 'unknown')}: {e}")
            return None
    
    def parse_pk_message(self, pk_message: Dict, members: List[Dict]) -> Optional[Dict]:
        """Parse a PluralKit message object"""
        try:
            # Find member by PK ID
            member_id = pk_message.get("member")
            member_name = "Unknown"
            
            if member_id:
                for member in members:
                    if member.get("pk_id") == member_id:
                        member_name = member["name"]
                        break
            
            # Parse timestamp (PK uses ISO format)
            timestamp_str = pk_message.get("timestamp", "")
            try:
                if timestamp_str:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    timestamp = dt.strftime("%H:%M")
                else:
                    timestamp = datetime.now().strftime("%H:%M")
            except:
                timestamp = datetime.now().strftime("%H:%M")
            
            message = {
                "member": member_name,
                "message": pk_message.get("content", ""),
                "timestamp": timestamp,
                "date": timestamp_str
            }
            
            # Add channel info if available
            if pk_message.get("channel"):
                message["channel"] = pk_message["channel"]
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error parsing message: {e}")
            return None
    
    def create_sample_pk_export(self) -> Dict:
        """Create a sample PK export structure for testing"""
        return {
            "version": "1.1",
            "id": "abcde",
            "name": "Test System",
            "description": "A test system for development",
            "tag": "test",
            "timezone": "UTC",
            "members": [
                {
                    "id": "member1",
                    "name": "Alice",
                    "display_name": "Alice (she/her)",
                    "pronouns": "she/her",
                    "color": "#ff6b6b",
                    "description": "The main fronter",
                    "avatar_url": "https://example.com/alice.png",
                    "proxy_tags": [
                        {"prefix": "", "suffix": " -a"},
                        {"prefix": "a:", "suffix": ""}
                    ],
                    "birthday": "2000-01-01"
                },
                {
                    "id": "member2", 
                    "name": "Bob",
                    "pronouns": "he/him",
                    "color": "#4ecdc4",
                    "proxy_tags": [
                        {"prefix": "", "suffix": " -bob"},
                        {"prefix": "b>", "suffix": ""}
                    ]
                }
            ],
            "messages": [
                {
                    "timestamp": "2024-01-01T12:00:00Z",
                    "member": "member1",
                    "content": "Hello world!",
                    "channel": "general"
                },
                {
                    "timestamp": "2024-01-01T12:01:00Z", 
                    "member": "member2",
                    "content": "Hey there!",
                    "channel": "general"
                }
            ]
        }


def test_parser():
    """Test the parser with sample data"""
    parser = PluralKitExportParser()
    sample_data = parser.create_sample_pk_export()
    
    try:
        result = parser.parse_pk_export(sample_data)
        parser.logger.info("Parser test successful!")
        parser.logger.info(f"Parsed {len(result['members'])} members")
        parser.logger.info(f"Parsed {len(result['messages'])} messages")
        parser.logger.info(f"System: {result['system_info']['name']}")
        
        # Show first member's proxy tags
        if result['members']:
            first_member = result['members'][0]
            parser.logger.info(f"First member: {first_member['name']}")
            if first_member.get('proxy_tags'):
                proxy_tags = json.loads(first_member['proxy_tags'])
                parser.logger.info(f"Proxy tags: {proxy_tags}")
        
        return True
    except Exception as e:
        parser.logger.error(f"Parser test failed: {e}")
        return False


if __name__ == "__main__":
    test_parser()