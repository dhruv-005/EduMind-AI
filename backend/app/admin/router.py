from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_admin, get_current_user
from app.admin.dashboard_service import dashboard_service
from app.admin.governance_dashboard import governance_dashboard
from app.admin.analytics_service import analytics_service
from app.admin.schemas import (
    AuditLogFilter,
    HumanReviewAction
)
from app.shared.response_models import success_response
from app.core.logger import logger

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin - Governance Dashboard"]
)


@router.get(
    "/dashboard",
    summary="Get admin dashboard statistics"
)
async def get_dashboard(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Get overall platform statistics for admin dashboard."""
    stats = dashboard_service.get_platform_stats(db=db)
    gov_stats = dashboard_service.get_governance_stats(db=db)
    model_health = dashboard_service.get_model_health()
    recent = dashboard_service.get_recent_activity(db=db)
    performance = dashboard_service.get_performance_metrics(
        db=db
    )

    return success_response(
        data={
            "platform_stats": stats,
            "governance_stats": gov_stats,
            "model_health": model_health,
            "recent_activity": recent,
            "performance": performance,
            "uptime_seconds": dashboard_service.get_uptime()
        },
        message="Dashboard data retrieved"
    )


@router.get(
    "/audit-logs",
    summary="Get audit logs"
)
async def get_audit_logs(
    challenge: Optional[str] = None,
    governance_status: Optional[str] = None,
    human_review_required: Optional[bool] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Get paginated audit logs with filters."""
    logs = dashboard_service.get_audit_logs(
        db=db,
        challenge=challenge,
        governance_status=governance_status,
        human_review_required=human_review_required,
        start_date=start_date,
        end_date=end_date,
        page=page,
        per_page=per_page
    )

    return success_response(
        data=logs,
        message="Audit logs retrieved"
    )


@router.get(
    "/governance",
    summary="Get governance report"
)
async def get_governance_report(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Get comprehensive governance report."""
    report = governance_dashboard.get_full_governance_report(
        db=db
    )
    safety = governance_dashboard.get_safety_summary(db=db)

    return success_response(
        data={
            "governance_report": report,
            "safety_summary": safety
        },
        message="Governance report retrieved"
    )


@router.get(
    "/reviews/pending",
    summary="Get pending human reviews"
)
async def get_pending_reviews(
    challenge: Optional[str] = None,
    priority: Optional[str] = None,
    admin: dict = Depends(require_admin)
):
    """Get all pending human review items."""
    reviews = governance_dashboard.get_pending_reviews(
        challenge=challenge,
        priority=priority
    )

    return success_response(
        data={
            "total": len(reviews),
            "items": reviews
        },
        message="Pending reviews retrieved"
    )


@router.post(
    "/reviews/approve",
    summary="Approve a review item"
)
async def approve_review(
    action: HumanReviewAction,
    admin: dict = Depends(require_admin)
):
    """Approve a human review item."""
    reviewer_id = action.reviewer_id or admin.get("user_id")
    result = governance_dashboard.approve_review(
        request_id=action.request_id,
        reviewer_id=reviewer_id,
        notes=action.notes or ""
    )

    return success_response(
        data=result,
        message="Review approved"
    )


@router.post(
    "/reviews/reject",
    summary="Reject a review item"
)
async def reject_review(
    action: HumanReviewAction,
    admin: dict = Depends(require_admin)
):
    """Reject a human review item."""
    reviewer_id = action.reviewer_id or admin.get("user_id")
    result = governance_dashboard.reject_review(
        request_id=action.request_id,
        reviewer_id=reviewer_id,
        notes=action.notes or ""
    )

    return success_response(
        data=result,
        message="Review rejected"
    )


@router.post(
    "/bias-check",
    summary="Run bias check on text"
)
async def run_bias_check(
    text: str,
    context: str = "",
    admin: dict = Depends(require_admin)
):
    """Run bias detection on provided text."""
    result = governance_dashboard.run_bias_check(
        text=text,
        context=context
    )

    return success_response(
        data=result,
        message="Bias check completed"
    )


@router.get(
    "/analytics/usage",
    summary="Get usage analytics"
)
async def get_usage_analytics(
    days: int = Query(default=7, ge=1, le=90),
    challenge: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Get usage trends and analytics."""
    trend = analytics_service.get_usage_trend(
        db=db, days=days, challenge=challenge
    )
    score_dist = analytics_service.get_score_distribution(db)
    subject_breakdown = analytics_service.get_subject_breakdown(db)

    return success_response(
        data={
            "usage_trend": trend,
            "score_distribution": score_dist,
            "subject_breakdown": subject_breakdown
        },
        message="Analytics retrieved"
    )


@router.get(
    "/analytics/voice",
    summary="Get voice tutor analytics"
)
async def get_voice_analytics(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Get voice tutor session analytics."""
    stats = analytics_service.get_voice_session_stats(db)
    return success_response(
        data=stats,
        message="Voice analytics retrieved"
    )


@router.get(
    "/analytics/sales",
    summary="Get sales analytics"
)
async def get_sales_analytics(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Get sales performance analytics."""
    stats = analytics_service.get_sales_analytics(db)
    return success_response(
        data=stats,
        message="Sales analytics retrieved"
    )


@router.get(
    "/analytics/spelling",
    summary="Get spelling error analytics"
)
async def get_spelling_analytics(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Get top spelling errors and trends."""
    top_errors = analytics_service.get_top_errors(db)
    return success_response(
        data={"top_errors": top_errors},
        message="Spelling analytics retrieved"
    )


@router.post(
    "/providers/{provider}/reset",
    summary="Reset LLM provider"
)
async def reset_provider(
    provider: str,
    admin: dict = Depends(require_admin)
):
    """Reset a LLM provider's failure count."""
    result = governance_dashboard.reset_provider(provider)
    return success_response(
        data=result,
        message=f"Provider {provider} reset"
    )


@router.get(
    "/prompt-versions",
    summary="Get prompt versions"
)
async def get_prompt_versions(
    admin: dict = Depends(require_admin)
):
    """Get all registered prompt versions."""
    versions = dashboard_service.get_prompt_versions()
    return success_response(
        data=versions,
        message="Prompt versions retrieved"
    )


@router.get(
    "/health",
    summary="System health check"
)
async def system_health(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Comprehensive system health check."""
    import time
    from app.core.database import check_db_connection

    health = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "uptime_seconds": dashboard_service.get_uptime(),
        "database": "unknown",
        "challenges": {
            "challenge1_evaluator": "active",
            "challenge2_generator": "active",
            "challenge3_spelling": "active",
            "challenge4_voice_tutor": "active",
            "challenge5_sales": "active"
        },
        "governance": {
            "pillars_active": 7,
            "content_filter": "active",
            "audit_logger": "active",
            "human_oversight": "active"
        }
    }

    # Check database
    try:
        db.execute("SELECT 1")
        health["database"] = "connected"
    except Exception:
        health["database"] = "error"
        health["status"] = "degraded"

    return success_response(
        data=health,
        message="System health check completed"
    )
