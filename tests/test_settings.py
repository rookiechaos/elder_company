"""
Tests for Settings Configuration
配置管理测试
"""

import pytest
import os
from config.settings import Settings, get_settings


def test_settings_defaults():
    """Test default settings values"""
    settings = Settings()
    
    assert settings.app_name == "Elder Company 照护协同平台 API"
    assert settings.app_version == "2.1.1"
    assert settings.debug is False
    assert settings.environment == "development"


def test_settings_database_url():
    """Test database URL setting"""
    settings = Settings()
    
    assert settings.database_url is not None
    assert isinstance(settings.database_url, str)


def test_settings_jwt_config():
    """Test JWT configuration"""
    settings = Settings()
    
    assert settings.jwt_algorithm == "HS256"
    assert settings.jwt_expiry_days == 30
    assert settings.jwt_secret_key is not None


def test_settings_ai_provider():
    """Test AI provider configuration"""
    settings = Settings()
    
    assert settings.ai_provider in ["openai", "claude", "gemini"]


def test_get_cors_origins_list():
    """Test CORS origins list conversion"""
    settings = Settings()
    origins = settings.get_cors_origins_list()
    
    assert isinstance(origins, list)
    assert len(origins) > 0


def test_is_production():
    """Test production check"""
    settings = Settings(environment="production")
    assert settings.is_production() is True
    
    settings = Settings(environment="development")
    assert settings.is_production() is False


def test_is_development():
    """Test development check"""
    settings = Settings(environment="development")
    assert settings.is_development() is True
    
    settings = Settings(environment="production")
    assert settings.is_development() is False


def test_get_ai_api_key():
    """Test getting AI API key"""
    settings = Settings(
        ai_provider="openai",
        openai_api_key="test_key_123"
    )
    
    api_key = settings.get_ai_api_key()
    assert api_key == "test_key_123"


def test_get_settings_cached():
    """Test that get_settings returns cached instance"""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2


def test_settings_from_env(monkeypatch):
    """Test loading settings from environment variables"""
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AI_PROVIDER", "claude")
    
    # Clear cache to reload settings
    from config.settings import get_settings
    import functools
    get_settings.cache_clear()
    
    settings = get_settings()
    
    assert settings.debug is True
    assert settings.environment == "production"
    assert settings.ai_provider == "claude"
