"""
Pytest configuration and fixtures
"""
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_BACKEND_ROOT = _REPO_ROOT / "backend"
for _path in (_REPO_ROOT, _BACKEND_ROOT):
    _path_str = str(_path)
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from models.database import Base
from models.auth_models import UserAuthDB, DeviceDB
from models.customer_models import CustomerDB

# Internal API tests should not apply rate limits
os.environ.setdefault("TEST_MODE", "true")

# Create in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def app():
    """FastAPI app with production error handlers registered."""
    from main import app as fastapi_app
    return fastapi_app


@pytest.fixture(scope="session")
def client(app):
    """TestClient mirroring production app configuration (including error handlers)."""
    return TestClient(app)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing"""
    return {
        "customer_id": "test_customer_001",
        "customer_type": "caregiver",
        "name": "Test Caregiver",
        "name_ja": "テスト介護者",
        "email": "test@example.com",
        "phone": "1234567890",
        "role": "caregiver",
        "experience_years": 5
    }


@pytest.fixture
def sample_elder_data():
    """Sample elder data for testing"""
    return {
        "customer_id": "test_elder_001",
        "customer_type": "elder",
        "name": "Test Elder",
        "name_ja": "テスト高齢者",
        "health_conditions": ["dementia"],
        "interests": ["crafts", "music"],
        "mobility_level": "limited"
    }


@pytest.fixture
def sample_user_auth_data():
    """Sample user authentication data"""
    return {
        "user_id": "test_user_001",
        "email": "test@example.com",
        "password": "test_password_123",
        "username": "testuser"
    }
