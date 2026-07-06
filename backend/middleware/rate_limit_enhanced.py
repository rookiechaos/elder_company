"""
Backward-compatible re-exports for rate limiting.

All logic lives in middleware.rate_limit (single shared Limiter instance).
"""

from middleware.rate_limit import (
    limiter,
    USE_REDIS,
    REDIS_URL,
    get_user_id,
    get_rate_limits,
    RATE_LIMITS,
    rate_limit,
    rate_limit_with_headers,
    RateLimitHeaderMiddleware,
    add_rate_limit_headers,
    setup_rate_limiting,
    setup_rate_limiting_enhanced,
)

__all__ = [
    "limiter",
    "USE_REDIS",
    "REDIS_URL",
    "get_user_id",
    "get_rate_limits",
    "RATE_LIMITS",
    "rate_limit",
    "rate_limit_with_headers",
    "RateLimitHeaderMiddleware",
    "add_rate_limit_headers",
    "setup_rate_limiting",
    "setup_rate_limiting_enhanced",
]
