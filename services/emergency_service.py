"""
Emergency Service
Handles emergency records, AI guidance, and brief report generation
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uuid

from models.emergency_models import EmergencyRecordDB
from services.base_service import BaseService
from services.logging_service import logger
from config.disclaimers import get_disclaimer_emergency


class EmergencyService(BaseService):
    """Emergency service"""
    
    def record_emergency(
        self,
        elder_id: str,
        caregiver_id: str,
        emergency_type: str,
        severity: str,
        description: str,
        actions_taken: Optional[List[str]] = None,
        org_id: Optional[str] = None,
        generate_guidance: bool = True,
        generate_summary: bool = True
    ) -> Dict[str, Any]:
        """
        Record an emergency
        
        Args:
            elder_id: Elder ID
            caregiver_id: Caregiver ID
            emergency_type: Emergency type (health, emotional, behavioral)
            severity: Severity (low, medium, high)
            description: Description
            actions_taken: Actions taken (optional)
            org_id: Organization ID (optional)
            generate_guidance: Generate AI guidance (default True)
            generate_summary: Generate brief report (default True)
            
        Returns:
            Emergency record
        """
        # Validate parameters
        from utils.security import validate_enum_value
        
        validate_enum_value(emergency_type, ["health", "emotional", "behavioral"], "emergency_type")
        validate_enum_value(severity, ["low", "medium", "high"], "severity")
        
        record_id = f"emergency_{uuid.uuid4().hex[:12]}"
        
        # Generate AI guidance if enabled
        ai_guidance = None
        relief_actions = None
        risk_notes = None
        voice_guidance_url = None
        
        if generate_guidance:
            try:
                guidance_result = self._generate_ai_guidance(
                    emergency_type=emergency_type,
                    severity=severity,
                    description=description
                )
                ai_guidance = guidance_result.get("guidance_text")
                relief_actions = guidance_result.get("relief_actions")
                risk_notes = guidance_result.get("risk_notes")
                
                # Generate voice guidance if enabled
                try:
                    voice_guidance_url = self._generate_voice_guidance(ai_guidance)
                except Exception as e:
                    logger.log_warning(f"Failed to generate voice guidance: {e}")
            except Exception as e:
                logger.log_warning(f"Failed to generate AI guidance: {e}")
        
        # Generate brief report if enabled
        summary = None
        if generate_summary:
            try:
                summary = self._generate_emergency_summary(
                    emergency_type=emergency_type,
                    severity=severity,
                    description=description,
                    actions_taken=actions_taken or []
                )
            except Exception as e:
                logger.log_warning(f"Failed to generate emergency summary: {e}")
        
        # Create record
        emergency_record = EmergencyRecordDB(
            record_id=record_id,
            elder_id=elder_id,
            caregiver_id=caregiver_id,
            org_id=org_id,
            emergency_type=emergency_type,
            severity=severity,
            description=description,
            actions_taken=actions_taken or [],
            ai_guidance=ai_guidance,
            voice_guidance_url=voice_guidance_url,
            relief_actions=relief_actions,
            risk_notes=risk_notes,
            summary=summary
        )
        
        self.db.add(emergency_record)
        self.safe_commit(action="record_emergency")
        self.safe_refresh(emergency_record, action="refresh_emergency_record")
        
        logger.log_info(
            f"Emergency recorded: {record_id}",
            {"record_id": record_id, "elder_id": elder_id, "emergency_type": emergency_type, "severity": severity}
        )
        
        return self._emergency_record_to_dict(emergency_record)
    
    def get_emergency_guidance(
        self,
        elder_id: str,
        emergency_type: str,
        current_situation: str,
        language: Optional[str] = "ja"
    ) -> Dict[str, Any]:
        """
        Get AI emergency guidance
        
        Args:
            elder_id: Elder ID
            emergency_type: Emergency type (health, emotional, behavioral)
            current_situation: Current situation description
            language: Disclaimer language (zh, ja, en); default ja
            
        Returns:
            AI guidance (voice, relief actions, risk notes)
        """
        try:
            guidance_result = self._generate_ai_guidance(
                emergency_type=emergency_type,
                severity="medium",  # Default to medium severity
                description=current_situation
            )
            
            ai_guidance = guidance_result.get("guidance_text")
            relief_actions = guidance_result.get("relief_actions")
            risk_notes = guidance_result.get("risk_notes")
            
            # Generate voice guidance
            voice_guidance_url = None
            try:
                voice_guidance_url = self._generate_voice_guidance(ai_guidance)
            except Exception as e:
                logger.log_warning(f"Failed to generate voice guidance: {e}")
            
            return {
                "voice_guidance": ai_guidance,
                "voice_guidance_url": voice_guidance_url,
                "relief_actions": relief_actions or [],
                "risk_notes": risk_notes or "",
                "disclaimer": get_disclaimer_emergency(language or "ja")
            }
        except Exception as e:
            logger.log_error(e, {"action": "get_emergency_guidance", "elder_id": elder_id})
            raise ValueError(f"Failed to generate emergency guidance: {str(e)}")
    
    def get_emergency_history(
        self,
        elder_id: Optional[str] = None,
        caregiver_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        org_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get emergency history
        
        Args:
            elder_id: Elder ID (optional)
            caregiver_id: Caregiver ID (optional)
            start_date: Start date (optional)
            end_date: End date (optional)
            org_id: Organization ID (optional)
            limit: Result limit
            
        Returns:
            List of emergency records
        """
        query = self.db.query(EmergencyRecordDB)
        
        if elder_id:
            query = query.filter(EmergencyRecordDB.elder_id == elder_id)
        if caregiver_id:
            query = query.filter(EmergencyRecordDB.caregiver_id == caregiver_id)
        if org_id:
            query = query.filter(EmergencyRecordDB.org_id == org_id)
        if start_date:
            query = query.filter(EmergencyRecordDB.timestamp >= start_date)
        if end_date:
            query = query.filter(EmergencyRecordDB.timestamp <= end_date)
        
        records = query.order_by(desc(EmergencyRecordDB.timestamp)).limit(limit).all()
        
        return [self._emergency_record_to_dict(record) for record in records]
    
    def _generate_ai_guidance(
        self,
        emergency_type: str,
        severity: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Generate AI guidance (internal)
        
        Args:
            emergency_type: Emergency type
            severity: Severity level
            description: Description
            
        Returns:
            Guidance (text, relief actions, risk notes)
        """
        try:
            from services.ai_providers import get_ai_provider
            
            ai_provider = get_ai_provider()
            
            # Build prompt
            prompt = f"""以下の緊急状況に対して、短く穏やかな音声ガイダンス、緩和動作、リスク注意事項を生成してください。

緊急タイプ：{emergency_type}
深刻度：{severity}
状況説明：{description}

要件：
1. 音声ガイダンス：短く（30字以内）、穏やかで落ち着いたトーン
2. 緩和動作：具体的で実行可能な動作を3つ以内
3. リスク注意事項：診断ではなく、リスク提示のみ
4. 日本語で

JSON形式で返してください：
{{
    "guidance_text": "音声ガイダンステキスト",
    "relief_actions": ["動作1", "動作2", "動作3"],
    "risk_notes": "リスク注意事項"
}}
"""
            
            messages = [
                {"role": "system", "content": "あなたは介護の専門家で、緊急状況に対する穏やかで落ち着いたガイダンスを生成するアシスタントです。診断は行わず、リスク提示のみを行います。本製品は介護・記録のためのツールであり、医療機器ではありません。ガイダンスは状況緩和と記録の補助であり、専門の医療判断に代わるものではありません。"},
                {"role": "user", "content": prompt}
            ]
            
            # Handle async/sync invocation
            import asyncio
            import inspect
            import json
            
            try:
                if inspect.iscoroutinefunction(ai_provider.chat):
                    loop = asyncio.get_event_loop()
                    response = loop.run_until_complete(
                        ai_provider.chat(
                            messages=messages,
                            temperature=0.5,  # Lower temperature for more stable output
                            max_tokens=300
                        )
                    )
                else:
                    response = ai_provider.chat(
                        messages=messages,
                        temperature=0.5,
                        max_tokens=300
                    )
                
                text = response.get("text", "").strip()
                
                # Try to parse JSON
                try:
                    # Extract JSON portion
                    if "{" in text and "}" in text:
                        json_start = text.find("{")
                        json_end = text.rfind("}") + 1
                        json_text = text[json_start:json_end]
                        result = json.loads(json_text)
                    else:
                        # If not JSON, use fallback
                        result = {
                            "guidance_text": text[:50] if len(text) > 50 else text,
                            "relief_actions": ["深呼吸をする", "静かな場所で休む", "落ち着いて話す"],
                            "risk_notes": "症状が続く場合は、医療機関に相談してください。"
                        }
                except json.JSONDecodeError:
                    # JSON parse failed, use fallback
                    result = {
                        "guidance_text": text[:50] if len(text) > 50 else text,
                        "relief_actions": ["深呼吸をする", "静かな場所で休む", "落ち着いて話す"],
                        "risk_notes": "症状が続く場合は、医療機関に相談してください。"
                    }
                
                return result
                
            except Exception as e:
                logger.log_warning(f"Failed to call AI provider: {e}")
                # Use fallback guidance
                return self._get_fallback_guidance(emergency_type, severity)
            
        except Exception as e:
            logger.log_warning(f"Failed to generate AI guidance: {e}")
            return self._get_fallback_guidance(emergency_type, severity)
    
    def _generate_voice_guidance(self, text: str) -> Optional[str]:
        """
        Generate voice guidance (TTS)
        
        Args:
            text: Guidance text
            
        Returns:
            Voice file URL on success
        """
        try:
            from services.voice_service import get_voice_service
            
            voice_service = get_voice_service()
            
            # Generate speech via TTS
            if hasattr(voice_service, 'text_to_speech'):
                result = voice_service.text_to_speech(
                    text=text,
                    language="ja",  # Japanese
                    voice="gentle"  # Gentle voice
                )
                # voice_service returns a dict; extract audio_url
                if isinstance(result, dict):
                    audio_url = result.get("audio_url")
                    return audio_url
                return None
            else:
                # Return None if voice_service lacks TTS
                logger.log_warning("Voice service does not support TTS")
                return None
                
        except Exception as e:
            logger.log_warning(f"Failed to generate voice guidance: {e}")
            return None
    
    def _generate_emergency_summary(
        self,
        emergency_type: str,
        severity: str,
        description: str,
        actions_taken: List[str]
    ) -> str:
        """
        Generate brief emergency report
        
        Args:
            emergency_type: Emergency type
            severity: Severity level
            description: Description
            actions_taken: Actions taken
            
        Returns:
            Brief report text
        """
        try:
            from services.ai_providers import get_ai_provider
            
            ai_provider = get_ai_provider()
            
            prompt = f"""以下の緊急状況の短い報告（50字以内）を生成してください。

緊急タイプ：{emergency_type}
深刻度：{severity}
状況：{description}
実施した行動：{', '.join(actions_taken) if actions_taken else 'なし'}

要件：
1. 簡潔で明確
2. 50字以内
3. 日本語で
"""
            
            messages = [
                {"role": "system", "content": "あなたは介護記録の専門家で、緊急状況の短い報告を生成するアシスタントです。"},
                {"role": "user", "content": prompt}
            ]
            
            import asyncio
            import inspect
            
            try:
                if inspect.iscoroutinefunction(ai_provider.chat):
                    loop = asyncio.get_event_loop()
                    response = loop.run_until_complete(
                        ai_provider.chat(
                            messages=messages,
                            temperature=0.5,
                            max_tokens=100
                        )
                    )
                else:
                    response = ai_provider.chat(
                        messages=messages,
                        temperature=0.5,
                        max_tokens=100
                    )
                
                summary = response.get("text", "").strip()
                return summary[:50] if len(summary) > 50 else summary
                
            except Exception as e:
                logger.log_warning(f"Failed to call AI provider for summary: {e}")
                # Use fallback report
                return f"{emergency_type}緊急：{description[:30]}"
            
        except Exception as e:
            logger.log_warning(f"Failed to generate emergency summary: {e}")
            return f"{emergency_type}緊急：{description[:30]}"
    
    def _get_fallback_guidance(
        self,
        emergency_type: str,
        severity: str
    ) -> Dict[str, Any]:
        """
        Get fallback guidance when AI unavailable
        
        Args:
            emergency_type: Emergency type
            severity: Severity level
            
        Returns:
            Fallback guidance
        """
        fallback_guidance = {
            "health": {
                "guidance_text": "落ち着いて、深呼吸をしましょう。",
                "relief_actions": ["安静にする", "体温を測る", "水分を取る"],
                "risk_notes": "症状が続く場合は、医療機関に相談してください。"
            },
            "emotional": {
                "guidance_text": "大丈夫です。一緒に深呼吸をしましょう。",
                "relief_actions": ["深呼吸をする", "静かな場所で休む", "落ち着いて話す"],
                "risk_notes": "不安が続く場合は、専門家に相談してください。"
            },
            "behavioral": {
                "guidance_text": "落ち着いて、ゆっくり話しましょう。",
                "relief_actions": ["環境を整える", "声をかける", "見守る"],
                "risk_notes": "行動が続く場合は、専門家に相談してください。"
            }
        }
        
        return fallback_guidance.get(emergency_type, {
            "guidance_text": "落ち着いて、状況を確認しましょう。",
            "relief_actions": ["状況を確認する", "安全を確保する", "必要に応じて専門家に相談する"],
            "risk_notes": "緊急の場合は、119番に連絡してください。"
        })
    
    def _emergency_record_to_dict(self, record: EmergencyRecordDB) -> Dict[str, Any]:
        """Convert emergency record to dict"""
        return {
            "record_id": record.record_id,
            "elder_id": record.elder_id,
            "caregiver_id": record.caregiver_id,
            "org_id": record.org_id,
            "emergency_type": record.emergency_type,
            "severity": record.severity,
            "description": record.description,
            "actions_taken": record.actions_taken or [],
            "ai_guidance": record.ai_guidance,
            "voice_guidance_url": record.voice_guidance_url,
            "relief_actions": record.relief_actions or [],
            "risk_notes": record.risk_notes,
            "summary": record.summary,
            "notified_contacts": record.notified_contacts or [],
            "timestamp": record.timestamp.isoformat() if record.timestamp else None,
            "created_at": record.created_at.isoformat() if record.created_at else None
        }


def get_emergency_service(db: Session) -> EmergencyService:
    """Get emergency service instance"""
    return EmergencyService(db)
