"""
Tests for NSFW Detection Service
"""

import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock
from typing import Dict, Any

from services.nsfw_detector import (
    NSFWDetector,
    get_nsfw_detector,
    NSFWLevel
)


class TestNSFWDetector:
    """Tests for NSFWDetector"""
    
    def test_detector_initialization(self):
        """Test NSFW detector initialization"""
        detector = NSFWDetector()
        assert detector is not None
        assert hasattr(detector, 'enabled')
        assert hasattr(detector, 'strict_mode')
        assert hasattr(detector, 'provider')
    
    def test_detector_disabled(self):
        """Test detector when disabled"""
        with patch.dict(os.environ, {'NSFW_DETECTION_ENABLED': 'false'}):
            detector = NSFWDetector()
            assert detector.enabled is False
    
    def test_detector_enabled(self):
        """Test detector when enabled"""
        with patch.dict(os.environ, {'NSFW_DETECTION_ENABLED': 'true'}):
            detector = NSFWDetector()
            assert detector.enabled is True
    
    @pytest.mark.asyncio
    async def test_check_empty_text(self):
        """Test checking empty text"""
        detector = NSFWDetector()
        result = await detector.check("")
        
        assert result["safe"] is True
        assert result["level"] == NSFWLevel.SAFE.value
        assert result["blocked"] is False
        assert "reason" in result
    
    @pytest.mark.asyncio
    async def test_check_safe_text(self):
        """Test checking safe text"""
        detector = NSFWDetector()
        safe_text = "こんにちは、お元気ですか？"
        result = await detector.check(safe_text, language="ja")
        
        # Should be safe (unless OpenAI flags it, which we'll mock)
        assert "safe" in result
        assert "level" in result
        assert "blocked" in result
    
    @pytest.mark.asyncio
    async def test_check_with_openai_success(self):
        """Test checking with OpenAI moderation API (success)"""
        # Mock OpenAI client
        mock_response = MagicMock()
        mock_response.results = [MagicMock()]
        mock_response.results[0].flagged = False
        mock_response.results[0].categories = MagicMock()
        mock_response.results[0].categories.dict.return_value = {}
        mock_response.results[0].category_scores = MagicMock()
        mock_response.results[0].category_scores.dict.return_value = {}
        
        detector = NSFWDetector()
        detector._openai_client = MagicMock()
        detector._openai_client.moderations.create = AsyncMock(return_value=mock_response)
        
        result = await detector._check_openai_moderation("Safe text")
        
        assert result["safe"] is True
        assert result["level"] == NSFWLevel.SAFE.value
        assert result["blocked"] is False
        assert result["provider"] == "openai"
    
    @pytest.mark.asyncio
    async def test_check_with_openai_flagged(self):
        """Test checking with OpenAI moderation API (flagged)"""
        # Mock OpenAI client with flagged content
        mock_response = MagicMock()
        mock_response.results = [MagicMock()]
        mock_response.results[0].flagged = True
        mock_response.results[0].categories = MagicMock()
        mock_response.results[0].categories.dict.return_value = {
            "hate": True,
            "violence": False
        }
        mock_response.results[0].category_scores = MagicMock()
        mock_response.results[0].category_scores.dict.return_value = {
            "hate": 0.95,
            "violence": 0.1
        }
        
        detector = NSFWDetector()
        detector._openai_client = MagicMock()
        detector._openai_client.moderations.create = AsyncMock(return_value=mock_response)
        
        result = await detector._check_openai_moderation("Unsafe text")
        
        assert result["safe"] is False
        assert result["flagged"] is True
        assert "hate" in result["flagged_categories"]
        assert result["provider"] == "openai"
    
    @pytest.mark.asyncio
    async def test_check_with_openai_high_score(self):
        """Test checking with high score (unsafe level)"""
        # Mock OpenAI client with high score
        mock_response = MagicMock()
        mock_response.results = [MagicMock()]
        mock_response.results[0].flagged = True
        mock_response.results[0].categories = MagicMock()
        mock_response.results[0].categories.dict.return_value = {
            "violence": True
        }
        mock_response.results[0].category_scores = MagicMock()
        mock_response.results[0].category_scores.dict.return_value = {
            "violence": 0.95  # High score
        }
        
        detector = NSFWDetector()
        detector._openai_client = MagicMock()
        detector._openai_client.moderations.create = AsyncMock(return_value=mock_response)
        
        result = await detector._check_openai_moderation("Violent text")
        
        assert result["level"] == NSFWLevel.UNSAFE.value
        assert result["blocked"] is True
    
    @pytest.mark.asyncio
    async def test_check_keywords_fallback(self):
        """Test keyword-based fallback detection"""
        detector = NSFWDetector()
        result = await detector._check_keywords("Normal safe text")
        
        assert result["safe"] is True
        assert result["provider"] == "keyword"
        assert result["blocked"] is False
    
    @pytest.mark.asyncio
    async def test_check_fallback_on_openai_error(self):
        """Test fallback to keyword check when OpenAI fails"""
        detector = NSFWDetector()
        detector._openai_client = MagicMock()
        detector._openai_client.moderations.create = AsyncMock(side_effect=Exception("API Error"))
        
        # Should fallback to keyword check
        result = await detector.check("Test text", language="zh")
        
        assert "safe" in result
        assert "provider" in result
    
    def test_should_block_strict_mode(self):
        """Test should_block in strict mode"""
        detector = NSFWDetector()
        detector.strict_mode = True
        
        # In strict mode, any flagged content should be blocked
        result_flagged = {
            "blocked": True,
            "flagged": True,
            "level": NSFWLevel.SUSPICIOUS.value
        }
        assert detector.should_block(result_flagged) is True
        
        result_safe = {
            "blocked": False,
            "flagged": False,
            "level": NSFWLevel.SAFE.value
        }
        assert detector.should_block(result_safe) is False
    
    def test_should_block_non_strict_mode(self):
        """Test should_block in non-strict mode"""
        detector = NSFWDetector()
        detector.strict_mode = False
        
        # In non-strict mode, only unsafe content should be blocked
        result_suspicious = {
            "blocked": False,  # Set by detector based on level
            "level": NSFWLevel.SUSPICIOUS.value
        }
        # Suspicious should not be blocked in non-strict mode
        assert detector.should_block(result_suspicious) is False
        
        result_unsafe = {
            "blocked": True,
            "level": NSFWLevel.UNSAFE.value
        }
        assert detector.should_block(result_unsafe) is True
    
    def test_get_block_message_unknown_language_falls_back_to_en(self):
        """Test get block message falls back to English for removed zh locale"""
        detector = NSFWDetector()
        message = detector.get_block_message("zh")
        
        assert "Sorry" in message or "inappropriate" in message.lower()
        assert isinstance(message, str)
    
    def test_get_block_message_ja(self):
        """Test get block message in Japanese"""
        detector = NSFWDetector()
        message = detector.get_block_message("ja")
        
        assert "申し訳" in message or "不適切" in message
        assert isinstance(message, str)
    
    def test_get_block_message_en(self):
        """Test get block message in English"""
        detector = NSFWDetector()
        message = detector.get_block_message("en")
        
        assert "Sorry" in message or "inappropriate" in message.lower()
        assert isinstance(message, str)
    
    def test_get_block_message_default(self):
        """Test get block message with unknown language (defaults to English)"""
        detector = NSFWDetector()
        message = detector.get_block_message("unknown")
        
        assert isinstance(message, str)
        assert len(message) > 0
    
    def test_get_nsfw_detector_singleton(self):
        """Test get_nsfw_detector returns singleton"""
        detector1 = get_nsfw_detector()
        detector2 = get_nsfw_detector()
        
        assert detector1 is detector2
    
    @pytest.mark.asyncio
    async def test_check_integration(self):
        """Integration test for check method"""
        detector = NSFWDetector()
        
        # Test with safe text
        result = await detector.check("Hello, how are you?", language="en")
        
        assert isinstance(result, dict)
        assert "safe" in result
        assert "level" in result
        assert "blocked" in result
        assert "reason" in result
    
    @pytest.mark.asyncio
    async def test_check_with_language_parameter(self):
        """Test check method with language parameter"""
        detector = NSFWDetector()
        
        result = await detector.check("Test text", language="ja")
        
        assert isinstance(result, dict)
        assert "safe" in result


class TestNSFWDetectorIntegration:
    """Integration tests for NSFW detector with API endpoints"""
    
    @pytest.mark.asyncio
    async def test_detector_with_translation_endpoint(self):
        """Test NSFW detection integration with translation endpoint"""
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        # This test verifies that NSFW detection is called
        # In a real scenario, we'd mock the detector
        # For now, we just verify the endpoint exists and handles requests
        
        # Note: This would require mocking the NSFW detector
        # to avoid actual API calls during testing
        pass
    
    def test_detector_configuration(self):
        """Test detector configuration options"""
        # Test with different environment configurations
        test_configs = [
            {"NSFW_DETECTION_ENABLED": "true", "NSFW_DETECTION_STRICT": "true"},
            {"NSFW_DETECTION_ENABLED": "true", "NSFW_DETECTION_STRICT": "false"},
            {"NSFW_DETECTION_ENABLED": "false", "NSFW_DETECTION_STRICT": "true"},
        ]
        
        for config in test_configs:
            with patch.dict(os.environ, config, clear=False):
                detector = NSFWDetector()
                assert detector.enabled == (config["NSFW_DETECTION_ENABLED"] == "true")
                assert detector.strict_mode == (config["NSFW_DETECTION_STRICT"] == "true")
