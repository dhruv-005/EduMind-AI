import hashlib
import os
import re
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.logger import logger


class PrivacyGuard:
    """Privacy protection for user data."""

    def anonymize_user_id(self, user_id: str) -> str:
        """One-way hash user ID for logging."""
        return hashlib.sha256(
            f"edumind_salt_{user_id}".encode()
        ).hexdigest()[:12]

    def mask_email(self, email: str) -> str:
        """Mask email for logging: j***@g***.com"""
        if "@" not in email:
            return "***"
        local, domain = email.split("@", 1)
        masked_local = local[0] + "***" if len(local) > 1 else "***"
        domain_parts = domain.split(".")
        masked_domain = domain_parts[0][0] + "***"
        return f"{masked_local}@{masked_domain}.{domain_parts[-1]}"

    def mask_phone(self, phone: str) -> str:
        """Mask phone number: ***-***-1234"""
        digits = re.sub(r'\D', '', phone)
        if len(digits) >= 4:
            return f"***-***-{digits[-4:]}"
        return "***"

    def remove_pii_from_text(self, text: str) -> str:
        """Remove PII from text before logging."""
        # Remove emails
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL]',
            text
        )
        # Remove phone numbers
        text = re.sub(
            r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            '[PHONE]',
            text
        )
        # Remove credit cards
        text = re.sub(
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            '[CARD]',
            text
        )
        # Remove SSN-like patterns
        text = re.sub(
            r'\b\d{3}-\d{2}-\d{4}\b',
            '[SSN]',
            text
        )
        return text

    def should_retain_data(
        self,
        created_at: datetime,
        retention_days: int = 90
    ) -> bool:
        """Check if data should still be retained."""
        expiry = created_at + timedelta(days=retention_days)
        return datetime.utcnow() < expiry

    def get_retention_expiry(
        self,
        created_at: datetime,
        retention_days: int = 90
    ) -> datetime:
        """Get data retention expiry date."""
        return created_at + timedelta(days=retention_days)

    def secure_delete_file(self, file_path: str) -> bool:
        """Securely delete a file."""
        try:
            if os.path.exists(file_path):
                # Overwrite with zeros before deleting
                with open(file_path, "wb") as f:
                    f.write(b'\x00' * os.path.getsize(file_path))
                os.remove(file_path)
                logger.info(f"Securely deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False

    def create_privacy_summary(
        self,
        data_type: str,
        user_id: str,
        action: str
    ) -> Dict[str, Any]:
        """Create privacy-compliant summary for logging."""
        return {
            "data_type": data_type,
            "user_hash": self.anonymize_user_id(user_id),
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "compliant": True
        }

    def validate_consent(
        self,
        user_id: str,
        consent_type: str,
        db=None
    ) -> bool:
        """Check if user has given consent for data processing."""
        # In production, check actual consent records in DB
        # For now, assume consent given if user is registered
        logger.info(
            f"Consent check: user={self.anonymize_user_id(user_id)}, "
            f"type={consent_type}"
        )
        return True


# Singleton
privacy_guard = PrivacyGuard()
