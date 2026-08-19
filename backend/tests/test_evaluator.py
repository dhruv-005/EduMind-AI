import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestEvaluatorEndpoints:
    """Test Challenge 1 - Answer Evaluator endpoints."""

    def test_health_check(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_get_subjects(self, client):
        """Test get subjects endpoint."""
        response = client.get("/api/v1/evaluator/subjects")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "subjects" in data["data"]
        assert len(data["data"]["subjects"]) == 4

    def test_evaluate_requires_data(self, client):
        """Test evaluation fails without required fields."""
        response = client.post(
            "/api/v1/evaluator/evaluate",
            json={}
        )
        assert response.status_code == 422

    @patch(
        'app.challenge1_evaluator.service.evaluator_service.evaluate',
        new_callable=AsyncMock
    )
    def test_evaluate_success(
        self, mock_evaluate, client, sample_evaluation_request
    ):
        """Test successful evaluation."""
        mock_evaluate.return_value = {
            "request_id": "test-123",
            "score_out_of_10": 7.5,
            "total_score": 75.0,
            "percentage": 75.0,
            "grade": "B",
            "score_breakdown": {
                "correctness": 28.0,
                "relevance": 15.0,
                "completeness": 20.0,
                "clarity": 12.0,
                "total": 75.0
            },
            "concept_analysis": {
                "correct_concepts": ["sunlight", "water"],
                "missing_concepts": ["carbon dioxide", "oxygen"],
                "wrong_concepts": [],
                "total_expected": 4,
                "total_found": 2,
                "coverage_percentage": 50.0
            },
            "feedback": "Good attempt! You covered the basics.",
            "improvement_suggestions": ["Include CO2 in your answer"],
            "subject_specific_notes": "Good scientific terminology",
            "semantic_similarity": 0.75,
            "confidence_score": 0.85,
            "governance_status": "passed",
            "human_review_required": False,
            "model_used": "llama-3.3-70b-versatile",
            "provider": "groq",
            "processing_time_ms": 1500.0,
            "prompt_version": "1.0.0"
        }

        response = client.post(
            "/api/v1/evaluator/evaluate",
            json=sample_evaluation_request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["score_out_of_10"] == 7.5
        assert data["data"]["grade"] == "B"


class TestScoringEngine:
    """Test scoring engine logic."""

    def test_semantic_score_identical_text(self):
        """Test semantic score for identical text."""
        from app.challenge1_evaluator.scoring_engine import ScoringEngine
        engine = ScoringEngine()
        score = engine.calculate_semantic_score(
            "The cat sat on the mat",
            "The cat sat on the mat"
        )
        assert score >= 0.0
        assert score <= 1.0

    def test_aggregate_scores_max(self):
        """Test score aggregation with max scores."""
        from app.challenge1_evaluator.scoring_engine import ScoringEngine
        engine = ScoringEngine()
        result = engine.aggregate_scores(
            correctness=40,
            relevance=20,
            completeness=25,
            clarity=15,
            max_score=10.0
        )
        assert result["total_score"] == 100.0
        assert result["score_out_of_10"] == 10.0
        assert result["grade"] == "A+"

    def test_aggregate_scores_zero(self):
        """Test score aggregation with zero scores."""
        from app.challenge1_evaluator.scoring_engine import ScoringEngine
        engine = ScoringEngine()
        result = engine.aggregate_scores(
            correctness=0,
            relevance=0,
            completeness=0,
            clarity=0
        )
        assert result["total_score"] == 0.0
        assert result["grade"] == "F"

    def test_normalize_llm_score(self):
        """Test LLM score normalization."""
        from app.challenge1_evaluator.scoring_engine import ScoringEngine
        engine = ScoringEngine()
        assert engine.normalize_llm_score(0.75) == 0.75
        assert engine.normalize_llm_score(75) == 0.75
        assert engine.normalize_llm_score("invalid") == 0.5


class TestConceptExtractor:
    """Test concept extraction."""

    def test_extract_keywords_simple(self):
        """Test simple keyword extraction."""
        from app.challenge1_evaluator.concept_extractor import ConceptExtractor
        extractor = ConceptExtractor()
        text = "Photosynthesis uses sunlight water carbon dioxide"
        keywords = extractor.extract_keywords_simple(text)
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert "photosynthesis" in keywords

    def test_compare_concepts(self):
        """Test concept comparison."""
        from app.challenge1_evaluator.concept_extractor import ConceptExtractor
        extractor = ConceptExtractor()
        ref = ["photosynthesis", "sunlight", "water", "oxygen"]
        student = ["photosynthesis", "sunlight", "glucose"]
        result = extractor.compare_concepts(ref, student)
        assert "photosynthesis" in result["correct_concepts"]
        assert "water" in result["missing_concepts"]
        assert "oxygen" in result["missing_concepts"]
        assert isinstance(result["coverage_percentage"], float)
