"""
Knowledge Base API Routes

doc_type medical denotes health/medical reference material for care communication and records; not medical advice.
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from dependencies import require_auth, get_rag_service_dependency, get_optional_user
from services.rag_service import RAGService
from middleware.rate_limit import rate_limit, RATE_LIMITS
from middleware.api_decorators import handle_api_errors
from exceptions import ValidationError

router = APIRouter(prefix="/api/knowledge-base", tags=["knowledge-base"])


class AddDocumentRequest(BaseModel):
    """Add document request"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    doc_type: str = Field(
        ...,
        description="Document type: medical (health/medical reference for care communication and records, not medical advice), diet, care_guide"
    )
    category: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: bool = False
    
    @validator('doc_type')
    def validate_doc_type(cls, v):
        valid_types = ['medical', 'diet', 'care_guide']
        if v not in valid_types:
            raise ValueError(f'Document type must be one of: {", ".join(valid_types)}')
        return v


class AskRequest(BaseModel):
    """RAG Q&A request"""
    question: str = Field(..., min_length=1, max_length=500)
    context: Optional[Dict[str, Any]] = None  # Includes elder_id, doc_type, category, etc.
    top_k: int = Field(3, ge=1, le=10)
    conversation_id: Optional[str] = None  # Conversation ID (for multi-turn dialogue)
    language: Optional[str] = Field("ja", description="Disclaimer language: zh, ja, en")


class CreateConversationRequest(BaseModel):
    """Create conversation request"""
    user_id: Optional[str] = None
    elder_id: Optional[str] = None


@router.post("/documents")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def add_document(
    request: AddDocumentRequest,
    current_user: dict = Depends(require_auth),
    rag_service: RAGService = Depends(get_rag_service_dependency)
):
    """Add document to knowledge base. doc_type medical is reference material; not medical advice."""
    doc = rag_service.add_document(
        title=request.title,
        content=request.content,
        doc_type=request.doc_type,
        category=request.category,
        source=request.source,
        source_url=request.source_url,
        tags=request.tags,
        org_id=current_user.get("org_id"),
        created_by=current_user.get("user_id"),
        is_public=request.is_public
    )
    
    return {
        "message": "Document added successfully",
        "document": doc
    }


@router.get("/documents")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def search_documents(
    q: Optional[str] = Query(None, description="Search query"),
    doc_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    tags: Optional[str] = Query(None, description="Tags (comma-separated)"),
    top_k: int = Query(5, ge=1, le=20),
    current_user: Optional[dict] = Depends(get_optional_user),
    rag_service: RAGService = Depends(get_rag_service_dependency)
):
    """Search documents"""
    if not q:
        raise ValidationError("Search query 'q' is required")
    
    tag_list = tags.split(",") if tags else None
    
    docs = rag_service.search_documents(
        query=q,
        doc_type=doc_type,
        category=category,
        tags=tag_list,
        top_k=top_k,
        org_id=current_user.get("org_id") if current_user else None
    )
    
    return {
        "documents": docs,
        "count": len(docs)
    }


@router.post("/conversations")
@rate_limit(limit=RATE_LIMITS.get("default", "20/minute"))
@handle_api_errors
async def create_conversation(
    request: CreateConversationRequest,
    current_user: dict = Depends(require_auth),
    rag_service: RAGService = Depends(get_rag_service_dependency)
):
    """Create a new conversation (for multi-turn dialogue)"""
    conversation_id = rag_service.create_conversation(
        user_id=request.user_id or current_user.get("user_id"),
        elder_id=request.elder_id,
        org_id=current_user.get("org_id")
    )
    
    return {
        "conversation_id": conversation_id,
        "message": "Conversation created successfully"
    }


@router.post("/ask")
@rate_limit(limit=RATE_LIMITS.get("default", "20/minute"))
@handle_api_errors
async def ask_question(
    request: AskRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
    rag_service: RAGService = Depends(get_rag_service_dependency)
):
    """RAG Q&A (supports multi-turn dialogue)"""
    result = rag_service.ask(
        question=request.question,
        context=request.context,
        top_k=request.top_k,
        conversation_id=request.conversation_id,
        language=request.language or "ja"
    )
    
    return result


@router.get("/sources")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_sources(
    current_user: Optional[dict] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get official source list"""
    from models.knowledge_models import KnowledgeBaseDB
    
    sources = db.query(KnowledgeBaseDB.source).filter(
        and_(
            KnowledgeBaseDB.source.isnot(None),
            KnowledgeBaseDB.is_active == True
        )
    ).distinct().all()
    
    source_list = [s[0] for s in sources if s[0]]
    
    return {
        "sources": source_list,
        "count": len(source_list)
    }
