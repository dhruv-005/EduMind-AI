import pytest


class TestIntentExtractor:
    """Test intent extraction."""

    def test_extract_budget_under(self):
        """Budget with 'under' should be extracted."""
        from app.challenge5_sales.intent_extractor import IntentExtractor
        ie = IntentExtractor()
        budget = ie.extract_budget("I need a laptop under $1000")
        assert budget["budget_max"] == 1000.0

    def test_extract_budget_range(self):
        """Budget range should be extracted."""
        from app.challenge5_sales.intent_extractor import IntentExtractor
        ie = IntentExtractor()
        budget = ie.extract_budget("My budget is $500 to $800")
        assert budget["budget_min"] == 500.0
        assert budget["budget_max"] == 800.0

    def test_extract_budget_none(self):
        """No budget mentioned should return None."""
        from app.challenge5_sales.intent_extractor import IntentExtractor
        ie = IntentExtractor()
        budget = ie.extract_budget("I want a good laptop")
        assert budget["budget_max"] is None

    def test_extract_urgency_high(self):
        """High urgency keywords should be detected."""
        from app.challenge5_sales.intent_extractor import IntentExtractor
        ie = IntentExtractor()
        urgency = ie.extract_urgency("I need it today urgently")
        assert urgency == "high"

    def test_extract_urgency_low(self):
        """Low urgency should be detected."""
        from app.challenge5_sales.intent_extractor import IntentExtractor
        ie = IntentExtractor()
        urgency = ie.extract_urgency("Just browsing, no rush")
        assert urgency == "low"

    def test_detect_objections(self):
        """Objections should be detected."""
        from app.challenge5_sales.intent_extractor import IntentExtractor
        ie = IntentExtractor()
        objections = ie.detect_objections("This is too expensive")
        assert "price_too_high" in objections

    def test_extract_features(self):
        """Features should be extracted."""
        from app.challenge5_sales.intent_extractor import IntentExtractor
        ie = IntentExtractor()
        features = ie.extract_features(
            "I need something with long battery and wireless"
        )
        assert isinstance(features, list)
        assert len(features) > 0


class TestLeadScorer:
    """Test lead scoring."""

    def test_score_with_clear_budget(self):
        """Clear budget should give high budget score."""
        from app.challenge5_sales.lead_scorer import LeadScorer
        scorer = LeadScorer()
        score = scorer.score_budget({
            "budget_min": 500.0,
            "budget_max": 1000.0
        })
        assert score == 25

    def test_score_no_budget(self):
        """No budget should give low budget score."""
        from app.challenge5_sales.lead_scorer import LeadScorer
        scorer = LeadScorer()
        score = scorer.score_budget({
            "budget_min": None,
            "budget_max": None,
            "purchase_intent": "low"
        })
        assert score <= 10

    def test_hot_lead_category(self):
        """High score should be hot lead."""
        from app.challenge5_sales.lead_scorer import LeadScorer
        from app.core.constants import get_lead_category
        scorer = LeadScorer()
        result = scorer.calculate_score(
            requirements={
                "budget_min": 500,
                "budget_max": 1000,
                "purchase_intent": "high",
                "urgency": "high",
                "objections": [],
                "required_features": ["fast", "lightweight"]
            },
            customer_name="John",
            customer_email="john@test.com",
            message_count=5
        )
        assert result["total_score"] > 0
        assert result["category"] in ["hot", "warm", "cool", "cold"]

    def test_cold_lead_no_info(self):
        """No information should result in cold lead."""
        from app.challenge5_sales.lead_scorer import LeadScorer
        scorer = LeadScorer()
        result = scorer.calculate_score(
            requirements={
                "budget_min": None,
                "budget_max": None,
                "purchase_intent": "low",
                "urgency": "low",
                "objections": ["not_sure", "need_to_compare"],
                "required_features": []
            }
        )
        assert result["category"] in ["cold", "cool"]


class TestEscalationManager:
    """Test escalation logic."""

    def test_hot_lead_triggers_escalation(self):
        """Hot lead should trigger escalation."""
        from app.challenge5_sales.escalation_manager import EscalationManager
        manager = EscalationManager()
        should_escalate, reason = manager.should_escalate(
            lead_score={"total_score": 90},
            conversation_turns=3,
            requirements={},
            message="I want to buy now"
        )
        assert should_escalate is True
        assert reason == "hot_lead"

    def test_enterprise_triggers_escalation(self):
        """Enterprise keywords should trigger escalation."""
        from app.challenge5_sales.escalation_manager import EscalationManager
        manager = EscalationManager()
        should_escalate, reason = manager.should_escalate(
            lead_score={"total_score": 50},
            conversation_turns=3,
            requirements={},
            message="We need bulk order for our enterprise"
        )
        assert should_escalate is True
        assert reason == "enterprise_deal"

    def test_normal_message_no_escalation(self):
        """Normal message should not escalate."""
        from app.challenge5_sales.escalation_manager import EscalationManager
        manager = EscalationManager()
        should_escalate, reason = manager.should_escalate(
            lead_score={"total_score": 40},
            conversation_turns=2,
            requirements={},
            message="What features does this have?"
        )
        assert should_escalate is False
