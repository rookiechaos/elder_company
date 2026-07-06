"""
Performance Monitoring Middleware - Track API performance metrics

"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from services.logging_service import logger
from collections import defaultdict
from datetime import datetime
from utils.time_utils import utc_now
import json


class PerformanceMetrics:
    """Performance metrics collector"""
    
    def __init__(self):
        self.metrics = {
            "request_count": 0,
            "total_response_time": 0,
            "endpoint_times": defaultdict(list),
            "slow_queries": [],  # Queries > 1 second
            "error_count": 0,
            "status_codes": defaultdict(int)
        }
    
    def record_request(
        self,
        endpoint: str,
        method: str,
        response_time: float,
        status_code: int
    ):
        """Record a request metric"""
        self.metrics["request_count"] += 1
        self.metrics["total_response_time"] += response_time
        self.metrics["endpoint_times"][f"{method} {endpoint}"].append(response_time)
        self.metrics["status_codes"][status_code] += 1
        
        # Track slow queries
        if response_time > 1.0:
            self.metrics["slow_queries"].append({
                "endpoint": endpoint,
                "method": method,
                "response_time": response_time,
                "timestamp": utc_now().isoformat()
            })
            # Keep only last 100 slow queries
            if len(self.metrics["slow_queries"]) > 100:
                self.metrics["slow_queries"] = self.metrics["slow_queries"][-100:]
        
        if status_code >= 400:
            self.metrics["error_count"] += 1
    
    def get_stats(self) -> dict:
        """Get performance statistics"""
        request_count = self.metrics["request_count"]
        avg_response_time = (
            self.metrics["total_response_time"] / request_count
            if request_count > 0 else 0
        )
        
        # Calculate endpoint averages
        endpoint_averages = {}
        for endpoint, times in self.metrics["endpoint_times"].items():
            if times:
                endpoint_averages[endpoint] = {
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "count": len(times)
                }
        
        return {
            "request_count": request_count,
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "error_count": self.metrics["error_count"],
            "error_rate": round(
                (self.metrics["error_count"] / request_count * 100) if request_count > 0 else 0,
                2
            ),
            "status_codes": dict(self.metrics["status_codes"]),
            "endpoint_averages": endpoint_averages,
            "slow_queries_count": len(self.metrics["slow_queries"]),
            "recent_slow_queries": self.metrics["slow_queries"][-10:]  # Last 10
        }
    
    def reset(self):
        """Reset metrics"""
        self.metrics = {
            "request_count": 0,
            "total_response_time": 0,
            "endpoint_times": defaultdict(list),
            "slow_queries": [],
            "error_count": 0,
            "status_codes": defaultdict(int)
        }


# Global metrics instance
performance_metrics = PerformanceMetrics()


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor API performance"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Skip monitoring for health checks and metrics endpoints
        if request.url.path in ["/health", "/metrics", "/api/metrics"]:
            return await call_next(request)
        
        try:
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Record metrics
            performance_metrics.record_request(
                endpoint=request.url.path,
                method=request.method,
                response_time=response_time,
                status_code=response.status_code
            )
            
            # Log query count for endpoint
            try:
                from services.query_analyzer import get_query_analyzer
                query_analyzer = get_query_analyzer()
                if query_analyzer:
                    query_analyzer.log_query_for_endpoint(request.url.path)
            except Exception:
                pass  # Ignore errors in query analyzer
            
            # Log slow queries
            if response_time > 1.0:
                logger.logger.warning(
                    f"Slow query detected: {request.method} {request.url.path} "
                    f"took {response_time:.2f}s"
                )
            
            # Add performance headers
            response.headers["X-Response-Time"] = f"{response_time:.3f}"
            
            return response
            
        except Exception as e:
            response_time = time.time() - start_time
            performance_metrics.record_request(
                endpoint=request.url.path,
                method=request.method,
                response_time=response_time,
                status_code=500
            )
            raise


def get_performance_stats() -> dict:
    """Get current performance statistics"""
    return performance_metrics.get_stats()


def reset_performance_stats():
    """Reset performance statistics"""
    performance_metrics.reset()
