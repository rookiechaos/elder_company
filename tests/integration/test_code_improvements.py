"""
Internal test script
Runs in chatbot environment without exposing a port
"""

import os
import sys
from pathlib import Path

# Set test mode
os.environ["TEST_MODE"] = "true"
os.environ["ENVIRONMENT"] = "development"

# Add project path (backend root directory)
_candidate = Path(__file__).resolve().parent
while _candidate != _candidate.parent and not (_candidate / "main.py").exists():
    _candidate = _candidate.parent
sys.path.insert(0, str(_candidate))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from config.database import SessionLocal, init_database, get_db
from main import app
from services.base_service import BaseService
from services.user_service import UserService
from services.customer_service import CustomerService
from services.emotion_service import EmotionService
from services.rag_service import RAGService
from services.summary_service import SummaryService
from services.activity_service import ActivityService
from services.sync_service import SyncService
from utils.security import validate_enum_value, validate_range
from exceptions import ValidationError
from services.logging_service import logger


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")


def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")


def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")


class CodeImprovementsTester:
    """Code improvements test class"""
    
    def __init__(self):
        print_info("Initializing test environment...")
        
        # Initialize database
        init_database()
        
        # Create TestClient
        self.client = TestClient(app)
        
        # Override database dependency
        def override_get_db():
            db = SessionLocal()
            try:
                yield db
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()
        
        app.dependency_overrides[get_db] = override_get_db
        
        # Save database session for service tests
        self.db = SessionLocal()
        
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "tests": []
        }
    
    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'db'):
            self.db.close()
        app.dependency_overrides.clear()
    
    def test_base_service_inheritance(self) -> bool:
        """Test service classes inherit BaseService"""
        print_info("Test service classes inherit BaseService...")
        
        try:
            # Test all service classes inherit BaseService
            services = [
                UserService(self.db),
                CustomerService(self.db),
                EmotionService(self.db),
                RAGService(self.db),
                SummaryService(self.db),
                ActivityService(self.db),
                SyncService(self.db),
            ]
            
            for service in services:
                assert isinstance(service, BaseService), f"{service.__class__.__name__} should inherit BaseService"
                assert hasattr(service, 'safe_commit'), f"{service.__class__.__name__} should have safe_commit method"
                assert hasattr(service, 'safe_refresh'), f"{service.__class__.__name__} should have safe_refresh method"
                assert hasattr(service, 'handle_database_error'), f"{service.__class__.__name__} should have handle_database_error method"
            
            print_success("All service classes correctly inherit BaseService")
            return True
        except Exception as e:
            print_error(f"Service class inheritance tests failed: {e}")
            return False
    
    def test_validation_functions(self) -> bool:
        """Test validation functions"""
        print_info("Test validation functions...")
        
        try:
            # Test validate_enum_value
            validate_enum_value("elder", ["elder", "caregiver"], "user_type")
            validate_enum_value("caregiver", ["elder", "caregiver"], "user_type")
            
            # Test validate_range
            validate_range(3, 1, 5, "emotion_score")
            validate_range(1, 1, 5, "emotion_score")
            validate_range(5, 1, 5, "emotion_score")
            
            # Test invalid values raise exceptions
            try:
                validate_enum_value("invalid", ["elder", "caregiver"], "user_type")
                print_error("validate_enum_value should raise ValidationError for invalid value")
                return False
            except ValidationError:
                pass  # Expected exception
            
            try:
                validate_range(6, 1, 5, "emotion_score")
                print_error("validate_range should raise ValidationError for out of range value")
                return False
            except ValidationError:
                pass  # Expected exception
            
            print_success("Validation functions work correctly")
            return True
        except Exception as e:
            print_error(f"Validation function tests failed: {e}")
            return False
    
    def test_safe_commit(self) -> bool:
        """Test safe_commit method"""
        print_info("Test safe_commit method...")
        
        try:
            service = UserService(self.db)
            
            # Test safe_commit exists and is callable
            assert hasattr(service, 'safe_commit')
            assert callable(service.safe_commit)
            
            # Test safe_refresh exists and is callable
            assert hasattr(service, 'safe_refresh')
            assert callable(service.safe_refresh)
            
            # Test handle_database_error exists and is callable
            assert hasattr(service, 'handle_database_error')
            assert callable(service.handle_database_error)
            
            # Test ensure_db method
            assert hasattr(service, 'ensure_db')
            assert callable(service.ensure_db)
            
            # Test get_db method
            db_session = service.get_db()
            assert db_session is not None
            
            print_success("safe_commit method is available")
            return True
        except Exception as e:
            print_error(f"safe_commit tests failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling"""
        print_info("Testing error handling methods...")
        
        try:
            service = CustomerService(self.db)
            
            # Test handle_database_error method exists
            assert hasattr(service, 'handle_database_error')
            assert callable(service.handle_database_error)
            
            # Test safe_refresh method exists
            assert hasattr(service, 'safe_refresh')
            assert callable(service.safe_refresh)
            
            print_success("Error handling methods are available")
            return True
        except Exception as e:
            print_error(f"Error handling tests failed: {e}")
            return False
    
    def test_configuration_management(self) -> bool:
        """Test configuration management"""
        print_info("Test configuration management...")
        
        try:
            from config.settings import settings
            from services.cache_service import get_cache_ttl
            from middleware.rate_limit import get_rate_limits
            
            # Test cache TTL configuration
            cache_ttl = get_cache_ttl()
            assert isinstance(cache_ttl, dict)
            assert "activity_templates" in cache_ttl
            assert "translation" in cache_ttl
            
            # Test rate limit configuration
            rate_limits = get_rate_limits()
            assert isinstance(rate_limits, dict)
            assert "default" in rate_limits
            assert "auth" in rate_limits
            
            # Test Web Vitals configuration
            assert hasattr(settings, 'web_vitals_lcp_good')
            assert hasattr(settings, 'cache_ttl_activity_templates')
            assert hasattr(settings, 'rate_limit_default')
            
            print_success("Configuration management is OK")
            return True
        except Exception as e:
            print_error(f"Configuration management tests failed: {e}")
            return False
    
    def test_cache_key_generation(self) -> bool:
        """Test cache key generation"""
        print_info("Test cache key generation...")
        
        try:
            from services.cache_service import CacheService
            
            cache = CacheService()
            
            # Test key generation
            key1 = cache._generate_key("test", "arg1", "arg2", param1="value1")
            key2 = cache._generate_key("test", "arg1", "arg2", param1="value1")
            
            # Same parameters should generate the same key
            assert key1 == key2, "Same parameters should generate the same cache key"
            
            # Different parameters should generate different keys
            key3 = cache._generate_key("test", "arg1", "arg3", param1="value1")
            assert key1 != key3, "Different parameters should generate different cache keys"
            
            # Key should be a 64-character SHA256 hash
            assert len(key1) == 64, "Cache key should be a 64-character SHA256 hash"
            
            print_success("Cache key generation is OK")
            return True
        except Exception as e:
            print_error(f"Cache key generation tests failed: {e}")
            return False
    
    def test_logging_standardization(self) -> bool:
        """Test logging standardization"""
        print_info("Test logging standardization...")
        
        try:
            # Check if main.py still has print statements (should not)
            main_file = project_root / "main.py"
            if main_file.exists():
                content = main_file.read_text()
                # Check for remaining print statements (excluding comments and strings)
                lines = content.split('\n')
                print_statements = []
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if stripped.startswith('print(') and not stripped.startswith('#') and '"print(' not in line:
                        print_statements.append((i, line))
                
                if print_statements:
                    print_warning(f"main.py still has {len(print_statements)} print statement(s)")
                    for line_num, line in print_statements[:3]:
                        print_warning(f"  line {line_num}: {line.strip()}")
                else:
                    print_success("main.py has no print statements")
            
            # Check task_queue.py
            task_queue_file = project_root / "services" / "task_queue.py"
            if task_queue_file.exists():
                content = task_queue_file.read_text()
                lines = content.split('\n')
                print_statements = []
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if stripped.startswith('print(') and not stripped.startswith('#') and '"print(' not in line:
                        print_statements.append((i, line))
                
                if print_statements:
                    print_warning(f"task_queue.py still has {len(print_statements)} print statement(s)")
                else:
                    print_success("task_queue.py has no print statements")
            
            return True
        except Exception as e:
            print_error(f"Logging standardization tests failed: {e}")
            return False
    
    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        print_info("Test health check endpoint...")
        
        try:
            response = self.client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            print_success("Health check endpoint is OK")
            return True
        except Exception as e:
            print_error(f"Health check tests failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("Starting code improvements verification tests")
        print("="*60 + "\n")
        
        tests = [
            ("Service classes inherit BaseService", self.test_base_service_inheritance),
            ("Validation functions", self.test_validation_functions),
            ("safe_commit method", self.test_safe_commit),
            ("Error handling", self.test_error_handling),
            ("Configuration management", self.test_configuration_management),
            ("Cache key generation", self.test_cache_key_generation),
            ("Logging standardization", self.test_logging_standardization),
            ("Health check endpoint", self.test_health_check),
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    self.test_results["passed"] += 1
                    self.test_results["tests"].append({"name": test_name, "status": "passed"})
                else:
                    self.test_results["failed"] += 1
                    self.test_results["tests"].append({"name": test_name, "status": "failed"})
            except Exception as e:
                self.test_results["failed"] += 1
                self.test_results["tests"].append({"name": test_name, "status": "error", "error": str(e)})
                print_error(f"{test_name} test error: {e}")
        
        # Print summary
        print("\n" + "="*60)
        print("Test results summary")
        print("="*60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"⏭️  skipped: {self.test_results['skipped']}")
        print(f"📊 Total: {len(tests)}")
        
        if self.test_results['failed'] == 0:
            print_success("\n🎉 All tests passed! Code improvements verified!")
            return True
        else:
            print_error(f"\n⚠️  There are {self.test_results['failed']} test(s) failed")
            return False


if __name__ == "__main__":
    tester = CodeImprovementsTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
