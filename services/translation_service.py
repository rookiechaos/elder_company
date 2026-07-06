"""
Translation Service - Handles translation using AI providers
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from services.ai_providers import get_ai_provider, AIProvider
from services.base_service import BaseService
from config.settings import settings

load_dotenv()


class TranslationService(BaseService):
    """Service for translation with caregiving context optimization"""
    
    def __init__(self, db=None):
        # TranslationService doesn't always need a DB session
        super().__init__(db)
        try:
            self.provider: AIProvider = get_ai_provider()
            self.provider_name = settings.ai_provider.lower()
        except Exception as e:
            raise ValueError(f"Failed to initialize AI provider: {str(e)}")
    
    def _get_translation_prompt(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: Optional[str] = None,
        personalization: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate translation prompt with caregiving context and personalization"""
        
        # Language names mapping
        lang_names = {
            "ja": "Japanese",
            "en": "English",
        }
        
        source_lang_name = lang_names.get(source_language, source_language)
        target_lang_name = lang_names.get(target_language, target_language)
        
        # Base translation guidelines
        base_guidelines = """Translation Guidelines:
1. Translate accurately and naturally
2. Use appropriate honorifics and respectful language when needed
3. Maintain the tone and formality level of the original text
4. For caregiving terminology, use standard professional terms
5. Keep the meaning clear and easy to understand
6. Preserve any important emotional nuances"""
        
        # Personalization instructions
        personalization_instructions = ""
        if personalization:
            style = personalization.get("translation_style", "professional")
            detail = personalization.get("detail_level", "moderate")
            use_honorifics = personalization.get("use_honorifics", True)
            custom_terms = personalization.get("custom_terms", {})
            care_scenarios = personalization.get("care_scenarios", [])
            role = personalization.get("role")
            
            personalization_instructions = "\n\nPersonalization Instructions:\n"
            
            # Translation style
            if style == "casual":
                personalization_instructions += "- Use a more casual, friendly tone\n"
            elif style == "formal":
                personalization_instructions += "- Use a formal, respectful tone\n"
            else:
                personalization_instructions += "- Use a professional, balanced tone\n"
            
            # Detail level
            if detail == "brief":
                personalization_instructions += "- Keep translations concise and to the point\n"
            elif detail == "detailed":
                personalization_instructions += "- Provide more detailed translations when context is helpful\n"
            
            # Honorifics
            if use_honorifics:
                personalization_instructions += "- Use appropriate honorifics and respectful language\n"
            else:
                personalization_instructions += "- Use standard language without excessive honorifics\n"
            
            # Custom terms
            if custom_terms:
                personalization_instructions += "\nCustom Terminology (use these translations):\n"
                for term, translation in list(custom_terms.items())[:10]:  # Limit to 10 terms
                    personalization_instructions += f"- {term} → {translation}\n"
            
            # Care scenarios
            if care_scenarios:
                personalization_instructions += f"\nCommon Care Scenarios: {', '.join(care_scenarios[:5])}\n"
            
            # Role context
            if role:
                personalization_instructions += f"\nUser Role: {role}\n"
        
        # Caregiving context instruction
        context_instruction = ""
        if context:
            context_instruction = f"\n\nContext: {context}"
        
        # Enhanced prompt for collaborative care context
        collaboration_context = ""
        if context and "activity" in context.lower():
            collaboration_context = "\n\nCollaboration Context: This translation is for collaborative activities between caregivers and elders. Focus on:\n- Clear, encouraging language\n- Activity-related terminology\n- Supportive and engaging tone"
        
        system_prompt = f"""You are a professional translator specializing in caregiving and elderly care communication. 
Your translations are used by caregivers in Japan to communicate with elderly people and their families, especially for collaborative activities.

{base_guidelines}
{personalization_instructions}
{collaboration_context}
{context_instruction}

Translate the following text from {source_lang_name} to {target_lang_name}.
Provide ONLY the translation, without explanations or additional text."""

        return system_prompt
    
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: Optional[str] = None,
        personalization: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Translate text using AI provider"""
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if source_language == target_language:
            return {
                "original_text": text,
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "provider": self.provider_name
            }
        
        try:
            system_prompt = self._get_translation_prompt(
                text, source_language, target_language, context, personalization
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
            
            response = await self.provider.chat(
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent translations
                max_tokens=2000
            )
            
            translated_text = response["text"].strip()
            
            # Clean up the response (remove any extra explanations)
            # Sometimes AI adds explanations, try to extract just the translation
            lines = translated_text.split("\n")
            if len(lines) > 1:
                # Check if first line is explanation
                first_line_lower = lines[0].lower()
                if any(word in first_line_lower for word in ["translation", "訳", "here", "the following"]):
                    translated_text = "\n".join(lines[1:]).strip()
            
            return {
                "original_text": text,
                "translated_text": translated_text,
                "source_language": source_language,
                "target_language": target_language,
                "provider": response.get("provider", self.provider_name),
                "model": response.get("model", "")
            }
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")
    
    async def translate_conversation(
        self,
        message: str,
        source_language: str,
        target_language: str,
        conversation_history: Optional[list] = None,
        personalization: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Translate conversation message with context"""
        
        context_prompt = ""
        if conversation_history:
            context_prompt = "\n\nPrevious conversation context:\n"
            for entry in conversation_history[-3:]:  # Last 3 messages for context
                context_prompt += f"- {entry.get('original', '')} -> {entry.get('translated', '')}\n"
        
        return await self.translate(
            message,
            source_language,
            target_language,
            context=context_prompt,
            personalization=personalization
        )
