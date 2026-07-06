"""
Error Handler Middleware - Unified error handling
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Dict, Any
import traceback
import os

from exceptions import (
    ElderCompanyException,
    NotFoundError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    RateLimitError,
    ServiceUnavailableError
)
from services.logging_service import logger
from config.settings import settings


async def elder_company_exception_handler(
    request: Request,
    exc: ElderCompanyException
) -> JSONResponse:
    """Handle Elder Company custom exceptions"""
    logger.log_error(
        error=exc,
        context={
            "endpoint": request.url.path,
            "method": request.method,
            "error_code": exc.error_code,
            "details": exc.details
        },
        user_id=getattr(request.state, "user_id", None)
    )
    
    # Determine status code based on error type
    status_code = status.HTTP_400_BAD_REQUEST
    if isinstance(exc, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AuthorizationError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, ConflictError):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, RateLimitError):
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
    elif isinstance(exc, ServiceUnavailableError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "code": exc.error_code,
                "details": exc.details
            }
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors"""
    logger.log_error(
        error=exc,
        context={
            "endpoint": request.url.path,
            "method": request.method,
            "validation_errors": exc.errors()
        },
        user_id=getattr(request.state, "user_id", None)
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "ValidationError",
                "message": "Request validation failed",
                "code": "VALIDATION_ERROR",
                "details": {
                    "errors": exc.errors()
                }
            }
        }
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """Handle HTTP exceptions"""
    logger.log_error(
        error=exc,
        context={
            "endpoint": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        },
        user_id=getattr(request.state, "user_id", None)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "message": exc.detail,
                "code": f"HTTP_{exc.status_code}",
                "details": {}
            }
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle general exceptions"""
    # Get debug mode and production status from settings
    debug_mode = settings.debug
    is_production = settings.is_production()
    
    # Only generate traceback in debug mode (never in production)
    error_traceback = traceback.format_exc() if (debug_mode and not is_production) else None
    
    # Log error with sanitized information
    logger.log_error(
        error=exc,
        context={
            "endpoint": request.url.path,
            "method": request.method,
            "traceback": error_traceback
        },
        user_id=getattr(request.state, "user_id", None)
    )
    
    # In production, completely hide detailed error information
    if is_production:
        error_message = "An internal server error occurred"
        error_details = {}
        # Never expose exception type or message in production
    else:
        # In development, show more details but still sanitize
        error_message = "An internal server error occurred"
        # Only show exception message in debug mode
        if debug_mode:
            error_message = f"An internal server error occurred: {type(exc).__name__}"
        error_details = {
            "traceback": error_traceback
        } if (debug_mode and error_traceback) else {}
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "InternalServerError",
                "message": error_message,
                "code": "INTERNAL_ERROR",
                "details": error_details
            }
        }
    )
