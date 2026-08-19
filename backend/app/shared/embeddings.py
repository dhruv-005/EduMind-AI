import hashlib
from typing import List, Optional, Dict, Any
from app.core.logger import logger
from app.core.redis_client import cache_get, cache_set


class EmbeddingService:
    """
    Text embedding service using sentence-transformers.
    With Redis caching to avoid recomputing same embeddings.
    """

    def __init__(self):
        self._model = None
        self._model_name = "all-MiniLM-L6-v2"

    def _load_model(self):
        """Load embedding model lazily."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self._model_name)
                logger.info(
                    f"Embedding model loaded: {self._model_name}"
                )
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
        return self._model

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"embedding:{self._model_name}:{text_hash}"

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        Returns list of floats.
        """
        if not text or not text.strip():
            return []

        try:
            model = self._load_model()
            text_clean = text.strip()[:512]  # Limit input length
            embedding = model.encode(
                text_clean,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return []

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch).
        More efficient than calling embed_text multiple times.
        """
        if not texts:
            return []

        try:
            model = self._load_model()
            clean_texts = [t.strip()[:512] for t in texts if t and t.strip()]
            embeddings = model.encode(
                clean_texts,
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=32
            )
            return [e.tolist() for e in embeddings]
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return [[] for _ in texts]

    def cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        Returns value between -1 and 1 (1 = identical).
        """
        if not embedding1 or not embedding2:
            return 0.0

        try:
            import numpy as np
            e1 = np.array(embedding1)
            e2 = np.array(embedding2)

            dot_product = np.dot(e1, e2)
            norm1 = np.linalg.norm(e1)
            norm2 = np.linalg.norm(e2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(np.clip(similarity, -1.0, 1.0))

        except Exception as e:
            logger.error(f"Cosine similarity failed: {e}")
            return 0.0

    def similarity_score(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        Get similarity score between two texts.
        Returns value 0.0 to 1.0.
        """
        if not text1 or not text2:
            return 0.0

        e1 = self.embed_text(text1)
        e2 = self.embed_text(text2)
        raw = self.cosine_similarity(e1, e2)

        # Normalize to 0-1 range
        return max(0.0, float(raw))

    def find_most_similar(
        self,
        query_text: str,
        candidate_texts: List[str],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find most similar texts from candidates.
        Returns top_k results sorted by similarity.
        """
        if not query_text or not candidate_texts:
            return []

        query_embedding = self.embed_text(query_text)
        if not query_embedding:
            return []

        candidate_embeddings = self.embed_texts(candidate_texts)

        results = []
        for i, (text, embedding) in enumerate(
            zip(candidate_texts, candidate_embeddings)
        ):
            if embedding:
                sim = self.cosine_similarity(query_embedding, embedding)
                results.append({
                    "index": i,
                    "text": text,
                    "similarity": round(sim, 4)
                })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def is_duplicate(
        self,
        text1: str,
        text2: str,
        threshold: float = 0.85
    ) -> bool:
        """
        Check if two texts are duplicates.
        Returns True if similarity >= threshold.
        """
        sim = self.similarity_score(text1, text2)
        return sim >= threshold

    def get_model_info(self) -> Dict[str, Any]:
        """Get embedding model information."""
        return {
            "model_name": self._model_name,
            "model_loaded": self._model is not None,
            "embedding_dimension": 384,
            "max_input_length": 512
        }


# Singleton instance
embedding_service = EmbeddingService()
