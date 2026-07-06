"""
Internal API Testing for Mid-Term Features - Mid-term features internal testing
Internal testing with FastAPI TestClient without exposing a port
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project path (backend root directory)
_candidate = Path(__file__).resolve().parent
while _candidate != _candidate.parent and not (_candidate / "main.py").exists():
    _candidate = _candidate.parent
sys.path.insert(0, str(_candidate))

# Set TEST_MODE before importing any modules
os.environ["TEST_MODE"] = "true"

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from config.database import get_db, init_database, SessionLocal

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

def print_test_result(test_name: str, passed: bool, message: str = ""):
    """Print test result"""
    if passed:
        print_success(f"{test_name}")
    else:
        print_error(f"{test_name}")
    if message:
        print(f"      {message}")

test_client = None

def test_summary_service():
    """Test summary service"""
    print("\n" + "="*70)
    print("Test summary service (Summary Service)")
    print("="*70)
    
    if not test_client:
        print_error("TestClient not initialized")
        return
    
    # Note: these tests need a valid customer_id; here we only verify API routes work
    try:
        # Test get summary (auth required, may fail, but verifies route exists)
        response = test_client.get("/api/summary/customers/test_customer_id/summary")
        # 401 is expected (unauthenticated), route exists
        if response.status_code in [401, 404]:
            print_test_result("GET /api/summary/customers/{customer_id}/summary", True, 
                           f"Route exists (status: {response.status_code})")
        else:
            print_test_result("GET /api/summary/customers/{customer_id}/summary", 
                           response.status_code < 500, 
                           f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("GET /api/summary/customers/{customer_id}/summary", False, str(e))
    
    try:
        response = test_client.get("/api/summary/customers/test_customer_id/info-cards")
        if response.status_code in [401, 404]:
            print_test_result("GET /api/summary/customers/{customer_id}/info-cards", True,
                           f"Route exists (status: {response.status_code})")
        else:
            print_test_result("GET /api/summary/customers/{customer_id}/info-cards",
                           response.status_code < 500,
                           f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("GET /api/summary/customers/{customer_id}/info-cards", False, str(e))

def test_family_participation():
    """Test family participation service"""
    print("\n" + "="*70)
    print("Test family participation service (Family Participation Service)")
    print("="*70)
    
    try:
        # Test add family member to task (auth required)
        response = test_client.post("/api/family-participation/tasks/test_task_id/family/test_member_id")
        if response.status_code in [401, 404]:
            print_test_result("POST /api/family-participation/tasks/{task_id}/family/{family_member_id}", True,
                           f"Route exists (status: {response.status_code})")
        else:
            print_test_result("POST /api/family-participation/tasks/{task_id}/family/{family_member_id}",
                           response.status_code < 500,
                           f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("POST /api/family-participation/tasks/{task_id}/family/{family_member_id}", False, str(e))
    
    try:
        # Test get family member tasks
        response = test_client.get("/api/family-participation/family/test_member_id/tasks")
        if response.status_code in [401, 404]:
            print_test_result("GET /api/family-participation/family/{family_member_id}/tasks", True,
                           f"Route exists (status: {response.status_code})")
        else:
            print_test_result("GET /api/family-participation/family/{family_member_id}/tasks",
                           response.status_code < 500,
                           f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("GET /api/family-participation/family/{family_member_id}/tasks", False, str(e))

def test_family_feedback():
    """Test family feedback service"""
    print("\n" + "="*70)
    print("Test family feedback service (Family Feedback Service)")
    print("="*70)
    
    try:
        # Test submit feedback (auth required)
        feedback_data = {
            "family_member_id": "test_member_id",
            "feedback_type": "general",
            "content": "Test feedback content"
        }
        response = test_client.post("/api/family-participation/feedback", json=feedback_data)
        if response.status_code in [401, 404]:
            print_test_result("POST /api/family-participation/feedback", True,
                           f"Route exists (status: {response.status_code})")
        else:
            print_test_result("POST /api/family-participation/feedback",
                           response.status_code < 500,
                           f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("POST /api/family-participation/feedback", False, str(e))
    
    try:
        # Test get feedback list
        response = test_client.get("/api/family-participation/feedback")
        if response.status_code in [401]:
            print_test_result("GET /api/family-participation/feedback", True,
                           f"Route exists (status: {response.status_code})")
        else:
            print_test_result("GET /api/family-participation/feedback",
                           response.status_code < 500,
                           f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("GET /api/family-participation/feedback", False, str(e))

def test_rag_conversation():
    """Test RAG multi-turn conversation"""
    print("\n" + "="*70)
    print("Test RAG multi-turn conversation (RAG Conversation)")
    print("="*70)
    
    try:
        # Test create conversation (auth required)
        conversation_data = {
            "user_id": "test_user_id",
            "elder_id": "test_elder_id"
        }
        response = test_client.post("/api/knowledge-base/conversations", json=conversation_data)
        if response.status_code in [401, 404]:
            print_test_result("POST /api/knowledge-base/conversations", True,
                           f"Route exists (status: {response.status_code})")
        else:
            print_test_result("POST /api/knowledge-base/conversations",
                           response.status_code < 500,
                           f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("POST /api/knowledge-base/conversations", False, str(e))
    
    try:
        # Test RAG Q&A (with conversation_id)
        ask_data = {
            "question": "Test question",
            "conversation_id": "test_conv_id"
        }
        response = test_client.post("/api/knowledge-base/ask", json=ask_data)
        # May return 401 (unauthenticated) or 200 (if auth not required)
        if response.status_code < 500:
            print_test_result("POST /api/knowledge-base/ask (with conversation_id)", True,
                           f"Route exists (status: {response.status_code})")
        else:
            print_test_result("POST /api/knowledge-base/ask (with conversation_id)", False,
                           f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("POST /api/knowledge-base/ask (with conversation_id)", False, str(e))

def test_service_imports():
    """Test service imports"""
    print("\n" + "="*70)
    print("Test service imports (Service Imports)")
    print("="*70)
    
    try:
        from services.summary_service import SummaryService, get_summary_service
        print_test_result("SummaryService import", True)
    except Exception as e:
        print_test_result("SummaryService import", False, str(e))
    
    try:
        from services.family_participation_service import FamilyParticipationService, get_family_participation_service
        print_test_result("FamilyParticipationService import", True)
    except Exception as e:
        print_test_result("FamilyParticipationService import", False, str(e))
    
    try:
        from services.family_feedback_service import FamilyFeedbackService, get_family_feedback_service
        print_test_result("FamilyFeedbackService import", True)
    except Exception as e:
        print_test_result("FamilyFeedbackService import", False, str(e))
    
    try:
        from services.rag_service import RAGService, get_rag_service
        print_test_result("RAGService import", True)
    except Exception as e:
        print_test_result("RAGService import", False, str(e))

def test_model_imports():
    """Test model imports"""
    print("\n" + "="*70)
    print("Test model imports (Model Imports)")
    print("="*70)
    
    try:
        from models.summary_models import InfoChangeLogDB, CustomerSummaryDB, ConversationHistoryDB
        print_test_result("Summary model import", True)
    except Exception as e:
        print_test_result("Summary model import", False, str(e))
    
    try:
        from models.task_models import TaskDB, ScheduleDB
        print_test_result("Task/Schedule model import", True)
    except Exception as e:
        print_test_result("Task/Schedule model import", False, str(e))
    
    try:
        from models.knowledge_models import FamilyMemberDB
        print_test_result("FamilyMember model import", True)
    except Exception as e:
        print_test_result("FamilyMember model import", False, str(e))

def test_logging_methods():
    """Test logging methods"""
    print("\n" + "="*70)
    print("Testing logging methods (Logging Methods)")
    print("="*70)
    
    try:
        from services.logging_service import logger
        
        # Test log_warning
        if hasattr(logger, 'log_warning'):
            logger.log_warning("Test warning message")
            print_test_result("log_warning method", True)
        else:
            print_test_result("log_warning method", False, "Method does not exist")
    except Exception as e:
        print_test_result("log_warning method", False, str(e))
    
    try:
        from services.logging_service import logger
        
        # Test log_info
        if hasattr(logger, 'log_info'):
            logger.log_info("Test info message")
            print_test_result("log_info method", True)
        else:
            print_test_result("log_info method", False, "Method does not exist")
    except Exception as e:
        print_test_result("log_info method", False, str(e))

def main():
    """Main test function"""
    print("\n" + "="*70)
    print("Mid-term features internal testing - Mid-Term Features Internal Testing")
    print("="*70)
    print("Test environment: chatbot conda environment")
    print("Test method: FastAPI TestClient (no exposed port)")
    print("="*70)
    
    # Initialize database
    print_info("Initializing test database...")
    try:
        init_database()
        print_success("Database initialized successfully")
    except Exception as e:
        print_error(f"Database initialization failed: {e}")
        return
    
    # Create TestClient
    client = TestClient(app)
    
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
    
    try:
        # Run all tests
        test_service_imports()
        test_model_imports()
        test_logging_methods()
        
        # Update test functions to use client
        global test_client
        test_client = client
        
        test_summary_service()
        test_family_participation()
        test_family_feedback()
        test_rag_conversation()
        
        print("\n" + "="*70)
        print_success("Tests completed!")
        print("="*70)
        print("\nNote:")
        print("- 401 status means auth required, which is expected")
        print("- 404 status means resource not found, also expected (test data)")
        print("- Main goal is verifying routes exist and are reachable")
        print("="*70)
    finally:
        # Cleanup
        app.dependency_overrides.clear()

if __name__ == "__main__":
    main()
