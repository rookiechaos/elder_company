"""
Care Terms Service - Enhanced caregiving terminology database
"""

from typing import Dict, List, Any, Optional


class CareTermsService:
    """Service for managing caregiving terminology"""
    
    def __init__(self):
        self.terms_database = self._load_terms_database()
    
    def _load_terms_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load comprehensive caregiving terms database"""
        return {
            "daily_care": [
                {"ja": "食事介助", "en": "Meal assistance", "category": "daily_care"},
                {"ja": "入浴介助", "en": "Bathing assistance", "category": "daily_care"},
                {"ja": "更衣介助", "en": "Dressing assistance", "category": "daily_care"},
                {"ja": "排泄介助", "en": "Toileting assistance", "category": "daily_care"},
                {"ja": "口腔ケア", "en": "Oral care", "category": "daily_care"},
                {"ja": "体位変換", "en": "Position change", "category": "daily_care"},
                {"ja": "移動介助", "en": "Mobility assistance", "category": "daily_care"},
                {"ja": "清拭", "en": "Bed bath", "category": "daily_care"},
                {"ja": "整容", "en": "Grooming", "category": "daily_care"},
                {"ja": "洗髪", "en": "Hair washing", "category": "daily_care"},
            ],
            "medical": [
                {"ja": "血圧測定", "en": "Blood pressure measurement", "category": "medical"},
                {"ja": "体温測定", "en": "Temperature measurement", "category": "medical"},
                {"ja": "服薬介助", "en": "Medication assistance", "category": "medical"},
                {"ja": "インスリン注射", "en": "Insulin injection", "category": "medical"},
                {"ja": "酸素吸入", "en": "Oxygen therapy", "category": "medical"},
                {"ja": "吸引", "en": "Suction", "category": "medical"},
                {"ja": "褥瘡ケア", "en": "Pressure sore care", "category": "medical"},
                {"ja": "ストーマケア", "en": "Stoma care", "category": "medical"},
                {"ja": "経管栄養", "en": "Tube feeding", "category": "medical"},
                {"ja": "点滴", "en": "IV drip", "category": "medical"},
            ],
            "facilities": [
                {"ja": "特別養護老人ホーム", "en": "Special nursing home", "category": "facilities"},
                {"ja": "介護老人保健施設", "en": "Health care facility for elderly", "category": "facilities"},
                {"ja": "介護療養型医療施設", "en": "Medical care facility", "category": "facilities"},
                {"ja": "グループホーム", "en": "Group home", "category": "facilities"},
                {"ja": "デイサービス", "en": "Day service", "category": "facilities"},
                {"ja": "ショートステイ", "en": "Short stay", "category": "facilities"},
                {"ja": "訪問介護", "en": "Home visit care", "category": "facilities"},
                {"ja": "訪問看護", "en": "Home nursing", "category": "facilities"},
            ],
            "conditions": [
                {"ja": "認知症", "en": "Dementia", "category": "conditions"},
                {"ja": "アルツハイマー病", "en": "Alzheimer's disease", "category": "conditions"},
                {"ja": "脳血管性認知症", "en": "Vascular dementia", "category": "conditions"},
                {"ja": "パーキンソン病", "en": "Parkinson's disease", "category": "conditions"},
                {"ja": "脳梗塞", "en": "Cerebral infarction", "category": "conditions"},
                {"ja": "糖尿病", "en": "Diabetes", "category": "conditions"},
                {"ja": "高血圧", "en": "Hypertension", "category": "conditions"},
                {"ja": "心不全", "en": "Heart failure", "category": "conditions"},
            ],
            "communication": [
                {"ja": "おはようございます", "en": "Good morning", "category": "communication"},
                {"ja": "こんにちは", "en": "Hello", "category": "communication"},
                {"ja": "お疲れ様です", "en": "Thank you for your hard work", "category": "communication"},
                {"ja": "ありがとうございます", "en": "Thank you", "category": "communication"},
                {"ja": "すみません", "en": "Excuse me / I'm sorry", "category": "communication"},
                {"ja": "大丈夫ですか", "en": "Are you okay?", "category": "communication"},
                {"ja": "痛みはありますか", "en": "Do you have any pain?", "category": "communication"},
                {"ja": "気分はどうですか", "en": "How are you feeling?", "category": "communication"},
            ],
            "equipment": [
                {"ja": "車椅子", "en": "Wheelchair", "category": "equipment"},
                {"ja": "歩行器", "en": "Walker", "category": "equipment"},
                {"ja": "ベッド", "en": "Bed", "category": "equipment"},
                {"ja": "ポータブルトイレ", "en": "Portable toilet", "category": "equipment"},
                {"ja": "介護ベッド", "en": "Care bed", "category": "equipment"},
                {"ja": "血圧計", "en": "Blood pressure monitor", "category": "equipment"},
                {"ja": "体温計", "en": "Thermometer", "category": "equipment"},
            ],
        }
    
    def get_all_terms(self) -> List[Dict[str, Any]]:
        """Get all terms"""
        all_terms = []
        for category_terms in self.terms_database.values():
            all_terms.extend(category_terms)
        return all_terms
    
    def get_terms_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get terms by category"""
        return self.terms_database.get(category, [])
    
    def search_terms(self, query: str, language: str = "ja") -> List[Dict[str, Any]]:
        """Search terms by query"""
        query_lower = query.lower()
        results = []
        
        for category_terms in self.terms_database.values():
            for term in category_terms:
                # Search in Japanese and English
                if (query_lower in term.get("ja", "").lower() or
                    query_lower in term.get("en", "").lower()):
                    results.append(term)
        
        return results
    
    def get_term_translation(
        self,
        term: str,
        source_language: str,
        target_language: str
    ) -> Optional[Dict[str, Any]]:
        """Get translation for a specific term"""
        if source_language == "zh":
            source_language = "en"
        if target_language == "zh":
            target_language = "en"

        for category_terms in self.terms_database.values():
            for term_dict in category_terms:
                if term_dict.get(source_language) == term:
                    return {
                        "original": term,
                        "translated": term_dict.get(target_language),
                        "category": term_dict.get("category"),
                        "all_languages": {
                            "ja": term_dict.get("ja"),
                            "en": term_dict.get("en"),
                        }
                    }
        return None
    
    def get_care_scenarios(self) -> List[Dict[str, Any]]:
        """Get predefined care scenarios"""
        return [
            {
                "id": "morning_care",
                "name_ja": "朝の介護",
                "name_en": "Morning care",
                "description_en": "Morning care activities including waking up, washing, and breakfast",
                "common_terms": ["起床", "洗顔", "歯磨き", "朝食"]
            },
            {
                "id": "meal_assistance",
                "name_ja": "食事介助",
                "name_en": "Meal assistance",
                "description_en": "Assist the elder with eating, including preparation, feeding, and cleanup",
                "common_terms": ["食事", "箸", "スプーン", "嚥下"]
            },
            {
                "id": "bathing",
                "name_ja": "入浴介助",
                "name_en": "Bathing assistance",
                "description_en": "Assist the elder with bathing, including preparation, washing, and drying",
                "common_terms": ["お風呂", "シャワー", "タオル", "石鹸"]
            },
            {
                "id": "medical_care",
                "name_ja": "医療的ケア",
                "name_en": "Medical care",
                "description_en": "Includes measuring vital signs, medication assistance, and medical procedures",
                "common_terms": ["血圧", "体温", "服薬", "注射"]
            },
            {
                "id": "mobility",
                "name_ja": "移動介助",
                "name_en": "Mobility assistance",
                "description_en": "Assist the elder with movement, including getting up, walking, and wheelchair use",
                "common_terms": ["歩行", "車椅子", "転倒", "安全"]
            },
        ]
