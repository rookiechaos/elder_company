"""
Health Check Service - Comprehensive system health monitoring
"""

import os
import time
from typing import Dict, Any, Optional
from datetime import datetime
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import text

from config.database import get_engine, SessionLocal


class HealthCheckService:
    """Service for comprehensive health checks"""
    
    def __init__(self):
        self.engine = get_engine()
    
    def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            db = SessionLocal()
            try:
                # Simple query to check connectivity
                result = db.execute(text("SELECT 1"))
                result.fetchone()
                
                # Check database type
                db_type = "sqlite" if "sqlite" in str(self.engine.url) else "postgresql"
                
                response_time = (time.time() - start_time) * 1000  # ms
                
                return {
                    "status": "healthy",
                    "type": db_type,
                    "response_time_ms": round(response_time, 2),
                    "connected": True
                }
            finally:
                db.close()
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "connected": False
            }
    
    def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        redis_url = os.getenv("REDIS_URL")
        
        if not redis_url:
            return {
                "status": "not_configured",
                "message": "Redis not configured (using in-memory rate limiting)"
            }
        
        try:
            import redis
            start_time = time.time()
            
            r = redis.from_url(redis_url)
            r.ping()
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Get Redis info
            info = r.info()
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "connected": True,
                "version": info.get("redis_version", "unknown"),
                "used_memory_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2)
            }
        except ImportError:
            return {
                "status": "not_available",
                "message": "Redis library not installed"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "connected": False
            }
    
    def check_ai_provider(self) -> Dict[str, Any]:
        """Check AI provider availability"""
        provider = os.getenv("AI_PROVIDER", "not_configured").lower()
        
        if provider == "not_configured":
            return {
                "status": "not_configured",
                "message": "AI provider not configured"
            }
        
        # Check if API key is set
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key or api_key == "your-openai-api-key":
                return {
                    "status": "not_configured",
                    "provider": "openai",
                    "message": "OpenAI API key not configured"
                }
        elif provider == "claude":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key or api_key == "your-anthropic-api-key":
                return {
                    "status": "not_configured",
                    "provider": "claude",
                    "message": "Anthropic API key not configured"
                }
        elif provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key or api_key == "your-google-api-key":
                return {
                    "status": "not_configured",
                    "provider": "gemini",
                    "message": "Google API key not configured"
                }
        
        # Note: We don't make actual API calls here to avoid rate limits
        # Just check if credentials are configured
        return {
            "status": "configured",
            "provider": provider,
            "message": f"{provider} API key is configured"
        }
    
    def check_storage(self) -> Dict[str, Any]:
        """Check storage service availability"""
        storage_type = os.getenv("STORAGE_TYPE", "local")
        
        if storage_type == "local":
            from utils.local_paths import default_storage_dir

            storage_dir = os.getenv("STORAGE_DIR", default_storage_dir())
            try:
                import os as os_module
                if os_module.path.exists(storage_dir):
                    # Check if writable
                    test_file = os_module.path.join(storage_dir, ".health_check")
                    try:
                        with open(test_file, "w") as f:
                            f.write("test")
                        os_module.remove(test_file)
                        return {
                            "status": "healthy",
                            "type": "local",
                            "path": storage_dir,
                            "writable": True
                        }
                    except Exception as e:
                        return {
                            "status": "unhealthy",
                            "type": "local",
                            "error": f"Storage not writable: {str(e)}"
                        }
                else:
                    return {
                        "status": "unhealthy",
                        "type": "local",
                        "error": f"Storage directory does not exist: {storage_dir}"
                    }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "type": "local",
                    "error": str(e)
                }
        else:
            # Cloud storage (S3, Azure, GCS) - basic check
            return {
                "status": "configured",
                "type": storage_type,
                "message": f"Cloud storage {storage_type} configured (not tested)"
            }
    
    def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive health status of all services"""
        checks = {
            "database": self.check_database(),
            "redis": self.check_redis(),
            "ai_provider": self.check_ai_provider(),
            "storage": self.check_storage()
        }
        
        # Determine overall status
        all_healthy = all(
            check.get("status") in ["healthy", "configured", "not_configured", "not_available"]
            for check in checks.values()
        )
        
        # Critical services must be healthy
        critical_healthy = checks["database"].get("status") == "healthy"
        
        overall_status = "healthy" if (all_healthy and critical_healthy) else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": utc_now().isoformat(),
            "checks": checks,
            "version": "2.1.0"
        }


# Global health check service instance
_health_check_service: Optional[HealthCheckService] = None


def get_health_check_service() -> HealthCheckService:
    """Get health check service instance"""
    global _health_check_service
    if _health_check_service is None:
        _health_check_service = HealthCheckService()
    return _health_check_service
