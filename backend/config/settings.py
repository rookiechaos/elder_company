"""
Settings Configuration - Unified configuration management
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache

from utils.local_paths import (
    default_database_url,
    default_log_file,
    default_error_log_file,
    ensure_local_dirs,
    env_file_path,
)

ensure_local_dirs()


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Application
    app_name: str = "Elder Company Care Collaboration Platform API"
    app_version: str = "2.1.2"
    debug: bool = False
    environment: str = "development"  # development, staging, production
    
    # Database
    database_url: str = default_database_url()
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_pre_ping: bool = True
    
    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_days: int = 30
    
    def __init__(self, **kwargs):
        """Initialize settings with security validation"""
        super().__init__(**kwargs)
        
        # Always validate JWT secret key (not just in production)
        from utils.security import validate_jwt_secret_key
        
        # Check if using default/weak key
        default_keys = {
            "your-secret-key-change-in-production",
            "change-me-in-production",
            "secret",
            "password",
            "123456"
        }
        
        if self.jwt_secret_key in default_keys:
            if self.is_production():
                raise ValueError(
                    "JWT_SECRET_KEY must be set to a secure value in production environment. "
                    "Using default key is INSECURE and will cause the application to fail. "
                    "Generate a secure key using: python -c 'import secrets; print(secrets.token_hex(32))'"
                )
            else:
                import warnings
                warnings.warn(
                    f"JWT_SECRET_KEY is set to default value '{self.jwt_secret_key}'. "
                    "This is INSECURE for production. "
                    "Please set a strong secret key (minimum 32 characters). "
                    "Generate one using: python -c 'import secrets; print(secrets.token_hex(32))'",
                    UserWarning
                )
        
        # Validate JWT secret key strength
        if not validate_jwt_secret_key(self.jwt_secret_key):
            if self.is_production():
                raise ValueError(
                    "JWT_SECRET_KEY is not secure for production. "
                    "Please set a strong secret key (minimum 32 characters). "
                    "Generate one using: python -c 'import secrets; print(secrets.token_hex(32))'"
                )
            else:
                import warnings
                warnings.warn(
                    f"JWT_SECRET_KEY is too weak (length: {len(self.jwt_secret_key)}). "
                    "Minimum 32 characters required for production. "
                    "Generate one using: python -c 'import secrets; print(secrets.token_hex(32))'",
                    UserWarning
                )
    
    # AI Provider
    ai_provider: str = "openai"  # openai, claude, gemini
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Redis (for distributed rate limiting)
    redis_url: Optional[str] = None  # redis://localhost:6379
    
    # Logging
    log_level: str = "INFO"
    log_file: str = default_log_file()
    error_log_file: str = default_error_log_file()
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_default: str = "100/minute"
    
    # Performance Monitoring
    performance_monitoring_enabled: bool = True
    slow_query_threshold_ms: int = 1000
    
    # Storage
    storage_type: str = "local"  # local, s3, gcs
    storage_path: str = "storage"
    
    # CDN
    cdn_enabled: bool = False
    cdn_base_url: Optional[str] = None
    
    # Image Optimization
    image_optimization_enabled: bool = True
    image_optimization_quality: int = 85
    image_optimization_format: str = "webp"
    
    # Task Queue
    task_queue_enabled: bool = True
    task_queue_type: str = "memory"  # memory, redis, celery
    
    # Web Vitals
    web_vitals_enabled: bool = True
    web_vitals_alert_threshold_lcp: float = 2.5
    web_vitals_alert_threshold_fid: float = 100.0
    web_vitals_alert_threshold_cls: float = 0.1
    # Web Vitals detailed thresholds (good/needs_improvement/poor)
    web_vitals_lcp_good: float = 2500.0  # milliseconds
    web_vitals_lcp_needs_improvement: float = 4000.0
    web_vitals_fid_good: float = 100.0  # milliseconds
    web_vitals_fid_needs_improvement: float = 300.0
    web_vitals_cls_good: float = 0.1
    web_vitals_cls_needs_improvement: float = 0.25
    web_vitals_fcp_good: float = 1800.0  # milliseconds
    web_vitals_fcp_needs_improvement: float = 3000.0
    web_vitals_ttfb_good: float = 800.0  # milliseconds
    web_vitals_ttfb_needs_improvement: float = 1800.0
    web_vitals_tti_good: float = 3800.0  # milliseconds
    web_vitals_tti_needs_improvement: float = 7300.0
    
    # NSFW Detection
    nsfw_detection_enabled: bool = True
    
    # Voice Services
    voice_stt_enabled: bool = False
    voice_tts_enabled: bool = False
    
    # Payment (Stripe)
    stripe_enabled: bool = False
    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # Email (for notifications)
    email_enabled: bool = False
    email_smtp_host: Optional[str] = None
    email_smtp_port: int = 587
    email_smtp_user: Optional[str] = None
    email_smtp_password: Optional[str] = None
    email_from: Optional[str] = None
    
    # Cache Configuration
    cache_ttl_activity_templates: int = 3600  # 1 hour
    cache_ttl_user_config: int = 1800  # 30 minutes
    cache_ttl_care_terms: int = 86400  # 24 hours
    cache_ttl_customer_info: int = 900  # 15 minutes
    cache_ttl_organization: int = 1800  # 30 minutes
    cache_ttl_translation: int = 300  # 5 minutes
    
    # Rate Limiting Configuration
    rate_limit_default: str = "100/minute"
    rate_limit_translation: str = "10/minute"
    rate_limit_auth: str = "5/minute"
    rate_limit_sync: str = "20/minute"
    
    # Test Mode
    test_mode: bool = False
    
    class Config:
        env_file = (str(env_file_path()), ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables
    
    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    def get_database_url(self) -> str:
        """Get database URL with proper format"""
        return self.database_url
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"
    
    def get_ai_api_key(self) -> Optional[str]:
        """Get API key for current AI provider"""
        provider = self.ai_provider.lower()
        if provider == "openai":
            return self.openai_api_key
        elif provider == "claude" or provider == "anthropic":
            return self.anthropic_api_key
        elif provider == "gemini" or provider == "google":
            return self.google_api_key
        return None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
