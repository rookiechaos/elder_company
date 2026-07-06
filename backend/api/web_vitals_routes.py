"""
Web Vitals API Routes - History and analytics
Web Vitals API Routes - Historical data and analytics
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from utils.time_utils import utc_now

from services.logging_service import logger
from services.web_vitals_alert import get_web_vitals_alert_service
from config.database import get_db

router = APIRouter(prefix="/api/metrics", tags=["web-vitals"])


class WebVitalsData(BaseModel):
    """Web Vitals data model"""
    lcp: Optional[float] = None
    fid: Optional[float] = None
    cls: Optional[float] = None
    fcp: Optional[float] = None
    ttfb: Optional[float] = None
    tti: Optional[float] = None
    timestamp: Optional[str] = None
    url: Optional[str] = None
    user_agent: Optional[str] = None


# In-memory storage for Web Vitals data (in production, use database)
web_vitals_storage: List[Dict[str, Any]] = []


@router.post("/web-vitals")
async def receive_web_vitals(data: Dict[str, Any]):
    """Receive Web Vitals reports from the frontend (existing endpoint, extended)."""
    try:
        # Extract metrics from data
        metrics_dict = {}
        if "metrics" in data:
            # Handle structured metrics
            for metric_name, metric_data in data["metrics"].items():
                if isinstance(metric_data, dict) and "value" in metric_data:
                    metrics_dict[metric_name] = metric_data["value"]
                elif isinstance(metric_data, (int, float)):
                    metrics_dict[metric_name] = metric_data
        elif "allMetrics" in data:
            # Handle allMetrics format
            for metric_name, metric_data in data["allMetrics"].items():
                if isinstance(metric_data, dict) and "value" in metric_data:
                    metrics_dict[metric_name] = metric_data["value"]
        
        # Check for alerts
        if metrics_dict:
            alert_service = get_web_vitals_alert_service()
            alert_result = alert_service.check_metrics(metrics_dict)
            
            # Add alert info to stored data
            data["alert_checked"] = True
            data["alerts"] = alert_result.get("alerts", [])
        
        # Store the data
        web_vitals_storage.append({
            **data,
            "received_at": utc_now().isoformat()
        })
        
        # Keep only last 10000 records
        if len(web_vitals_storage) > 10000:
            web_vitals_storage[:] = web_vitals_storage[-10000:]
        
        logger.log_info("Web Vitals data received", data)
        return {
            "message": "Web Vitals data received successfully",
            "alerts_triggered": len(data.get("alerts", []))
        }
    except Exception as e:
        logger.log_error(e, {"action": "receive_web_vitals"})
        raise HTTPException(status_code=500, detail=f"Failed to receive Web Vitals: {str(e)}")


@router.get("/web-vitals/history")
async def get_web_vitals_history(
    days: int = Query(7, description="Number of days to query"),
    metric: Optional[str] = Query(None, description="Metric type (lcp, fid, cls, etc.)"),
    db: Session = Depends(get_db)
):
    """Get Web Vitals historical data"""
    try:
        cutoff_date = utc_now() - timedelta(days=days)
        
        # Filter data by date
        filtered_data = [
            item for item in web_vitals_storage
            if datetime.fromisoformat(item.get("timestamp", item.get("received_at", ""))) >= cutoff_date
        ]
        
        # Extract metrics
        metrics = []
        for item in filtered_data:
            metric_data = {
                "date": item.get("timestamp") or item.get("received_at"),
                "lcp": item.get("metrics", {}).get("LCP", {}).get("value") or item.get("lcp"),
                "fid": item.get("metrics", {}).get("FID", {}).get("value") or item.get("fid"),
                "cls": item.get("metrics", {}).get("CLS", {}).get("value") or item.get("cls"),
                "fcp": item.get("metrics", {}).get("FCP", {}).get("value") or item.get("fcp"),
                "ttfb": item.get("metrics", {}).get("TTFB", {}).get("value") or item.get("ttfb"),
                "url": item.get("url"),
            }
            
            # Filter by metric if specified
            if metric and metric_data.get(metric) is None:
                continue
            
            metrics.append(metric_data)
        
        # Sort by date
        metrics.sort(key=lambda x: x["date"])
        
        return {
            "metrics": metrics,
            "count": len(metrics),
            "days": days,
            "date_range": {
                "from": cutoff_date.isoformat(),
                "to": utc_now().isoformat()
            }
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_web_vitals_history"})
        raise HTTPException(status_code=500, detail=f"Failed to get Web Vitals history: {str(e)}")


@router.get("/web-vitals/summary")
async def get_web_vitals_summary(
    days: int = Query(7, description="Number of days to query"),
    db: Session = Depends(get_db)
):
    """Get Web Vitals aggregate statistics"""
    try:
        cutoff_date = utc_now() - timedelta(days=days)
        
        filtered_data = [
            item for item in web_vitals_storage
            if datetime.fromisoformat(item.get("timestamp", item.get("received_at", ""))) >= cutoff_date
        ]
        
        # Calculate statistics
        lcp_values = []
        fid_values = []
        cls_values = []
        fcp_values = []
        ttfb_values = []
        
        for item in filtered_data:
            metrics = item.get("metrics", {})
            if metrics.get("LCP", {}).get("value"):
                lcp_values.append(metrics["LCP"]["value"])
            if metrics.get("FID", {}).get("value"):
                fid_values.append(metrics["FID"]["value"])
            if metrics.get("CLS", {}).get("value"):
                cls_values.append(metrics["CLS"]["value"])
            if metrics.get("FCP", {}).get("value"):
                fcp_values.append(metrics["FCP"]["value"])
            if metrics.get("TTFB", {}).get("value"):
                ttfb_values.append(metrics["TTFB"]["value"])
        
        def calculate_stats(values):
            if not values:
                return None
            return {
                "count": len(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "p50": sorted(values)[len(values) // 2] if values else None,
                "p95": sorted(values)[int(len(values) * 0.95)] if values else None
            }
        
        return {
            "lcp": calculate_stats(lcp_values),
            "fid": calculate_stats(fid_values),
            "cls": calculate_stats(cls_values),
            "fcp": calculate_stats(fcp_values),
            "ttfb": calculate_stats(ttfb_values),
            "total_samples": len(filtered_data),
            "date_range": {
                "from": cutoff_date.isoformat(),
                "to": utc_now().isoformat()
            }
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_web_vitals_summary"})
        raise HTTPException(status_code=500, detail=f"Failed to get Web Vitals summary: {str(e)}")


@router.get("/web-vitals/alerts/history")
async def get_web_vitals_alert_history(
    limit: int = Query(100, description="Number of results to return")
):
    """Get Web Vitals alert history"""
    try:
        alert_service = get_web_vitals_alert_service()
        history = alert_service.get_alert_history(limit=limit)
        return {
            "alerts": history,
            "count": len(history)
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_web_vitals_alert_history"})
        raise HTTPException(status_code=500, detail=f"Failed to get alert history: {str(e)}")


@router.get("/web-vitals/thresholds")
async def get_web_vitals_thresholds():
    """Get Web Vitals alert threshold configuration"""
    try:
        alert_service = get_web_vitals_alert_service()
        thresholds = alert_service.get_thresholds()
        return {
            "thresholds": thresholds,
            "configurable": True
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_web_vitals_thresholds"})
        raise HTTPException(status_code=500, detail=f"Failed to get thresholds: {str(e)}")


@router.post("/web-vitals/thresholds")
async def update_web_vitals_thresholds(
    metric: str,
    thresholds: Dict[str, float]
):
    """Update Web Vitals alert thresholds"""
    try:
        alert_service = get_web_vitals_alert_service()
        alert_service.update_thresholds(metric, thresholds)
        return {
            "message": f"Thresholds updated for {metric}",
            "metric": metric,
            "thresholds": alert_service.get_thresholds()[metric]
        }
    except Exception as e:
        logger.log_error(e, {"action": "update_web_vitals_thresholds"})
        raise HTTPException(status_code=500, detail=f"Failed to update thresholds: {str(e)}")
