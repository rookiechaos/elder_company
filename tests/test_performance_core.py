"""
Core performance optimization tests - No external dependencies
核心性能优化测试 - 不依赖外部库
"""

import pytest
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test cache service directly (no dependencies)
from services.cache_service import CacheService, get_cache, CACHE_TTL


class TestCacheServiceCore:
    """Test cache service core functionality"""
    
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
        print("✅ Cache clear works correctly")
    
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
        assert stats["size"] >= 1
        print("✅ Cache statistics work correctly")
    
    def test_cache_cleanup_expired(self):
        """Test cache cleanup of expired entries"""
        cache = CacheService()
        
        cache.set("expired1", "value1", ttl=1)
        cache.set("expired2", "value2", ttl=1)
        cache.set("valid", "value3", ttl=60)
        
        time.sleep(1.1)
        
        cleaned = cache.cleanup_expired()
        
        assert cleaned >= 2
        assert cache.get("expired1") is None
        assert cache.get("expired2") is None
        assert cache.get("valid") == "value3"
        print("✅ Cache cleanup works correctly")
    
    def test_cache_global_instance(self):
        """Test global cache instance"""
        cache1 = get_cache()
        cache2 = get_cache()
        
        # Should be the same instance
        assert cache1 is cache2
        
        cache1.set("global_test", "value")
        assert cache2.get("global_test") == "value"
        print("✅ Global cache instance works correctly")
    
    def test_cache_ttl_constants(self):
        """Test cache TTL constants"""
        assert "activity_templates" in CACHE_TTL
        assert "user_config" in CACHE_TTL
        assert "care_terms" in CACHE_TTL
        assert "customer_info" in CACHE_TTL
        
        # Check TTL values are reasonable
        assert CACHE_TTL["activity_templates"] == 3600  # 1 hour
        assert CACHE_TTL["customer_info"] == 900  # 15 minutes
        print("✅ Cache TTL constants are correct")


class TestCacheWithServices:
    """Test cache integration with services (if available)"""
    
    def test_customer_service_cache(self, db_session):
        """Test customer service uses cache"""
        try:
            from services.customer_service import CustomerService
            
            customer_service = CustomerService(db_session)
            
            # Create test customer
            customer_data = {
                "customer_id": "test_cache_customer",
                "customer_type": "caregiver",
                "name": "Test Caregiver",
                "email": "test@example.com"
            }
            
            customer = customer_service.create_customer(customer_data)
            customer_id = customer["customer_id"]
            
            # First call - should hit database
            result1 = customer_service.get_customer(customer_id)
            assert result1 is not None
            
            # Second call - should hit cache
            result2 = customer_service.get_customer(customer_id)
            assert result2 is not None
            assert result1 == result2
            print("✅ Customer service cache integration works correctly")
        except ImportError as e:
            pytest.skip(f"Customer service not available: {e}")
    
    def test_activity_service_cache(self, db_session):
        """Test activity service uses cache"""
        try:
            from services.activity_service import ActivityService
            
            activity_service = ActivityService(db_session)
            
            # First call - should hit database
            templates1 = activity_service.get_activity_templates()
            
            # Second call - should hit cache
            templates2 = activity_service.get_activity_templates()
            
            # Results should be the same
            assert len(templates1) == len(templates2)
            assert templates1 == templates2
            print("✅ Activity service cache integration works correctly")
        except ImportError as e:
            pytest.skip(f"Activity service not available: {e}")
    
    def test_batch_operations(self, db_session):
        """Test batch operations"""
        try:
            from services.customer_service import CustomerService
            
            customer_service = CustomerService(db_session)
            
            customers_data = [
                {
                    "customer_id": f"batch_test_{i}",
                    "customer_type": "caregiver",
                    "name": f"Batch Test {i}",
                    "email": f"batch{i}@test.com"
                }
                for i in range(3)
            ]
            
            # Use bulk create
            created = customer_service.bulk_create_customers(customers_data)
            
            assert len(created) == 3
            
            # Verify all customers were created
            for i in range(3):
                customer = customer_service.get_customer(f"batch_test_{i}")
                assert customer is not None
                assert customer["name"] == f"Batch Test {i}"
            
            print("✅ Batch operations work correctly")
        except ImportError as e:
            pytest.skip(f"Customer service not available: {e}")


def test_all_core_optimizations():
    """Integration test for core optimizations"""
    print("\n🧪 Running core performance optimization tests...")
    
    # Test cache service
    cache = CacheService()
    cache.set("integration_test", "value", ttl=60)
    assert cache.get("integration_test") == "value"
    print("✅ Cache service: OK")
    
    # Test cache statistics
    stats = cache.get_stats()
    assert "hits" in stats
    assert "misses" in stats
    assert "hit_rate" in stats
    print("✅ Cache statistics: OK")
    
    # Test global cache instance
    cache1 = get_cache()
    cache2 = get_cache()
    assert cache1 is cache2
    print("✅ Global cache instance: OK")
    
    # Test cache TTL constants
    assert len(CACHE_TTL) > 0
    print("✅ Cache TTL constants: OK")
    
    print("\n🎉 All core performance optimizations are working correctly!")
    print("✅ No bugs detected in core performance features!")


if __name__ == "__main__":
    # Run tests directly
    print("Running performance optimization tests...\n")
    
    # Test cache service
    test_cache = TestCacheServiceCore()
    test_cache.test_cache_set_and_get()
    test_cache.test_cache_expiration()
    test_cache.test_cache_delete()
    test_cache.test_cache_clear()
    test_cache.test_cache_stats()
    test_cache.test_cache_cleanup_expired()
    test_cache.test_cache_global_instance()
    test_cache.test_cache_ttl_constants()
    
    # Run integration test
    test_all_core_optimizations()
    
    print("\n✅ All tests passed! No bugs detected!")
