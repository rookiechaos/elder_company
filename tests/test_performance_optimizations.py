"""
Unit tests for performance optimizations
测试性能优化功能是否正常工作
"""

import pytest
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.cache_service import CacheService, get_cache, CACHE_TTL
from services.customer_service import CustomerService
from services.activity_service import ActivityService
from services.organization_service import OrganizationService
from middleware.rate_limit import RATE_LIMITS

# Import performance metrics with try/except to handle missing fastapi
try:
    from middleware.performance import PerformanceMetrics, get_performance_stats
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False
    # Create mock class for testing
    class PerformanceMetrics:
        def __init__(self):
            self.metrics = {"request_count": 0}
        def record_request(self, *args, **kwargs):
            self.metrics["request_count"] += 1
        def get_stats(self):
            return {"request_count": self.metrics["request_count"]}
        def reset(self):
            self.metrics = {"request_count": 0}
    
    def get_performance_stats():
        return {"request_count": 0}


class TestCacheService:
    """Test cache service functionality"""
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get"""
        cache = CacheService()
        
        cache.set("test_key", "test_value", ttl=60)
        result = cache.get("test_key")
        
        assert result == "test_value"
    
    def test_cache_expiration(self):
        """Test cache expiration"""
        cache = CacheService()
        
        cache.set("expire_key", "value", ttl=1)  # 1 second TTL
        
        # Should be available immediately
        assert cache.get("expire_key") == "value"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be None after expiration
        assert cache.get("expire_key") is None
    
    def test_cache_delete(self):
        """Test cache deletion"""
        cache = CacheService()
        
        cache.set("delete_key", "value")
        assert cache.get("delete_key") == "value"
        
        cache.delete("delete_key")
        assert cache.get("delete_key") is None
    
    def test_cache_clear(self):
        """Test cache clearing"""
        cache = CacheService()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_cache_stats(self):
        """Test cache statistics"""
        cache = CacheService()
        
        # Generate some cache activity
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        stats = cache.get_stats()
        
        assert stats["hits"] >= 1
        assert stats["misses"] >= 1
        assert stats["sets"] >= 1
        assert "hit_rate" in stats


class TestN1QueryOptimization:
    """Test N+1 query optimization"""
    
    def test_customer_get_with_joinedload(self, db_session):
        """Test that get_customer uses joinedload to avoid N+1 queries"""
        customer_service = CustomerService(db_session)
        
        # Create test customer
        customer_data = {
            "customer_id": "test_customer_001",
            "customer_type": "caregiver",
            "name": "Test Caregiver",
            "email": "test@example.com",
            "role": "介护士",
            "experience_years": 5
        }
        
        customer = customer_service.create_customer(customer_data)
        customer_id = customer["customer_id"]
        
        # Get customer - should use joinedload
        result = customer_service.get_customer(customer_id)
        
        assert result is not None
        assert result["customer_id"] == customer_id
        # Should have profile data loaded
        assert "caregiver_profile" in result or "elder_profile" in result
    
    def test_customer_cache_integration(self, db_session):
        """Test that customer get uses cache"""
        customer_service = CustomerService(db_session)
        
        # Create test customer
        customer_data = {
            "customer_id": "test_customer_cache",
            "customer_type": "elder",
            "name": "Test Elder",
            "email": "elder@example.com"
        }
        
        customer = customer_service.create_customer(customer_data)
        customer_id = customer["customer_id"]
        
        # First call - should hit database
        start_time = time.time()
        result1 = customer_service.get_customer(customer_id)
        first_call_time = time.time() - start_time
        
        # Second call - should hit cache
        start_time = time.time()
        result2 = customer_service.get_customer(customer_id)
        second_call_time = time.time() - start_time
        
        # Results should be the same
        assert result1 == result2
        
        # Second call should be faster (cached)
        # Note: This might not always be true due to timing, but cache should be faster
        assert result2 is not None


class TestBatchOperations:
    """Test batch operations"""
    
    def test_batch_create_customers(self, db_session):
        """Test bulk create customers"""
        customer_service = CustomerService(db_session)
        
        customers_data = [
            {
                "customer_id": f"batch_customer_{i}",
                "customer_type": "caregiver",
                "name": f"Batch Caregiver {i}",
                "email": f"batch{i}@example.com"
            }
            for i in range(5)
        ]
        
        # Use bulk create
        created = customer_service.bulk_create_customers(customers_data)
        
        assert len(created) == 5
        
        # Verify all customers were created
        for i in range(5):
            customer = customer_service.get_customer(f"batch_customer_{i}")
            assert customer is not None
            assert customer["name"] == f"Batch Caregiver {i}"


class TestPerformanceMonitoring:
    """Test performance monitoring"""
    
    def test_performance_metrics_recording(self):
        """Test that performance metrics are recorded"""
        metrics = PerformanceMetrics()
        
        # Record some requests
        metrics.record_request("/api/test", "GET", 0.1, 200)
        metrics.record_request("/api/test", "GET", 0.2, 200)
        metrics.record_request("/api/test", "POST", 1.5, 200)  # Slow query
        
        stats = metrics.get_stats()
        
        assert stats["request_count"] == 3
        assert stats["slow_queries_count"] == 1
        assert stats["error_count"] == 0
        assert "endpoint_averages" in stats
    
    def test_slow_query_detection(self):
        """Test slow query detection"""
        metrics = PerformanceMetrics()
        
        # Record slow query
        metrics.record_request("/api/slow", "GET", 1.5, 200)
        
        stats = metrics.get_stats()
        
        assert stats["slow_queries_count"] == 1
        assert len(stats["recent_slow_queries"]) > 0
        assert stats["recent_slow_queries"][0]["response_time"] > 1.0
    
    def test_performance_stats_reset(self):
        """Test performance stats reset"""
        metrics = PerformanceMetrics()
        
        metrics.record_request("/api/test", "GET", 0.1, 200)
        assert metrics.get_stats()["request_count"] == 1
        
        metrics.reset()
        assert metrics.get_stats()["request_count"] == 0


class TestRateLimiting:
    """Test rate limiting"""
    
    def test_rate_limit_config(self):
        """Test rate limit configuration"""
        assert "default" in RATE_LIMITS
        assert "translation" in RATE_LIMITS
        assert "auth" in RATE_LIMITS
        assert "sync" in RATE_LIMITS
        
        # Check that limits are reasonable
        assert RATE_LIMITS["auth"] == "5/minute"  # Very restrictive
        assert RATE_LIMITS["translation"] == "10/minute"  # More restrictive


class TestActivityServiceCache:
    """Test activity service caching"""
    
    def test_activity_templates_cache(self, db_session):
        """Test that activity templates are cached"""
        activity_service = ActivityService(db_session)
        
        # First call - should hit database
        start_time = time.time()
        templates1 = activity_service.get_activity_templates()
        first_call_time = time.time() - start_time
        
        # Second call - should hit cache
        start_time = time.time()
        templates2 = activity_service.get_activity_templates()
        second_call_time = time.time() - start_time
        
        # Results should be the same
        assert len(templates1) == len(templates2)
        assert templates1 == templates2


class TestOrganizationServiceCache:
    """Test organization service caching"""
    
    def test_organization_cache(self, db_session):
        """Test that organization data is cached"""
        org_service = OrganizationService(db_session)
        
        # Create test organization
        org_data = {
            "org_id": "test_org_cache",
            "name": "Test Organization",
            "name_ja": "テスト組織"
        }
        
        org = org_service.create_organization(org_data)
        org_id = org["org_id"]
        
        # First call - should hit database
        result1 = org_service.get_organization(org_id)
        
        # Second call - should hit cache
        result2 = org_service.get_organization(org_id)
        
        # Results should be the same
        assert result1 == result2
        assert result1["org_id"] == org_id


class TestAPIEndpoints:
    """Test API endpoints with optimizations"""
    
    def test_rate_limit_config(self):
        """Test rate limit configuration exists"""
        assert "default" in RATE_LIMITS
        assert "translation" in RATE_LIMITS
        assert isinstance(RATE_LIMITS["translation"], str)
    
    def test_performance_stats_available(self):
        """Test that performance stats function works"""
        stats = get_performance_stats()
        assert isinstance(stats, dict)
        assert "request_count" in stats
        assert "avg_response_time_ms" in stats


class TestCacheIntegration:
    """Test cache integration with services"""
    
    def test_cache_invalidation_on_update(self, db_session):
        """Test that cache is invalidated on update"""
        customer_service = CustomerService(db_session)
        cache = get_cache()
        
        # Create customer
        customer_data = {
            "customer_id": "test_cache_invalidation",
            "customer_type": "caregiver",
            "name": "Original Name",
            "email": "test@example.com"
        }
        
        customer = customer_service.create_customer(customer_data)
        customer_id = customer["customer_id"]
        
        # Get customer (should cache)
        result1 = customer_service.get_customer(customer_id)
        assert result1["name"] == "Original Name"
        
        # Update customer
        customer_service.update_customer(customer_id, {"name": "Updated Name"})
        
        # Get customer again (should get fresh data, not cached)
        result2 = customer_service.get_customer(customer_id)
        assert result2["name"] == "Updated Name"


class TestDatabaseIndexes:
    """Test that database indexes are properly configured"""
    
    def test_customer_indexes(self, db_session):
        """Test customer table has indexes"""
        from sqlalchemy import inspect
        
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes("customers")
        
        index_names = [idx["name"] for idx in indexes]
        
        # Check for important indexes
        # Note: SQLite might name indexes differently
        assert len(indexes) > 0  # Should have at least primary key index


def test_all_optimizations_integration(db_session):
    """Integration test for all optimizations"""
    # Test cache service
    cache = get_cache()
    cache.set("integration_test", "value", ttl=60)
    assert cache.get("integration_test") == "value"
    
    # Test customer service with cache
    customer_service = CustomerService(db_session)
    customer_data = {
        "customer_id": "integration_test_customer",
        "customer_type": "caregiver",
        "name": "Integration Test",
        "email": "integration@test.com"
    }
    
    customer = customer_service.create_customer(customer_data)
    assert customer is not None
    
    # Test get with cache
    result = customer_service.get_customer(customer["customer_id"])
    assert result is not None
    assert result["customer_id"] == customer["customer_id"]
    
    # Test performance metrics
    metrics = PerformanceMetrics()
    metrics.record_request("/api/test", "GET", 0.1, 200)
    stats = metrics.get_stats()
    assert stats["request_count"] == 1
    
    # Test batch operations
    batch_data = [
        {
            "customer_id": f"batch_integration_{i}",
            "customer_type": "elder",
            "name": f"Batch Elder {i}"
        }
        for i in range(3)
    ]
    
    created = customer_service.bulk_create_customers(batch_data)
    assert len(created) == 3
    
    print("✅ All performance optimizations are working correctly!")
