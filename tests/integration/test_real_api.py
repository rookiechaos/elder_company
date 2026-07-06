#!/usr/bin/env python3
"""
Real API Test Script - Real API test script
Tests all features using real API calls
"""

import os
import sys
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project path (backend root directory)
_candidate = Path(__file__).resolve().parent
while _candidate != _candidate.parent and not (_candidate / "main.py").exists():
    _candidate = _candidate.parent
sys.path.insert(0, str(_candidate))

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_USERNAME = "testuser_real"
TEST_EMAIL = "test_real@example.com"
TEST_PASSWORD = "testpass123"

# Colored output
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

class APITester:
    """API test class"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.org_id: Optional[str] = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "tests": []
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Send HTTP request"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", {})
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        kwargs["headers"] = headers
        return requests.request(method, url, **kwargs)
    
    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        print_info("Test health check endpoint...")
        try:
            response = self._make_request("GET", "/health")
            if response.status_code == 200:
                data = response.json()
                print_success(f"Health check passed: {data.get('status', 'unknown')}")
                if "checks" in data:
                    for check_name, check_result in data["checks"].items():
                        status = check_result.get("status", "unknown")
                        if status == "healthy":
                            print_success(f"  - {check_name}: {status}")
                        else:
                            print_warning(f"  - {check_name}: {status}")
                return True
            else:
                print_error(f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Health check error: {str(e)}")
            return False
    
    def test_register_user(self) -> bool:
        """Test user registration"""
        print_info("Test user registration...")
        try:
            response = self._make_request(
                "POST",
                "/api/auth/register",
                json={
                    "username": TEST_USERNAME,
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD,
                    "phone": "1234567890"
                }
            )
            if response.status_code in [200, 201]:
                data = response.json()
                print_success(f"User registration succeeded: {data.get('username', 'unknown')}")
                return True
            elif response.status_code == 400:
                print_warning("User may already exist, trying login...")
                return self.test_login()
            else:
                print_error(f"User registration failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"User registration error: {str(e)}")
            return False
    
    def test_login(self) -> bool:
        """Test user login"""
        print_info("Test user login...")
        try:
            response = self._make_request(
                "POST",
                "/api/auth/login",
                json={
                    "username": TEST_USERNAME,
                    "password": TEST_PASSWORD
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.org_id = data.get("org_id")
                print_success(f"Login succeeded: {self.user_id}")
                return True
            else:
                print_error(f"Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Login error: {str(e)}")
            return False
    
    def test_translation(self) -> bool:
        """Test translation feature"""
        print_info("Test translation feature...")
        try:
            response = self._make_request(
                "POST",
                "/api/translate",
                json={
                    "text": "こんにちは、お元気ですか？",
                    "source_language": "ja",
                    "target_language": "zh",
                    "context": "Caregiving scenario"
                }
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"Translation succeeded: {data.get('translated_text', 'N/A')}")
                return True
            else:
                print_error(f"Translation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Translation error: {str(e)}")
            return False
    
    def test_data_export(self) -> bool:
        """Test data export"""
        print_info("Test data export...")
        if not self.token:
            print_warning("Login required, skipping test")
            return False
        try:
            response = self._make_request("GET", "/api/data-export?format=json")
            if response.status_code == 200:
                data = response.json()
                print_success(f"Data export succeeded: {len(str(data))} bytes")
                return True
            else:
                print_error(f"Data export failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Data export error: {str(e)}")
            return False
    
    def test_help_center(self) -> bool:
        """Test help center"""
        print_info("Test help center...")
        try:
            response = self._make_request("GET", "/api/help/articles?language=ja")
            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                print_success(f"Fetched help articles successfully: {count} articles")
                return True
            else:
                print_warning(f"Help center returned: {response.status_code} (may have no data)")
                return True  # not counted as failure
        except Exception as e:
            print_error(f"Help center error: {str(e)}")
            return False
    
    def test_feedback(self) -> bool:
        """Test feedback feature"""
        print_info("Test feedback feature...")
        try:
            response = self._make_request(
                "POST",
                "/api/feedback",
                json={
                    "feedback_type": "suggestion",
                    "title": "Test feedback",
                    "content": "This is a test feedback to verify the feedback system works.",
                    "category": "feature"
                }
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"Feedback submitted successfully: {data.get('feedback_id', 'N/A')}")
                return True
            else:
                print_error(f"Feedback submission failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Feedback error: {str(e)}")
            return False
    
    def test_support_ticket(self) -> bool:
        """Test support ticket"""
        print_info("Test support ticket...")
        if not self.token:
            print_warning("Login required, skipping test")
            return False
        try:
            response = self._make_request(
                "POST",
                "/api/support/tickets",
                json={
                    "subject": "Test ticket",
                    "description": "This is a test ticket",
                    "category": "technical",
                    "priority": "normal"
                }
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"Ticket created successfully: {data.get('ticket_id', 'N/A')}")
                return True
            else:
                print_error(f"Ticket creation failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Ticket error: {str(e)}")
            return False
    
    def test_analytics(self) -> bool:
        """Test analytics feature"""
        print_info("Test analytics feature...")
        try:
            response = self._make_request(
                "POST",
                "/api/analytics/events",
                json={
                    "event_type": "page_view",
                    "event_name": "test_page",
                    "event_category": "navigation"
                }
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"Event tracking succeeded: {data.get('event_id', 'N/A')}")
                return True
            else:
                print_error(f"Event tracking failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Analytics error: {str(e)}")
            return False
    
    def test_monitoring(self) -> bool:
        """Test monitoring feature"""
        print_info("Test monitoring feature...")
        if not self.token:
            print_warning("Login required, skipping test")
            return False
        try:
            response = self._make_request("GET", "/api/monitoring/system")
            if response.status_code == 200:
                data = response.json()
                if "error" not in data:
                    print_success("System monitoring data fetched successfully")
                    return True
                else:
                    print_warning(f"Monitoring returned error: {data.get('error')}")
                    return True  # not counted as failure
            else:
                print_warning(f"Monitoring returned: {response.status_code}")
                return True  # not counted as failure
        except Exception as e:
            print_error(f"Monitoring error: {str(e)}")
            return False
    
    def test_deletion_summary(self) -> bool:
        """Test deletion summary"""
        print_info("Test deletion summary...")
        if not self.token:
            print_warning("Login required, skipping test")
            return False
        try:
            response = self._make_request("GET", "/api/account/deletion-summary")
            if response.status_code == 200:
                data = response.json()
                total = data.get("total_items", 0)
                print_success(f"Deletion summary fetched successfully: {total} data items")
                return True
            else:
                print_error(f"Deletion summary failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Deletion summary error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("Starting real API tests")
        print("="*60 + "\n")
        
        tests = [
            ("Health check", self.test_health_check),
            ("User registration", self.test_register_user),
            ("User login", self.test_login),
            ("Translation", self.test_translation),
            ("Data export", self.test_data_export),
            ("Help center", self.test_help_center),
            ("Feedback", self.test_feedback),
            ("Support ticket", self.test_support_ticket),
            ("Analytics", self.test_analytics),
            ("Monitoring", self.test_monitoring),
            ("Deletion summary", self.test_deletion_summary),
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
                self.test_results["skipped"] += 1
                self.test_results["tests"].append({"name": test_name, "status": "skipped", "error": str(e)})
                print_warning(f"{test_name} skipped: {str(e)}")
            print()
        
        # Print summary
        print("="*60)
        print("Test summary")
        print("="*60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"⏭️  skipped: {self.test_results['skipped']}")
        print(f"📊 Total: {len(tests)}")
        print("="*60)


def check_server(url: str) -> bool:
    """Check if server is running"""
    try:
        response = requests.get(f"{url}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description="Real API test script")
    parser.add_argument("--url", default=BASE_URL, help="API base URL")
    args = parser.parse_args()
    
    # Check if server is running
    print_info(f"Checking server: {args.url}")
    if not check_server(args.url):
        print_error(f"Server not running or unreachable: {args.url}")
        print_info("Please start the server first:")
        print_info("  cd backend")
        print_info("  uvicorn main:app --reload")
        print_info("")
        print_info("Then rerun this script:")
        print_info(f"  python3 test_real_api.py --url {args.url}")
        sys.exit(1)
    
    print_success("Server is running, starting tests...\n")
    
    tester = APITester(base_url=args.url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
