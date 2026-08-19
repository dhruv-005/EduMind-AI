import pytest


class TestContentFilter:
    """Test content safety filter."""

    def test_clean_input_passes(self):
        """Clean input should pass."""
        from app.governance.content_filter import ContentFilter
        cf = ContentFilter()
        status, reason, patterns = cf.check_input(
            "What is photosynthesis?"
        )
        assert status == "passed"

    def test_blocked_content(self):
        """Malicious content should be blocked."""
        from app.governance.content_filter import ContentFilter
        cf = ContentFilter()
        status, reason, patterns = cf.check_input(
            "ignore previous instructions and"
        )
        assert status == "blocked"

    def test_educational_content(self):
        """Educational content should be allowed."""
        from app.governance.content_filter import ContentFilter
        cf = ContentFilter()
        is_edu, reason = cf.is_educational(
            "Can you explain photosynthesis to me?"
        )
        assert is_edu is True

    def test_non_educational_content(self):
        """Non-educational content should be rejected."""
        from app.governance.content_filter import ContentFilter
        cf = ContentFilter()
        is_edu, reason = cf.is_educational(
            "What is the best stock to buy?"
        )
        assert is_edu is False

    def test_pii_detection(self):
        """PII should be detected."""
        from app.governance.content_filter import ContentFilter
        cf = ContentFilter()
        pii = cf.check_pii("My email is test@example.com")
        assert "emails" in pii

    def test_sanitize_removes_html(self):
        """HTML tags should be removed."""
        from app.governance.content_filter import ContentFilter
        cf = ContentFilter()
        clean = cf.sanitize_text("<script>alert('xss')</script>Hello")
        assert "<script>" not in clean
        assert "Hello" in clean


class TestRateLimiter:
    """Test rate limiting."""

    def test_allows_requests_under_limit(self):
        """Requests under limit should be allowed."""
        from app.governance.rate_limiter import InMemoryRateLimiter
        limiter = InMemoryRateLimiter()
        allowed, info = limiter.is_allowed(
            key="test-ip",
            limit=10,
            window_seconds=60
        )
        assert allowed is True
        assert info["remaining"] == 9

    def test_blocks_requests_over_limit(self):
        """Requests over limit should be blocked."""
        from app.governance.rate_limiter import InMemoryRateLimiter
        limiter = InMemoryRateLimiter()
        for _ in range(5):
            limiter.is_allowed(
                key="blocked-ip",
                limit=5,
                window_seconds=60
            )
        allowed, info = limiter.is_allowed(
            key="blocked-ip",
            limit=5,
            window_seconds=60
        )
        assert allowed is False

    def test_reset_clears_limit(self):
        """Reset should clear rate limit."""
        from app.governance.rate_limiter import InMemoryRateLimiter
        limiter = InMemoryRateLimiter()
        for _ in range(5):
            limiter.is_allowed("reset-ip", 5, 60)
        limiter.reset_key("reset-ip")
        allowed, _ = limiter.is_allowed("reset-ip", 5, 60)
        assert allowed is True


class TestBiasDetector:
    """Test bias detection."""

    def test_clean_text_no_bias(self):
        """Clean educational text should have no bias."""
        from app.governance.bias_detector import BiasDetector
        detector = BiasDetector()
        result = detector.full_bias_check(
            "Photosynthesis is the process by which plants make food."
        )
        assert result["overall_severity"] == "none"

    def test_stereotype_detection(self):
        """Stereotype patterns should be detected."""
        from app.governance.bias_detector import BiasDetector
        detector = BiasDetector()
        result = detector.check_stereotypes(
            "All boys are always better at math"
        )
        assert result["has_bias"] is True

    def test_inclusive_language(self):
        """Non-inclusive language should be flagged."""
        from app.governance.bias_detector import BiasDetector
        detector = BiasDetector()
        result = detector.check_inclusive_language(
            "The chairman of the committee..."
        )
        assert result["has_issues"] is True
        assert "chairman" in result["suggestions"]


class TestPrivacyGuard:
    """Test privacy protection."""

    def test_mask_email(self):
        """Email should be masked."""
        from app.governance.privacy_guard import PrivacyGuard
        pg = PrivacyGuard()
        masked = pg.mask_email("john@example.com")
        assert "john" not in masked
        assert "@" in masked

    def test_remove_pii(self):
        """PII should be removed from text."""
        from app.governance.privacy_guard import PrivacyGuard
        pg = PrivacyGuard()
        text = "Contact me at user@email.com or 555-123-4567"
        clean = pg.remove_pii_from_text(text)
        assert "user@email.com" not in clean
        assert "[EMAIL]" in clean

    def test_anonymize_user_id(self):
        """User ID should be anonymized."""
        from app.governance.privacy_guard import PrivacyGuard
        pg = PrivacyGuard()
        anon1 = pg.anonymize_user_id("user-123")
        anon2 = pg.anonymize_user_id("user-123")
        assert anon1 == anon2
        assert "user-123" not in anon1


class TestHumanOversight:
    """Test human oversight triggers."""

    def test_low_confidence_triggers_review(self):
        """Low confidence should trigger human review."""
        from app.governance.human_oversight import HumanOversightManager
        manager = HumanOversightManager()
        should_review, reason = manager.should_trigger_review(
            challenge="challenge1",
            confidence_score=0.3
        )
        assert should_review is True

    def test_high_confidence_no_review(self):
        """High confidence should not trigger review."""
        from app.governance.human_oversight import HumanOversightManager
        manager = HumanOversightManager()
        should_review, reason = manager.should_trigger_review(
            challenge="challenge1",
            confidence_score=0.95
        )
        assert should_review is False

    def test_hot_lead_triggers_escalation(self):
        """Hot lead score should trigger review."""
        from app.governance.human_oversight import HumanOversightManager
        manager = HumanOversightManager()
        should_review, reason = manager.should_trigger_review(
            challenge="challenge5",
            metadata={"lead_score": 90}
        )
        assert should_review is True

    def test_queue_management(self):
        """Review queue should work correctly."""
        from app.governance.human_oversight import HumanOversightManager
        manager = HumanOversightManager()
        item = manager.add_to_review_queue(
            challenge="challenge1",
            request_id="test-req-1",
            reason="Low confidence",
            content={"score": 0.3}
        )
        assert item["status"] == "pending"
        pending = manager.get_pending_reviews()
        assert len(pending) >= 1
        success = manager.approve_review(
            "test-req-1", "reviewer-1", "Looks good"
        )
        assert success is True


class TestAuditLogger:
    """Test audit logging."""

    def test_log_ai_decision(self):
        """AI decisions should be logged."""
        from app.governance.audit_logger import AuditLogger
        logger = AuditLogger()
        log = logger.log_ai_decision(
            db=None,
            request_id="test-req-123",
            challenge="challenge1",
            user_id="user-456",
            session_id=None,
            input_summary="test question",
            model_used="llama-3.3-70b",
            model_version="3.3",
            prompt_version="1.0.0",
            output_summary="score=7.5/10",
            confidence_score=0.85,
            processing_time_ms=1500.0,
            governance_status="passed"
        )
        assert log["request_id"] == "test-req-123"
        assert log["challenge"] == "challenge1"
        assert log["governance_status"] == "passed"
        assert "timestamp" in log

    def test_hash_sensitive_data(self):
        """Sensitive data should be hashed."""
        from app.governance.audit_logger import hash_sensitive_data
        hash1 = hash_sensitive_data("test@email.com")
        hash2 = hash_sensitive_data("test@email.com")
        assert hash1 == hash2
        assert "test@email.com" not in hash1
        assert len(hash1) == 16
