"""
Query Analyzer Service - SQLAlchemy query logging and slow query detection
"""

import time
import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import Pool

from services.logging_service import logger
from utils.time_utils import utc_now
from utils.hash_utils import query_statement_hash


class QueryAnalyzer:
    """Query analyzer for SQLAlchemy queries"""
    
    def __init__(self, slow_query_threshold: float = 1.0):
        """
        Initialize query analyzer
        
        Args:
            slow_query_threshold: Threshold in seconds for slow queries (default: 1.0)
        """
        self.slow_query_threshold = slow_query_threshold
        self.query_stats = {
            "total_queries": 0,
            "slow_queries": [],
            "query_times": [],
            "query_counts_by_endpoint": defaultdict(int),
            "query_types": defaultdict(int)
        }
        self._enabled = True
    
    def enable(self):
        """Enable query analysis"""
        self._enabled = True
    
    def disable(self):
        """Disable query analysis"""
        self._enabled = False
    
    def setup_listeners(self, engine: Engine):
        """Setup SQLAlchemy event listeners"""
        @event.listens_for(engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Record query start time"""
            conn.info.setdefault('query_start_time', []).append(time.time())
        
        @event.listens_for(engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Record query execution time and log slow queries"""
            if not self._enabled:
                return
            
            total = conn.info.get('query_start_time', [])
            if total:
                query_start_time = total.pop(-1)
                query_time = time.time() - query_start_time
                
                # Record query
                self.query_stats["total_queries"] += 1
                self.query_stats["query_times"].append(query_time)
                
                # Keep only last 1000 query times
                if len(self.query_stats["query_times"]) > 1000:
                    self.query_stats["query_times"] = self.query_stats["query_times"][-1000:]
                
                # Detect slow queries
                if query_time > self.slow_query_threshold:
                    slow_query_info = {
                        "statement": statement[:200] if len(statement) > 200 else statement,
                        "parameters": str(parameters)[:200] if parameters else None,
                        "query_time": round(query_time, 3),
                        "time_taken": query_time,
                        "timestamp": utc_now().isoformat(),
                        "query_type": self._get_query_type(statement),
                        "query_hash": query_statement_hash(statement),
                    }
                    
                    # Analyze and generate optimization suggestions
                    try:
                        from services.query_optimizer import get_query_optimizer
                        optimizer = get_query_optimizer()
                        analysis = optimizer.analyze_slow_query(
                            statement=statement,
                            execution_time=query_time,
                            parameters=parameters
                        )
                        slow_query_info["optimization"] = analysis
                    except Exception as e:
                        # Don't fail if optimization analysis fails
                        print(f"Failed to analyze slow query: {e}")
                    
                    self.query_stats["slow_queries"].append(slow_query_info)
                    
                    # Keep only last 100 slow queries
                    if len(self.query_stats["slow_queries"]) > 100:
                        self.query_stats["slow_queries"] = self.query_stats["slow_queries"][-100:]
                    
                    # Log slow query warning
                    logger.logger.warning(
                        f"Slow query detected: {query_time:.3f}s - {slow_query_info['query_type']}",
                        extra={
                            "query_time": query_time,
                            "query_type": slow_query_info["query_type"],
                            "statement_preview": slow_query_info["statement"][:100]
                        }
                    )
                
                # Track query types
                query_type = self._get_query_type(statement)
                self.query_stats["query_types"][query_type] += 1
    
    def _get_query_type(self, statement: str) -> str:
        """Extract query type from SQL statement"""
        statement_upper = statement.strip().upper()
        if statement_upper.startswith("SELECT"):
            return "SELECT"
        elif statement_upper.startswith("INSERT"):
            return "INSERT"
        elif statement_upper.startswith("UPDATE"):
            return "UPDATE"
        elif statement_upper.startswith("DELETE"):
            return "DELETE"
        else:
            return "OTHER"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get query statistics"""
        query_times = self.query_stats["query_times"]
        
        stats = {
            "total_queries": self.query_stats["total_queries"],
            "slow_queries_count": len(self.query_stats["slow_queries"]),
            "slow_query_threshold": self.slow_query_threshold,
            "query_types": dict(self.query_stats["query_types"]),
            "query_counts_by_endpoint": dict(self.query_stats["query_counts_by_endpoint"])
        }
        
        if query_times:
            stats["avg_query_time"] = round(sum(query_times) / len(query_times), 3)
            stats["min_query_time"] = round(min(query_times), 3)
            stats["max_query_time"] = round(max(query_times), 3)
            stats["p50_query_time"] = round(sorted(query_times)[len(query_times) // 2], 3)
            stats["p95_query_time"] = round(sorted(query_times)[int(len(query_times) * 0.95)], 3)
            stats["p99_query_time"] = round(sorted(query_times)[int(len(query_times) * 0.99)], 3)
        else:
            stats["avg_query_time"] = 0
            stats["min_query_time"] = 0
            stats["max_query_time"] = 0
            stats["p50_query_time"] = 0
            stats["p95_query_time"] = 0
            stats["p99_query_time"] = 0
        
        return stats
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent slow queries"""
        return self.query_stats["slow_queries"][-limit:]
    
    def reset_stats(self):
        """Reset query statistics"""
        self.query_stats = {
            "total_queries": 0,
            "slow_queries": [],
            "query_times": [],
            "query_counts_by_endpoint": defaultdict(int),
            "query_types": defaultdict(int)
        }
    
    def log_query_for_endpoint(self, endpoint: str):
        """Increment query count for an endpoint"""
        self.query_stats["query_counts_by_endpoint"][endpoint] += 1


# Global query analyzer instance
_query_analyzer: Optional[QueryAnalyzer] = None


def get_query_analyzer(slow_query_threshold: float = 1.0) -> QueryAnalyzer:
    """Get global query analyzer instance"""
    global _query_analyzer
    if _query_analyzer is None:
        _query_analyzer = QueryAnalyzer(slow_query_threshold=slow_query_threshold)
    return _query_analyzer


def setup_query_analysis(engine: Engine, slow_query_threshold: float = 1.0):
    """Setup query analysis for SQLAlchemy engine"""
    analyzer = get_query_analyzer(slow_query_threshold)
    analyzer.setup_listeners(engine)
    return analyzer
