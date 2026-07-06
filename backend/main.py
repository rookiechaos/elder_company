"""
Elder Company - Care Collaboration Platform Backend API
Helps caregivers and elders co-create meaningful activities and communicate effectively.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_BACKEND_ROOT = Path(__file__).resolve().parent
for _path in (_REPO_ROOT, _BACKEND_ROOT):
    _path_str = str(_path)
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)

import os
import time
import uuid
import importlib
from datetime import datetime
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.translation_service import TranslationService
from services.user_service import UserService
from services.organization_service import OrganizationService
from services.logging_service import logger
from config.database import init_database, get_db, setup_query_analysis
from config.settings import settings
from middleware.rate_limit import setup_rate_limiting, rate_limit, RATE_LIMITS
from middleware.performance import (
    PerformanceMonitoringMiddleware,
    get_performance_stats
)
from services.query_analyzer import get_query_analyzer
from exceptions import ElderCompanyException
from middleware.error_handler import (
    elder_company_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


def register_router(app: FastAPI, router_module: str, router_name: str = "router") -> bool:
    """
    Register an optional API router module on the FastAPI app.

    Args:
        app: FastAPI application instance
        router_module: Module path (e.g. 'api.auth_routes')
        router_name: Router attribute name (default: 'router')

    Returns:
        True if registration succeeded, False otherwise
    """
    try:
        module = importlib.import_module(router_module)
        router = getattr(module, router_name)
        app.include_router(router)
        return True
    except ImportError as e:
        logger.log_warning(f"Router module {router_module} not available: {e}", {"router_module": router_module})
        return False
    except AttributeError as e:
        logger.log_warning(f"Router {router_name} not found in {router_module}: {e}", {"router_module": router_module, "router_name": router_name})
        return False


# Import core routers (required)
try:
    from api.organization_routes import router as org_router
    from api.care_terms_routes import router as care_terms_router
    from api.activity_routes import router as activity_router
    from api.activity_enhanced_routes import router as activity_enhanced_router
    from api.auth_routes import router as auth_router
    from api.sync_routes import router as sync_router
    from api.customer_routes import router as customer_router
    from api.task_routes import router as task_router
    from api.schedule_routes import router as schedule_router
    from api.emotion_routes import router as emotion_router
    from api.knowledge_routes import router as knowledge_router
    from api.family_routes import router as family_router
    from api.notification_routes import router as notification_router
    from api.summary_routes import router as summary_router
    from api.family_participation_routes import router as family_participation_router
    from api.emergency_routes import router as emergency_router
    from api.night_mode_routes import router as night_mode_router
    ROUTERS_AVAILABLE = True
except ImportError as e:
    # Fallback if routers not available (for development)
    from fastapi import APIRouter
    org_router = APIRouter()
    care_terms_router = APIRouter()
    activity_router = APIRouter()
    auth_router = APIRouter()
    sync_router = APIRouter()
    customer_router = APIRouter()
    activity_enhanced_router = APIRouter()
    task_router = APIRouter()
    schedule_router = APIRouter()
    emotion_router = APIRouter()
    knowledge_router = APIRouter()
    family_router = APIRouter()
    notification_router = APIRouter()
    summary_router = APIRouter()
    family_participation_router = APIRouter()
    emergency_router = APIRouter()
    night_mode_router = APIRouter()
    ROUTERS_AVAILABLE = False
    logger.log_warning(f"API routers not available: {e}", {"error": str(e)})

from utils.local_paths import ensure_local_dirs, env_file_path

ensure_local_dirs()
load_dotenv(env_file_path())
load_dotenv()

# Initialize database
init_database()

# Use settings for configuration
if settings.test_mode:
    os.environ["TEST_MODE"] = "true"

# Setup query analysis
query_analyzer = setup_query_analysis()

# Initialize task queue
try:
    from services.task_queue import init_task_queue
    init_task_queue()
    logger.log_info("Task queue initialized successfully")
except (ImportError, ValueError) as e:
    logger.log_warning(f"Task queue initialization failed: {e}", {"error": str(e)})
except Exception as e:
    # Log unexpected errors but don't fail startup
    logger.log_error(e, {"action": "task_queue_init"})
    logger.log_warning(f"Task queue initialization failed: {e}", {"error": str(e)})

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Care collaboration platform API — helps caregivers and elders "
        "co-create meaningful activities and communicate effectively."
    ),
    debug=settings.debug
)

# Unified error handlers (frontend expects { error: { message } })
app.add_exception_handler(ElderCompanyException, elder_company_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
if ROUTERS_AVAILABLE:
    core_routers = [
        auth_router,
        sync_router,
        customer_router,
        org_router,
        care_terms_router,
        activity_router,
        activity_enhanced_router,
        task_router,
        schedule_router,
        emotion_router,
        knowledge_router,
        family_router,
        notification_router,
        summary_router,
        family_participation_router,
        emergency_router,
        night_mode_router,
    ]
    for router in core_routers:
        app.include_router(router)

    optional_routers = [
        "api.voice_routes",
        "api.cdn_routes",
        "api.image_optimization_routes",
        "api.web_vitals_routes",
        "api.api_key_routes",
        "api.data_export_routes",
        "api.help_routes",
        "api.feedback_routes",
        "api.data_deletion_routes",
        "api.support_routes",
        "api.payment_routes",
        "api.monitoring_routes",
        "api.analytics_routes",
        "game.backend.game_routes",  # Game API routes
    ]
    
    for router_module in optional_routers:
        register_router(app, router_module)

# Security Headers - Add first to ensure all responses have security headers
from middleware.security_headers import setup_security_headers
app = setup_security_headers(app, environment=settings.environment)

# Performance Monitoring - Add after security headers to track all requests
app.add_middleware(PerformanceMonitoringMiddleware)

# Response Compression - Add before CORS
# Compress responses > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate Limiting
app = setup_rate_limiting(app)

# CORS Configuration
# In production, use strict CORS settings
cors_origins = settings.get_cors_origins_list()

# Security: Never allow wildcard origins
if "*" in cors_origins:
    if settings.is_production():
        raise ValueError(
            "CORS_ORIGINS cannot contain '*' wildcard in production. "
            "This is a security risk. Please specify exact origins."
        )
    else:
        import warnings
        warnings.warn(
            "CORS_ORIGINS contains '*' wildcard. This is INSECURE and will be rejected in production.",
            UserWarning
        )
        # Remove wildcard for development
        cors_origins = [origin for origin in cors_origins if origin != "*"]

if settings.is_production():
    # Production: Only allow configured origins
    if not cors_origins:
        raise ValueError(
            "CORS_ORIGINS must be configured in production. "
            "Please set CORS_ORIGINS environment variable with allowed origins."
        )
    if cors_origins == ["http://localhost:3000", "http://localhost:5173"]:
        raise ValueError(
            "CORS_ORIGINS is set to default localhost origins in production. "
            "This is INSECURE! Please configure proper production origins."
        )
    # Validate that all origins are HTTPS in production
    for origin in cors_origins:
        if origin.startswith("http://") and not origin.startswith("http://localhost"):
            import warnings
            warnings.warn(
                f"CORS origin '{origin}' uses HTTP instead of HTTPS in production. "
                "This is a security risk.",
                UserWarning
            )

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Initialize translation service
try:
    translation_service = TranslationService()
except Exception as e:
    logger.log_warning(
        f"Failed to initialize translation service: {e}",
        {"error": str(e), "message": "Please check your .env file and API keys"}
    )
    translation_service = None


# Request/Response Models
class TranslationRequest(BaseModel):
    text: str
    source_language: str = "ja"
    target_language: str = "en"
    context: Optional[str] = None
    user_id: Optional[str] = None
    org_id: Optional[str] = None


class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    timestamp: str


class ChatMessage(BaseModel):
    message: str
    source_language: str = "ja"
    target_language: str = "en"
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None


class WebVitalsRequest(BaseModel):
    """Web Vitals metrics request payload."""
    metrics: Optional[Dict[str, Any]] = None
    metric: Optional[str] = None
    value: Optional[float] = None
    rating: Optional[str] = None
    allMetrics: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    url: Optional[str] = None
    userAgent: Optional[str] = None
    connection: Optional[Dict[str, Any]] = None


class UserProfileRequest(BaseModel):
    """User profile update request."""
    name: Optional[str] = None
    role: Optional[str] = None
    experience_years: Optional[int] = None
    preferred_source_language: Optional[str] = None
    preferred_target_language: Optional[str] = None
    translation_style: Optional[str] = None  # professional, casual, formal
    detail_level: Optional[str] = None  # brief, moderate, detailed
    use_honorifics: Optional[bool] = None
    care_scenarios: Optional[List[str]] = None
    custom_terms: Optional[Dict[str, str]] = None
    work_shift: Optional[str] = None
    common_tasks: Optional[List[str]] = None
    preferences: Optional[Dict[str, Any]] = None


@app.get("/")
async def root():
    return {
        "message": "Elder Company Care Collaboration Platform API",
        "version": settings.app_version,
        "status": "running",
        "description": (
            "Helps caregivers and elders co-create meaningful activities "
            "and communicate effectively."
        )
    }


@app.get("/health")
async def health_check():
    """Health check endpoint — verifies dependent services."""
    try:
        from services.health_check_service import get_health_check_service
        health_service = get_health_check_service()
        return health_service.get_comprehensive_health()
    except Exception as e:
        # Fallback to simple health check
        provider_status = "available" if translation_service else "unavailable"
        provider_name = os.getenv("AI_PROVIDER", "not_configured")
        
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "service": "translation",
            "provider": provider_name,
            "provider_status": provider_status,
            "error": str(e)
        }


@app.get("/api/metrics")
async def get_metrics():
    """Get performance metrics"""
    from services.cache_service import get_cache
    
    cache_stats = get_cache().get_stats()
    performance_stats = get_performance_stats()
    
    # Add query analysis stats
    query_stats = {}
    if query_analyzer:
        query_stats = query_analyzer.get_stats()
    
    return {
        "cache": cache_stats,
        "performance": performance_stats,
        "queries": query_stats,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/metrics/queries/slow")
async def get_slow_queries(limit: int = 10):
    """Get slow query list"""
    if not query_analyzer:
        return {"message": "Query analyzer not available", "slow_queries": []}
    
    slow_queries = query_analyzer.get_slow_queries(limit=limit)
    return {
        "slow_queries": slow_queries,
        "count": len(slow_queries),
        "threshold": query_analyzer.slow_query_threshold
    }


@app.get("/api/metrics/queries/optimization-report")
async def get_query_optimization_report(limit: int = 20):
    """Get query optimization report"""
    try:
        from services.query_optimizer import get_query_optimizer
        
        if not query_analyzer:
            return {"message": "Query analyzer not available", "report": None}
        
        slow_queries = query_analyzer.get_slow_queries(limit=limit)
        
        optimizer = get_query_optimizer()
        report = optimizer.generate_optimization_report(slow_queries)
        
        return report
    except Exception as e:
        logger.log_error(e, {"action": "get_query_optimization_report"})
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate optimization report: {str(e)}"
        )


@app.get("/api/metrics/queries/analyze/{query_hash}")
async def analyze_query(query_hash: str):
    """Analyze optimization suggestions for a specific query"""
    try:
        from services.query_optimizer import get_query_optimizer
        
        if not query_analyzer:
            raise HTTPException(
                status_code=404,
                detail="Query analyzer not available"
            )
        
        # Find query by stable SHA-256 hash
        slow_queries = query_analyzer.get_slow_queries(limit=1000)
        query_info = None

        for q in slow_queries:
            if q.get("query_hash") == query_hash:
                query_info = q
                break
        
        if not query_info:
            raise HTTPException(status_code=404, detail="Query not found")
        
        optimizer = get_query_optimizer()
        analysis = optimizer.analyze_slow_query(
            statement=query_info.get("statement", ""),
            execution_time=query_info.get("time_taken", 0),
            parameters=query_info.get("parameters")
        )
        
        return {
            "query": query_info,
            "analysis": analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(e, {"action": "analyze_query"})
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze query: {str(e)}"
        )


class QueryRewriteRequest(BaseModel):
    """Query rewrite request"""
    query: str
    execution_time: Optional[float] = None


@app.post("/api/metrics/queries/rewrite")
async def rewrite_query(request: QueryRewriteRequest):
    """Rewrite query to apply optimizations"""
    try:
        from services.query_optimizer import get_query_optimizer
        
        optimizer = get_query_optimizer()
        result = optimizer.rewrite_query(request.query)
        
        return result
    except Exception as e:
        logger.log_error(e, {"action": "rewrite_query"})
        raise HTTPException(
            status_code=500,
            detail=f"Failed to rewrite query: {str(e)}"
        )


@app.post("/api/metrics/queries/auto-optimize")
async def auto_optimize_query(request: QueryRewriteRequest):
    """Auto-optimize query (analyze + rewrite)"""
    try:
        from services.query_optimizer import get_query_optimizer
        
        optimizer = get_query_optimizer()
        result = optimizer.auto_optimize_query(
            statement=request.query,
            execution_time=request.execution_time
        )
        
        return result
    except Exception as e:
        logger.log_error(e, {"action": "auto_optimize_query"})
        raise HTTPException(
            status_code=500,
            detail=f"Failed to auto-optimize query: {str(e)}"
        )


@app.get("/api/ai/provider")
async def get_ai_provider_info():
    """Get current AI provider information"""
    provider_name = os.getenv("AI_PROVIDER", "openai").lower()
    provider_status = "available" if translation_service else "unavailable"
    
    return {
        "provider": provider_name,
        "status": provider_status,
        "supported_providers": ["openai", "claude", "gemini"]
    }


@app.post("/api/translate", response_model=TranslationResponse)
@rate_limit(limit=RATE_LIMITS["translation"])
async def translate(
    http_request: Request,
    request: TranslationRequest,
    db: Session = Depends(get_db),
):
    """
    Translate text with optional user/org personalization and care-scenario context.
    """
    start_time = time.time()
    
    # Input validation and sanitization
    from utils.security import sanitize_input
    sanitized_text = sanitize_input(request.text, max_length=10000)  # Max 10k characters
    if not sanitized_text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # NSFW detection - check input text
    from services.nsfw_detector import get_nsfw_detector
    nsfw_detector = get_nsfw_detector()
    nsfw_result = await nsfw_detector.check(
        sanitized_text, language=request.source_language
    )
    
    if nsfw_detector.should_block(nsfw_result):
        logger.log_warning(
            f"NSFW content blocked in translation request",
            {
                "text_preview": sanitized_text[:50],
                "level": nsfw_result.get("level"),
                "reason": nsfw_result.get("reason")
            }
        )
        raise HTTPException(
            status_code=400,
            detail=nsfw_detector.get_block_message(
                request.source_language or "en"
            )
        )
    
    if not translation_service:
        raise HTTPException(
            status_code=503,
            detail=(
                "Translation service not available. "
                "Please check API configuration."
            )
        )
    
    if request.org_id:
        org_service = OrganizationService(db)
        can_translate, error_msg = org_service.check_translation_limit(
            request.org_id
        )
        if not can_translate:
            raise HTTPException(status_code=403, detail=error_msg)
    
    try:
        org_context = None
        if request.org_id:
            org_service = OrganizationService(db)
            org_context = org_service.get_organization(request.org_id)
            if not org_context:
                raise HTTPException(
                    status_code=404,
                    detail="Organization not found"
                )
        
        personalization = None
        if request.user_id:
            user_service = UserService(db)
            personalization = user_service.get_personalization_context(
                request.user_id,
                org_context=org_context
            )
        elif org_context:
            personalization = {
                "translation_style": "professional",
                "detail_level": "moderate",
                "use_honorifics": True,
                "care_scenarios": org_context.get("org_care_scenarios", []),
                "custom_terms": org_context.get("org_custom_terms", {}),
            }
        
        result = await translation_service.translate(
            text=sanitized_text,
            source_language=request.source_language,
            target_language=request.target_language,
            context=request.context,
            personalization=personalization
        )
        
        translation_time_ms = int((time.time() - start_time) * 1000)
        
        if request.user_id or request.org_id:
            user_service = UserService(db)
            user_service.save_translation_history(
                user_id=request.user_id or "anonymous",
                original_text=result["original_text"],
                translated_text=result["translated_text"],
                source_language=result["source_language"],
                target_language=result["target_language"],
                context=request.context,
                org_id=request.org_id,
                text_length=len(sanitized_text),
                translation_time_ms=translation_time_ms,
                provider=result.get("provider", "unknown")
            )
            
            if request.org_id:
                org_service = OrganizationService(db)
                org_service.record_translation(
                    org_id=request.org_id,
                    user_id=request.user_id or "anonymous",
                    text_length=len(sanitized_text),
                    translation_time_ms=translation_time_ms,
                    source_language=result["source_language"],
                    target_language=result["target_language"]
                )
        
        logger.log_translation(
            user_id=request.user_id or "anonymous",
            org_id=request.org_id,
            source_lang=result["source_language"],
            target_lang=result["target_language"],
            text_length=len(sanitized_text),
            translation_time_ms=translation_time_ms,
            success=True
        )
        
        return TranslationResponse(
            original_text=result["original_text"],
            translated_text=result["translated_text"],
            source_language=result["source_language"],
            target_language=result["target_language"],
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.log_translation(
            user_id=request.user_id or "anonymous",
            org_id=request.org_id,
            source_lang=request.source_language,
            target_lang=request.target_language,
            text_length=len(sanitized_text) if 'sanitized_text' in locals() else 0,
            translation_time_ms=int((time.time() - start_time) * 1000),
            success=False,
            error=str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))
    except (ConnectionError, TimeoutError) as e:
        # Network-related errors
        from exceptions import ServiceUnavailableError
        logger.log_error(e, {
            "action": "translate",
            "user_id": request.user_id,
            "org_id": request.org_id,
            "error_type": "network_error"
        })
        raise ServiceUnavailableError(
            service="Translation Service",
            details={"error": str(e)}
        )
    except Exception as e:
        # Catch-all for unexpected errors
        from exceptions import TranslationError
        logger.log_error(e, {
            "action": "translate",
            "user_id": request.user_id,
            "org_id": request.org_id
        })
        raise TranslationError(
            message=f"Translation failed: {str(e)}",
            details={"error": str(e)}
        )


@app.post("/api/chat")
async def chat(message: ChatMessage, db: Session = Depends(get_db)):
    """Translate a chat message with optional conversation history and personalization."""
    # Input validation and sanitization
    from utils.security import sanitize_input
    sanitized_message = sanitize_input(message.message, max_length=10000)  # Max 10k characters
    if not sanitized_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # NSFW detection - check input message
    from services.nsfw_detector import get_nsfw_detector
    nsfw_detector = get_nsfw_detector()
    nsfw_result = await nsfw_detector.check(
        sanitized_message, language=message.source_language
    )
    
    if nsfw_detector.should_block(nsfw_result):
        logger.log_warning(
            f"NSFW content blocked in chat request",
            {
                "message_preview": sanitized_message[:50],
                "level": nsfw_result.get("level"),
                "reason": nsfw_result.get("reason")
            }
        )
        raise HTTPException(
            status_code=400,
            detail=nsfw_detector.get_block_message(
                message.source_language or "en"
            )
        )
    
    if not translation_service:
        raise HTTPException(
            status_code=503,
            detail=(
                "Translation service not available. "
                "Please check API configuration."
            )
        )
    
    try:
        personalization = None
        conversation_history = None
        if message.user_id:
            user_service = UserService(db)
            personalization = user_service.get_personalization_context(message.user_id)
            history = user_service.get_translation_history(message.user_id, limit=5)
            conversation_history = [
                {"original": h["original_text"], "translated": h["translated_text"]}
                for h in history
            ]

        result = await translation_service.translate_conversation(
            message=sanitized_message,
            source_language=message.source_language,
            target_language=message.target_language,
            conversation_history=conversation_history,
            personalization=personalization,
        )

        if message.user_id:
            user_service = UserService(db)
            user_service.save_translation_history(
                user_id=message.user_id,
                original_text=result["original_text"],
                translated_text=result["translated_text"],
                source_language=result["source_language"],
                target_language=result["target_language"],
                context=None
            )
        
        return {
            "message": result["translated_text"],
            "original_message": result["original_text"],
            "source_language": result["source_language"],
            "target_language": result["target_language"],
            "provider": result.get("provider", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.get("/api/languages")
async def get_supported_languages():
    """Get supported language list"""
    return {
        "languages": [
            {"code": "ja", "name": "日本語", "name_en": "Japanese"},
            {"code": "en", "name": "English", "name_en": "English"},
        ]
    }


@app.get("/api/terms")
async def get_care_terms():
    """Get common care terms (migrated to /api/care-terms)"""
    from services.care_terms_service import CareTermsService
    service = CareTermsService()
    return {
        "terms": service.get_all_terms(),
        "message": "This endpoint is deprecated. Please use /api/care-terms instead."
    }


# User Profile Endpoints
@app.get("/api/user/{user_id}/profile")
async def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """Get user personal configuration"""
    try:
        user_service = UserService(db)
        profile = user_service.get_user_profile(user_id)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")


@app.post("/api/user/{user_id}/profile")
async def update_user_profile(
    user_id: str,
    profile_data: UserProfileRequest,
    db: Session = Depends(get_db)
):
    """Update user personal configuration"""
    try:
        user_service = UserService(db)
        
        # Convert Pydantic model to dict
        update_data = profile_data.dict(exclude_unset=True)
        
        profile = user_service.update_user_profile(user_id, update_data)
        
        return {
            "message": "User profile updated successfully",
            "profile": profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user profile: {str(e)}")


@app.get("/api/user/{user_id}/history")
async def get_translation_history(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user translation history"""
    try:
        user_service = UserService(db)
        history = user_service.get_translation_history(user_id, limit=limit)
        return {
            "user_id": user_id,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get translation history: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
