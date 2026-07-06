"""
CDN Service - Content Delivery Network integration
"""

import os
from typing import Optional, Dict, Any
from urllib.parse import urljoin
import hashlib


class CDNService:
    """Service for CDN integration"""
    
    def __init__(self, cdn_url: Optional[str] = None):
        """
        Initialize CDN service
        
        Args:
            cdn_url: CDN base URL (e.g., https://cdn.example.com)
                    If None, will read from CDN_URL environment variable
        """
        self.cdn_url = cdn_url or os.getenv("CDN_URL", "")
        self.enabled = bool(self.cdn_url)
        
        if self.enabled:
            # Ensure CDN URL ends with /
            if not self.cdn_url.endswith("/"):
                self.cdn_url += "/"
    
    def get_image_url(self, image_path: str, version: Optional[str] = None) -> str:
        """
        Get CDN URL for an image
        
        Args:
            image_path: Relative path to the image (e.g., "images/photo.jpg")
            version: Optional version string for cache busting
        
        Returns:
            Full CDN URL or original path if CDN not enabled
        """
        if not self.enabled:
            return image_path
        
        # Remove leading slash if present
        if image_path.startswith("/"):
            image_path = image_path[1:]
        
        # Add version for cache busting if provided
        if version:
            # Add version as query parameter or in path
            if "?" in image_path:
                image_path += f"&v={version}"
            else:
                image_path += f"?v={version}"
        
        return urljoin(self.cdn_url, image_path)
    
    def get_video_url(self, video_path: str, version: Optional[str] = None) -> str:
        """Get CDN URL for a video"""
        return self.get_image_url(video_path, version)
    
    def get_audio_url(self, audio_path: str, version: Optional[str] = None) -> str:
        """Get CDN URL for an audio file"""
        return self.get_image_url(audio_path, version)
    
    def get_static_url(self, static_path: str, version: Optional[str] = None) -> str:
        """Get CDN URL for any static resource"""
        return self.get_image_url(static_path, version)
    
    def generate_cache_key(self, path: str) -> str:
        """
        Generate cache key for a resource
        
        Args:
            path: Resource path
        
        Returns:
            Cache key (hash of path)
        """
        return hashlib.md5(path.encode()).hexdigest()[:12]
    
    def is_enabled(self) -> bool:
        """Check if CDN is enabled"""
        return self.enabled
    
    def get_config(self) -> Dict[str, Any]:
        """Get CDN configuration"""
        return {
            "enabled": self.enabled,
            "cdn_url": self.cdn_url if self.enabled else None,
            "status": "enabled" if self.enabled else "disabled"
        }


# Global CDN service instance
_cdn_service: Optional[CDNService] = None


def get_cdn_service() -> CDNService:
    """Get global CDN service instance"""
    global _cdn_service
    if _cdn_service is None:
        _cdn_service = CDNService()
    return _cdn_service


def set_cdn_service(service: CDNService):
    """Set global CDN service instance (for testing)"""
    global _cdn_service
    _cdn_service = service
