"""
Rate Limiting Middleware - Prevent API abuse
"""

import os
import time
import inspect
import warnings
from typing import Callable, Dict

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

REDIS_URL = os.getenv("REDIS_URL", None)
USE_REDIS = REDIS_URL is not None

if USE_REDIS:
    try:
        import redis  # noqa: F401
        limiter = Limiter(key_func=get_remote_address, storage_uri=REDIS_URL)
    except ImportError:
        limiter = Limiter(key_func=get_remote_address)
        USE_REDIS = False
else:
    limiter = Limiter(key_func=get_remote_address)


def get_user_id(request: Request) -> str:
    """Get user ID from request for rate limiting."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return str(user_id)
    return get_remote_address(request)


def get_rate_limits() -> Dict[str, str]:
    """Get rate limit configurations from settings."""
    from config.settings import settings
    return {
        "default": settings.rate_limit_default,
        "translation": settings.rate_limit_translation,
        "auth": settings.rate_limit_auth,
        "sync": settings.rate_limit_sync,
    }


RATE_LIMITS = {
    "default": "100/minute",
    "translation": "10/minute",
    "auth": "5/minute",
    "sync": "20/minute",
}


def _parse_limit_value(limit: str) -> str:
    return limit.split("/")[0] if "/" in limit else limit


def _apply_rate_limit_headers(response: Response, limit: str) -> None:
    limit_value = _parse_limit_value(limit)
    response.headers["X-RateLimit-Limit"] = limit_value
    response.headers["X-RateLimit-Remaining"] = "N/A"
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)


def _endpoint_has_request_param(func) -> bool:
    sig = inspect.signature(func)
    return "request" in sig.parameters or "http_request" in sig.parameters


def rate_limit(limit: str = "100/minute", key_func: Callable = get_remote_address):
    """
    Rate-limit decorator with response headers.

    Requires the endpoint to accept `request: Request` or `http_request: Request`.
    """
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
    if test_mode:
        def pass_through_decorator(func):
            return func
        return pass_through_decorator

    def decorator(func):
        if not _endpoint_has_request_param(func):
            return func

        try:
            limited_func = limiter.limit(limit, key_func=key_func)(func)
        except Exception as e:
            warnings.warn(f"Rate limiting failed for {func.__name__}: {e}")
            return func

        async def wrapper(*args, **kwargs):
            try:
                response = await limited_func(*args, **kwargs)
                if isinstance(response, Response):
                    _apply_rate_limit_headers(response, limit)
                return response
            except RateLimitExceeded:
                limit_value = _parse_limit_value(limit)
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "type": "RateLimitExceeded",
                            "message": "Too many requests. Please try again later.",
                            "code": "RATE_LIMIT_EXCEEDED",
                            "details": {"retry_after": 60},
                        }
                    },
                    headers={
                        "X-RateLimit-Limit": limit_value,
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time()) + 60),
                        "Retry-After": "60",
                    },
                )

        return wrapper
    return decorator


# Backward-compatible alias
rate_limit_with_headers = rate_limit


class RateLimitHeaderMiddleware(BaseHTTPMiddleware):
    """Add default rate-limit headers when not set by the decorator."""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        if hasattr(response, "headers") and "X-RateLimit-Limit" not in response.headers:
            response.headers["X-RateLimit-Limit"] = "100"
            response.headers["X-RateLimit-Remaining"] = "N/A"
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        return response


def add_rate_limit_headers(response: Response, limit: str, remaining: int = None, reset: int = None):
    """Add rate limit headers to response."""
    response.headers["X-RateLimit-Limit"] = limit
    if remaining is not None:
        response.headers["X-RateLimit-Remaining"] = str(remaining)
    if reset is not None:
        response.headers["X-RateLimit-Reset"] = str(reset)
    return response


def setup_rate_limiting(app, add_header_middleware: bool = False):
    """Setup rate limiting for FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    if add_header_middleware:
        app.add_middleware(RateLimitHeaderMiddleware)
    return app


def setup_rate_limiting_enhanced(app):
    """Backward-compatible enhanced setup (same shared limiter)."""
    return setup_rate_limiting(app, add_header_middleware=True)
