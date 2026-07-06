"""
Help Center Routes - Help articles and FAQ
Help Center Routes - Help articles and FAQs
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session

from dependencies import get_optional_user, get_help_service_dependency
from services.help_service import HelpService
from middleware.api_decorators import handle_api_errors
from exceptions import NotFoundError

router = APIRouter(prefix="/api/help", tags=["help"])


class FeedbackRequest(BaseModel):
    """Feedback request"""
    article_id: Optional[str] = None
    faq_id: Optional[str] = None
    feedback_type: str = "helpful"  # helpful, not_helpful, comment
    comment: Optional[str] = None


@router.get("/articles")
@handle_api_errors
async def get_articles(
    category: Optional[str] = Query(None, description="Filter by category"),
    language: str = Query("ja", description="Language (ja, zh, en)"),
    featured_only: bool = Query(False, description="Only featured articles"),
    search: Optional[str] = Query(None, description="Search query"),
    help_service: HelpService = Depends(get_help_service_dependency)
):
    """Get help article list"""
    articles = help_service.get_articles(
        category=category,
        language=language,
        featured_only=featured_only,
        search_query=search
    )
    
    return {
        "articles": articles,
        "count": len(articles)
    }


@router.get("/articles/{article_id}")
@handle_api_errors
async def get_article(
    article_id: str,
    language: str = Query("ja", description="Language (ja, zh, en)"),
    help_service: HelpService = Depends(get_help_service_dependency)
):
    """Get a single help article"""
    article = help_service.get_article(article_id, language=language)
    
    if not article:
        raise NotFoundError("Article not found")
    
    return article


@router.get("/faqs")
@handle_api_errors
async def get_faqs(
    category: Optional[str] = Query(None, description="Filter by category"),
    language: str = Query("ja", description="Language (ja, zh, en)"),
    featured_only: bool = Query(False, description="Only featured FAQs"),
    search: Optional[str] = Query(None, description="Search query"),
    help_service: HelpService = Depends(get_help_service_dependency)
):
    """Get FAQ list"""
    faqs = help_service.get_faqs(
        category=category,
        language=language,
        featured_only=featured_only,
        search_query=search
    )
    
    return {
        "faqs": faqs,
        "count": len(faqs)
    }


@router.get("/faqs/{faq_id}")
@handle_api_errors
async def get_faq(
    faq_id: str,
    language: str = Query("ja", description="Language (ja, zh, en)"),
    help_service: HelpService = Depends(get_help_service_dependency)
):
    """Get a single FAQ"""
    faq = help_service.get_faq(faq_id, language=language)
    
    if not faq:
        raise NotFoundError("FAQ not found")
    
    return faq


@router.post("/feedback")
@handle_api_errors
async def submit_feedback(
    request: FeedbackRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
    help_service: HelpService = Depends(get_help_service_dependency)
):
    """Submit feedback"""
    user_id = current_user.get("user_id") if current_user else None
    
    result = help_service.submit_feedback(
        article_id=request.article_id,
        faq_id=request.faq_id,
        feedback_type=request.feedback_type,
        comment=request.comment,
        user_id=user_id
    )
    
    return result


@router.get("/categories")
@handle_api_errors
async def get_categories(help_service: HelpService = Depends(get_help_service_dependency)):
    """Get all categories"""
    categories = help_service.get_categories()
    
    return {
        "categories": categories,
        "count": len(categories)
    }


@router.get("/search")
@handle_api_errors
async def search_help(
    q: str = Query(..., description="Search query"),
    language: str = Query("ja", description="Language (ja, zh, en)"),
    help_service: HelpService = Depends(get_help_service_dependency)
):
    """Search help content"""
    results = help_service.search(q, language=language)
    
    return results
