"""
Customer Service - Manages customer information for personalization
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import uuid

from models.customer_models import (
    CustomerDB, CaregiverProfileDB, ElderProfileDB,
    CareRelationshipDB, PersonalizationDataDB,
    BehaviorLogDB, PreferenceLearningDB, InteractionHistoryDB
)
from services.cache_service import get_cache, CACHE_TTL
from services.base_service import BaseService


class CustomerService(BaseService):
    """Service for managing customer information and personalization"""
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    # ==================== Customer Management ====================
    
    def create_customer(
        self,
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new customer"""
        customer_id = customer_data.get("customer_id") or f"customer_{uuid.uuid4().hex[:12]}"
        
        # Check if customer exists
        existing = self.db.query(CustomerDB).filter(
            CustomerDB.customer_id == customer_id
        ).first()
        
        if existing:
            raise ValueError(f"Customer {customer_id} already exists")
        
        customer = CustomerDB(
            customer_id=customer_id,
            customer_type=customer_data.get("customer_type", "caregiver"),
            name=customer_data.get("name", ""),
            name_ja=customer_data.get("name_ja"),
            name_zh=customer_data.get("name_zh"),
            email=customer_data.get("email"),
            phone=customer_data.get("phone"),
            gender=customer_data.get("gender"),
            birth_date=customer_data.get("birth_date"),
            age=customer_data.get("age"),
            address=customer_data.get("address"),
            city=customer_data.get("city"),
            prefecture=customer_data.get("prefecture"),
            country=customer_data.get("country", "Japan"),
            native_language=customer_data.get("native_language", "ja"),
            spoken_languages=customer_data.get("spoken_languages", []),
            preferred_language=customer_data.get("preferred_language", "ja"),
            org_id=customer_data.get("org_id"),
            user_id=customer_data.get("user_id")
        )
        
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        
        # Create profile based on type
        if customer_data.get("customer_type") == "caregiver":
            self._create_caregiver_profile(customer_id, customer_data)
        elif customer_data.get("customer_type") == "elder":
            self._create_elder_profile(customer_id, customer_data)
        
        return self._customer_to_dict(customer)
    
    def bulk_create_customers(
        self,
        customers_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Bulk create customers for better performance"""
        from sqlalchemy import inspect
        
        customers_to_create = []
        profiles_to_create = []
        
        for customer_data in customers_data:
            customer_id = customer_data.get("customer_id") or f"customer_{uuid.uuid4().hex[:12]}"
            
            # Check if customer exists
            existing = self.db.query(CustomerDB).filter(
                CustomerDB.customer_id == customer_id
            ).first()
            
            if existing:
                continue  # Skip existing customers
            
            customer = CustomerDB(
                customer_id=customer_id,
                customer_type=customer_data.get("customer_type", "caregiver"),
                name=customer_data.get("name", ""),
                name_ja=customer_data.get("name_ja"),
                name_zh=customer_data.get("name_zh"),
                email=customer_data.get("email"),
                phone=customer_data.get("phone"),
                gender=customer_data.get("gender"),
                birth_date=customer_data.get("birth_date"),
                age=customer_data.get("age"),
                address=customer_data.get("address"),
                city=customer_data.get("city"),
                prefecture=customer_data.get("prefecture"),
                country=customer_data.get("country", "Japan"),
                native_language=customer_data.get("native_language", "ja"),
                spoken_languages=customer_data.get("spoken_languages", []),
                preferred_language=customer_data.get("preferred_language", "ja"),
                org_id=customer_data.get("org_id"),
                user_id=customer_data.get("user_id")
            )
            customers_to_create.append(customer)
            profiles_to_create.append((customer_id, customer_data))
        
        # Bulk insert customers
        if customers_to_create:
            self.db.add_all(customers_to_create)
            self.safe_commit("bulk_create_customers")
            
            # Create profiles
            for customer_id, customer_data in profiles_to_create:
                if customer_data.get("customer_type") == "caregiver":
                    self._create_caregiver_profile(customer_id, customer_data)
                elif customer_data.get("customer_type") == "elder":
                    self._create_elder_profile(customer_id, customer_data)
            
            # Refresh and return
            self.safe_commit("bulk_create_customers_profiles")
            return [self._customer_to_dict(c) for c in customers_to_create]
        
        return []
    
    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get customer information
        
        Args:
            customer_id: Customer unique ID
        
        Returns:
            Dict with customer info, or None if not found
        
        Raises:
            CustomerNotFoundError: If the customer does not exist
        
        Example:
            >>> service = CustomerService(db)
            >>> customer = service.get_customer("customer_123")
            >>> print(customer["name"])
            '田中太郎'
        """
        """Get customer by ID with optimized query (no N+1) and caching"""
        from sqlalchemy.orm import joinedload
        
        cache = get_cache()
        cache_key = f"customer:info:{customer_id}"
        
        # Try cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Use joinedload to avoid N+1 query problem
        customer = self.db.query(CustomerDB)\
            .options(
                joinedload(CustomerDB.caregiver_profile),
                joinedload(CustomerDB.elder_profile)
            )\
            .filter(CustomerDB.customer_id == customer_id)\
            .first()
        
        if not customer:
            return None
        
        result = self._customer_to_dict(customer)
        
        # Add profile data (already loaded via joinedload)
        if customer.caregiver_profile:
            result["caregiver_profile"] = self._caregiver_profile_to_dict(customer.caregiver_profile)
        elif customer.elder_profile:
            result["elder_profile"] = self._elder_profile_to_dict(customer.elder_profile)
        
        # Cache result
        cache.set(cache_key, result, CACHE_TTL["customer_info"])
        
        return result
    
    def update_customer(
        self,
        customer_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update customer information"""
        customer = self.db.query(CustomerDB).filter(
            CustomerDB.customer_id == customer_id
        ).first()
        
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Update basic info
        for key, value in update_data.items():
            if hasattr(customer, key) and key not in ["customer_id", "created_at"]:
                setattr(customer, key, value)
        
        customer.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(customer)
        
        result = self._customer_to_dict(customer)
        
        # Invalidate cache
        cache = get_cache()
        cache.delete(f"customer:info:{customer_id}")
        
        return result
    
    # ==================== Care Relationship ====================
    
    def create_care_relationship(
        self,
        caregiver_id: str,
        elder_id: str,
        relationship_data: Dict[str, Any],
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create care relationship between caregiver and elder"""
        relationship_id = f"rel_{uuid.uuid4().hex[:12]}"
        
        relationship = CareRelationshipDB(
            relationship_id=relationship_id,
            caregiver_id=caregiver_id,
            elder_id=elder_id,
            org_id=org_id,
            relationship_type=relationship_data.get("relationship_type", "professional"),
            relationship_start_date=relationship_data.get("relationship_start_date", utc_now()),
            care_frequency=relationship_data.get("care_frequency"),
            care_duration_hours=relationship_data.get("care_duration_hours")
        )
        
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        
        return self._relationship_to_dict(relationship)
    
    def get_care_relationships(
        self,
        caregiver_id: Optional[str] = None,
        elder_id: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get care relationships"""
        query = self.db.query(CareRelationshipDB)
        
        if caregiver_id:
            query = query.filter(CareRelationshipDB.caregiver_id == caregiver_id)
        
        if elder_id:
            query = query.filter(CareRelationshipDB.elder_id == elder_id)
        
        if org_id:
            query = query.filter(CareRelationshipDB.org_id == org_id)
        
        relationships = query.filter(
            CareRelationshipDB.relationship_status == "active"
        ).all()
        
        return [self._relationship_to_dict(rel) for rel in relationships]
    
    # ==================== Personalization Data ====================
    
    def save_personalization_data(
        self,
        customer_id: str,
        data_type: str,
        preference_data: Dict[str, Any],
        source: str = "explicit",
        confidence_score: float = 1.0
    ) -> Dict[str, Any]:
        """Save personalization data"""
        data_id = f"pref_{uuid.uuid4().hex[:12]}"
        
        # Check if data exists
        existing = self.db.query(PersonalizationDataDB).filter(
            and_(
                PersonalizationDataDB.customer_id == customer_id,
                PersonalizationDataDB.data_type == data_type
            )
        ).first()
        
        if existing:
            # Update existing
            existing.preference_data = preference_data
            existing.source = source
            existing.confidence_score = confidence_score
            existing.updated_at = utc_now()
            data_id = existing.data_id
        else:
            # Create new
            personalization = PersonalizationDataDB(
                data_id=data_id,
                customer_id=customer_id,
                data_type=data_type,
                preference_data=preference_data,
                source=source,
                confidence_score=confidence_score
            )
            self.db.add(personalization)
        
        self.db.commit()
        
        return {
            "data_id": data_id,
            "customer_id": customer_id,
            "data_type": data_type,
            "preference_data": preference_data
        }
    
    def get_personalization_data(
        self,
        customer_id: str,
        data_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get personalization data for customer"""
        query = self.db.query(PersonalizationDataDB).filter(
            PersonalizationDataDB.customer_id == customer_id
        )
        
        if data_type:
            query = query.filter(PersonalizationDataDB.data_type == data_type)
        
        data_list = query.order_by(desc(PersonalizationDataDB.confidence_score)).all()
        
        return [
            {
                "data_id": d.data_id,
                "data_type": d.data_type,
                "preference_data": d.preference_data,
                "source": d.source,
                "confidence_score": d.confidence_score,
                "usage_count": d.usage_count,
                "last_used_at": d.last_used_at.isoformat() if d.last_used_at else None
            }
            for d in data_list
        ]
    
    def get_combined_personalization(
        self,
        customer_id: str,
        relationship_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get combined personalization data for optimization"""
        # Get customer personalization
        customer_prefs = self.get_personalization_data(customer_id)
        
        # Get relationship-based preferences if provided
        relationship_prefs = []
        if relationship_id:
            relationship_prefs = self.db.query(PreferenceLearningDB).filter(
                PreferenceLearningDB.relationship_id == relationship_id
            ).all()
        
        # Combine preferences
        combined = {
            "translation_preferences": {},
            "activity_preferences": {},
            "communication_preferences": {},
            "care_preferences": {}
        }
        
        for pref in customer_prefs:
            pref_type = pref["data_type"]
            if pref_type in combined:
                combined[pref_type].update(pref["preference_data"])
        
        # Add relationship preferences
        for rel_pref in relationship_prefs:
            learned = rel_pref.learned_preferences
            for key, value in learned.items():
                if key in combined:
                    combined[key].update(value)
        
        return combined
    
    # ==================== Behavior Logging ====================
    
    def log_behavior(
        self,
        customer_id: str,
        behavior_type: str,
        behavior_data: Dict[str, Any],
        caregiver_id: Optional[str] = None,
        elder_id: Optional[str] = None,
        org_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Log customer behavior for learning"""
        log_id = f"log_{uuid.uuid4().hex[:12]}"
        
        log = BehaviorLogDB(
            log_id=log_id,
            customer_id=customer_id,
            caregiver_id=caregiver_id,
            elder_id=elder_id,
            org_id=org_id,
            behavior_type=behavior_type,
            action=behavior_data.get("action"),
            behavior_data=behavior_data,
            context=context,
            outcome=behavior_data.get("outcome"),
            feedback=behavior_data.get("feedback"),
            device_id=context.get("device_id") if context else None,
            session_id=context.get("session_id") if context else None
        )
        
        self.db.add(log)
        self.db.commit()
        
        return {"log_id": log_id, "timestamp": log.timestamp.isoformat()}
    
    def get_behavior_patterns(
        self,
        customer_id: str,
        behavior_type: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Analyze behavior patterns"""
        start_date = utc_now() - timedelta(days=days)
        
        query = self.db.query(BehaviorLogDB).filter(
            and_(
                BehaviorLogDB.customer_id == customer_id,
                BehaviorLogDB.timestamp >= start_date
            )
        )
        
        if behavior_type:
            query = query.filter(BehaviorLogDB.behavior_type == behavior_type)
        
        logs = query.all()
        
        # Analyze patterns
        behavior_counts = {}
        outcome_counts = {}
        time_patterns = {}
        
        for log in logs:
            # Count by type
            behavior_counts[log.behavior_type] = behavior_counts.get(log.behavior_type, 0) + 1
            
            # Count outcomes
            if log.outcome:
                outcome_counts[log.outcome] = outcome_counts.get(log.outcome, 0) + 1
            
            # Time patterns
            hour = log.timestamp.hour
            time_patterns[hour] = time_patterns.get(hour, 0) + 1
        
        return {
            "customer_id": customer_id,
            "period_days": days,
            "total_behaviors": len(logs),
            "behavior_counts": behavior_counts,
            "outcome_counts": outcome_counts,
            "time_patterns": time_patterns,
            "recent_behaviors": [
                {
                    "behavior_type": log.behavior_type,
                    "action": log.action,
                    "timestamp": log.timestamp.isoformat()
                }
                for log in logs[-10:]  # Last 10 behaviors
            ]
        }
    
    # ==================== Interaction History ====================
    
    def log_interaction(
        self,
        caregiver_id: str,
        elder_id: str,
        interaction_data: Dict[str, Any],
        relationship_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log interaction between caregiver and elder"""
        interaction_id = f"inter_{uuid.uuid4().hex[:12]}"
        
        interaction = InteractionHistoryDB(
            interaction_id=interaction_id,
            caregiver_id=caregiver_id,
            elder_id=elder_id,
            relationship_id=relationship_id,
            interaction_type=interaction_data.get("interaction_type"),
            content=interaction_data.get("content"),
            content_metadata=interaction_data.get("content_metadata"),
            quality_score=interaction_data.get("quality_score"),
            engagement_level=interaction_data.get("engagement_level"),
            satisfaction_score=interaction_data.get("satisfaction_score"),
            elder_mood_before=interaction_data.get("elder_mood_before"),
            elder_mood_after=interaction_data.get("elder_mood_after"),
            caregiver_feedback=interaction_data.get("caregiver_feedback"),
            elder_feedback=interaction_data.get("elder_feedback"),
            duration_minutes=interaction_data.get("duration_minutes")
        )
        
        self.db.add(interaction)
        self.db.commit()
        
        return self._interaction_to_dict(interaction)
    
    def get_interaction_history(
        self,
        caregiver_id: Optional[str] = None,
        elder_id: Optional[str] = None,
        relationship_id: Optional[str] = None,
        days: int = 30,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get interaction history"""
        start_date = utc_now() - timedelta(days=days)
        
        query = self.db.query(InteractionHistoryDB).filter(
            InteractionHistoryDB.interaction_date >= start_date
        )
        
        if caregiver_id:
            query = query.filter(InteractionHistoryDB.caregiver_id == caregiver_id)
        
        if elder_id:
            query = query.filter(InteractionHistoryDB.elder_id == elder_id)
        
        if relationship_id:
            query = query.filter(InteractionHistoryDB.relationship_id == relationship_id)
        
        interactions = query.order_by(
            desc(InteractionHistoryDB.interaction_date)
        ).limit(limit).all()
        
        return [self._interaction_to_dict(inter) for inter in interactions]
    
    # ==================== Helper Methods ====================
    
    def _create_caregiver_profile(
        self,
        customer_id: str,
        customer_data: Dict[str, Any]
    ):
        """Create caregiver profile"""
        profile = CaregiverProfileDB(
            customer_id=customer_id,
            role=customer_data.get("role"),
            certification=customer_data.get("certification"),
            experience_years=customer_data.get("experience_years"),
            work_shift=customer_data.get("work_shift"),
            work_schedule=customer_data.get("work_schedule"),
            specialties=customer_data.get("specialties"),
            preferred_care_style=customer_data.get("preferred_care_style"),
            communication_style=customer_data.get("communication_style"),
            translation_preferences=customer_data.get("translation_preferences"),
            activity_preferences=customer_data.get("activity_preferences")
        )
        self.db.add(profile)
        self.db.commit()
    
    def _create_elder_profile(
        self,
        customer_id: str,
        customer_data: Dict[str, Any]
    ):
        """Create elder profile"""
        profile = ElderProfileDB(
            customer_id=customer_id,
            health_status=customer_data.get("health_status"),
            health_conditions=customer_data.get("health_conditions"),
            mobility_level=customer_data.get("mobility_level"),
            cognitive_level=customer_data.get("cognitive_level"),
            adl_scores=customer_data.get("adl_scores"),
            iadl_scores=customer_data.get("iadl_scores"),
            interests=customer_data.get("interests"),
            hobbies=customer_data.get("hobbies"),
            favorite_topics=customer_data.get("favorite_topics"),
            occupation_history=customer_data.get("occupation_history"),
            family_info=customer_data.get("family_info"),
            life_story=customer_data.get("life_story"),
            communication_preferences=customer_data.get("communication_preferences"),
            preferred_communication_style=customer_data.get("preferred_communication_style"),
            activity_capabilities=customer_data.get("activity_capabilities"),
            activity_limitations=customer_data.get("activity_limitations"),
            personality_traits=customer_data.get("personality_traits"),
            mood_patterns=customer_data.get("mood_patterns")
        )
        self.db.add(profile)
        self.db.commit()
    
    def _customer_to_dict(self, customer: CustomerDB) -> Dict[str, Any]:
        """Convert customer to dictionary"""
        return {
            "customer_id": customer.customer_id,
            "customer_type": customer.customer_type,
            "name": customer.name,
            "name_ja": customer.name_ja,
            "name_zh": customer.name_zh,
            "email": customer.email,
            "phone": customer.phone,
            "gender": customer.gender,
            "birth_date": customer.birth_date.isoformat() if customer.birth_date else None,
            "age": customer.age,
            "address": customer.address,
            "city": customer.city,
            "prefecture": customer.prefecture,
            "country": customer.country,
            "native_language": customer.native_language,
            "spoken_languages": customer.spoken_languages or [],
            "preferred_language": customer.preferred_language,
            "org_id": customer.org_id,
            "user_id": customer.user_id,
            "is_active": customer.is_active,
            "registration_date": customer.registration_date.isoformat() if customer.registration_date else None,
            "created_at": customer.created_at.isoformat() if customer.created_at else None,
            "updated_at": customer.updated_at.isoformat() if customer.updated_at else None
        }
    
    def _caregiver_profile_to_dict(self, profile: CaregiverProfileDB) -> Dict[str, Any]:
        """Convert caregiver profile to dictionary"""
        return {
            "role": profile.role,
            "certification": profile.certification or [],
            "experience_years": profile.experience_years,
            "work_shift": profile.work_shift,
            "work_schedule": profile.work_schedule or {},
            "specialties": profile.specialties or [],
            "preferred_care_style": profile.preferred_care_style,
            "communication_style": profile.communication_style,
            "translation_preferences": profile.translation_preferences or {},
            "activity_preferences": profile.activity_preferences or {}
        }
    
    def _elder_profile_to_dict(self, profile: ElderProfileDB) -> Dict[str, Any]:
        """Convert elder profile to dictionary"""
        return {
            "health_status": profile.health_status,
            "health_conditions": profile.health_conditions or [],
            "mobility_level": profile.mobility_level,
            "cognitive_level": profile.cognitive_level,
            "adl_scores": profile.adl_scores or {},
            "iadl_scores": profile.iadl_scores or {},
            "interests": profile.interests or [],
            "hobbies": profile.hobbies or [],
            "favorite_topics": profile.favorite_topics or [],
            "occupation_history": profile.occupation_history,
            "family_info": profile.family_info or {},
            "life_story": profile.life_story,
            "communication_preferences": profile.communication_preferences or {},
            "preferred_communication_style": profile.preferred_communication_style,
            "activity_capabilities": profile.activity_capabilities or [],
            "activity_limitations": profile.activity_limitations or [],
            "personality_traits": profile.personality_traits or [],
            "mood_patterns": profile.mood_patterns or {}
        }
    
    def _relationship_to_dict(self, relationship: CareRelationshipDB) -> Dict[str, Any]:
        """Convert relationship to dictionary"""
        return {
            "relationship_id": relationship.relationship_id,
            "caregiver_id": relationship.caregiver_id,
            "elder_id": relationship.elder_id,
            "org_id": relationship.org_id,
            "relationship_type": relationship.relationship_type,
            "relationship_start_date": relationship.relationship_start_date.isoformat() if relationship.relationship_start_date else None,
            "relationship_status": relationship.relationship_status,
            "care_frequency": relationship.care_frequency,
            "care_duration_hours": relationship.care_duration_hours,
            "interaction_quality": relationship.interaction_quality,
            "communication_effectiveness": relationship.communication_effectiveness,
            "created_at": relationship.created_at.isoformat() if relationship.created_at else None
        }
    
    def _interaction_to_dict(self, interaction: InteractionHistoryDB) -> Dict[str, Any]:
        """Convert interaction to dictionary"""
        return {
            "interaction_id": interaction.interaction_id,
            "caregiver_id": interaction.caregiver_id,
            "elder_id": interaction.elder_id,
            "relationship_id": interaction.relationship_id,
            "interaction_type": interaction.interaction_type,
            "content": interaction.content,
            "quality_score": interaction.quality_score,
            "engagement_level": interaction.engagement_level,
            "satisfaction_score": interaction.satisfaction_score,
            "elder_mood_before": interaction.elder_mood_before,
            "elder_mood_after": interaction.elder_mood_after,
            "duration_minutes": interaction.duration_minutes,
            "interaction_date": interaction.interaction_date.isoformat() if interaction.interaction_date else None
        }
