from sqlalchemy import (
    Column, String, Boolean, DateTime,
    Integer, Text, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    SALES_REP = "sales_rep"


class User(Base):
    """User model for authentication and profile."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(
        SQLEnum(UserRole),
        default=UserRole.STUDENT,
        nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Profile
    grade_level = Column(String(50), nullable=True)
    subject_preference = Column(String(100), nullable=True)
    institution = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    last_login = Column(DateTime, nullable=True)

    # Consent
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_date = Column(DateTime, nullable=True)

    # Relationships
    evaluations = relationship(
        "Evaluation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    sessions = relationship(
        "TutorSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<User id={self.id} "
            f"email={self.email} "
            f"role={self.role}>"
        )

    def to_dict(self):
        """Convert to dictionary (safe for API response)."""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value if self.role else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "grade_level": self.grade_level,
            "subject_preference": self.subject_preference,
            "institution": self.institution,
            "created_at": self.created_at.isoformat()
            if self.created_at else None,
            "last_login": self.last_login.isoformat()
            if self.last_login else None
        }
