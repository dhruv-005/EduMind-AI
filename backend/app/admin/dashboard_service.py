import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.logger import logger
from app.governance.human_oversight import human_oversight
from app.governance.model_fallback import model_fallback
from app.governance.prompt_versioning import prompt_versioning


class DashboardService:
    """
    Service for admin dashboard statistics.
    Aggregates data from all 5 challenges.
    """

    def __init__(self):
        self._start_time = time.time()

    def get_platform_stats(
        self,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Get overall platform statistics."""
        stats = {
            "total_evaluations": 0,
            "total_questions_generated": 0,
            "total_spell_checks": 0,
            "total_voice_sessions": 0,
            "total_sales_conversations": 0,
            "total_users": 0,
            "active_sessions": 0,
            "avg_evaluation_score": 0.0,
            "total_api_calls_today": 0,
            "governance_flags_today": 0
        }

        if not db:
            return stats

        try:
            from app.models.evaluation import Evaluation
            from app.models.question import GeneratedQuestion
            from app.models.spelling_report import SpellingReport
            from app.models.session import TutorSession
            from app.models.user import User
            from app.models.audit_log import AuditLog

            # Count evaluations
            stats["total_evaluations"] = db.query(
                Evaluation
            ).count()

            # Average score
            evals = db.query(
                Evaluation.score_out_of_10
            ).all()
            if evals:
                scores = [
                    e[0] for e in evals
                    if e[0] is not None
                ]
                stats["avg_evaluation_score"] = round(
                    sum(scores) / len(scores), 2
                ) if scores else 0.0

            # Count generated questions
            stats["total_questions_generated"] = db.query(
                GeneratedQuestion
            ).count()

            # Count spell checks
            stats["total_spell_checks"] = db.query(
                SpellingReport
            ).count()

            # Count voice sessions
            stats["total_voice_sessions"] = db.query(
                TutorSession
            ).count()

            # Active sessions
            stats["active_sessions"] = db.query(
                TutorSession
            ).filter(
                TutorSession.status == "active"
            ).count()

            # Total users
            stats["total_users"] = db.query(User).count()

            # Today's API calls
            today = datetime.utcnow().date()
            today_start = datetime(
                today.year, today.month, today.day
            )
            stats["total_api_calls_today"] = db.query(
                AuditLog
            ).filter(
                AuditLog.timestamp >= today_start
            ).count()

            # Today's governance flags
            stats["governance_flags_today"] = db.query(
                AuditLog
            ).filter(
                AuditLog.timestamp >= today_start,
                AuditLog.governance_status == "flagged"
            ).count()

        except Exception as e:
            logger.error(f"Stats collection failed: {e}")

        return stats

    def get_governance_stats(
        self,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Get governance and safety statistics."""
        stats = {
            "total_requests": 0,
            "passed": 0,
            "flagged": 0,
            "blocked": 0,
            "human_reviews_pending": 0,
            "human_reviews_completed": 0,
            "bias_detections": 0,
            "rate_limit_hits": 0,
            "by_challenge": {}
        }

        if db:
            try:
                from app.models.audit_log import AuditLog
                from sqlalchemy import func

                # Total requests
                stats["total_requests"] = db.query(
                    AuditLog
                ).count()

                # By status
                status_counts = db.query(
                    AuditLog.governance_status,
                    func.count(AuditLog.id)
                ).group_by(
                    AuditLog.governance_status
                ).all()

                for status, count in status_counts:
                    if status in stats:
                        stats[status] = count

                # Human reviews
                stats["human_reviews_pending"] = db.query(
                    AuditLog
                ).filter(
                    AuditLog.human_review_triggered == True,
                    AuditLog.human_review_completed == False
                ).count()

                stats["human_reviews_completed"] = db.query(
                    AuditLog
                ).filter(
                    AuditLog.human_review_completed == True
                ).count()

                # By challenge
                challenge_counts = db.query(
                    AuditLog.challenge,
                    func.count(AuditLog.id)
                ).group_by(AuditLog.challenge).all()

                for challenge, count in challenge_counts:
                    stats["by_challenge"][challenge] = count

            except Exception as e:
                logger.error(
                    f"Governance stats failed: {e}"
                )

        # Add human oversight queue stats
        queue_stats = human_oversight.get_queue_stats()
        stats["human_reviews_pending"] = max(
            stats["human_reviews_pending"],
            queue_stats.get("pending", 0)
        )

        return stats

    def get_audit_logs(
        self,
        db: Session,
        challenge: Optional[str] = None,
        governance_status: Optional[str] = None,
        human_review_required: Optional[bool] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get paginated audit logs with filters."""
        try:
            from app.models.audit_log import AuditLog

            query = db.query(AuditLog)

            if challenge:
                query = query.filter(
                    AuditLog.challenge == challenge
                )

            if governance_status:
                query = query.filter(
                    AuditLog.governance_status == governance_status
                )

            if human_review_required is not None:
                query = query.filter(
                    AuditLog.human_review_triggered == human_review_required
                )

            if start_date:
                try:
                    start = datetime.fromisoformat(start_date)
                    query = query.filter(
                        AuditLog.timestamp >= start
                    )
                except ValueError:
                    pass

            if end_date:
                try:
                    end = datetime.fromisoformat(end_date)
                    query = query.filter(
                        AuditLog.timestamp <= end
                    )
                except ValueError:
                    pass

            total = query.count()
            logs = (
                query
                .order_by(AuditLog.timestamp.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
                .all()
            )

            return {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (
                    total + per_page - 1
                ) // per_page,
                "items": [log.to_dict() for log in logs]
            }

        except Exception as e:
            logger.error(f"Audit log query failed: {e}")
            return {
                "total": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0,
                "items": []
            }

    def get_model_health(self) -> Dict[str, Any]:
        """Get LLM provider health statistics."""
        provider_stats = model_fallback.get_provider_stats()

        return {
            "providers": provider_stats,
            "current_provider": model_fallback.current_provider,
            "recommended": (
                model_fallback.get_recommended_provider()
            )
        }

    def get_prompt_versions(self) -> Dict[str, Any]:
        """Get all registered prompt versions."""
        return prompt_versioning.list_all_versions()

    def get_uptime(self) -> float:
        """Get system uptime in seconds."""
        return time.time() - self._start_time

    def get_recent_activity(
        self,
        db: Session,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent AI activity across all challenges."""
        try:
            from app.models.audit_log import AuditLog

            recent = db.query(AuditLog).order_by(
                AuditLog.timestamp.desc()
            ).limit(limit).all()

            return [log.to_dict() for log in recent]

        except Exception as e:
            logger.error(f"Recent activity query failed: {e}")
            return []

    def get_performance_metrics(
        self,
        db: Session,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get performance metrics for last N hours."""
        try:
            from app.models.audit_log import AuditLog
            from sqlalchemy import func

            since = datetime.utcnow() - timedelta(hours=hours)

            # Average processing time by challenge
            perf = db.query(
                AuditLog.challenge,
                func.avg(AuditLog.processing_time_ms),
                func.count(AuditLog.id)
            ).filter(
                AuditLog.timestamp >= since
            ).group_by(AuditLog.challenge).all()

            metrics = {}
            for challenge, avg_time, count in perf:
                metrics[challenge] = {
                    "avg_processing_time_ms": round(
                        avg_time or 0, 1
                    ),
                    "total_requests": count
                }

            return {
                "period_hours": hours,
                "by_challenge": metrics
            }

        except Exception as e:
            logger.error(f"Performance metrics failed: {e}")
            return {"period_hours": hours, "by_challenge": {}}


# Singleton
dashboard_service = DashboardService()
