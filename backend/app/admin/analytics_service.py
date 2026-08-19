from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.logger import logger


class AnalyticsService:
    """
    Analytics service for platform insights.
    Provides trends, usage patterns, and performance data.
    """

    def get_usage_trend(
        self,
        db: Session,
        days: int = 7,
        challenge: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get daily usage trend for last N days."""
        try:
            from app.models.audit_log import AuditLog
            from sqlalchemy import func, cast, Date

            since = datetime.utcnow() - timedelta(days=days)

            query = db.query(
                func.date(AuditLog.timestamp).label("date"),
                func.count(AuditLog.id).label("count"),
                AuditLog.challenge
            ).filter(
                AuditLog.timestamp >= since
            )

            if challenge:
                query = query.filter(
                    AuditLog.challenge == challenge
                )

            results = query.group_by(
                func.date(AuditLog.timestamp),
                AuditLog.challenge
            ).order_by(
                func.date(AuditLog.timestamp)
            ).all()

            trend = []
            for date, count, ch in results:
                trend.append({
                    "date": str(date),
                    "count": count,
                    "challenge": ch
                })

            return trend

        except Exception as e:
            logger.error(f"Usage trend query failed: {e}")
            return []

    def get_score_distribution(
        self,
        db: Session
    ) -> Dict[str, Any]:
        """Get evaluation score distribution."""
        try:
            from app.models.evaluation import Evaluation
            from sqlalchemy import func

            # Score ranges
            ranges = {
                "excellent (9-10)": 0,
                "good (7-8)": 0,
                "average (5-6)": 0,
                "below_average (3-4)": 0,
                "poor (0-2)": 0
            }

            evals = db.query(
                Evaluation.score_out_of_10
            ).all()

            for (score,) in evals:
                if score is None:
                    continue
                if score >= 9:
                    ranges["excellent (9-10)"] += 1
                elif score >= 7:
                    ranges["good (7-8)"] += 1
                elif score >= 5:
                    ranges["average (5-6)"] += 1
                elif score >= 3:
                    ranges["below_average (3-4)"] += 1
                else:
                    ranges["poor (0-2)"] += 1

            total = sum(ranges.values())

            return {
                "distribution": ranges,
                "total_evaluations": total,
                "percentages": {
                    k: round(v / total * 100, 1) if total > 0 else 0
                    for k, v in ranges.items()
                }
            }

        except Exception as e:
            logger.error(
                f"Score distribution query failed: {e}"
            )
            return {"distribution": {}, "total_evaluations": 0}

    def get_subject_breakdown(
        self,
        db: Session
    ) -> Dict[str, Any]:
        """Get evaluation breakdown by subject."""
        try:
            from app.models.evaluation import Evaluation
            from sqlalchemy import func

            results = db.query(
                Evaluation.subject,
                func.count(Evaluation.id).label("count"),
                func.avg(
                    Evaluation.score_out_of_10
                ).label("avg_score")
            ).group_by(
                Evaluation.subject
            ).all()

            breakdown = {}
            for subject, count, avg_score in results:
                breakdown[subject or "general"] = {
                    "count": count,
                    "avg_score": round(avg_score or 0, 2)
                }

            return breakdown

        except Exception as e:
            logger.error(
                f"Subject breakdown query failed: {e}"
            )
            return {}

    def get_top_errors(
        self,
        db: Session,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get most common spelling errors."""
        try:
            from app.models.spelling_report import SpellingReport

            reports = db.query(
                SpellingReport.errors
            ).filter(
                SpellingReport.errors.isnot(None)
            ).limit(100).all()

            error_counts = {}
            for (errors,) in reports:
                if not errors:
                    continue
                for error in errors:
                    word = error.get("word", "").lower()
                    correction = error.get("correction", "")
                    if word:
                        if word not in error_counts:
                            error_counts[word] = {
                                "word": word,
                                "correction": correction,
                                "count": 0
                            }
                        error_counts[word]["count"] += 1

            sorted_errors = sorted(
                error_counts.values(),
                key=lambda x: x["count"],
                reverse=True
            )

            return sorted_errors[:limit]

        except Exception as e:
            logger.error(f"Top errors query failed: {e}")
            return []

    def get_voice_session_stats(
        self,
        db: Session
    ) -> Dict[str, Any]:
        """Get voice tutor session statistics."""
        try:
            from app.models.session import TutorSession
            from sqlalchemy import func

            total = db.query(TutorSession).count()
            completed = db.query(TutorSession).filter(
                TutorSession.status == "completed"
            ).count()
            escalated = db.query(TutorSession).filter(
                TutorSession.escalated == True
            ).count()

            avg_interactions = db.query(
                func.avg(TutorSession.total_interactions)
            ).scalar() or 0

            subjects = db.query(
                TutorSession.subject,
                func.count(TutorSession.id)
            ).group_by(TutorSession.subject).all()

            return {
                "total_sessions": total,
                "completed_sessions": completed,
                "escalated_sessions": escalated,
                "completion_rate": round(
                    completed / total * 100, 1
                ) if total > 0 else 0,
                "avg_interactions": round(
                    float(avg_interactions), 1
                ),
                "by_subject": {
                    s or "general": c
                    for s, c in subjects
                }
            }

        except Exception as e:
            logger.error(
                f"Voice session stats failed: {e}"
            )
            return {}

    def get_sales_analytics(
        self,
        db: Session
    ) -> Dict[str, Any]:
        """Get sales performance analytics."""
        try:
            from app.models.product import Lead
            from sqlalchemy import func

            total_leads = db.query(Lead).count()

            by_category = db.query(
                Lead.lead_category,
                func.count(Lead.id)
            ).group_by(Lead.lead_category).all()

            avg_score = db.query(
                func.avg(Lead.total_score)
            ).scalar() or 0

            escalated = db.query(Lead).filter(
                Lead.escalated_to_human == True
            ).count()

            return {
                "total_leads": total_leads,
                "avg_lead_score": round(float(avg_score), 1),
                "escalated_leads": escalated,
                "by_category": {
                    cat: count
                    for cat, count in by_category
                },
                "conversion_rate": round(
                    escalated / total_leads * 100, 1
                ) if total_leads > 0 else 0
            }

        except Exception as e:
            logger.error(
                f"Sales analytics failed: {e}"
            )
            return {}


# Singleton
analytics_service = AnalyticsService()
