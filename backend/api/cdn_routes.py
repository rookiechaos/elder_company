"""
CDN API Routes
CDN API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

from services.cdn_service import get_cdn_service
from services.logging_service import logger

router = APIRouter(prefix="/api/cdn", tags=["cdn"])


class CDNUrlRequest(BaseModel):
    """CDN URL request"""
    path: str
    version: Optional[str] = None


class BatchCDNUrlRequest(BaseModel):
    """Batch CDN URL request"""
    paths: List[str]
    version: Optional[str] = None


@router.get("/config")
async def get_cdn_config():
    """Get CDN configuration"""
    try:
        cdn_service = get_cdn_service()
        return cdn_service.get_config()
    except Exception as e:
        logger.log_error(e, {"action": "get_cdn_config"})
        raise HTTPException(status_code=500, detail=f"Failed to get CDN config: {str(e)}")


@router.post("/url")
async def get_cdn_url(request: CDNUrlRequest):
    """Get CDN URL for a single resource"""
    try:
        cdn_service = get_cdn_service()
        url = cdn_service.get_image_url(request.path, request.version)
        return {
            "url": url,
            "original_path": request.path,
            "cdn_enabled": cdn_service.is_enabled()
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_cdn_url"})
        raise HTTPException(status_code=500, detail=f"Failed to get CDN URL: {str(e)}")


@router.post("/urls/batch")
async def get_batch_cdn_urls(request: BatchCDNUrlRequest):
    """Batch get CDN URLs"""
    try:
        cdn_service = get_cdn_service()
        urls = {}
        for path in request.paths:
            urls[path] = cdn_service.get_image_url(path, request.version)
        
        return {
            "urls": urls,
            "count": len(urls),
            "cdn_enabled": cdn_service.is_enabled()
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_batch_cdn_urls"})
        raise HTTPException(status_code=500, detail=f"Failed to get batch CDN URLs: {str(e)}")


@router.get("/url")
async def get_cdn_url_query(
    path: str = Query(..., description="Resource path"),
    version: Optional[str] = Query(None, description="Version number (for cache busting)")
):
    """Get CDN URL via query parameters"""
    try:
        cdn_service = get_cdn_service()
        url = cdn_service.get_image_url(path, version)
        return {
            "url": url,
            "original_path": path,
            "cdn_enabled": cdn_service.is_enabled()
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_cdn_url_query"})
        raise HTTPException(status_code=500, detail=f"Failed to get CDN URL: {str(e)}")
