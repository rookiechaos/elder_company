"""
RAG Service Unit Tests
"""

import pytest
from sqlalchemy.orm import Session

from services.rag_service import RAGService, get_rag_service
from models.knowledge_models import KnowledgeBaseDB
from config.database import SessionLocal, init_database


@pytest.fixture
def db_session():
    """Create test database session"""
    init_database()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def rag_service(db_session):
    """Create RAG service instance"""
    return get_rag_service(db_session)


class TestRAGService:
    """RAG service test class"""
    
    def test_add_document(self, rag_service):
        """Test add document"""
        doc = rag_service.add_document(
            title="Test document",
            content="This is test document content.",
            doc_type="care_guide",
            category="Test category",
            source="Test source",
            source_url="https://example.com",
            tags=["test", "document"]
        )
        
        assert doc is not None
        assert doc["title"] == "Test document"
        assert doc["doc_type"] == "care_guide"
        assert doc["category"] == "Test category"
        assert "doc_id" in doc
    
    def test_search_documents(self, rag_service):
        """Test search documents"""
        # Add document
        rag_service.add_document(
            title="認知症ケアガイド",
            content="認知症の方へのケアの基本について説明します。",
            doc_type="care_guide",
            category="認知症"
        )
        
        # Search documents
        results = rag_service.search_documents(
            query="認知症",
            top_k=5
        )
        
        assert len(results) >= 1
        assert any("認知症" in doc["title"] or "認知症" in doc["content"] for doc in results)
    
    def test_search_documents_by_type(self, rag_service):
        """Test search documents by type"""
        # Add documents of different types
        rag_service.add_document(
            title="医療ガイド",
            content="医療に関する情報です。",
            doc_type="medical"
        )
        rag_service.add_document(
            title="食事ガイド",
            content="食事に関する情報です。",
            doc_type="diet"
        )
        
        # Search by type
        medical_docs = rag_service.search_documents(
            query="医療",
            doc_type="medical",
            top_k=5
        )
        
        assert len(medical_docs) >= 1
        assert all(doc["doc_type"] == "medical" for doc in medical_docs)
    
    def test_ask_question(self, rag_service):
        """Test RAG Q&A"""
        # Add document
        rag_service.add_document(
            title="認知症ケア",
            content="認知症の方へのケアでは、優しく接することが重要です。",
            doc_type="care_guide",
            source="厚生労働省",
            source_url="https://example.com"
        )
        
        # Ask question
        result = rag_service.ask(
            question="認知症の方へのケアの注意点は？",
            top_k=3
        )
        
        assert result is not None
        assert "answer" in result
        assert "sources" in result
        assert "disclaimer" in result
        assert len(result["answer"]) > 0
        assert len(result["sources"]) >= 1
    
    def test_ask_question_no_results(self, rag_service):
        """Test Q&A when no results are found"""
        result = rag_service.ask(
            question="存在しない情報について",
            top_k=3
        )
        
        assert result is not None
        assert "answer" in result
        assert "sources" in result
        assert len(result["sources"]) == 0
