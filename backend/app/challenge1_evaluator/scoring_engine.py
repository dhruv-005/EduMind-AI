from typing import Dict, Any, Optional
from app.core.logger import logger
from app.core.constants import get_grade
from app.shared.embeddings import embedding_service


class ScoringEngine:
    """
    Multi-layer scoring engine for answer evaluation.
    Combines semantic similarity + LLM scores + concept coverage.
    """

    # Score weights (must sum to 100)
    WEIGHTS = {
        "correctness": 40,   # Is the core answer correct?
        "relevance": 20,     # Is it relevant to the question?
        "completeness": 25,  # Are all concepts covered?
        "clarity": 15        # Is it clearly written?
    }

    def calculate_semantic_score(
        self,
        student_answer: str,
        reference_answer: str
    ) -> float:
        """
        Calculate semantic similarity score using embeddings.
        Returns 0.0 to 1.0.
        """
        try:
            similarity = embedding_service.similarity_score(
                student_answer,
                reference_answer
            )
            return round(float(similarity), 4)
        except Exception as e:
            logger.warning(f"Semantic score failed: {e}")
            return 0.0

    def calculate_correctness_score(
        self,
        semantic_similarity: float,
        llm_correctness: float,
        concept_coverage: float
    ) -> float:
        """
        Calculate correctness score (0-40).
        Combines semantic similarity + LLM judgment + concept coverage.
        """
        # Weighted average of three signals
        weighted = (
            semantic_similarity * 0.3 +
            llm_correctness * 0.5 +
            concept_coverage * 0.2
        )
        # Scale to 0-40
        score = weighted * self.WEIGHTS["correctness"]
        return round(min(score, self.WEIGHTS["correctness"]), 2)

    def calculate_relevance_score(
        self,
        semantic_similarity: float,
        llm_relevance: float
    ) -> float:
        """
        Calculate relevance score (0-20).
        How relevant is the answer to the question?
        """
        weighted = (
            semantic_similarity * 0.4 +
            llm_relevance * 0.6
        )
        score = weighted * self.WEIGHTS["relevance"]
        return round(min(score, self.WEIGHTS["relevance"]), 2)

    def calculate_completeness_score(
        self,
        concept_coverage: float,
        llm_completeness: float
    ) -> float:
        """
        Calculate completeness score (0-25).
        How many required concepts were covered?
        """
        weighted = (
            concept_coverage * 0.5 +
            llm_completeness * 0.5
        )
        score = weighted * self.WEIGHTS["completeness"]
        return round(min(score, self.WEIGHTS["completeness"]), 2)

    def calculate_clarity_score(
        self,
        llm_clarity: float
    ) -> float:
        """
        Calculate clarity score (0-15).
        How clearly is the answer written?
        """
        score = llm_clarity * self.WEIGHTS["clarity"]
        return round(min(score, self.WEIGHTS["clarity"]), 2)

    def aggregate_scores(
        self,
        correctness: float,
        relevance: float,
        completeness: float,
        clarity: float,
        max_score: float = 10.0
    ) -> Dict[str, Any]:
        """
        Aggregate all scores into final result.
        Returns complete score breakdown.
        """
        # Total out of 100
        total_100 = correctness + relevance + completeness + clarity
        total_100 = round(min(total_100, 100.0), 2)

        # Convert to max_score scale
        score_out_of_max = round(
            (total_100 / 100.0) * max_score, 2
        )

        # Percentage
        percentage = round(total_100, 1)

        # Grade
        grade = get_grade(percentage)

        return {
            "score_breakdown": {
                "correctness": correctness,
                "relevance": relevance,
                "completeness": completeness,
                "clarity": clarity,
                "total": total_100
            },
            "total_score": total_100,
            "score_out_of_10": round(
                (total_100 / 100.0) * 10.0, 2
            ),
            "score_out_of_max": score_out_of_max,
            "percentage": percentage,
            "grade": grade
        }

    def apply_penalties(
        self,
        score: float,
        penalties: Dict[str, float]
    ) -> float:
        """
        Apply penalties to score.
        Examples: off-topic (-20%), plagiarism detected (-30%)
        """
        total_penalty = sum(penalties.values())
        penalized = score * (1.0 - total_penalty)
        return max(0.0, round(penalized, 2))

    def apply_strict_mode(
        self,
        scores: Dict[str, float],
        missing_concept_count: int
    ) -> Dict[str, float]:
        """
        Apply strict mode penalties for missing concepts.
        Each missing concept reduces completeness score.
        """
        if missing_concept_count > 0:
            penalty_per_concept = 2.0
            completeness_penalty = min(
                penalty_per_concept * missing_concept_count,
                scores["completeness"] * 0.5
            )
            scores["completeness"] = max(
                0.0,
                scores["completeness"] - completeness_penalty
            )
            logger.debug(
                f"Strict mode penalty: "
                f"-{completeness_penalty:.1f} for "
                f"{missing_concept_count} missing concepts"
            )
        return scores

    def normalize_llm_score(
        self,
        llm_score: Any,
        min_val: float = 0.0,
        max_val: float = 1.0
    ) -> float:
        """
        Normalize LLM-provided score to 0.0-1.0 range.
        Handles various LLM output formats.
        """
        try:
            score = float(llm_score)

            # If score is in 0-100 range, normalize
            if score > 1.0:
                score = score / 100.0

            return round(max(min_val, min(max_val, score)), 4)

        except (ValueError, TypeError):
            logger.warning(
                f"Could not normalize LLM score: {llm_score}"
            )
            return 0.5  # Default to middle score

    def compute_confidence(
        self,
        semantic_similarity: float,
        concept_coverage: float,
        answer_length_ratio: float
    ) -> float:
        """
        Compute confidence score for the evaluation.
        Low confidence triggers human review.
        Returns 0.0 to 1.0.
        """
        # High semantic similarity = high confidence
        sim_confidence = semantic_similarity

        # Good concept coverage = high confidence
        concept_confidence = concept_coverage

        # Reasonable answer length = higher confidence
        # Ratio: student_len / reference_len
        if answer_length_ratio < 0.1:
            length_confidence = 0.3  # Very short answer
        elif answer_length_ratio > 3.0:
            length_confidence = 0.6  # Very long answer
        else:
            length_confidence = 0.9  # Reasonable length

        confidence = (
            sim_confidence * 0.4 +
            concept_confidence * 0.4 +
            length_confidence * 0.2
        )

        return round(max(0.0, min(1.0, confidence)), 3)


# Singleton
scoring_engine = ScoringEngine()
