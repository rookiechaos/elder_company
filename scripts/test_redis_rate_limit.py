#!/usr/bin/env python3
"""
Test Redis Rate Limiting
测试 Redis 分布式限流功能
"""

import os
import sys
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_redis_connection():
    """Test Redis connection"""
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url)
        r.ping()
        print("✅ Redis 连接成功")
        return True
    except ImportError:
        print("⚠️  redis 库未安装，请运行: pip install redis")
        return False
    except Exception as e:
        print(f"❌ Redis 连接失败: {e}")
        print("请确保 Redis 服务正在运行")
        return False

def test_rate_limit_api(base_url="http://localhost:8000", endpoint="/api/translate"):
    """Test rate limiting via API"""
    if not REQUESTS_AVAILABLE:
        print("⚠️  requests 库未安装，跳过 API 测试")
        print("   安装: pip install requests")
        return False
    
    print(f"\n🧪 测试 API 限流: {base_url}{endpoint}")
    
    # Make requests to test rate limiting
    results = {
        "success": 0,
        "rate_limited": 0,
        "errors": 0
    }
    
    # Test with multiple concurrent requests
    def make_request(i):
        try:
            response = requests.post(
                f"{base_url}{endpoint}",
                json={
                    "text": f"Test request {i}",
                    "source_lang": "ja",
                    "target_lang": "zh"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                return "success"
            elif response.status_code == 429:
                return "rate_limited"
            else:
                return f"error_{response.status_code}"
        except Exception as e:
            return f"error_{str(e)}"
    
    if not CONCURRENT_AVAILABLE:
        print("⚠️  concurrent.futures 不可用，使用顺序请求")
        for i in range(10):
            result = make_request(i)
            if result == "success":
                results["success"] += 1
            elif result == "rate_limited":
                results["rate_limited"] += 1
            else:
                results["errors"] += 1
    else:
        print("发送 20 个并发请求...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(20)]
            
            for future in as_completed(futures):
                result = future.result()
                if result == "success":
                    results["success"] += 1
                elif result == "rate_limited":
                    results["rate_limited"] += 1
                else:
                    results["errors"] += 1
    
    print(f"\n📊 测试结果:")
    print(f"  成功: {results['success']}")
    print(f"  限流: {results['rate_limited']}")
    print(f"  错误: {results['errors']}")
    
    if results["rate_limited"] > 0:
        print("✅ 限流功能正常工作")
        return True
    else:
        print("⚠️  未检测到限流，可能限流Threshold较高或未启用")
        return True

def test_rate_limit_headers(base_url="http://localhost:8000", endpoint="/api/translate"):
    """Test rate limit headers in response"""
    if not REQUESTS_AVAILABLE:
        print("⚠️  requests 库未安装，跳过响应头测试")
        return False
    
    print(f"\n🧪 测试限流响应头")
    
    try:
        response = requests.post(
            f"{base_url}{endpoint}",
            json={
                "text": "Test",
                "source_lang": "ja",
                "target_lang": "zh"
            },
            timeout=5
        )
        
        headers = response.headers
        rate_limit_headers = {
            "X-RateLimit-Limit": headers.get("X-RateLimit-Limit"),
            "X-RateLimit-Remaining": headers.get("X-RateLimit-Remaining"),
            "X-RateLimit-Reset": headers.get("X-RateLimit-Reset"),
        }
        
        if any(rate_limit_headers.values()):
            print("✅ 检测到限流响应头:")
            for key, value in rate_limit_headers.items():
                if value:
                    print(f"  {key}: {value}")
            return True
        else:
            print("⚠️  未检测到限流响应头")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def check_redis_usage():
    """Check if Redis is being used for rate limiting"""
    print(f"\n🔍 检查 Redis 使用情况")
    
    try:
        import redis
        redis_url = os.getenv("REDIS_URL")
        
        if not redis_url:
            print("⚠️  REDIS_URL 环境变量未设置")
            print("   限流将使用内存模式（非分布式）")
            return False
        
        print(f"✅ REDIS_URL 已设置: {redis_url}")
        
        # Check Redis keys related to rate limiting
        r = redis.from_url(redis_url)
        keys = r.keys("LIMITER:*")
        
        if keys:
            print(f"✅ 发现 {len(keys)} 个限流相关的 Redis key")
            print("   这表明 Redis 正在用于分布式限流")
            return True
        else:
            print("ℹ️  当前没有活跃的限流 key（可能没有请求）")
            return True
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("Elder Company - Redis 分布式限流测试")
    print("=" * 50)
    print("")
    
    # Load environment variables
    from dotenv import load_dotenv

    root = os.path.dirname(os.path.dirname(__file__))
    env_candidates = [
        os.path.join(root, "do-not-upload", "env", ".env"),
        os.path.join(root, "backend", ".env"),
    ]
    loaded = False
    for env_path in env_candidates:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"Loaded env: {env_path}")
            loaded = True
            break
    if not loaded:
        print("No .env found — using system environment variables")
        print("  Expected: do-not-upload/env/.env")
    
    print("")
    
    # Test 1: Redis connection
    if not test_redis_connection():
        print("\n❌ Redis 连接测试失败，请先设置 Redis")
        return 1
    
    # Test 2: Check Redis usage
    check_redis_usage()
    
    # Test 3: Rate limit headers
    test_rate_limit_headers()
    
    # Test 4: Rate limit API (optional, requires running server)
    print("\n" + "=" * 50)
    print("可选测试: API 限流测试")
    print("=" * 50)
    print("注意: 此测试需要后端服务正在运行")
    print("如果服务未运行，可以跳过此测试")
    print("")
    
    response = input("是否运行 API 限流测试? (y/N): ").strip().lower()
    if response == 'y':
        test_rate_limit_api()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
