from typing import Dict, Any, Optional, List
from datetime import datetime
from app.core.logger import logger
from app.core.config import settings


# Thresholds for human review triggers
REVIEW_THRESHOLDS = {
    "challenge1": {
        "confidence_threshold": 0.60,
        "reason": "Low confidence evaluation needs teacher review"
    },
    "challenge2": {
        "similarity_threshold": 0.90,
        "reason": "Generated question too similar to source"
    },
    "challenge3": {
        "ocr_confidence_threshold": 0.70,
        "reason": "Low OCR confidence needs human verification"
    },
    "challenge4": {
        "distress_keywords": [
            "help me", "i'm struggling", "i give up",
            "i don't understand anything", "i want to quit"
        ],
        "reason": "Student may need counselor support"
    },
    "challenge5": {
        "hot_lead_threshold": 85,
        "reason": "Hot lead - immediate human sales rep needed"
    }
}


class HumanOversightManager:
    """Manage human-in-the-loop triggers and review queue."""

    def __init__(self):
        self.review_queue: List[Dict[str, Any]] = []

    def should_trigger_review(
        self,
        challenge: str,
        confidence_score: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple:
        """
        Check if human review should be triggered.
        Returns: (should_review, reason)
        """
        metadata = metadata or {}

        if challenge == "challenge1":
            threshold = REVIEW_THRESHOLDS["challenge1"]["confidence_threshold"]
            if confidence_score < threshold:
                return True, REVIEW_THRESHOLDS["challenge1"]["reason"]

        elif challenge == "challenge2":
            similarity = metadata.get("max_similarity", 0.0)
            threshold = REVIEW_THRESHOLDS["challenge2"]["similarity_threshold"]
            if similarity > threshold:
                return True, REVIEW_THRESHOLDS["challenge2"]["reason"]

        elif challenge == "challenge3":
            ocr_conf = metadata.get("ocr_confidence", 1.0)
            threshold = REVIEW_THRESHOLDS["challenge3"]["ocr_confidence_threshold"]
            if ocr_conf < threshold:
                return True, REVIEW_THRESHOLDS["challenge3"]["reason"]

        elif challenge == "challenge4":
            text = metadata.get("student_text", "").lower()
            distress_words = REVIEW_THRESHOLDS["challenge4"]["distress_keywords"]
            for keyword in distress_words:
                if keyword in text:
                    return True, REVIEW_THRESHOLDS["challenge4"]["reason"]

        elif challenge == "challenge5":
            lead_score = metadata.get("lead_score", 0)
            threshold = REVIEW_THRESHOLDS["challenge5"]["hot_lead_threshold"]
            if lead_score >= threshold:
                return True, REVIEW_THRESHOLDS["challenge5"]["reason"]

        return False, "No review needed"

    def add_to_review_queue(
        self,
        challenge: str,
        request_id: str,
        reason: str,
        content: Dict[str, Any],
        priority: str = "normal",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add item to human review queue."""
        queue_item = {
            "id": request_id,
            "challenge": challenge,
            "reason": reason,
            "content": content,
            "priority": priority,
            "user_id": user_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "reviewed_at": None,
            "reviewer_id": None,
            "reviewer_decision": None,
            "reviewer_notes": ""
        }

        self.review_queue.append(queue_item)

        logger.warning(
            f"HUMAN_REVIEW_QUEUED | challenge={challenge} | "
            f"id={request_id} | reason={reason} | priority={priority}"
        )

        return queue_item

    def get_pending_reviews(
        self,
        challenge: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all pending review items."""
        results = [
            item for item in self.review_queue
            if item["status"] == "pending"
        ]

        if challenge:
            results = [r for r in results if r["challenge"] == challenge]

        if priority:
            results = [r for r in results if r["priority"] == priority]

        return sorted(results, key=lambda x: x["created_at"], reverse=True)

    def approve_review(
        self,
        request_id: str,
        reviewer_id: str,
        notes: str = ""
    ) -> bool:
        """Mark review item as approved."""
        for item in self.review_queue:
            if item["id"] == request_id:
                item["status"] = "approved"
                item["reviewed_at"] = datetime.utcnow().isoformat()
                item["reviewer_id"] = reviewer_id
                item["reviewer_decision"] = "approved"
                item["reviewer_notes"] = notes
                logger.info(f"Review approved: {request_id} by {reviewer_id}")
                return True
        return False

    def reject_review(
        self,
        request_id: str,
        reviewer_id: str,
        notes: str = ""
    ) -> bool:
        """Mark review item as rejected."""
        for item in self.review_queue:
            if item["id"] == request_id:
                item["status"] = "rejected"
                item["reviewed_at"] = datetime.utcnow().isoformat()
                item["reviewer_id"] = reviewer_id
                item["reviewer_decision"] = "rejected"
                item["reviewer_notes"] = notes
                logger.warning(f"Review rejected: {request_id} by {reviewer_id}")
                return True
        return False

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get review queue statistics."""
        total = len(self.review_queue)
        pending = sum(1 for i in self.review_queue if i["status"] == "pending")
        approved = sum(1 for i in self.review_queue if i["status"] == "approved")
        rejected = sum(1 for i in self.review_queue if i["status"] == "rejected")

        by_challenge = {}
        for item in self.review_queue:
            ch = item["challenge"]
            if ch not in by_challenge:
                by_challenge[ch] = {"pending": 0, "approved": 0, "rejected": 0}
            by_challenge[ch][item["status"]] = (
                by_challenge[ch].get(item["status"], 0) + 1
            )

        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "by_challenge": by_challenge
        }


# Singleton
human_oversight = HumanOversightManager()
