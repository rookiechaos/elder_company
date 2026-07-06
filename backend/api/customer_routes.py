"""
Customer Management API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from services.customer_service import CustomerService
from dependencies import require_auth, get_customer_service_dependency
from services.logging_service import logger
from config.database import get_db
from exceptions import CustomerNotFoundError, ValidationError, ConflictError
from middleware.api_decorators import handle_api_errors

router = APIRouter(prefix="/api/customers", tags=["customers"])


class CustomerCreateRequest(BaseModel):
    """Create customer request"""
    customer_type: str  # caregiver, elder, family_member
    name: str
    name_ja: Optional[str] = None
    name_zh: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None  # ISO format
    age: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    prefecture: Optional[str] = None
    country: Optional[str] = "Japan"
    native_language: Optional[str] = "ja"
    spoken_languages: Optional[List[str]] = []
    preferred_language: Optional[str] = "ja"
    org_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Caregiver specific
    role: Optional[str] = None
    experience_years: Optional[int] = None
    work_shift: Optional[str] = None
    specialties: Optional[List[str]] = None
    
    # Elder specific
    health_status: Optional[str] = None
    health_conditions: Optional[List[str]] = None
    mobility_level: Optional[str] = None
    cognitive_level: Optional[str] = None
    interests: Optional[List[str]] = None
    hobbies: Optional[List[str]] = None


class CareRelationshipRequest(BaseModel):
    """Create care relationship request"""
    caregiver_id: str
    elder_id: str
    relationship_type: Optional[str] = "professional"
    care_frequency: Optional[str] = None
    care_duration_hours: Optional[float] = None


class PersonalizationDataRequest(BaseModel):
    """Personalization data request"""
    data_type: str  # translation_pref, activity_pref, communication_pref
    preference_data: Dict[str, Any]
    source: Optional[str] = "explicit"
    confidence_score: Optional[float] = 1.0


class BehaviorLogRequest(BaseModel):
    """Behavior log request"""
    behavior_type: str  # translation, activity, communication, search
    behavior_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class InteractionLogRequest(BaseModel):
    """Interaction record request"""
    caregiver_id: str
    elder_id: str
    interaction_type: str
    content: Optional[str] = None
    quality_score: Optional[float] = None
    engagement_level: Optional[str] = None
    elder_mood_before: Optional[str] = None
    elder_mood_after: Optional[str] = None
    duration_minutes: Optional[int] = None


class BatchCustomerCreateRequest(BaseModel):
    """Batch create customers request"""
    customers: List[CustomerCreateRequest]
    skip_errors: bool = False  # Whether to skip errors and continue processing


class BatchCustomerUpdateRequest(BaseModel):
    """Batch update customers request"""
    updates: List[Dict[str, Any]]  # [{"customer_id": "...", "update_data": {...}}, ...]
    skip_errors: bool = False


@router.post("")
@handle_api_errors
async def create_customer(
    customer_data: CustomerCreateRequest,
    current_user: dict = Depends(require_auth),
    customer_service: CustomerService = Depends(get_customer_service_dependency)
):
    """Create customer"""
    try:
        
        # Parse birth_date if provided
        customer_dict = customer_data.dict()
        if customer_dict.get("birth_date"):
            customer_dict["birth_date"] = datetime.fromisoformat(customer_dict["birth_date"])
        
        # Set user_id from token if not provided
        if not customer_dict.get("user_id"):
            customer_dict["user_id"] = current_user["user_id"]
        
        customer = customer_service.create_customer(customer_dict)
        
        logger.log_api_request(
            endpoint="/api/customers",
            method="POST",
            user_id=current_user["user_id"],
            org_id=None,
            status_code=200,
            response_time_ms=0
        )
        
        return {
            "message": "Customer created successfully",
            "customer": customer
        }
    except ValueError as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            raise ConflictError(f"Customer already exists: {str(e)}")
        raise ValidationError(f"Invalid customer data: {str(e)}")
    except Exception as e:
        logger.log_error(e, {"action": "create_customer"})
        raise


@router.get(
    "/{customer_id}",
    summary="Get customer information",
    description="Fetch detailed customer information by customer ID.",
    response_description="Customer details",
    responses={
        200: {"description": "Customer retrieved successfully"},
        404: {"description": "Customer not found"},
        401: {"description": "Not authenticated"},
        500: {"description": "Internal server error"}
    }
)
@handle_api_errors
async def get_customer(
    customer_id: str,
    current_user: dict = Depends(require_auth),
    customer_service: CustomerService = Depends(get_customer_service_dependency)
):
    """
    Get customer information
    
    Fetch full customer record by ID, including linked caregiver/elder profiles.
    
    - **customer_id**: Unique customer identifier
    
    Returns customer details including:
    - Basic info (name, contact, etc.)
    - Caregiver profile (if caregiver)
    - Elder profile (if elder)
    - Relationships
    """
    customer = customer_service.get_customer(customer_id)
    
    if not customer:
        raise CustomerNotFoundError(customer_id=customer_id)
    
    return customer


@router.put("/{customer_id}")
@handle_api_errors
async def update_customer(
    customer_id: str,
    update_data: Dict[str, Any],
    current_user: dict = Depends(require_auth),
    customer_service: CustomerService = Depends(get_customer_service_dependency)
):
    """Update customer information"""
    try:
        customer = customer_service.update_customer(customer_id, update_data)
        return {
            "message": "Customer updated successfully",
            "customer": customer
        }
    except ValueError as e:
        if "not found" in str(e).lower():
            raise CustomerNotFoundError(customer_id=customer_id)
        raise ValidationError(f"Invalid update data: {str(e)}")


@router.post("/relationships")
@handle_api_errors
async def create_care_relationship(
    relationship_data: CareRelationshipRequest,
    current_user: dict = Depends(require_auth),
    org_id: Optional[str] = None,
    customer_service: CustomerService = Depends(get_customer_service_dependency)
):
    """Create care relationship"""
    relationship = customer_service.create_care_relationship(
        caregiver_id=relationship_data.caregiver_id,
        elder_id=relationship_data.elder_id,
        relationship_data=relationship_data.dict(),
        org_id=org_id or current_user.get("org_id")
    )
    
    return {
        "message": "Care relationship created successfully",
        "relationship": relationship
    }


@router.get("/relationships")
@handle_api_errors
async def get_care_relationships(
    caregiver_id: Optional[str] = Query(None),
    elder_id: Optional[str] = Query(None),
    org_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_auth),
    customer_service: CustomerService = Depends(get_customer_service_dependency)
):
    """Get care relationship list"""
    relationships = customer_service.get_care_relationships(
        caregiver_id=caregiver_id,
        elder_id=elder_id,
        org_id=org_id or current_user.get("org_id")
    )
    
    return {
        "relationships": relationships,
        "count": len(relationships)
    }


@router.post("/{customer_id}/personalization")
@handle_api_errors
async def save_personalization_data(
    customer_id: str,
    personalization_data: PersonalizationDataRequest,
    current_user: dict = Depends(require_auth),
    customer_service: CustomerService = Depends(get_customer_service_dependency)
):
    """Save personalization data"""
    result = customer_service.save_personalization_data(
        customer_id=customer_id,
        data_type=personalization_data.data_type,
        preference_data=personalization_data.preference_data,
        source=personalization_data.source,
        confidence_score=personalization_data.confidence_score
    )
    
    return {
        "message": "Personalization data saved successfully",
        "data": result
    }


@router.get("/{customer_id}/personalization")
@handle_api_errors
async def get_personalization_data(
    customer_id: str,
    data_type: Optional[str] = Query(None),
    relationship_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_auth),
    customer_service: CustomerService = Depends(get_customer_service_dependency)
):
    """Get personalization data"""
    try:
        
        if relationship_id:
            # Get combined personalization
            personalization = customer_service.get_combined_personalization(
                customer_id=customer_id,
                relationship_id=relationship_id
            )
        else:
            # Get customer personalization only
            data_list = customer_service.get_personalization_data(
                customer_id=customer_id,
                data_type=data_type
            )
            personalization = {
                "translation_preferences": {},
                "activity_preferences": {},
                "communication_preferences": {}
            }
            for data in data_list:
                if data["data_type"] in personalization:
                    personalization[data["data_type"]].update(data["preference_data"])
        
        return {
            "customer_id": customer_id,
            "relationship_id": relationship_id,
            "personalization": personalization
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_personalization_data"})
        raise HTTPException(status_code=500, detail=f"Failed to get personalization data: {str(e)}")


@router.post("/{customer_id}/behavior")
@handle_api_errors
async def log_behavior(
    customer_id: str,
    behavior_log: BehaviorLogRequest,
    caregiver_id: Optional[str] = Query(None),
    elder_id: Optional[str] = Query(None),
    org_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_auth),
    customer_service: CustomerService = Depends(get_customer_service_dependency)
):
    """Record behavior log"""
    result = customer_service.log_behavior(
        customer_id=customer_id,
        behavior_type=behavior_log.behavior_type,
        behavior_data=behavior_log.behavior_data,
        caregiver_id=caregiver_id,
        elder_id=elder_id,
        org_id=org_id or current_user.get("org_id"),
        context=behavior_log.context
    )
    
    return {
        "message": "Behavior logged successfully",
        "log": result
    }


@router.get("/{customer_id}/behavior-patterns")
@handle_api_errors
async def get_behavior_patterns(
    customer_id: str,
    behavior_type: Optional[str] = Query(None),
    days: int = Query(30),
    current_user: dict = Depends(require_auth),
    customer_service: CustomerService = Depends(get_customer_service_dependency)
):
    """Get behavior pattern analysis"""
    patterns = customer_service.get_behavior_patterns(
        customer_id=customer_id,
        behavior_type=behavior_type,
        days=days
    )
    
    return patterns


@router.post("/interactions")
@handle_api_errors
async def log_interaction(
    interaction_data: InteractionLogRequest,
    relationship_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_auth),
    customer_service: CustomerService = Depends(get_customer_service_dependency)
):
    """Record caregiver-elder interaction"""
    interaction = customer_service.log_interaction(
        caregiver_id=interaction_data.caregiver_id,
        elder_id=interaction_data.elder_id,
        interaction_data=interaction_data.dict(),
        relationship_id=relationship_id
    )
    
    return {
        "message": "Interaction logged successfully",
        "interaction": interaction
    }


@router.get("/interactions")
@handle_api_errors
async def get_interaction_history(
    caregiver_id: Optional[str] = Query(None),
    elder_id: Optional[str] = Query(None),
    relationship_id: Optional[str] = Query(None),
    days: int = Query(30),
    limit: int = Query(100),
    current_user: dict = Depends(require_auth),
    customer_service: CustomerService = Depends(get_customer_service_dependency)
):
    """Get interaction history"""
    history = customer_service.get_interaction_history(
        caregiver_id=caregiver_id,
        elder_id=elder_id,
        relationship_id=relationship_id,
        days=days,
        limit=limit
    )
    
    return {
        "interactions": history,
        "count": len(history)
    }


@router.post("/batch")
@handle_api_errors
async def batch_create_customers(
    batch_request: BatchCustomerCreateRequest,
    current_user: dict = Depends(require_auth),
    customer_service: CustomerService = Depends(get_customer_service_dependency)
):
    """Batch create customers (optimized with bulk insert)"""
    try:
        
        # Prepare customer data
        customers_data = []
        for customer_data in batch_request.customers:
            customer_dict = customer_data.dict()
            
            # Parse birth_date if provided
            if customer_dict.get("birth_date"):
                customer_dict["birth_date"] = datetime.fromisoformat(customer_dict["birth_date"])
            
            # Set user_id from token if not provided
            if not customer_dict.get("user_id"):
                customer_dict["user_id"] = current_user["user_id"]
            
            customers_data.append(customer_dict)
        
        # Use bulk create for better performance
        try:
            created_customers = customer_service.bulk_create_customers(customers_data)
            
            results = [
                {
                    "index": idx,
                    "status": "success",
                    "customer": customer
                }
                for idx, customer in enumerate(created_customers)
            ]
            
            return {
                "message": f"Batch operation completed: {len(results)} processed",
                "success_count": len(results),
                "error_count": len(batch_request.customers) - len(results),
                "results": results
            }
        except Exception as e:
            if not batch_request.skip_errors:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to batch create customers: {str(e)}"
                )
            # Fallback to individual creation
            results = []
            errors = []
            for idx, customer_data in enumerate(batch_request.customers):
                try:
                    customer_dict = customer_data.dict()
                    if customer_dict.get("birth_date"):
                        customer_dict["birth_date"] = datetime.fromisoformat(customer_dict["birth_date"])
                    if not customer_dict.get("user_id"):
                        customer_dict["user_id"] = current_user["user_id"]
                    
                    customer = customer_service.create_customer(customer_dict)
                    results.append({
                        "index": idx,
                        "status": "success",
                        "customer": customer
                    })
                except Exception as err:
                    error_info = {
                        "index": idx,
                        "status": "error",
                        "error": str(err)
                    }
                    errors.append(error_info)
                    results.append(error_info)
            
            return {
                "message": f"Batch operation completed: {len(results)} processed",
                "success_count": len([r for r in results if r.get("status") == "success"]),
                "error_count": len(errors),
                "results": results
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(e, {"action": "batch_create_customers"})
        raise HTTPException(status_code=500, detail=f"Failed to batch create customers: {str(e)}")


@router.put("/batch")
@handle_api_errors
async def batch_update_customers(
    batch_request: BatchCustomerUpdateRequest,
    current_user: dict = Depends(require_auth),
    customer_service: CustomerService = Depends(get_customer_service_dependency)
):
    """Batch update customers"""
    try:
        results = []
        errors = []
        
        for idx, update_item in enumerate(batch_request.updates):
            try:
                customer_id = update_item.get("customer_id")
                update_data = update_item.get("update_data", {})
                
                if not customer_id:
                    raise ValueError("customer_id is required")
                
                customer = customer_service.update_customer(customer_id, update_data)
                results.append({
                    "index": idx,
                    "customer_id": customer_id,
                    "status": "success",
                    "customer": customer
                })
            except Exception as e:
                error_info = {
                    "index": idx,
                    "customer_id": update_item.get("customer_id"),
                    "status": "error",
                    "error": str(e)
                }
                errors.append(error_info)
                
                if not batch_request.skip_errors:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to update customer at index {idx}: {str(e)}"
                    )
                results.append(error_info)
        
        return {
            "message": f"Batch update completed: {len(results)} processed",
            "success_count": len([r for r in results if r.get("status") == "success"]),
            "error_count": len(errors),
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(e, {"action": "batch_update_customers"})
        raise HTTPException(status_code=500, detail=f"Failed to batch update customers: {str(e)}")
