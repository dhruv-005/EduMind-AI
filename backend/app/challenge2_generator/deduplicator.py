import uuid
from typing import List, Dict, Any, Tuple, Optional
from app.core.logger import logger
from app.shared.embeddings import embedding_service


class Deduplicator:
    """
    Remove duplicate questions from generated set.
    Uses cosine similarity on embeddings to detect duplicates.
    """

    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def find_duplicates(
        self,
        questions: List[Dict[str, Any]],
        source_questions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find duplicate questions within generated set.
        Returns list with is_duplicate flag set.
        """
        if not questions:
            return questions

        texts = [q.get("question_text", "") for q in questions]

        logger.info(
            f"Generating embeddings for {len(texts)} questions..."
        )
        embeddings = embedding_service.embed_texts(texts)

        duplicate_indices = set()

        for i in range(len(questions)):
            if i in duplicate_indices:
                continue

            for j in range(i + 1, len(questions)):
                if j in duplicate_indices:
                    continue

                if not embeddings[i] or not embeddings[j]:
                    continue

                sim = embedding_service.cosine_similarity(
                    embeddings[i],
                    embeddings[j]
                )

                if sim >= self.threshold:
                    duplicate_indices.add(j)
                    logger.debug(
                        f"Duplicate found: Q{i+1} ≈ Q{j+1} "
                        f"(similarity={sim:.3f})"
                    )

        if source_questions:
            source_embeddings = embedding_service.embed_texts(
                source_questions
            )

            for i, (text, emb) in enumerate(
                zip(texts, embeddings)
            ):
                if i in duplicate_indices:
                    continue

                for src_emb in source_embeddings:
                    if not emb or not src_emb:
                        continue

                    sim = embedding_service.cosine_similarity(
                        emb, src_emb
                    )
                    if sim >= self.threshold:
                        duplicate_indices.add(i)
                        logger.debug(
                            f"Q{i+1} duplicates source paper "
                            f"(similarity={sim:.3f})"
                        )
                        break

        for i, question in enumerate(questions):
            question["is_duplicate"] = i in duplicate_indices
            question["similarity_checked"] = True

        logger.info(
            f"Deduplication complete: "
            f"{len(duplicate_indices)} duplicates found "
            f"out of {len(questions)} questions"
        )

        return questions

    def remove_duplicates(
        self,
        questions: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Remove duplicates from questions list.
        Returns (clean_questions, removed_count).
        """
        marked = self.find_duplicates(questions)
        clean = [q for q in marked if not q.get("is_duplicate")]
        removed = len(marked) - len(clean)

        logger.info(
            f"Removed {removed} duplicates. "
            f"{len(clean)} unique questions remain."
        )

        return clean, removed

    def is_duplicate_of_existing(
        self,
        new_question: str,
        existing_questions: List[str],
        threshold: Optional[float] = None
    ) -> Tuple[bool, float]:
        """
        Check if a single new question is duplicate of existing ones.
        Returns (is_duplicate, max_similarity).
        """
        threshold = threshold or self.threshold

        if not existing_questions:
            return False, 0.0

        new_emb = embedding_service.embed_text(new_question)
        if not new_emb:
            return False, 0.0

        max_sim = 0.0
        for existing in existing_questions:
            existing_emb = embedding_service.embed_text(existing)
            if not existing_emb:
                continue

            sim = embedding_service.cosine_similarity(
                new_emb, existing_emb
            )
            max_sim = max(max_sim, sim)

            if sim >= threshold:
                return True, sim

        return False, max_sim


# Singleton
deduplicator = Deduplicator(threshold=0.85)
