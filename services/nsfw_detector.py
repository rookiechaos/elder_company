"""
NSFW Detection Service - Content moderation for user interactions
"""

import os
from typing import Dict, Any, Optional, List
from enum import Enum
from dotenv import load_dotenv

from config.settings import settings

load_dotenv()


class NSFWLevel(Enum):
    """NSFW detection level"""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    UNSAFE = "unsafe"


class NSFWDetector:
    """Service for detecting NSFW content in user interactions"""
    
    def __init__(self):
        self.provider = settings.ai_provider.lower()
        enabled_env = os.getenv("NSFW_DETECTION_ENABLED", "true").lower()
        self.enabled = enabled_env == "true"
        strict_env = os.getenv("NSFW_DETECTION_STRICT", "true").lower()
        self.strict_mode = strict_env == "true"
        
        # Initialize provider-specific clients
        self._openai_client = None
        if self.provider == "openai":
            try:
                from openai import AsyncOpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self._openai_client = AsyncOpenAI(api_key=api_key)
            except ImportError:
                print("Warning: OpenAI not available for NSFW detection")
        
        # Basic keyword list (as fallback)
        self._unsafe_keywords = self._load_keywords()
    
    def _load_keywords(self) -> List[str]:
        """Load unsafe keywords (basic fallback)"""
        # This is a basic list - in production, use a more comprehensive list
        # or rely primarily on AI moderation APIs
        return [
            # Add basic keywords if needed (but prefer AI-based detection)
        ]
    
    async def check(
        self, text: str, language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if text contains NSFW content
        
        Args:
            text: Text to check
            language: Optional language code for better detection
        
        Returns:
            Dict with detection results
        """
        if not self.enabled:
            return {
                "safe": True,
                "level": NSFWLevel.SAFE.value,
                "reason": "NSFW detection disabled",
                "blocked": False
            }
        
        if not text or not text.strip():
            return {
                "safe": True,
                "level": NSFWLevel.SAFE.value,
                "reason": "Empty text",
                "blocked": False
            }
        
        # Try AI-based detection first
        if self.provider == "openai" and self._openai_client:
            try:
                result = await self._check_openai_moderation(text)
                return result
            except Exception as e:
                print(
                    f"OpenAI moderation failed: {e}, "
                    f"falling back to keyword check"
                )
        
        # Fallback to keyword-based detection
        return await self._check_keywords(text)
    
    async def _check_openai_moderation(self, text: str) -> Dict[str, Any]:
        """Check using OpenAI Moderation API"""
        try:
            response = await self._openai_client.moderations.create(
                input=text
            )
            
            result = response.results[0]
            flagged = result.flagged
            
            # Get categories
            categories = result.categories
            category_scores = result.category_scores
            
            # Determine level
            if flagged:
                # Check severity
                max_score = max(category_scores.dict().values())
                if max_score > 0.9:
                    level = NSFWLevel.UNSAFE
                else:
                    level = NSFWLevel.SUSPICIOUS
            else:
                level = NSFWLevel.SAFE
            
            # Get flagged categories
            flagged_categories = [
                cat for cat, is_flagged in categories.dict().items()
                if is_flagged
            ]
            
            # Determine if should block
            should_block = False
            if self.strict_mode:
                # In strict mode, block if flagged at all
                should_block = flagged
            else:
                # In non-strict mode, only block unsafe content
                should_block = level == NSFWLevel.UNSAFE
            
            return {
                "safe": not flagged,
                "level": level.value,
                "flagged": flagged,
                "flagged_categories": flagged_categories,
                "scores": category_scores.dict(),
                "blocked": should_block,
                "reason": (
                    f"OpenAI moderation: "
                    f"{', '.join(flagged_categories) if flagged_categories else 'safe'}"
                ),
                "provider": "openai"
            }
        except Exception as e:
            raise Exception(f"OpenAI moderation API error: {str(e)}")
    
    async def _check_keywords(self, text: str) -> Dict[str, Any]:
        """Fallback keyword-based detection"""
        text_lower = text.lower()
        
        # Check for unsafe keywords
        found_keywords = [
            keyword for keyword in self._unsafe_keywords
            if keyword.lower() in text_lower
        ]
        
        if found_keywords:
            return {
                "safe": False,
                "level": NSFWLevel.SUSPICIOUS.value,
                "flagged": True,
                "flagged_categories": ["keyword_match"],
                "blocked": True,
                "reason": f"Keyword match detected",
                "provider": "keyword"
            }
        
        return {
            "safe": True,
            "level": NSFWLevel.SAFE.value,
            "flagged": False,
            "blocked": False,
            "reason": "No unsafe content detected",
            "provider": "keyword"
        }
    
    def should_block(self, detection_result: Dict[str, Any]) -> bool:
        """Check if content should be blocked based on detection result"""
        return detection_result.get("blocked", False)
    
    def get_block_message(self, language: str = "en") -> str:
        """Get user-friendly block message"""
        messages = {
            "ja": (
                "申し訳ございませんが、入力されたContentに不適切なContentが"
                "含まれているため、処理できません。礼儀正しい言葉を使用してください。"
            ),
            "en": (
                "Sorry, your input contains inappropriate content and "
                "cannot be processed. Please use polite and respectful "
                "language."
            )
        }
        return messages.get(language, messages["en"])


# Global NSFW detector instance
_nsfw_detector: Optional[NSFWDetector] = None


def get_nsfw_detector() -> NSFWDetector:
    """Get global NSFW detector instance"""
    global _nsfw_detector
    if _nsfw_detector is None:
        _nsfw_detector = NSFWDetector()
    return _nsfw_detector
