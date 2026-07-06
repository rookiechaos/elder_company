"""
Security Headers Middleware - Add security headers to responses

"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
from typing import Callable
import os


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    Middleware that adds security headers to all responses
    """
    
    def __init__(self, app, environment: str = "development"):
        super().__init__(app)
        self.environment = environment
        self.is_production = environment.lower() == "production"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Content Security Policy (CSP)
        # Set CSP based on environment
        if self.is_production:
            # Production: strict CSP
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https://api.eldercompany.com; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        else:
            # Development: relaxed CSP (allows localhost)
            csp = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval' http://localhost:*; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' http://localhost:*; "
                "style-src 'self' 'unsafe-inline' http://localhost:*; "
                "img-src 'self' data: https: http://localhost:*; "
                "connect-src 'self' http://localhost:* https://api.eldercompany.com; "
                "frame-ancestors 'self' http://localhost:*"
            )
        
        # X-Content-Type-Options: Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-Frame-Options: Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-XSS-Protection: XSS protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy: Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy: Control browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=()"
        )
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = csp
        
        # Strict-Transport-Security (HSTS) - Enabled only in production over HTTPS
        if self.is_production:
            # Note: set HSTS only when served over HTTPS
            if request.url.scheme == "https":
                response.headers["Strict-Transport-Security"] = (
                    "max-age=31536000; "
                    "includeSubDomains; "
                    "preload"
                )
        
        return response


def setup_security_headers(app, environment: str = None):
    """
    Setup security headers middleware
    
    Args:
        app: FastAPI application
        environment: Environment name (development/production)
    """
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    
    app.add_middleware(SecurityHeadersMiddleware, environment=environment)
    return app
