from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.logger import logger
from app.governance.human_oversight import human_oversight
from app.governance.bias_detector import bias_detector
from app.governance.model_fallback import model_fallback
from app.governance.content_filter import content_filter


class GovernanceDashboard:
    """
    Governance dashboard service.
    Provides comprehensive governance monitoring and controls.
    """

    def get_full_governance_report(
        self,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Get comprehensive governance report."""
        queue_stats = human_oversight.get_queue_stats()
        provider_stats = model_fallback.get_provider_stats()

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "human_oversight": {
                "queue_stats": queue_stats,
                "pending_reviews": (
                    human_oversight.get_pending_reviews()[:5]
                )
            },
            "model_health": {
                "providers": provider_stats,
                "current": model_fallback.current_provider
            },
            "content_safety": {
                "filter_active": True,
                "blocked_patterns_count": len(
                    content_filter.blocked_patterns
                ),
                "flagged_patterns_count": len(
                    content_filter.flagged_patterns
                )
            },
            "pillars": {
                "content_safety": "active",
                "audit_trail": "active",
                "human_oversight": "active",
                "bias_detection": "active",
                "rate_limiting": "active",
                "data_privacy": "active",
                "model_versioning": "active"
            }
        }

        return report

    def get_pending_reviews(
        self,
        challenge: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get pending human review items."""
        return human_oversight.get_pending_reviews(
            challenge=challenge,
            priority=priority
        )

    def approve_review(
        self,
        request_id: str,
        reviewer_id: str,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Approve a human review item."""
        success = human_oversight.approve_review(
            request_id=request_id,
            reviewer_id=reviewer_id,
            notes=notes
        )

        if success:
            logger.info(
                f"Review approved: {request_id} "
                f"by {reviewer_id}"
            )
            # Update DB if available
            return {
                "success": True,
                "request_id": request_id,
                "action": "approved",
                "reviewed_by": reviewer_id,
                "notes": notes,
                "timestamp": datetime.utcnow().isoformat()
            }

        return {
            "success": False,
            "message": "Review item not found"
        }

    def reject_review(
        self,
        request_id: str,
        reviewer_id: str,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Reject a human review item."""
        success = human_oversight.reject_review(
            request_id=request_id,
            reviewer_id=reviewer_id,
            notes=notes
        )

        if success:
            logger.warning(
                f"Review rejected: {request_id} "
                f"by {reviewer_id}"
            )
            return {
                "success": True,
                "request_id": request_id,
                "action": "rejected",
                "reviewed_by": reviewer_id,
                "notes": notes,
                "timestamp": datetime.utcnow().isoformat()
            }

        return {
            "success": False,
            "message": "Review item not found"
        }

    def run_bias_check(
        self,
        text: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """Run bias detection on provided text."""
        result = bias_detector.full_bias_check(
            text=text,
            context=context
        )
        return result

    def get_safety_summary(
        self,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Get content safety summary."""
        summary = {
            "filter_status": "active",
            "blocked_patterns": len(
                content_filter.blocked_patterns
            ),
            "flagged_patterns": len(
                content_filter.flagged_patterns
            ),
            "non_education_patterns": len(
                content_filter.non_education_patterns
            )
        }

        if db:
            try:
                from app.models.audit_log import AuditLog
                from sqlalchemy import func
                from datetime import timedelta

                since = datetime.utcnow() - timedelta(days=7)

                blocked = db.query(AuditLog).filter(
                    AuditLog.governance_status == "blocked",
                    AuditLog.timestamp >= since
                ).count()

                flagged = db.query(AuditLog).filter(
                    AuditLog.governance_status == "flagged",
                    AuditLog.timestamp >= since
                ).count()

                summary["last_7_days"] = {
                    "blocked": blocked,
                    "flagged": flagged
                }

            except Exception as e:
                logger.warning(
                    f"Safety summary DB query failed: {e}"
                )

        return summary

    def reset_provider(
        self,
        provider: str
    ) -> Dict[str, Any]:
        """Reset a provider's failure count."""
        model_fallback.reset_provider(provider)
        return {
            "success": True,
            "provider": provider,
            "message": f"Provider {provider} reset successfully"
        }


# Singleton
governance_dashboard = GovernanceDashboard()
