from utils.time_utils import utc_now
"""
RAG Service - Retrieval-Augmented Generation Service
RAG Service - Retrieval-Augmented Generation
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import numpy as np
import json
import os

from services.base_service import BaseService
from services.logging_service import logger
from models.knowledge_models import KnowledgeBaseDB
from config.disclaimers import get_disclaimer_knowledge, get_disclaimer_knowledge_empty
from services.ai_providers import get_ai_provider, AIProvider


class RAGService(BaseService):
    """RAG service - retrieval-augmented generation"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        try:
            self.ai_provider: AIProvider = get_ai_provider()
        except Exception as e:
            logger.log_warning(f"AI provider not available for RAG: {e}")
            self.ai_provider = None
    
    def add_document(
        self,
        title: str,
        content: str,
        doc_type: str,
        category: Optional[str] = None,
        source: Optional[str] = None,
        source_url: Optional[str] = None,
        tags: Optional[List[str]] = None,
        org_id: Optional[str] = None,
        created_by: Optional[str] = None,
        is_public: bool = False,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> Dict[str, Any]:
        """
        Add document to knowledge base (with chunking)
        
        Args:
            title: Document title
            content: Document content
            doc_type: Document type (medical, diet, care_guide)
            category: Category (optional)
            source: Source (optional)
            source_url: Source URL (optional)
            tags: Tag list (optional)
            org_id: Organization ID (optional)
            created_by: Creator ID (optional)
            is_public: Public flag (default False)
            chunk_size: Chunk size in characters (default 500)
            chunk_overlap: Chunk overlap in characters (default 50)
            
        Returns:
            Created document (includes chunk info)
        """
        import uuid
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        
        # Chunk document content
        chunks = self._chunk_document(content, chunk_size, chunk_overlap)
        
        # Generate embedding for each chunk
        chunk_embeddings = []
        for chunk in chunks:
            embedding = self._generate_embedding(chunk)
            chunk_embeddings.append({
                "text": chunk,
                "embedding": embedding
            })
        
        # Use first chunk embedding as document embedding (or merge all)
        main_embedding = chunk_embeddings[0]["embedding"] if chunk_embeddings else None
        
        # Store chunk info in metadata
        extra_metadata = {
            "chunks": chunks,
            "chunk_count": len(chunks),
            "chunk_embeddings": chunk_embeddings  # Note: production may store chunks separately
        }
        
        doc = KnowledgeBaseDB(
            doc_id=doc_id,
            title=title,
            content=content,
            doc_type=doc_type,
            category=category,
            source=source,
            source_url=source_url,
            tags=tags or [],
            embedding=main_embedding,
            org_id=org_id,
            created_by=created_by,
            is_public=is_public,
            extra_metadata=extra_metadata
        )
        
        self.db.add(doc)
        try:
            self.safe_commit("add_document")
            self.safe_refresh(doc, "add_document")
            logger.log_info(f"Document added to knowledge base: {doc_id} (chunks: {len(chunks)})")
        except Exception as e:
            self.handle_database_error(e, "add_document", {"doc_id": doc_id})
            raise
        
        result = self._doc_to_dict(doc)
        result["chunk_count"] = len(chunks)
        
        return result
    
    def _chunk_document(self, content: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
        """
        Chunk document content
        
        Args:
            content: Document content
            chunk_size: Chunk size in characters
            chunk_overlap: Chunk overlap in characters
            
        Returns:
            List of chunks
        """
        if len(content) <= chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            
            # Split at sentence boundaries, newlines, etc.
            if end < len(content):
                # Find best split point
                for split_char in ['\n\n', '\n', '。', '.', '！', '!']:
                    split_pos = content.rfind(split_char, start, end)
                    if split_pos != -1:
                        end = split_pos + 1
                        break
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Advance to next chunk (with overlap)
            start = end - chunk_overlap
            if start >= len(content):
                break
        
        return chunks
    
    def search_documents(
        self,
        query: str,
        doc_type: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        top_k: int = 5,
        org_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search relevant documents
        
        Args:
            query: Search query
            doc_type: Document type filter (optional)
            category: Category filter (optional)
            tags: Tag filter (optional)
            top_k: Number of results (default 5)
            org_id: Organization ID (optional)
            
        Returns:
            Relevant documents sorted by similarity
        """
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        if not query_embedding:
            # Fall back to text search if embedding unavailable
            return self._text_search(query, doc_type, category, tags, top_k, org_id)
        
        # Fetch all documents
        query_obj = self.db.query(KnowledgeBaseDB).filter(
            KnowledgeBaseDB.is_active == True
        )
        
        if doc_type:
            query_obj = query_obj.filter(KnowledgeBaseDB.doc_type == doc_type)
        if category:
            query_obj = query_obj.filter(KnowledgeBaseDB.category == category)
        if org_id:
            query_obj = query_obj.filter(
                (KnowledgeBaseDB.org_id == org_id) | (KnowledgeBaseDB.is_public == True)
            )
        else:
            query_obj = query_obj.filter(KnowledgeBaseDB.is_public == True)
        
        docs = query_obj.all()
        
        # Compute similarity
        results = []
        for doc in docs:
            if not doc.embedding:
                continue
            
            # Filter by tags
            if tags:
                doc_tags = doc.tags or []
                if not any(tag in doc_tags for tag in tags):
                    continue
            
            # Compute cosine similarity
            similarity = self._cosine_similarity(query_embedding, doc.embedding)
            
            results.append({
                "doc": doc,
                "similarity": similarity
            })
        
        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Return top_k results
        top_results = results[:top_k]
        
        # Update search count
        try:
            for result in top_results:
                doc = result["doc"]
                doc.search_count = (doc.search_count or 0) + 1
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.log_warning(f"Failed to update search count: {e}")
            # Log warning only; search count failure must not affect results
        
        return [self._doc_to_dict(result["doc"]) for result in top_results]
    
    def ask(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        top_k: int = 3,
        conversation_id: Optional[str] = None,
        language: str = "ja"
    ) -> Dict[str, Any]:
        """
        RAG Q&A (supports multi-turn dialogue)
        
        Args:
            question: Question
            context: Context (optional; elder_id, etc.)
            top_k: Number of documents to retrieve (default 3)
            conversation_id: Conversation ID for multi-turn dialogue (optional)
            language: Disclaimer language (zh, ja, en); default ja
            
        Returns:
            Answer and source links
        """
        # Load conversation history when conversation_id is provided
        conversation_history = []
        if conversation_id:
            conversation_history = self._get_conversation_history(conversation_id)
        
        # 1. Search relevant documents (question + history context)
        search_query = question
        if conversation_history:
            # Include recent questions in search
            recent_questions = [msg.get("content", "") for msg in conversation_history[-2:] if msg.get("type") == "question"]
            if recent_questions:
                search_query = " ".join(recent_questions) + " " + question
        
        doc_type = context.get("doc_type") if context else None
        category = context.get("category") if context else None
        
        relevant_docs = self.search_documents(
            query=search_query,
            doc_type=doc_type,
            category=category,
            top_k=top_k
        )
        
        lang = language or "ja"
        if not relevant_docs:
            return {
                "answer": (
                    "申し訳ございませんが、関連する情報が見つかりませんでした。"
                    if lang == "ja"
                    else "No relevant information found."
                ),
                "sources": [],
                "disclaimer": get_disclaimer_knowledge_empty(lang),
                "conversation_id": conversation_id
            }
        
        # 2. Build context (enhanced, includes conversation history)
        context_text = self._build_enhanced_context(relevant_docs, conversation_history)
        
        # 3. Generate answer with LLM (includes conversation history)
        answer = self._generate_answer_with_history(question, context_text, conversation_history)
        
        # 4. Save conversation history
        if conversation_id:
            self._save_conversation_message(conversation_id, question, answer, relevant_docs)
        
        # 5. Extract source links
        sources = [
            {
                "title": doc["title"],
                "source": doc.get("source"),
                "url": doc.get("source_url"),
                "doc_type": doc.get("doc_type")
            }
            for doc in relevant_docs
        ]
        
        return {
            "answer": answer,
            "sources": sources,
            "disclaimer": get_disclaimer_knowledge(lang),
            "conversation_id": conversation_id
        }
    
    def create_conversation(
        self,
        user_id: Optional[str] = None,
        elder_id: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> str:
        """
        Create new conversation
        
        Args:
            user_id: User ID (optional)
            elder_id: Elder ID (optional)
            org_id: Organization ID (optional)
            
        Returns:
            Conversation ID
        """
        from models.summary_models import ConversationHistoryDB
        import uuid
        
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        
        conversation = ConversationHistoryDB(
            conversation_id=conversation_id,
            user_id=user_id,
            elder_id=elder_id,
            org_id=org_id,
            messages=[]
        )
        
        self.db.add(conversation)
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.log_error(e, {"action": "create_conversation", "user_id": user_id})
            raise ValueError(f"Failed to create conversation: {str(e)}")
        
        return conversation_id
    
    def _get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history"""
        from models.summary_models import ConversationHistoryDB
        
        conversation = self.db.query(ConversationHistoryDB).filter(
            ConversationHistoryDB.conversation_id == conversation_id
        ).first()
        
        if not conversation:
            return []
        
        return conversation.messages or []
    
    def _save_conversation_message(
        self,
        conversation_id: str,
        question: str,
        answer: str,
        relevant_docs: List[Dict[str, Any]]
    ):
        """Save conversation message"""
        from models.summary_models import ConversationHistoryDB
        from datetime import datetime
        
        conversation = self.db.query(ConversationHistoryDB).filter(
            ConversationHistoryDB.conversation_id == conversation_id
        ).first()
        
        if not conversation:
            return
        
        messages = conversation.messages or []
        
        # Append question and answer
        messages.append({
            "type": "question",
            "content": question,
            "timestamp": utc_now().isoformat()
        })
        
        messages.append({
            "type": "answer",
            "content": answer,
            "sources": [doc.get("doc_id") for doc in relevant_docs],
            "timestamp": utc_now().isoformat()
        })
        
        conversation.messages = messages
        conversation.last_message_at = utc_now()
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.log_warning(f"Failed to save conversation message: {e}")
    
    def _build_enhanced_context(
        self,
        docs: List[Dict[str, Any]],
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        """Build enhanced context with conversation history"""
        context_parts = []
        
        # Add document context
        for i, doc in enumerate(docs, 1):
            # Use most relevant chunk when document is chunked
            chunks = doc.get("extra_metadata", {}).get("chunks", [])
            if chunks:
                # Use first chunk (or pick most relevant per question)
                content = chunks[0][:500] if len(chunks[0]) > 500 else chunks[0]
            else:
                content = doc['content'][:500] if len(doc['content']) > 500 else doc['content']
            
            context_parts.append(f"[Document{i}】{doc['title']}\n{content}...")
        
        # Add conversation history context if present
        if conversation_history:
            history_text = "[Conversation history]\n"
            for msg in conversation_history[-3:]:  # Use only the last 3 conversation turns
                if msg.get("type") == "question":
                    history_text += f"Q: {msg.get('content', '')}\n"
                elif msg.get("type") == "answer":
                    history_text += f"A: {msg.get('content', '')[:200]}...\n"
            context_parts.insert(0, history_text)
        
        return "\n\n".join(context_parts)
    
    def _generate_answer_with_history(
        self,
        question: str,
        context: str,
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        """Generate answer with LLM using conversation history"""
        if not self.ai_provider:
            return "AIサービスが利用できません。"
        
        try:
            # Build message history
            messages = [
                {"role": "system", "content": "あなたは介護の専門知識を持つアシスタントです。参考情報に基づいて、安全で正確な回答を提供してください。会話の文脈を考慮して回答してください。"}
            ]
            
            # Add conversation history
            for msg in conversation_history[-4:]:  # Last 4 messages
                if msg.get("type") == "question":
                    messages.append({"role": "user", "content": msg.get("content", "")})
                elif msg.get("type") == "answer":
                    messages.append({"role": "assistant", "content": msg.get("content", "")})
            
            # Add current question and context
            prompt = f"""以下の情報を参考に、質問に答えてください。

参考情報：
{context}

質問：{question}

回答の要件：
1. 参考情報に基づいて回答してください
2. 会話の文脈を考慮してください
3. 医療診断は行わないでください
4. 明確で分かりやすい回答をしてください
5. 日本語で回答してください
"""
            messages.append({"role": "user", "content": prompt})
            
            # Simplified async call handling
            response = self._call_ai_provider_safe(messages)
            return response.get("text", "回答を生成できませんでした。")
        except Exception as e:
            logger.log_error(e, {"action": "generate_answer_with_history", "question": question})
            return "回答の生成中にエラーが発生しました。"
    
    def _call_ai_provider_safe(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Safely call AI provider (simplified async handling)"""
        import asyncio
        import inspect
        
        try:
            if inspect.iscoroutinefunction(self.ai_provider.chat):
                # Async call - simplified approach
                try:
                    # Try to get current event loop
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If loop is running, use run_in_executor
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(
                                lambda: asyncio.run(
                                    self.ai_provider.chat(
                                        messages=messages,
                                        temperature=0.3,
                                        max_tokens=1000
                                    )
                                )
                            )
                            return future.result(timeout=30)
                    else:
                        # If loop is not running, call directly
                        return loop.run_until_complete(
                            self.ai_provider.chat(
                                messages=messages,
                                temperature=0.3,
                                max_tokens=1000
                            )
                        )
                except RuntimeError:
                    # If no event loop, create one
                    return asyncio.run(
                        self.ai_provider.chat(
                            messages=messages,
                            temperature=0.3,
                            max_tokens=1000
                        )
                    )
            else:
                # Synchronous call
                return self.ai_provider.chat(
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1000
                )
        except Exception as e:
            logger.log_warning(f"Failed to call AI provider: {e}")
            raise
    
    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate text embedding
        
        Args:
            text: Text
            
        Returns:
            Embedding vector (list)
        """
        try:
            from services.embedding_service import get_embedding_service
            
            embedding_service = get_embedding_service()
            embedding = embedding_service.generate_embedding(text)
            
            return embedding
        except Exception as e:
            logger.log_warning(f"Failed to generate embedding: {e}")
            return None
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity"""
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception:
            return 0.0
    
    def _text_search(
        self,
        query: str,
        doc_type: Optional[str],
        category: Optional[str],
        tags: Optional[List[str]],
        top_k: int,
        org_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Text search when vector search unavailable"""
        query_obj = self.db.query(KnowledgeBaseDB).filter(
            KnowledgeBaseDB.is_active == True
        )
        
        if doc_type:
            query_obj = query_obj.filter(KnowledgeBaseDB.doc_type == doc_type)
        if category:
            query_obj = query_obj.filter(KnowledgeBaseDB.category == category)
        if org_id:
            query_obj = query_obj.filter(
                (KnowledgeBaseDB.org_id == org_id) | (KnowledgeBaseDB.is_public == True)
            )
        else:
            query_obj = query_obj.filter(KnowledgeBaseDB.is_public == True)
        
        # Simple text matching
        docs = query_obj.filter(
            (KnowledgeBaseDB.title.contains(query)) | (KnowledgeBaseDB.content.contains(query))
        ).limit(top_k).all()
        
        return [self._doc_to_dict(doc) for doc in docs]
    
    def _build_context(self, docs: List[Dict[str, Any]]) -> str:
        """Build context text"""
        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"[Document{i}】{doc['title']}\n{doc['content'][:500]}...")
        return "\n\n".join(context_parts)
    
    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer with LLM"""
        if not self.ai_provider:
            return "AIサービスが利用できません。"
        
        try:
            prompt = f"""以下の情報を参考に、質問に答えてください。

参考情報：
{context}

質問：{question}

回答の要件：
1. 参考情報に基づいて回答してください
2. 医療診断は行わないでください
3. 明確で分かりやすい回答をしてください
4. 日本語で回答してください
"""
            
            messages = [
                {"role": "system", "content": "あなたは介護の専門知識を持つアシスタントです。参考情報に基づいて、安全で正確な回答を提供してください。"},
                {"role": "user", "content": prompt}
            ]
            
            # Use unified async call handling
            response = self._call_ai_provider_safe(messages)
            return response.get("text", "回答を生成できませんでした。")
        except Exception as e:
            logger.log_error(e, {"action": "generate_answer", "question": question})
            return "回答の生成中にエラーが発生しました。"
    
    def _doc_to_dict(self, doc: KnowledgeBaseDB) -> Dict[str, Any]:
        """Convert document to dict"""
        return {
            "doc_id": doc.doc_id,
            "title": doc.title,
            "content": doc.content,
            "doc_type": doc.doc_type,
            "category": doc.category,
            "source": doc.source,
            "source_url": doc.source_url,
            "tags": doc.tags or [],
            "org_id": doc.org_id,
            "created_by": doc.created_by,
            "is_public": doc.is_public,
            "view_count": doc.view_count or 0,
            "search_count": doc.search_count or 0,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "updated_at": doc.updated_at.isoformat() if doc.updated_at else None
        }


def get_rag_service(db: Session) -> RAGService:
    """Get RAG service instance"""
    return RAGService(db)
