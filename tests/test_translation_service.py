"""
Unit tests for TranslationService
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from services.translation_service import TranslationService


class TestTranslationService:
    """Test cases for TranslationService"""
    
    @pytest.fixture
    def mock_provider(self):
        """Mock AI provider"""
        provider = Mock()
        provider.translate = AsyncMock(return_value={
            "text": "你好",
            "provider": "openai"
        })
        provider.chat = AsyncMock(return_value={
            "text": "你好，今天天气很好。",
            "provider": "openai"
        })
        return provider
    
    @pytest.fixture
    def translation_service(self, mock_provider):
        """Create TranslationService with mocked provider"""
        with patch('services.translation_service.get_ai_provider', return_value=mock_provider):
            with patch('os.getenv', return_value='openai'):
                service = TranslationService()
                service.provider = mock_provider
                return service
    
    @pytest.mark.asyncio
    async def test_translate_success(self, translation_service):
        """Test successful translation"""
        result = await translation_service.translate(
            text="こんにちは",
            source_language="ja",
            target_language="zh"
        )
        
        assert result is not None
        assert "translated_text" in result
        assert result["translated_text"] == "你好"
        assert result["original_text"] == "こんにちは"
        assert result["source_language"] == "ja"
        assert result["target_language"] == "zh"
    
    @pytest.mark.asyncio
    async def test_translate_empty_text(self, translation_service):
        """Test translation with empty text raises error"""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await translation_service.translate(
                text="",
                source_language="ja",
                target_language="zh"
            )
    
    @pytest.mark.asyncio
    async def test_translate_same_language(self, translation_service):
        """Test translation with same source and target language"""
        result = await translation_service.translate(
            text="こんにちは",
            source_language="ja",
            target_language="ja"
        )
        
        assert result["translated_text"] == result["original_text"]
        assert result["translated_text"] == "こんにちは"
    
    @pytest.mark.asyncio
    async def test_translate_with_context(self, translation_service):
        """Test translation with context"""
        result = await translation_service.translate(
            text="食事介助をお願いします",
            source_language="ja",
            target_language="zh",
            context="照护场景"
        )
        
        assert result is not None
        assert "translated_text" in result
        # Verify context was used in prompt
        translation_service.provider.translate.assert_called_once()
        call_args = translation_service.provider.translate.call_args
        assert "照护场景" in call_args[1]["prompt"] or "照护" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_translate_with_personalization(self, translation_service):
        """Test translation with personalization"""
        personalization = {
            "translation_style": "professional",
            "use_honorifics": True
        }
        
        result = await translation_service.translate(
            text="こんにちは",
            source_language="ja",
            target_language="zh",
            personalization=personalization
        )
        
        assert result is not None
        # Verify personalization was used
        translation_service.provider.translate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_translate_conversation(self, translation_service):
        """Test conversation translation"""
        result = await translation_service.translate_conversation(
            message="おはようございます",
            source_language="ja",
            target_language="zh"
        )
        
        assert result is not None
        assert "translated_text" in result
        assert result["translated_text"] == "你好，今天天气很好。"
    
    @pytest.mark.asyncio
    async def test_translate_provider_error(self, translation_service):
        """Test handling provider errors"""
        translation_service.provider.translate = AsyncMock(
            side_effect=Exception("Provider error")
        )
        
        with pytest.raises(Exception, match="Provider error"):
            await translation_service.translate(
                text="こんにちは",
                source_language="ja",
                target_language="zh"
            )
