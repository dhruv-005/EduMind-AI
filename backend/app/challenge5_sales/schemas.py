from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any


class CatalogueUploadResponse(BaseModel):
    """Response after uploading product catalogue."""
    catalogue_id: str
    total_products: int
    indexed_products: int
    categories: List[str]
    message: str


class CustomerMessage(BaseModel):
    """Customer message in sales chat."""
    conversation_id: str
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000
    )
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_abc123",
                "message": "I'm looking for a laptop under $1000 for gaming",
                "customer_name": "John"
            }
        }


class StartConversationRequest(BaseModel):
    """Request to start a new sales conversation."""
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    initial_message: Optional[str] = None
    catalogue_id: Optional[str] = None


class ProductRecommendation(BaseModel):
    """Single product recommendation."""
    product_id: str
    name: str
    brand: Optional[str]
    category: Optional[str]
    price: float
    currency: str = "USD"
    final_price: Optional[float]
    short_description: Optional[str]
    features: Optional[List[str]]
    rating: Optional[float]
    in_stock: bool
    match_score: float = Field(ge=0.0, le=1.0)
    match_reasons: List[str] = []
    image_url: Optional[str] = None


class CustomerRequirements(BaseModel):
    """Extracted customer requirements."""
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    required_features: List[str] = []
    preferred_brands: List[str] = []
    avoided_brands: List[str] = []
    category_interest: Optional[str] = None
    urgency: str = "normal"
    objections: List[str] = []


class LeadScore(BaseModel):
    """Lead scoring result."""
    total_score: int = Field(ge=0, le=100)
    budget_score: int = Field(ge=0, le=25)
    intent_score: int = Field(ge=0, le=25)
    authority_score: int = Field(ge=0, le=25)
    urgency_score: int = Field(ge=0, le=25)
    category: str
    explanation: str
    next_action: str


class SalesResponse(BaseModel):
    """Sales AI response to customer."""
    conversation_id: str
    message: str
    recommendations: Optional[List[ProductRecommendation]] = None
    requirements: Optional[CustomerRequirements] = None
    lead_score: Optional[LeadScore] = None
    followup_email: Optional[str] = None
    followup_whatsapp: Optional[str] = None
    escalate_to_human: bool = False
    escalation_reason: Optional[str] = None
    processing_time_ms: float
    model_used: str
    governance_status: str = "passed"


class FollowUpRequest(BaseModel):
    """Request to generate follow-up content."""
    conversation_id: str
    format: str = Field(
        default="email",
        description="email or whatsapp"
    )
    include_products: bool = True
    custom_note: Optional[str] = None


class EscalationRequest(BaseModel):
    """Request to escalate to human rep."""
    conversation_id: str
    reason: str
    priority: str = "normal"
