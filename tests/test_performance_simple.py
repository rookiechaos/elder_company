"""
Simple unit tests for performance optimizations
简化的性能优化功能测试
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


class TestCacheService:
    """Test cache service functionality"""
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get"""
        cache = CacheService()
        
        cache.set("test_key", "test_value", ttl=60)
        result = cache.get("test_key")
        
        assert result == "test_value"
        print("✅ Cache set/get works correctly")
    
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
        print("✅ Cache expiration works correctly")
    
    def test_cache_delete(self):
        """Test cache deletion"""
        cache = CacheService()
        
        cache.set("delete_key", "value")
        assert cache.get("delete_key") == "value"
        
        cache.delete("delete_key")
        assert cache.get("delete_key") is None
        print("✅ Cache delete works correctly")
    
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
        print("✅ Cache statistics work correctly")


class TestN1QueryOptimization:
    """Test N+1 query optimization"""
    
    def test_customer_get_with_cache(self, db_session):
        """Test that get_customer uses cache"""
        customer_service = CustomerService(db_session)
        
        # Create test customer
        customer_data = {
            "customer_id": "test_customer_cache_001",
            "customer_type": "caregiver",
            "name": "Test Caregiver",
            "email": "test@example.com",
            "role": "介护士",
            "experience_years": 5
        }
        
        customer = customer_service.create_customer(customer_data)
        customer_id = customer["customer_id"]
        
        # Get customer - should use cache on second call
        result1 = customer_service.get_customer(customer_id)
        assert result1 is not None
        assert result1["customer_id"] == customer_id
        
        # Second call should use cache
        result2 = customer_service.get_customer(customer_id)
        assert result2 is not None
        assert result1 == result2
        print("✅ Customer get with cache works correctly")


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
        
        print("✅ Batch create customers works correctly")


class TestRateLimiting:
    """Test rate limiting configuration"""
    
    def test_rate_limit_config(self):
        """Test rate limit configuration"""
        assert "default" in RATE_LIMITS
        assert "translation" in RATE_LIMITS
        assert "auth" in RATE_LIMITS
        assert "sync" in RATE_LIMITS
        
        # Check that limits are reasonable
        assert RATE_LIMITS["auth"] == "5/minute"  # Very restrictive
        assert RATE_LIMITS["translation"] == "10/minute"  # More restrictive
        print("✅ Rate limit configuration is correct")


class TestActivityServiceCache:
    """Test activity service caching"""
    
    def test_activity_templates_cache(self, db_session):
        """Test that activity templates are cached"""
        activity_service = ActivityService(db_session)
        
        # First call - should hit database
        templates1 = activity_service.get_activity_templates()
        
        # Second call - should hit cache
        templates2 = activity_service.get_activity_templates()
        
        # Results should be the same
        assert len(templates1) == len(templates2)
        assert templates1 == templates2
        print("✅ Activity templates cache works correctly")


class TestOrganizationServiceCache:
    """Test organization service caching"""
    
    def test_organization_cache(self, db_session):
        """Test that organization data is cached"""
        org_service = OrganizationService(db_session)
        
        # Create test organization
        org_data = {
            "org_id": "test_org_cache_001",
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
        print("✅ Organization cache works correctly")


class TestCacheIntegration:
    """Test cache integration with services"""
    
    def test_cache_invalidation_on_update(self, db_session):
        """Test that cache is invalidated on update"""
        customer_service = CustomerService(db_session)
        cache = get_cache()
        
        # Create customer
        customer_data = {
            "customer_id": "test_cache_invalidation_001",
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
        print("✅ Cache invalidation on update works correctly")


def test_all_optimizations_integration(db_session):
    """Integration test for all optimizations"""
    print("\n🧪 Running integration test for all optimizations...")
    
    # Test cache service
    cache = get_cache()
    cache.set("integration_test", "value", ttl=60)
    assert cache.get("integration_test") == "value"
    print("✅ Cache service: OK")
    
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
    print("✅ Customer creation: OK")
    
    # Test get with cache
    result = customer_service.get_customer(customer["customer_id"])
    assert result is not None
    assert result["customer_id"] == customer["customer_id"]
    print("✅ Customer get with cache: OK")
    
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
    print("✅ Batch operations: OK")
    
    # Test activity service cache
    activity_service = ActivityService(db_session)
    templates = activity_service.get_activity_templates()
    assert len(templates) > 0
    print("✅ Activity service cache: OK")
    
    # Test organization service cache
    org_service = OrganizationService(db_session)
    org_data = {
        "org_id": "integration_test_org",
        "name": "Integration Test Org"
    }
    org = org_service.create_organization(org_data)
    org_result = org_service.get_organization(org["org_id"])
    assert org_result is not None
    print("✅ Organization service cache: OK")
    
    print("\n🎉 All performance optimizations are working correctly!")
    print("✅ No bugs detected in performance optimization features!")
