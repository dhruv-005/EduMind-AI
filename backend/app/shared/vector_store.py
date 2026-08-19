import os
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logger import logger


class VectorStore:
    """
    ChromaDB vector store wrapper.
    Used for semantic search across questions and products.
    """

    def __init__(self):
        self._client = None
        self._collections: Dict[str, Any] = {}

    def _get_client(self):
        """Initialize ChromaDB client lazily."""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings

                os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)

                self._client = chromadb.PersistentClient(
                    path=settings.CHROMA_PERSIST_DIR,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                logger.info(
                    f"ChromaDB initialized at: {settings.CHROMA_PERSIST_DIR}"
                )
            except Exception as e:
                logger.error(f"ChromaDB init failed: {e}")
                raise
        return self._client

    def get_or_create_collection(
        self,
        collection_name: str,
        metadata: Optional[Dict] = None
    ) -> Any:
        """Get or create a ChromaDB collection."""
        if collection_name not in self._collections:
            try:
                client = self._get_client()
                collection = client.get_or_create_collection(
                    name=collection_name,
                    metadata=metadata or {"hnsw:space": "cosine"}
                )
                self._collections[collection_name] = collection
                logger.info(f"Collection ready: {collection_name}")
            except Exception as e:
                logger.error(
                    f"Failed to get/create collection "
                    f"'{collection_name}': {e}"
                )
                raise
        return self._collections[collection_name]

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        embeddings: List[List[float]],
        ids: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> bool:
        """Add documents with embeddings to collection."""
        try:
            collection = self.get_or_create_collection(collection_name)

            collection.add(
                documents=documents,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas or [{} for _ in documents]
            )

            logger.info(
                f"Added {len(documents)} docs to '{collection_name}'"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False

    def search(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search in collection.
        Returns list of results with documents, metadata, distances.
        """
        try:
            collection = self.get_or_create_collection(collection_name)

            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": min(top_k, collection.count() or 1),
                "include": ["documents", "metadatas", "distances"]
            }

            if where:
                query_params["where"] = where

            results = collection.query(**query_params)

            formatted = []
            if results and results.get("documents"):
                docs = results["documents"][0]
                metas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0]

                for doc, meta, dist in zip(docs, metas, distances):
                    similarity = max(0.0, 1.0 - float(dist))
                    formatted.append({
                        "document": doc,
                        "metadata": meta or {},
                        "similarity": round(similarity, 4),
                        "distance": round(float(dist), 4)
                    })

            return formatted

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection entirely."""
        try:
            client = self._get_client()
            client.delete_collection(collection_name)
            if collection_name in self._collections:
                del self._collections[collection_name]
            logger.info(f"Collection deleted: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False

    def clear_collection(self, collection_name: str) -> bool:
        """Clear all documents from a collection."""
        try:
            collection = self.get_or_create_collection(collection_name)
            all_ids = collection.get()["ids"]
            if all_ids:
                collection.delete(ids=all_ids)
            logger.info(
                f"Cleared {len(all_ids)} docs from '{collection_name}'"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False

    def count(self, collection_name: str) -> int:
        """Count documents in collection."""
        try:
            collection = self.get_or_create_collection(collection_name)
            return collection.count()
        except Exception as e:
            logger.error(f"Count failed for '{collection_name}': {e}")
            return 0

    def upsert_documents(
        self,
        collection_name: str,
        documents: List[str],
        embeddings: List[List[float]],
        ids: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> bool:
        """Upsert documents (add or update)."""
        try:
            collection = self.get_or_create_collection(collection_name)
            collection.upsert(
                documents=documents,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas or [{} for _ in documents]
            )
            logger.info(
                f"Upserted {len(documents)} docs in '{collection_name}'"
            )
            return True
        except Exception as e:
            logger.error(f"Upsert failed: {e}")
            return False

    def get_collection_info(
        self,
        collection_name: str
    ) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            collection = self.get_or_create_collection(collection_name)
            count = collection.count()
            return {
                "name": collection_name,
                "document_count": count,
                "status": "ready"
            }
        except Exception as e:
            return {
                "name": collection_name,
                "document_count": 0,
                "status": f"error: {str(e)}"
            }


# Singleton
vector_store = VectorStore()

# Collection names
COLLECTION_QUESTIONS = "exam_questions"
COLLECTION_PRODUCTS = "products_catalogue"
COLLECTION_SESSIONS = "tutor_sessions"
