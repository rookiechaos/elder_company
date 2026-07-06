"""
Query Optimizer Service - Automatic query optimization and suggestions
"""

import re
from typing import Dict, Any, Optional, List
from collections import defaultdict
from datetime import datetime
from utils.time_utils import utc_now


class QueryOptimizer:
    """Service for query optimization and suggestions"""
    
    def __init__(self):
        self.optimization_suggestions: List[Dict[str, Any]] = []
        self.index_suggestions: List[Dict[str, Any]] = []
    
    def analyze_slow_query(
        self,
        statement: str,
        execution_time: float,
        parameters: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze a slow query and generate optimization suggestions
        
        Args:
            statement: SQL statement
            execution_time: Query execution time in seconds
            parameters: Query parameters
        
        Returns:
            Dict with analysis and suggestions
        """
        analysis = {
            "statement": statement,
            "execution_time": execution_time,
            "suggestions": [],
            "index_suggestions": [],
            "optimization_score": 0
        }
        
        # Extract query type
        query_type = self._get_query_type(statement)
        analysis["query_type"] = query_type
        
        # Analyze SELECT queries
        if query_type == "SELECT":
            suggestions = self._analyze_select_query(statement)
            analysis["suggestions"].extend(suggestions)
            
            # Index suggestions
            index_suggestions = self._suggest_indexes(statement)
            analysis["index_suggestions"].extend(index_suggestions)
        
        # Analyze JOIN queries
        if "JOIN" in statement.upper():
            join_suggestions = self._analyze_join_query(statement)
            analysis["suggestions"].extend(join_suggestions)
        
        # Analyze WHERE clauses
        where_suggestions = self._analyze_where_clause(statement)
        analysis["suggestions"].extend(where_suggestions)
        
        # Calculate optimization score
        analysis["optimization_score"] = self._calculate_optimization_score(analysis)
        
        return analysis
    
    def _get_query_type(self, statement: str) -> str:
        """
        Extract query type from SQL statement.
        
        Args:
            statement: SQL statement string
            
        Returns:
            Query type: "SELECT", "INSERT", "UPDATE", "DELETE", or "OTHER"
        """
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
    
    def _analyze_select_query(self, statement: str) -> List[Dict[str, Any]]:
        """Analyze SELECT query for optimization opportunities"""
        suggestions = []
        statement_upper = statement.upper()
        
        # Check for SELECT *
        if re.search(r'SELECT\s+\*', statement, re.IGNORECASE):
            suggestions.append({
                "type": "select_all",
                "severity": "medium",
                "message": "Avoid SELECT *; specify only needed columns",
                "suggestion": "List required column names to reduce data transfer",
                "impact": "Reduces network transfer and memory use"
            })
        
        # Check for missing LIMIT
        if "LIMIT" not in statement_upper and "TOP" not in statement_upper:
            if "COUNT" not in statement_upper:  # COUNT queries don't need LIMIT
                suggestions.append({
                    "type": "missing_limit",
                    "severity": "high",
                    "message": "Query missing LIMIT clause",
                    "suggestion": "Add LIMIT to cap returned rows",
                    "impact": "Prevents oversized result sets and improves performance"
                })
        
        # Check for ORDER BY without index
        if "ORDER BY" in statement_upper:
            suggestions.append({
                "type": "order_by_optimization",
                "severity": "medium",
                "message": "ORDER BY may need index support",
                "suggestion": "Create index on ORDER BY columns",
                "impact": "Improves sort performance"
            })
        
        return suggestions
    
    def _analyze_join_query(self, statement: str) -> List[Dict[str, Any]]:
        """
        Analyze JOIN query for optimization opportunities.
        
        Args:
            statement: SQL statement string
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        statement_upper = statement.upper()
        
        # Check for multiple JOINs
        join_count = statement_upper.count("JOIN")
        if join_count > 3:
            suggestions.append({
                "type": "too_many_joins",
                "severity": "medium",
                "message": f"Query contains {join_count} JOINs; may hurt performance",
                "suggestion": "Consider subqueries or materialized views",
                "impact": "Reduces join complexity and improves speed"
            })
        
        # Check for missing JOIN conditions
        if "JOIN" in statement_upper and "ON" not in statement_upper:
            suggestions.append({
                "type": "missing_join_condition",
                "severity": "high",
                "message": "JOIN missing ON clause",
                "suggestion": "Add appropriate JOIN conditions",
                "impact": "Avoids cartesian products and improves efficiency"
            })
        
        return suggestions
    
    def _analyze_where_clause(self, statement: str) -> List[Dict[str, Any]]:
        """
        Analyze WHERE clause for optimization opportunities.
        
        Args:
            statement: SQL statement string
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        # Extract WHERE clause
        where_match = re.search(r'WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)', statement, re.IGNORECASE | re.DOTALL)
        if not where_match:
            return suggestions
        
        where_clause = where_match.group(1)
        
        # Check for functions in WHERE clause
        if re.search(r'\w+\s*\([^)]*\)', where_clause):
            suggestions.append({
                "type": "function_in_where",
                "severity": "medium",
                "message": "Functions in WHERE may prevent index use",
                "suggestion": "Move functions to app layer or use computed columns",
                "impact": "Enables index use and improves query performance"
            })
        
        # Check for LIKE with leading wildcard
        if re.search(r'LIKE\s+[\'"]%', where_clause, re.IGNORECASE):
            suggestions.append({
                "type": "leading_wildcard",
                "severity": "high",
                "message": "Leading-wildcard LIKE cannot use indexes",
                "suggestion": "Avoid leading wildcards or use full-text search",
                "impact": "Enables indexes and greatly improves performance"
            })
        
        # Check for OR conditions
        if re.search(r'\s+OR\s+', where_clause, re.IGNORECASE):
            suggestions.append({
                "type": "or_condition",
                "severity": "low",
                "message": "OR in WHERE may reduce index use",
                "suggestion": "Consider UNION or separate queries",
                "impact": "Improves index utilization"
            })
        
        return suggestions
    
    def _suggest_indexes(self, statement: str) -> List[Dict[str, Any]]:
        """
        Suggest database indexes for a query.
        
        Args:
            statement: SQL statement string
            
        Returns:
            List of index suggestions with SQL statements
        """
        suggestions = []
        
        # Extract table names
        table_match = re.search(r'FROM\s+(\w+)', statement, re.IGNORECASE)
        if not table_match:
            return suggestions
        
        table_name = table_match.group(1)
        
        # Extract WHERE columns
        where_match = re.search(r'WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)', statement, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1)
            # Extract column names from WHERE
            columns = re.findall(r'(\w+)\s*[=<>!]', where_clause)
            if columns:
                suggestions.append({
                    "type": "where_index",
                    "table": table_name,
                    "columns": columns,
                    "suggestion": f"Create index on {table_name}({', '.join(columns)})",
                    "sql": f"CREATE INDEX idx_{table_name}_{'_'.join(columns)} ON {table_name}({', '.join(columns)})",
                    "priority": "high"
                })
        
        # Extract ORDER BY columns
        order_match = re.search(r'ORDER\s+BY\s+(\w+)', statement, re.IGNORECASE)
        if order_match:
            order_column = order_match.group(1)
            suggestions.append({
                "type": "order_by_index",
                "table": table_name,
                "columns": [order_column],
                "suggestion": f"Create index on {table_name}({order_column}) to optimize sorting",
                "sql": f"CREATE INDEX idx_{table_name}_{order_column} ON {table_name}({order_column})",
                "priority": "medium"
            })
        
        # Extract JOIN columns
        join_matches = re.findall(r'JOIN\s+\w+\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', statement, re.IGNORECASE)
        for match in join_matches:
            table1, col1, table2, col2 = match
            suggestions.append({
                "type": "join_index",
                "table": table1,
                "columns": [col1],
                "suggestion": f"Create index on {table1}({col1}) to optimize JOIN",
                "sql": f"CREATE INDEX idx_{table1}_{col1} ON {table1}({col1})",
                "priority": "high"
            })
            suggestions.append({
                "type": "join_index",
                "table": table2,
                "columns": [col2],
                "suggestion": f"Create index on {table2}({col2}) to optimize JOIN",
                "sql": f"CREATE INDEX idx_{table2}_{col2} ON {table2}({col2})",
                "priority": "high"
            })
        
        return suggestions
    
    def _calculate_optimization_score(self, analysis: Dict[str, Any]) -> int:
        """
        Calculate optimization score based on suggestions.
        
        Args:
            analysis: Query analysis dictionary with suggestions
            
        Returns:
            Optimization score from 0 to 100 (higher is better)
        """
        score = 100
        
        # Deduct points for each suggestion
        for suggestion in analysis.get("suggestions", []):
            severity = suggestion.get("severity", "low")
            if severity == "high":
                score -= 20
            elif severity == "medium":
                score -= 10
            else:
                score -= 5
        
        # Deduct points for missing indexes
        for index_suggestion in analysis.get("index_suggestions", []):
            priority = index_suggestion.get("priority", "low")
            if priority == "high":
                score -= 15
            elif priority == "medium":
                score -= 10
        
        return max(0, score)
    
    def generate_optimization_report(
        self,
        slow_queries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate optimization report for multiple slow queries
        
        Args:
            slow_queries: List of slow query information
        
        Returns:
            Optimization report
        """
        all_suggestions = []
        all_index_suggestions = []
        query_analyses = []
        
        for query_info in slow_queries:
            statement = query_info.get("statement", "")
            execution_time = query_info.get("time_taken", 0)
            
            analysis = self.analyze_slow_query(statement, execution_time)
            query_analyses.append(analysis)
            
            all_suggestions.extend(analysis.get("suggestions", []))
            all_index_suggestions.extend(analysis.get("index_suggestions", []))
        
        # Aggregate index suggestions by table
        index_by_table = defaultdict(list)
        for idx_suggestion in all_index_suggestions:
            table = idx_suggestion.get("table", "unknown")
            index_by_table[table].append(idx_suggestion)
        
        return {
            "total_queries": len(slow_queries),
            "query_analyses": query_analyses,
            "summary": {
                "total_suggestions": len(all_suggestions),
                "total_index_suggestions": len(all_index_suggestions),
                "high_priority_suggestions": len([s for s in all_suggestions if s.get("severity") == "high"]),
                "index_suggestions_by_table": dict(index_by_table)
            },
            "recommendations": self._generate_recommendations(all_suggestions, all_index_suggestions),
            "generated_at": utc_now().isoformat()
        }
    
    def _generate_recommendations(
        self,
        suggestions: List[Dict[str, Any]],
        index_suggestions: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate high-level optimization recommendations.
        
        Args:
            suggestions: List of optimization suggestions
            index_suggestions: List of index suggestions
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Count suggestion types
        suggestion_types = defaultdict(int)
        for suggestion in suggestions:
            suggestion_types[suggestion.get("type")] += 1
        
        # Generate recommendations based on frequency
        if suggestion_types.get("missing_limit", 0) > 0:
            recommendations.append(f"Found {suggestion_types['missing_limit']} queries missing LIMIT; add LIMIT to cap results")
        
        if suggestion_types.get("leading_wildcard", 0) > 0:
            recommendations.append(f"Found {suggestion_types['leading_wildcard']} queries with leading wildcards; optimize to avoid full scans")
        
        if len(index_suggestions) > 0:
            recommendations.append(f"Recommend creating {len(index_suggestions)} indexes to optimize query performance")
        
        if suggestion_types.get("too_many_joins", 0) > 0:
            recommendations.append(f"Found {suggestion_types['too_many_joins']} queries with too many JOINs; consider refactoring")
        
        return recommendations
    
    def rewrite_query(self, statement: str) -> Dict[str, Any]:
        """
        Rewrite a query with optimizations applied
        
        Args:
            statement: Original SQL statement
        
        Returns:
            Dict with original query, rewritten query, and changes made
        """
        original = statement.strip()
        rewritten = original
        changes = []
        
        statement_upper = original.upper()
        
        # 1. Add LIMIT if missing (for SELECT queries without COUNT)
        if statement_upper.startswith("SELECT") and "LIMIT" not in statement_upper and "TOP" not in statement_upper:
            if "COUNT" not in statement_upper:
                # Add LIMIT 100 as default
                if ";" in rewritten:
                    rewritten = rewritten.rstrip(";") + " LIMIT 100;"
                else:
                    rewritten = rewritten + " LIMIT 100"
                changes.append({
                    "type": "added_limit",
                    "description": "Added LIMIT 100 to cap returned rows",
                    "original": original[-50:],
                    "optimized": rewritten[-50:]
                })
        
        # 2. Replace SELECT * with specific columns (if we can detect table)
        if re.search(r'SELECT\s+\*', rewritten, re.IGNORECASE):
            table_match = re.search(r'FROM\s+(\w+)', rewritten, re.IGNORECASE)
            if table_match:
                table_name = table_match.group(1)
                # Replace SELECT * with SELECT id (assuming id exists)
                # In production, this would query the schema
                rewritten = re.sub(
                    r'SELECT\s+\*',
                    f'SELECT {table_name}.id',  # Simplified - in production, get actual columns
                    rewritten,
                    flags=re.IGNORECASE
                )
                changes.append({
                    "type": "replaced_select_all",
                    "description": f"Replaced SELECT * with SELECT {table_name}.id (specify all needed columns explicitly)",
                    "original": original[:100],
                    "optimized": rewritten[:100]
                })
        
        # 3. Optimize LIKE queries with leading wildcard
        like_pattern = r"LIKE\s+['\"]%([^%']+)['\"]"
        if re.search(like_pattern, rewritten, re.IGNORECASE):
            # Suggest removing leading wildcard or using full-text search
            changes.append({
                "type": "like_optimization",
                "description": "Leading wildcard LIKE detected; remove leading % or use full-text search",
                "suggestion": "Change LIKE '%text' to LIKE 'text%' or use full-text index"
            })
        
        # 4. Optimize OR conditions to UNION (for simple cases)
        if re.search(r'\s+OR\s+', rewritten, re.IGNORECASE) and statement_upper.startswith("SELECT"):
            # This is complex, so we just suggest it
            changes.append({
                "type": "or_to_union",
                "description": "OR condition detected; consider UNION for better index use",
                "suggestion": "Split OR into separate queries merged with UNION"
            })
        
        return {
            "original": original,
            "rewritten": rewritten,
            "changes": changes,
            "optimization_applied": len(changes) > 0
        }
    
    def auto_optimize_query(
        self,
        statement: str,
        execution_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Automatically optimize a query by applying all suggestions
        
        Args:
            statement: SQL statement to optimize
            execution_time: Optional execution time for context
        
        Returns:
            Dict with optimization results
        """
        # First, analyze the query
        analysis = self.analyze_slow_query(
            statement=statement,
            execution_time=execution_time or 0.0
        )
        
        # Then, rewrite the query
        rewrite_result = self.rewrite_query(statement)
        
        # Combine results
        return {
            "original_query": statement,
            "optimized_query": rewrite_result["rewritten"],
            "analysis": analysis,
            "rewrite_changes": rewrite_result["changes"],
            "suggestions": analysis.get("suggestions", []),
            "index_suggestions": analysis.get("index_suggestions", []),
            "optimization_score": analysis.get("optimization_score", 0),
            "estimated_improvement": self._estimate_improvement(analysis, rewrite_result),
            "optimization_applied": rewrite_result["optimization_applied"]
        }
    
    def _estimate_improvement(
        self,
        analysis: Dict[str, Any],
        rewrite_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Estimate performance improvement from optimizations.
        
        Args:
            analysis: Query analysis dictionary
            rewrite_result: Query rewrite result dictionary
            
        Returns:
            Dictionary with estimated improvement percentage and reasons
        """
        improvement_percentage = 0
        reasons = []
        
        # Calculate improvement based on suggestions
        suggestions = analysis.get("suggestions", [])
        for suggestion in suggestions:
            severity = suggestion.get("severity", "low")
            if severity == "high":
                improvement_percentage += 30
                reasons.append(f"High-priority optimization: {suggestion.get('message', '')}")
            elif severity == "medium":
                improvement_percentage += 15
                reasons.append(f"Medium-priority optimization: {suggestion.get('message', '')}")
            else:
                improvement_percentage += 5
                reasons.append(f"Low-priority optimization: {suggestion.get('message', '')}")
        
        # Index suggestions can provide significant improvement
        index_suggestions = analysis.get("index_suggestions", [])
        high_priority_indexes = [idx for idx in index_suggestions if idx.get("priority") == "high"]
        if high_priority_indexes:
            improvement_percentage += 40
            reasons.append(f"Create {len(high_priority_indexes)} high-priority indexes for significant gains")
        
        # Rewrite changes
        if rewrite_result.get("optimization_applied"):
            improvement_percentage += 10
            reasons.append("Query rewrite applied")
        
        # Cap at 90% improvement
        improvement_percentage = min(improvement_percentage, 90)
        
        return {
            "estimated_percentage": improvement_percentage,
            "reasons": reasons,
            "confidence": "medium" if improvement_percentage > 30 else "low"
        }


# Global query optimizer instance
_query_optimizer: Optional[QueryOptimizer] = None


def get_query_optimizer() -> QueryOptimizer:
    """Get global query optimizer instance"""
    global _query_optimizer
    if _query_optimizer is None:
        _query_optimizer = QueryOptimizer()
    return _query_optimizer
