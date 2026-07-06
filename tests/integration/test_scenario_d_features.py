#!/usr/bin/env python3
"""
Internal test script - verify Scenario D features (night mode and emergency records)
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
from services.night_mode_service import NightModeService, get_night_mode_service
from services.emergency_service import EmergencyService, get_emergency_service
from services.reminder_service import ReminderService
from models.emergency_models import EmergencyRecordDB, NightModeConfigDB
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


class ScenarioDFeaturesTester:
    """Scenario D feature test class"""
    
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
    
    def test_night_mode_service(self) -> bool:
        """Test night mode service"""
        print_info("Test night mode service...")
        
        try:
            service = get_night_mode_service(self.db)
            
            # Test create configuration
            config = service.update_night_mode_config(
                user_id=self.test_user_id,
                user_type="elder",
                enabled=True,
                brightness="low",
                sound_enabled=False,
                text_prompts=True,
                start_time="22:00",
                end_time="07:00",
                font_size="large",
                color_scheme="dark"
            )
            
            assert config is not None
            assert config["enabled"] is True
            assert config["brightness"] == "low"
            assert config["start_time"] == "22:00"
            assert config["end_time"] == "07:00"
            
            # Test get configuration
            loaded_config = service.get_night_mode_config(self.test_user_id)
            assert loaded_config is not None
            assert loaded_config["enabled"] is True
            
            # Test update configuration
            updated_config = service.update_night_mode_config(
                user_id=self.test_user_id,
                user_type="elder",
                brightness="medium"
            )
            assert updated_config["brightness"] == "medium"
            
            # Test activation check
            is_active = service.is_night_mode_active(self.test_user_id)
            assert isinstance(is_active, bool)
            
            print_success("Night mode service tests passed")
            return True
        except Exception as e:
            print_error(f"Night mode service tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_emergency_service(self) -> bool:
        """Test emergency service"""
        print_info("Test emergency service...")
        
        try:
            service = get_emergency_service(self.db)
            
            # Test record emergency (no AI guidance to avoid API calls)
            record = service.record_emergency(
                elder_id=self.test_elder_id,
                caregiver_id=self.test_caregiver_id,
                emergency_type="emotional",
                severity="medium",
                description="テスト用の緊急状況",
                actions_taken=["声をかけた", "静かな場所に移動した"],
                generate_guidance=False,  # Avoid AI API calls
                generate_summary=False    # Avoid AI API calls
            )
            
            assert record is not None
            assert record["emergency_type"] == "emotional"
            assert record["severity"] == "medium"
            assert record["description"] == "テスト用の緊急状況"
            assert len(record["actions_taken"]) == 2
            
            # Test get history
            history = service.get_emergency_history(
                elder_id=self.test_elder_id,
                limit=10
            )
            assert isinstance(history, list)
            assert len(history) > 0
            assert history[0]["record_id"] == record["record_id"]
            
            print_success("Emergency service tests passed")
            return True
        except Exception as e:
            print_error(f"Emergency service tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_reminder_service(self) -> bool:
        """Test reminder service"""
        print_info("Test reminder service...")
        
        try:
            # Test generate reminder (no AI, use fallback reminder)
            # ReminderService uses static methods; test fallback reminder directly
            fallback_reminder = ReminderService._get_fallback_reminder("medication", "お薬")
            assert fallback_reminder is not None
            assert len(fallback_reminder) > 0
            assert "お薬" in fallback_reminder or "お時間" in fallback_reminder
            
            print_success("Reminder service tests passed")
            return True
        except Exception as e:
            print_error(f"Reminder service tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_night_mode_api(self) -> bool:
        """Test night mode API endpoints"""
        print_info("Test night mode API endpoints...")
        
        try:
            # Note: these endpoints require auth and may return 401 in tests
            # Main goal is verifying endpoints exist and routes are correct
            
            # Test get configuration endpoint (may return 401, but endpoint should exist)
            response = self.client.get(f"/api/night-mode/config?user_id={self.test_user_id}")
            # 401 is expected (unauthenticated); 404 or 500 is a problem
            assert response.status_code in [200, 401], f"Unexpected status code: {response.status_code}"
            
            # Test check activation endpoint
            response = self.client.get(f"/api/night-mode/active?user_id={self.test_user_id}")
            assert response.status_code in [200, 401], f"Unexpected status code: {response.status_code}"
            
            print_success("Night mode API endpoint tests passed")
            return True
        except Exception as e:
            print_error(f"Night mode API endpoint tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_emergency_api(self) -> bool:
        """Test emergency API endpoints"""
        print_info("Test emergency API endpoints...")
        
        try:
            # Test record emergency endpoint (auth required, may return 401)
            response = self.client.post(
                "/api/emergency/record",
                json={
                    "elder_id": self.test_elder_id,
                    "caregiver_id": self.test_caregiver_id,
                    "emergency_type": "emotional",
                    "severity": "medium",
                    "description": "テスト用の緊急状況",
                    "actions_taken": ["声をかけた"],
                    "generate_guidance": False,
                    "generate_summary": False
                }
            )
            # 401 is expected (unauthenticated); 400/500 is a problem
            assert response.status_code in [200, 401, 400], f"Unexpected status code: {response.status_code}"
            
            # Test get history endpoint
            response = self.client.get(f"/api/emergency/history?elder_id={self.test_elder_id}")
            assert response.status_code in [200, 401], f"Unexpected status code: {response.status_code}"
            
            print_success("Emergency API endpoint tests passed")
            return True
        except Exception as e:
            print_error(f"Emergency API endpoint tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_database_models(self) -> bool:
        """Test database models"""
        print_info("Test database models...")
        
        try:
            # Test NightModeConfigDB model
            from models.emergency_models import NightModeConfigDB
            config = NightModeConfigDB(
                config_id="test_config_123",
                user_id=self.test_user_id,
                user_type="elder",
                enabled=True,
                brightness="low"
            )
            assert config.config_id == "test_config_123"
            assert config.user_id == self.test_user_id
            assert config.enabled is True
            
            # Test EmergencyRecordDB model
            from models.emergency_models import EmergencyRecordDB
            record = EmergencyRecordDB(
                record_id="test_record_123",
                elder_id=self.test_elder_id,
                caregiver_id=self.test_caregiver_id,
                emergency_type="emotional",
                severity="medium",
                description="テスト"
            )
            assert record.record_id == "test_record_123"
            assert record.emergency_type == "emotional"
            assert record.severity == "medium"
            
            print_success("Database model tests passed")
            return True
        except Exception as e:
            print_error(f"Database model tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_frontend_components(self) -> bool:
        """Test frontend component files exist"""
        print_info("Testing frontend component files...")
        
        try:
            frontend_path = project_root.parent / "frontend" / "src" / "components"
            
            # Check NightMode component
            night_mode_jsx = frontend_path / "NightMode.jsx"
            night_mode_css = frontend_path / "NightMode.css"
            assert night_mode_jsx.exists(), f"NightMode.jsx not found at {night_mode_jsx}"
            assert night_mode_css.exists(), f"NightMode.css not found at {night_mode_css}"
            
            # Check EmergencyRecord component
            emergency_jsx = frontend_path / "EmergencyRecord.jsx"
            emergency_css = frontend_path / "EmergencyRecord.css"
            assert emergency_jsx.exists(), f"EmergencyRecord.jsx not found at {emergency_jsx}"
            assert emergency_css.exists(), f"EmergencyRecord.css not found at {emergency_css}"
            
            # Check file contents (basic syntax check)
            night_mode_content = night_mode_jsx.read_text()
            assert "export default" in night_mode_content or "export" in night_mode_content, "NightMode.jsx missing export"
            assert "NightMode" in night_mode_content, "NightMode.jsx missing component name"
            
            emergency_content = emergency_jsx.read_text()
            assert "export default" in emergency_content or "export" in emergency_content, "EmergencyRecord.jsx missing export"
            assert "EmergencyRecord" in emergency_content, "EmergencyRecord.jsx missing component name"
            
            print_success("Frontend component file tests passed")
            return True
        except Exception as e:
            print_error(f"Frontend component file tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_app_integration(self) -> bool:
        """Test App.jsx integration"""
        print_info("Test App.jsx integration...")
        
        try:
            app_jsx_path = project_root.parent / "frontend" / "src" / "App.jsx"
            assert app_jsx_path.exists(), f"App.jsx not found at {app_jsx_path}"
            
            app_content = app_jsx_path.read_text()
            
            # Check NightMode import
            assert "NightMode" in app_content, "App.jsx missing NightMode import"
            assert "night-mode" in app_content or "nightMode" in app_content, "App.jsx missing night-mode route"
            
            # Check EmergencyRecord import
            assert "EmergencyRecord" in app_content, "App.jsx missing EmergencyRecord import"
            assert "showEmergencyRecord" in app_content or "emergency" in app_content.lower(), "App.jsx missing emergency record state"
            
            # Check icon imports
            assert "Moon" in app_content or "AlertTriangle" in app_content, "App.jsx missing icon imports"
            
            print_success("App.jsx integration tests passed")
            return True
        except Exception as e:
            print_error(f"App.jsx integration tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("Starting Scenario D feature verification tests")
        print("="*60 + "\n")
        
        tests = [
            ("Database models", self.test_database_models),
            ("Night mode service", self.test_night_mode_service),
            ("Emergency service", self.test_emergency_service),
            ("Reminder service", self.test_reminder_service),
            ("Night mode API endpoints", self.test_night_mode_api),
            ("Emergency API endpoints", self.test_emergency_api),
            ("Frontend component files", self.test_frontend_components),
            ("App.jsx integration", self.test_app_integration),
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
            print_success("\n🎉 All tests passed! Scenario D feature verification succeeded!")
            return True
        else:
            print_error(f"\n⚠️  There are {self.test_results['failed']} test(s) failed")
            return False


if __name__ == "__main__":
    tester = ScenarioDFeaturesTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
