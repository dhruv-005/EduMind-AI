import pytest


class TestSpellDetector:
    """Test spelling detection."""

    def test_tokenize_text(self):
        """Text should be tokenized into words."""
        from app.challenge3_spelling.spell_detector import SpellDetector
        detector = SpellDetector()
        words = detector.tokenize_text(
            "Hello world this is a test"
        )
        assert isinstance(words, list)
        assert len(words) > 0

    def test_check_with_pyspellchecker(self):
        """PySpellChecker should detect misspelled words."""
        from app.challenge3_spelling.spell_detector import SpellDetector
        detector = SpellDetector()
        errors = detector.check_with_pyspellchecker(
            ["recieve", "definately", "correct", "hello"]
        )
        assert isinstance(errors, dict)


class TestSmartFilter:
    """Test smart filtering."""

    def test_abbreviation_skipped(self):
        """Abbreviations should be skipped."""
        from app.challenge3_spelling.smart_filter import SmartFilter
        sf = SmartFilter()
        should_skip, reason = sf.should_skip("NASA")
        assert should_skip is True

    def test_all_caps_skipped(self):
        """ALL CAPS words should be skipped."""
        from app.challenge3_spelling.smart_filter import SmartFilter
        sf = SmartFilter()
        should_skip, reason = sf.should_skip("USA")
        assert should_skip is True

    def test_technical_term_skipped(self):
        """Technical terms should be skipped."""
        from app.challenge3_spelling.smart_filter import SmartFilter
        sf = SmartFilter()
        should_skip, reason = sf.should_skip("photosynthesis")
        assert should_skip is True

    def test_regular_word_not_skipped(self):
        """Regular misspelled words should not be skipped."""
        from app.challenge3_spelling.smart_filter import SmartFilter
        sf = SmartFilter()
        should_skip, reason = sf.should_skip("recieve")
        assert should_skip is False

    def test_short_word_skipped(self):
        """Very short words should be skipped."""
        from app.challenge3_spelling.smart_filter import SmartFilter
        sf = SmartFilter()
        should_skip, reason = sf.should_skip("a")
        assert should_skip is True


class TestReportGenerator:
    """Test report generation."""

    def test_error_rate_calculation(self):
        """Error rate should be calculated correctly."""
        from app.challenge3_spelling.report_generator import ReportGenerator
        rg = ReportGenerator()
        rate = rg.calculate_error_rate(100, 5)
        assert rate == 0.05

    def test_error_rate_zero_words(self):
        """Zero words should return 0 error rate."""
        from app.challenge3_spelling.report_generator import ReportGenerator
        rg = ReportGenerator()
        rate = rg.calculate_error_rate(0, 0)
        assert rate == 0.0

    def test_severity_levels(self):
        """Severity levels should be correct."""
        from app.challenge3_spelling.report_generator import ReportGenerator
        rg = ReportGenerator()
        assert rg.get_severity_level(0.005) == "excellent"
        assert rg.get_severity_level(0.02) == "good"
        assert rg.get_severity_level(0.05) == "fair"
        assert rg.get_severity_level(0.10) == "poor"
        assert rg.get_severity_level(0.20) == "critical"
