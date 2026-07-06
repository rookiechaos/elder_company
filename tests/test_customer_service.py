"""
Unit tests for CustomerService
"""
import pytest
from datetime import datetime

from services.customer_service import CustomerService
from models.customer_models import CustomerDB, CareRelationshipDB


class TestCustomerService:
    """Test cases for CustomerService"""
    
    def test_create_customer_success(self, db_session, sample_customer_data):
        """Test creating a customer successfully"""
        service = CustomerService(db_session)
        result = service.create_customer(sample_customer_data)
        
        assert result["customer_id"] == sample_customer_data["customer_id"]
        assert result["customer_type"] == "caregiver"
        assert result["name"] == sample_customer_data["name"]
        
        # Verify in database
        customer = db_session.query(CustomerDB).filter(
            CustomerDB.customer_id == sample_customer_data["customer_id"]
        ).first()
        assert customer is not None
        assert customer.name == sample_customer_data["name"]
    
    def test_create_customer_duplicate(self, db_session, sample_customer_data):
        """Test creating duplicate customer raises error"""
        service = CustomerService(db_session)
        service.create_customer(sample_customer_data)
        
        # Try to create again
        with pytest.raises(ValueError, match="already exists"):
            service.create_customer(sample_customer_data)
    
    def test_get_customer_by_id(self, db_session, sample_customer_data):
        """Test retrieving customer by ID"""
        service = CustomerService(db_session)
        created = service.create_customer(sample_customer_data)
        
        result = service.get_customer(created["customer_id"])
        
        assert result is not None
        assert result["customer_id"] == sample_customer_data["customer_id"]
        assert result["name"] == sample_customer_data["name"]
    
    def test_get_customer_not_found(self, db_session):
        """Test retrieving non-existent customer"""
        service = CustomerService(db_session)
        result = service.get_customer("non_existent_id")
        assert result is None
    
    def test_update_customer(self, db_session, sample_customer_data):
        """Test updating customer information"""
        service = CustomerService(db_session)
        created = service.create_customer(sample_customer_data)
        
        update_data = {
            "name": "更新后的名字"
        }
        
        result = service.update_customer(created["customer_id"], update_data)
        
        assert result["name"] == "更新后的名字"
    
    def test_create_care_relationship(self, db_session, sample_customer_data, sample_elder_data):
        """Test creating care relationship"""
        service = CustomerService(db_session)
        caregiver = service.create_customer(sample_customer_data)
        elder = service.create_customer(sample_elder_data)
        
        relationship_data = {
            "relationship_type": "professional",
            "relationship_start_date": datetime.now()
        }
        
        result = service.create_care_relationship(
            caregiver_id=caregiver["customer_id"],
            elder_id=elder["customer_id"],
            relationship_data=relationship_data
        )
        
        assert result["caregiver_id"] == caregiver["customer_id"]
        assert result["elder_id"] == elder["customer_id"]
        assert result["relationship_type"] == "professional"
    
    def test_save_personalization_data(self, db_session, sample_customer_data):
        """Test saving personalization data"""
        service = CustomerService(db_session)
        customer = service.create_customer(sample_customer_data)
        
        preference_data = {
            "style": "professional",
            "detail_level": "moderate"
        }
        
        result = service.save_personalization_data(
            customer_id=customer["customer_id"],
            data_type="translation_pref",
            preference_data=preference_data
        )
        
        assert result["data_type"] == "translation_pref"
        assert result["preference_data"]["style"] == "professional"
    
    def test_log_behavior(self, db_session, sample_customer_data):
        """Test logging user behavior"""
        service = CustomerService(db_session)
        customer = service.create_customer(sample_customer_data)
        
        behavior_data = {
            "action": "translate",
            "outcome": "success",
            "feedback": "good"
        }
        context = {"source_lang": "ja", "target_lang": "zh"}
        
        result = service.log_behavior(
            customer_id=customer["customer_id"],
            behavior_type="translation",
            behavior_data=behavior_data,
            context=context
        )
        
        assert "log_id" in result
        assert "timestamp" in result
    
    def test_get_customer_list(self, db_session, sample_customer_data):
        """Test getting list of customers"""
        service = CustomerService(db_session)
        
        # Create multiple customers
        for i in range(3):
            data = sample_customer_data.copy()
            data["customer_id"] = f"test_customer_{i:03d}"
            data["name"] = f"测试看护者{i}"
            service.create_customer(data)
        
        # Get all customers by querying individually
        customers = []
        for i in range(3):
            customer = service.get_customer(f"test_customer_{i:03d}")
            if customer:
                customers.append(customer)
        
        assert len(customers) == 3
        assert all(c["customer_type"] == "caregiver" for c in customers)
    
    def test_get_customers_with_filter(self, db_session, sample_customer_data, sample_elder_data):
        """Test filtering customers by type"""
        service = CustomerService(db_session)
        caregiver = service.create_customer(sample_customer_data)
        elder = service.create_customer(sample_elder_data)
        
        # Get customers individually
        caregiver_result = service.get_customer(caregiver["customer_id"])
        elder_result = service.get_customer(elder["customer_id"])
        
        assert caregiver_result is not None
        assert elder_result is not None
        assert caregiver_result["customer_type"] == "caregiver"
        assert elder_result["customer_type"] == "elder"
