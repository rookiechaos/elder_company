"""
API Decorators - Unified error handling and common patterns

"""

from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException
from services.logging_service import logger
from exceptions import ValidationError, NotFoundError, ConflictError, AuthenticationError


def handle_api_errors(func: Callable) -> Callable:
    """
    Unified error handling decorator for API endpoints.
    Unified error-handling decorator for API endpoints
    
    Automatically converts service exceptions to HTTP exceptions:
    - ValidationError -> 400 Bad Request
    - NotFoundError -> 404 Not Found
    - ConflictError -> 409 Conflict
    - AuthenticationError -> 401 Unauthorized
    - Other exceptions -> 500 Internal Server Error
    
    Usage:
        @router.post("/endpoint")
        @handle_api_errors
        async def my_endpoint(...):
            # No need for try-except
            service.do_something()
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ConflictError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except AuthenticationError as e:
            raise HTTPException(status_code=401, detail=str(e))
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.log_error(
                error=e,
                context={
                    "action": func.__name__,
                    "endpoint": getattr(func, "__name__", "unknown")
                }
            )
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ConflictError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except AuthenticationError as e:
            raise HTTPException(status_code=401, detail=str(e))
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.log_error(
                error=e,
                context={
                    "action": func.__name__,
                    "endpoint": getattr(func, "__name__", "unknown")
                }
            )
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
    
    # Return appropriate wrapper based on whether function is async
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
