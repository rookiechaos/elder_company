"""
Embedding Service - OpenAI text embedding generation
"""

from typing import List, Optional
import os
from dotenv import load_dotenv

from services.logging_service import logger

load_dotenv()


class EmbeddingService:
    """Vector embedding service"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "text-embedding-3-small"
        self.dimension = 1536  # text-embedding-3-small output dimension
        
        if not self.api_key:
            logger.log_warning("OPENAI_API_KEY not found. Embedding service will not work.")
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate text embedding
        
        Args:
            text: Input text
            
        Returns:
            1536-d embedding vector, or None on failure
        """
        if not self.api_key:
            return None
        
        if not text or not text.strip():
            return None
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.embeddings.create(
                model=self.model,
                input=text.strip()
            )
            
            embedding = response.data[0].embedding
            
            logger.log_info(f"Generated embedding for text (length: {len(text)})")
            
            return embedding
            
        except ImportError:
            logger.log_warning("OpenAI library not installed. Install with: pip install openai")
            return None
        except Exception as e:
            logger.log_error(e, {"action": "generate_embedding", "text_length": len(text)})
            return None
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input texts
            
        Returns:
            Embedding list aligned with input texts
        """
        if not self.api_key:
            return [None] * len(texts)
        
        if not texts:
            return []
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            # Filter empty strings
            valid_texts = [t.strip() for t in texts if t and t.strip()]
            if not valid_texts:
                return [None] * len(texts)
            
            response = client.embeddings.create(
                model=self.model,
                input=valid_texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            # Map back to original list, using None for empty inputs
            result = []
            valid_idx = 0
            for text in texts:
                if text and text.strip():
                    result.append(embeddings[valid_idx])
                    valid_idx += 1
                else:
                    result.append(None)
            
            logger.log_info(f"Generated {len(embeddings)} embeddings in batch")
            
            return result
            
        except ImportError:
            logger.log_warning("OpenAI library not installed. Install with: pip install openai")
            return [None] * len(texts)
        except Exception as e:
            logger.log_error(e, {"action": "generate_embeddings_batch", "text_count": len(texts)})
            return [None] * len(texts)
    
    def get_dimension(self) -> int:
        """Return embedding vector dimension"""
        return self.dimension


# Global instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get embedding service instance (singleton)"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
