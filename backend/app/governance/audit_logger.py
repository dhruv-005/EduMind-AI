import hashlib
import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.core.logger import logger


def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for privacy-preserving logging."""
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def generate_request_id() -> str:
    """Generate unique request ID."""
    return str(uuid.uuid4())


class AuditLogger:
    """Comprehensive audit logging for all AI decisions."""

    def __init__(self):
        self.logs_buffer = []

    def log_ai_decision(
        self,
        db: Optional[Session],
        request_id: str,
        challenge: str,
        user_id: Optional[str],
        session_id: Optional[str],
        input_summary: str,
        model_used: str,
        model_version: str,
        prompt_version: str,
        output_summary: str,
        confidence_score: float,
        processing_time_ms: float,
        governance_status: str,
        governance_reason: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Log an AI decision to database and logger."""

        log_entry = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "challenge": challenge,
            "user_id": hash_sensitive_data(user_id) if user_id else "anonymous",
            "session_id": session_id or "none",
            "input_hash": hash_sensitive_data(input_summary),
            "model_used": model_used,
            "model_version": model_version,
            "prompt_version": prompt_version,
            "output_summary": output_summary[:200],
            "confidence_score": round(confidence_score, 3),
            "processing_time_ms": round(processing_time_ms, 2),
            "governance_status": governance_status,
            "governance_reason": governance_reason,
            "metadata": metadata or {}
        }

        # Log to file
        logger.info(
            f"AUDIT | {challenge} | {request_id} | "
            f"model={model_used} | confidence={confidence_score:.2f} | "
            f"status={governance_status} | time={processing_time_ms:.0f}ms"
        )

        # Store in database if session available
        if db:
            try:
                self._save_to_db(db, log_entry)
            except Exception as e:
                logger.error(f"Failed to save audit log to DB: {e}")
                self.logs_buffer.append(log_entry)

        return log_entry

    def _save_to_db(self, db: Session, log_entry: Dict[str, Any]):
        """Save audit log entry to database."""
        try:
            from app.models.audit_log import AuditLog
            audit_log = AuditLog(
                request_id=log_entry["request_id"],
                timestamp=datetime.utcnow(),
                challenge=log_entry["challenge"],
                user_id=log_entry["user_id"],
                session_id=log_entry["session_id"],
                input_hash=log_entry["input_hash"],
                model_used=log_entry["model_used"],
                model_version=log_entry["model_version"],
                prompt_version=log_entry["prompt_version"],
                output_summary=log_entry["output_summary"],
                confidence_score=log_entry["confidence_score"],
                processing_time_ms=log_entry["processing_time_ms"],
                governance_status=log_entry["governance_status"],
                governance_reason=log_entry["governance_reason"],
                extra_metadata=json.dumps(log_entry["metadata"])
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"DB audit log save failed: {e}")
            raise

    def log_governance_event(
        self,
        event_type: str,
        challenge: str,
        details: str,
        severity: str = "info"
    ):
        """Log a governance event."""
        log_msg = (
            f"GOVERNANCE | {event_type} | "
            f"challenge={challenge} | "
            f"severity={severity} | "
            f"details={details}"
        )
        if severity == "critical":
            logger.critical(log_msg)
        elif severity == "warning":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

    def log_human_review_trigger(
        self,
        challenge: str,
        request_id: str,
        reason: str,
        confidence: float
    ):
        """Log when human review is triggered."""
        logger.warning(
            f"HUMAN_REVIEW_TRIGGERED | challenge={challenge} | "
            f"request_id={request_id} | reason={reason} | "
            f"confidence={confidence:.2f}"
        )

    def get_buffered_logs(self) -> list:
        """Get logs that failed to save to DB."""
        return self.logs_buffer.copy()

    def flush_buffer(self, db: Session):
        """Retry saving buffered logs to DB."""
        failed = []
        for log_entry in self.logs_buffer:
            try:
                self._save_to_db(db, log_entry)
            except Exception:
                failed.append(log_entry)
        self.logs_buffer = failed
        logger.info(f"Flushed audit buffer: {len(self.logs_buffer)} remaining")


# Singleton
audit_logger = AuditLogger()
