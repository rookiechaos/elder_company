"""
Care Terms API Routes
"""

from fastapi import APIRouter, Query
from typing import Optional

from services.care_terms_service import CareTermsService

router = APIRouter(prefix="/api/care-terms", tags=["care-terms"])

care_terms_service = CareTermsService()


@router.get("")
async def get_all_terms(category: Optional[str] = Query(None, description="Filter by category")):
    """Get all care terms"""
    if category:
        terms = care_terms_service.get_terms_by_category(category)
    else:
        terms = care_terms_service.get_all_terms()
    
    return {
        "terms": terms,
        "count": len(terms),
        "categories": list(care_terms_service.terms_database.keys())
    }


@router.get("/search")
async def search_terms(q: str = Query(..., description="Search query")):
    """Search terms"""
    results = care_terms_service.search_terms(q)
    
    return {
        "query": q,
        "results": results,
        "count": len(results)
    }


@router.get("/translate")
async def translate_term(
    term: str = Query(..., description="Term to translate"),
    source_language: str = Query("ja", description="Source language"),
    target_language: str = Query("zh", description="Target language")
):
    """Translate a single term"""
    result = care_terms_service.get_term_translation(term, source_language, target_language)
    
    if not result:
        return {
            "found": False,
            "message": f"Term '{term}' not found in database"
        }
    
    return {
        "found": True,
        "translation": result
    }


@router.get("/scenarios")
async def get_care_scenarios():
    """Get care scenario templates"""
    scenarios = care_terms_service.get_care_scenarios()
    
    return {
        "scenarios": scenarios,
        "count": len(scenarios)
    }
