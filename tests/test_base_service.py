"""
Tests for BaseService class
测试基础服务类
"""

import pytest
from sqlalchemy.orm import Session
from unittest.mock import Mock

from services.base_service import BaseService


class TestBaseService:
    """Test BaseService class"""
    
    def test_init_with_db(self):
        """Test initialization with database session"""
        mock_db = Mock(spec=Session)
        service = BaseService(db=mock_db)
        
        assert service.db == mock_db
    
    def test_init_without_db(self):
        """Test initialization without database session"""
        service = BaseService()
        
        assert service.db is None
    
    def test_get_db_with_session(self):
        """Test get_db when session is available"""
        mock_db = Mock(spec=Session)
        service = BaseService(db=mock_db)
        
        db = service.get_db()
        assert db == mock_db
    
    def test_get_db_without_session(self):
        """Test get_db when session is not available"""
        service = BaseService()
        
        with pytest.raises(ValueError) as exc_info:
            service.get_db()
        
        assert "Database session not available" in str(exc_info.value)
    
    def test_ensure_db_with_session(self):
        """Test ensure_db when session is available"""
        mock_db = Mock(spec=Session)
        service = BaseService(db=mock_db)
        
        db = service.ensure_db()
        assert db == mock_db
    
    def test_ensure_db_without_session(self):
        """Test ensure_db when session is not available"""
        service = BaseService()
        
        with pytest.raises(ValueError) as exc_info:
            service.ensure_db()
        
        assert "Database session not available" in str(exc_info.value)
