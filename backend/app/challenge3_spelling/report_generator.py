from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.logger import logger


class ReportGenerator:
    """
    Generate spelling check reports.
    Summarizes errors, statistics, and recommendations.
    """

    def calculate_error_rate(
        self,
        total_words: int,
        total_errors: int
    ) -> float:
        """Calculate error rate as percentage."""
        if total_words == 0:
            return 0.0
        return round(total_errors / total_words, 4)

    def get_severity_level(
        self,
        error_rate: float
    ) -> str:
        """
        Get severity level based on error rate.
        """
        if error_rate < 0.01:
            return "excellent"   # < 1% errors
        elif error_rate < 0.03:
            return "good"        # 1-3% errors
        elif error_rate < 0.07:
            return "fair"        # 3-7% errors
        elif error_rate < 0.15:
            return "poor"        # 7-15% errors
        else:
            return "critical"    # > 15% errors

    def get_severity_color(self, severity: str) -> str:
        """Get color code for severity level."""
        colors = {
            "excellent": "#10B981",  # Green
            "good": "#3B82F6",       # Blue
            "fair": "#F59E0B",       # Amber
            "poor": "#EF4444",       # Red
            "critical": "#7C3AED"    # Purple
        }
        return colors.get(severity, "#6B7280")

    def group_errors_by_page(
        self,
        errors: List[Dict[str, Any]]
    ) -> Dict[int, List[Dict]]:
        """Group errors by page number."""
        by_page = {}
        for error in errors:
            page = error.get("page", 1)
            if page not in by_page:
                by_page[page] = []
            by_page[page].append(error)
        return by_page

    def get_most_common_errors(
        self,
        errors: List[Dict[str, Any]],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """Get most commonly occurring errors."""
        from collections import Counter
        word_counts = Counter(
            e.get("word", "").lower() for e in errors
        )
        most_common = word_counts.most_common(top_n)

        result = []
        for word, count in most_common:
            # Find correction for this word
            correction = next(
                (
                    e.get("correction", word)
                    for e in errors
                    if e.get("word", "").lower() == word
                ),
                word
            )
            result.append({
                "word": word,
                "count": count,
                "correction": correction
            })

        return result

    def generate_recommendations(
        self,
        error_rate: float,
        most_common: List[Dict],
        severity: str
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if severity in ["poor", "critical"]:
            recommendations.append(
                "High error rate detected. "
                "Consider using a word processor with "
                "built-in spell check before submitting."
            )

        if most_common:
            top_words = [e["word"] for e in most_common[:3]]
            recommendations.append(
                f"Focus on frequently misspelled words: "
                f"{', '.join(top_words)}"
            )

        if error_rate > 0.05:
            recommendations.append(
                "Read through the document carefully "
                "before finalizing."
            )

        recommendations.append(
            "Review all highlighted words and apply "
            "suggested corrections where appropriate."
        )

        return recommendations

    def build_report(
        self,
        errors: List[Dict[str, Any]],
        skipped_words: List[str],
        total_words: int,
        original_filename: str,
        file_type: str,
        page_count: int,
        ocr_used: bool,
        ocr_confidence: Optional[float],
        processing_time_ms: float,
        report_id: str,
        request_id: str,
        annotated_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build complete spell check report.
        Returns structured report dict.
        """
        total_errors = len(errors)
        error_rate = self.calculate_error_rate(
            total_words, total_errors
        )
        severity = self.get_severity_level(error_rate)
        most_common = self.get_most_common_errors(errors)
        recommendations = self.generate_recommendations(
            error_rate, most_common, severity
        )
        errors_by_page = self.group_errors_by_page(errors)

        report = {
            "report_id": report_id,
            "request_id": request_id,
            "original_filename": original_filename,
            "file_type": file_type,
            "generated_at": datetime.utcnow().isoformat(),

            "summary": {
                "total_words": total_words,
                "total_errors": total_errors,
                "error_rate": error_rate,
                "error_percentage": round(error_rate * 100, 2),
                "skipped_count": len(skipped_words),
                "pages_checked": page_count,
                "ocr_used": ocr_used,
                "ocr_confidence": ocr_confidence,
                "severity": severity,
                "severity_color": self.get_severity_color(
                    severity
                )
            },

            "errors": errors,
            "errors_by_page": {
                str(page): errs
                for page, errs in errors_by_page.items()
            },
            "skipped_words": skipped_words[:50],
            "most_common_errors": most_common,
            "recommendations": recommendations,

            "annotated_file_available": bool(
                annotated_file_path
            ),
            "annotated_file_path": annotated_file_path,

            "metadata": {
                "processing_time_ms": processing_time_ms,
                "layers_used": [
                    "pyspellchecker",
                    "languagetool",
                    "llm_verification"
                ],
                "governance_status": "passed",
                "human_verification_required": (
                    ocr_confidence is not None and
                    ocr_confidence < 0.70
                )
            }
        }

        logger.info(
            f"Report built: "
            f"errors={total_errors} "
            f"severity={severity} "
            f"rate={error_rate:.3f}"
        )

        return report


# Singleton
report_generator = ReportGenerator()
