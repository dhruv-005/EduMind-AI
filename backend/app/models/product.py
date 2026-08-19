from sqlalchemy import (
    Column, String, Integer, Float,
    DateTime, Text, Boolean, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Product(Base):
    """
    Stores product catalogue for Challenge 5 (Sales AI).
    """

    __tablename__ = "products"

    id = Column(String(36), primary_key=True, index=True)
    catalogue_id = Column(String(36), index=True, nullable=True)

    # Basic info
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)
    subcategory = Column(String(100), nullable=True)
    sku = Column(String(100), nullable=True, unique=True)

    # Description
    short_description = Column(String(500), nullable=True)
    full_description = Column(Text, nullable=True)

    # Pricing
    price = Column(Float, nullable=False, default=0.0)
    currency = Column(String(10), default="USD", nullable=False)
    discount_percentage = Column(Float, default=0.0, nullable=False)
    final_price = Column(Float, nullable=True)

    # Inventory
    in_stock = Column(Boolean, default=True, nullable=False)
    stock_quantity = Column(Integer, nullable=True)

    # Features (for matching)
    features = Column(JSON, nullable=True)
    # Format: ["feature1", "feature2", ...]

    specifications = Column(JSON, nullable=True)
    # Format: {"key": "value", ...}

    # Target audience
    target_audience = Column(String(200), nullable=True)
    use_cases = Column(JSON, nullable=True)

    # Rating
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, default=0, nullable=False)

    # Business
    profit_margin = Column(Float, nullable=True)
    commission_rate = Column(Float, nullable=True)

    # Media
    image_url = Column(String(500), nullable=True)
    product_url = Column(String(500), nullable=True)

    # Vector embedding stored in ChromaDB (not here)
    chroma_indexed = Column(Boolean, default=False, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

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

    def __repr__(self):
        return (
            f"<Product id={self.id} "
            f"name={self.name} "
            f"price={self.price}>"
        )

    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "short_description": self.short_description,
            "price": self.price,
            "currency": self.currency,
            "discount_percentage": self.discount_percentage,
            "final_price": self.final_price or self.price,
            "in_stock": self.in_stock,
            "features": self.features or [],
            "specifications": self.specifications or {},
            "rating": self.rating,
            "review_count": self.review_count,
            "image_url": self.image_url,
            "product_url": self.product_url,
            "is_active": self.is_active
        }

    def to_embedding_text(self) -> str:
        """
        Generate text for vector embedding.
        Used when indexing in ChromaDB.
        """
        parts = [
            self.name or "",
            self.brand or "",
            self.category or "",
            self.short_description or "",
            self.full_description or "",
            " ".join(self.features or []),
            " ".join(
                f"{k}: {v}"
                for k, v in (self.specifications or {}).items()
            ),
            self.target_audience or "",
            " ".join(self.use_cases or [])
        ]
        return " ".join(filter(None, parts))


class Lead(Base):
    """
    Stores sales leads for Challenge 5.
    """

    __tablename__ = "leads"

    id = Column(String(36), primary_key=True, index=True)
    conversation_id = Column(String(36), index=True, nullable=True)

    # Customer info
    customer_name = Column(String(255), nullable=True)
    customer_email = Column(String(255), nullable=True)
    customer_phone = Column(String(50), nullable=True)

    # Requirements extracted
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    required_features = Column(JSON, nullable=True)
    preferred_brands = Column(JSON, nullable=True)
    category_interest = Column(String(100), nullable=True)

    # Lead scoring
    total_score = Column(Integer, default=0, nullable=False)
    budget_score = Column(Integer, default=0, nullable=False)
    intent_score = Column(Integer, default=0, nullable=False)
    authority_score = Column(Integer, default=0, nullable=False)
    urgency_score = Column(Integer, default=0, nullable=False)
    lead_category = Column(
        String(20), default="cold", nullable=False
    )
    # Categories: hot, warm, cool, cold

    # Recommended products
    recommended_products = Column(JSON, nullable=True)

    # Follow-up content
    followup_email = Column(Text, nullable=True)
    followup_whatsapp = Column(Text, nullable=True)

    # Status
    status = Column(String(50), default="new", nullable=False)
    # Statuses: new, contacted, qualified, closed_won, closed_lost

    # Escalation
    escalated_to_human = Column(Boolean, default=False)
    escalation_reason = Column(String(255), nullable=True)
    human_rep_id = Column(String(36), nullable=True)

    # Conversation summary
    conversation_summary = Column(Text, nullable=True)
    objections_raised = Column(JSON, nullable=True)

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

    def __repr__(self):
        return (
            f"<Lead id={self.id} "
            f"score={self.total_score} "
            f"category={self.lead_category}>"
        )

    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "customer_name": self.customer_name,
            "budget": {
                "min": self.budget_min,
                "max": self.budget_max
            },
            "required_features": self.required_features or [],
            "preferred_brands": self.preferred_brands or [],
            "scoring": {
                "total": self.total_score,
                "budget": self.budget_score,
                "intent": self.intent_score,
                "authority": self.authority_score,
                "urgency": self.urgency_score,
                "category": self.lead_category
            },
            "recommended_products": (
                self.recommended_products or []
            ),
            "status": self.status,
            "escalated_to_human": self.escalated_to_human,
            "created_at": self.created_at.isoformat()
            if self.created_at else None
        }
