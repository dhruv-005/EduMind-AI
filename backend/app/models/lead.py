# Lead model is defined inside product.py
# This file re-exports for clean imports

from app.models.product import Lead

__all__ = ["Lead"]
