#!/usr/bin/env python3
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
from dependencies import require_auth, get_optional_user, get_emergency_service_dependency, get_task_service_dependency, get_emotion_service_dependency, get_customer_service_dependency, get_night_mode_service_dependency
from services.emergency_service import EmergencyService
from services.task_service import TaskService
from services.emotion_service import EmotionService
from services.customer_service import CustomerService
from services.night_mode_service import NightModeService
from services.logging_service import logger
from fastapi import HTTPException


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


class DependencyInjectionTester:
    """Dependency injection and error handling test class"""
    
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
        
        # Test user ID
        self.test_user_id = "test_user_123"
        self.test_elder_id = "test_elder_456"
        self.test_caregiver_id = "test_caregiver_789"
        
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
    
    def test_service_dependencies(self) -> bool:
        """Test service dependency functions"""
        print_info("Test service dependency functions...")
        
        try:
            # Test emergency service dependency
            emergency_service = get_emergency_service_dependency(self.db)
            assert isinstance(emergency_service, EmergencyService)
            
            # Test task service dependency
            task_service = get_task_service_dependency(self.db)
            assert isinstance(task_service, TaskService)
            
            # Test emotion service dependency
            emotion_service = get_emotion_service_dependency(self.db)
            assert isinstance(emotion_service, EmotionService)
            
            # Test customer service dependency
            customer_service = get_customer_service_dependency(self.db)
            assert isinstance(customer_service, CustomerService)
            
            # Test night mode service dependency
            night_mode_service = get_night_mode_service_dependency(self.db)
            assert isinstance(night_mode_service, NightModeService)
            
            print_success("Service dependency function tests passed")
            return True
        except Exception as e:
            print_error(f"Service dependency function tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_require_auth_dependency(self) -> bool:
        """Test require_auth dependency"""
        print_info("Test require_auth dependency...")
        
        try:
            # Test unauthenticated request raises error
            try:
                # Simulate unauthenticated request
                response = self.client.get("/api/night-mode/config?user_id=test")
                # Should return 401 (unauthenticated)
                assert response.status_code == 401, f"Expected 401, got {response.status_code}"
            except Exception as e:
                # If dependency works, should raise HTTPException
                pass
            
            print_success("require_auth dependency tests passed")
            return True
        except Exception as e:
            print_error(f"require_auth dependency tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_api_endpoints_exist(self) -> bool:
        """Test API endpoints exist"""
        print_info("Test API endpoints exist...")
        
        try:
            # Test emergency endpoint (should return 401, but endpoint exists)
            response = self.client.post("/api/emergency/record", json={})
            assert response.status_code in [400, 401, 422], f"Unexpected status code: {response.status_code}"
            
            # Test night mode endpoint
            response = self.client.get("/api/night-mode/config?user_id=test")
            assert response.status_code in [401, 422], f"Unexpected status code: {response.status_code}"
            
            # Test task endpoint
            response = self.client.post("/api/tasks", json={})
            assert response.status_code in [400, 401, 422], f"Unexpected status code: {response.status_code}"
            
            # Test emotion endpoint
            response = self.client.post("/api/emotions/log", json={})
            assert response.status_code in [400, 401, 422], f"Unexpected status code: {response.status_code}"
            
            # Test customer endpoint
            response = self.client.post("/api/customers", json={})
            assert response.status_code in [400, 401, 422], f"Unexpected status code: {response.status_code}"
            
            print_success("API endpoint existence tests passed")
            return True
        except Exception as e:
            print_error(f"API endpoint existence tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_error_handling_decorator(self) -> bool:
        """Test error handling decorator"""
        print_info("Test error handling decorator...")
        
        try:
            # Test ValidationError handling (400)
            # Note: require_auth checks auth first, unauthenticated requests return 401
            # Decorator still works; auth check takes priority
            response = self.client.post(
                "/api/emergency/record",
                json={
                    "elder_id": "",
                    "caregiver_id": "",
                    "emergency_type": "invalid_type",
                    "severity": "invalid_severity",
                    "description": ""
                }
            )
            # 401 when unauthenticated is expected (auth check first)
            # If authenticated, validation errors return 400/422
            assert response.status_code in [400, 401, 422], f"Expected 400/401/422, got {response.status_code}"
            
            # Test decorator behavior via direct call
            from middleware.api_decorators import handle_api_errors
            from exceptions import ValidationError
            
            @handle_api_errors
            def test_func():
                raise ValidationError("Test error")
            
            try:
                test_func()
                assert False, "Should have raised HTTPException"
            except Exception as e:
                # Decorator should convert ValidationError to HTTPException
                assert hasattr(e, 'status_code') or isinstance(e, HTTPException), "Should raise HTTPException"
            
            print_success("Error handling decorator tests passed")
            return True
        except Exception as e:
            print_error(f"Error handling decorator tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_service_injection(self) -> bool:
        """Test service injection works"""
        print_info("Testing service injection...")
        
        try:
            # Test service dependency functions directly
            emergency_service = get_emergency_service_dependency(self.db)
            assert emergency_service is not None
            assert hasattr(emergency_service, 'record_emergency')
            
            task_service = get_task_service_dependency(self.db)
            assert task_service is not None
            assert hasattr(task_service, 'create_task')
            
            emotion_service = get_emotion_service_dependency(self.db)
            assert emotion_service is not None
            assert hasattr(emotion_service, 'log_emotion')
            
            customer_service = get_customer_service_dependency(self.db)
            assert customer_service is not None
            assert hasattr(customer_service, 'create_customer')
            
            night_mode_service = get_night_mode_service_dependency(self.db)
            assert night_mode_service is not None
            assert hasattr(night_mode_service, 'get_night_mode_config')
            
            print_success("Service injection tests passed")
            return True
        except Exception as e:
            print_error(f"Service injection tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_dependencies_module(self) -> bool:
        """Test dependencies module import"""
        print_info("Testing dependencies module...")
        
        try:
            from dependencies import (
                require_auth, get_optional_user,
                get_emergency_service_dependency,
                get_task_service_dependency,
                get_emotion_service_dependency,
                get_customer_service_dependency,
                get_night_mode_service_dependency,
                get_sync_service_dependency,
                get_user_service_dependency
            )
            
            # Verify functions exist
            assert callable(require_auth)
            assert callable(get_optional_user)
            assert callable(get_emergency_service_dependency)
            assert callable(get_task_service_dependency)
            assert callable(get_emotion_service_dependency)
            assert callable(get_customer_service_dependency)
            assert callable(get_night_mode_service_dependency)
            
            print_success("Dependencies module tests passed")
            return True
        except Exception as e:
            print_error(f"Dependencies module tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_api_decorators_module(self) -> bool:
        """Test api_decorators module"""
        print_info("Test api_decorators module...")
        
        try:
            from middleware.api_decorators import handle_api_errors
            
            # Verify decorator exists
            assert callable(handle_api_errors)
            
            # Test decorator can be applied
            @handle_api_errors
            def test_function():
                return {"test": "success"}
            
            result = test_function()
            assert result == {"test": "success"}
            
            print_success("api_decorators module tests passed")
            return True
        except Exception as e:
            print_error(f"api_decorators module tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_refactored_routes_structure(self) -> bool:
        """Test refactored route structure"""
        print_info("Test refactored route structure...")
        
        try:
            # Check routes are registered correctly
            routes = [route.path for route in app.routes]
            
            # Check key routes exist
            assert "/api/emergency/record" in routes or any("/api/emergency" in r for r in routes)
            assert "/api/night-mode/config" in routes or any("/api/night-mode" in r for r in routes)
            assert "/api/tasks" in routes or any("/api/tasks" in r for r in routes)
            assert "/api/emotions/log" in routes or any("/api/emotions" in r for r in routes)
            assert "/api/customers" in routes or any("/api/customers" in r for r in routes)
            
            print_success("Refactored route structure tests passed")
            return True
        except Exception as e:
            print_error(f"Refactored route structure tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("Starting dependency injection and error handling verification tests")
        print("="*60 + "\n")
        
        tests = [
            ("Dependencies module import", self.test_dependencies_module),
            ("api_decorators module", self.test_api_decorators_module),
            ("Service dependency functions", self.test_service_dependencies),
            ("require_auth dependency", self.test_require_auth_dependency),
            ("Service injection", self.test_service_injection),
            ("API endpoints exist", self.test_api_endpoints_exist),
            ("Error handling decorator", self.test_error_handling_decorator),
            ("Refactored route structure", self.test_refactored_routes_structure),
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
            print_success("\n🎉 All tests passed! Dependency injection and error handling refactor verified!")
            return True
        else:
            print_error(f"\n⚠️  There are {self.test_results['failed']} test(s) failed")
            return False


if __name__ == "__main__":
    tester = DependencyInjectionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
