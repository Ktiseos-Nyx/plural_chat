"""Proxy tag detection for automatic member switching."""

import logging
import re
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class ProxyDetector:
    """Detects proxy tags in messages to automatically switch members."""

    def __init__(self, system_db):
        self.system_db = system_db
        self._proxy_patterns = {}
        self._build_proxy_patterns()

    def _build_proxy_patterns(self):
        """Build regex patterns from member proxy tags."""
        members = self.system_db.get_all_members()

        for member in members:
            proxy_tags = member.get('proxy_tags')
            if not proxy_tags:
                continue

            # Parse proxy tags (could be JSON string or dict)
            if isinstance(proxy_tags, str):
                try:
                    import json
                    proxy_tags = json.loads(proxy_tags)
                except:
                    continue

            if not isinstance(proxy_tags, list):
                continue

            for tag in proxy_tags:
                prefix = tag.get('prefix', '')
                suffix = tag.get('suffix', '')

                if not prefix and not suffix:
                    continue

                # Build regex pattern
                pattern = self._build_pattern(prefix, suffix)
                if pattern:
                    self._proxy_patterns[member['id']] = {
                        'pattern': pattern,
                        'prefix': prefix,
                        'suffix': suffix
                    }

    def _build_pattern(self, prefix: str, suffix: str) -> Optional[re.Pattern]:
        """Build a regex pattern from prefix and suffix."""
        try:
            # Escape special regex characters
            prefix_escaped = re.escape(prefix) if prefix else ''
            suffix_escaped = re.escape(suffix) if suffix else ''

            # Build pattern to capture the message
            if prefix and suffix:
                pattern_str = f"^{prefix_escaped}(.+?){suffix_escaped}$"
            elif prefix:
                pattern_str = f"^{prefix_escaped}(.+)$"
            elif suffix:
                pattern_str = f"^(.+){suffix_escaped}$"
            else:
                return None

            return re.compile(pattern_str, re.DOTALL)

        except Exception as e:
            logger.error(f"Failed to build pattern for {prefix}/{suffix}: {e}")
            return None

    def detect_proxy(self, text: str) -> Optional[Dict]:
        """
        Detect if a message contains a proxy tag.

        Returns:
            Dict with 'member_id', 'message' (without proxy), 'prefix', 'suffix'
            or None if no proxy detected
        """
        for member_id, proxy_data in self._proxy_patterns.items():
            pattern = proxy_data['pattern']
            match = pattern.match(text)

            if match:
                # Extract the message without proxy tags
                message = match.group(1).strip()

                return {
                    'member_id': member_id,
                    'message': message,
                    'prefix': proxy_data['prefix'],
                    'suffix': proxy_data['suffix']
                }

        return None

    def refresh(self):
        """Refresh proxy patterns from database."""
        self._proxy_patterns.clear()
        self._build_proxy_patterns()
