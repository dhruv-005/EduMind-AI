import uuid
import time
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.core.logger import logger
from app.challenge5_sales.intent_extractor import (
    intent_extractor
)
from app.challenge5_sales.recommender import recommender
from app.challenge5_sales.lead_scorer import lead_scorer
from app.challenge5_sales.followup_generator import (
    followup_generator
)
from app.challenge5_sales.objection_handler import (
    objection_handler
)
from app.challenge5_sales.escalation_manager import (
    escalation_manager
)
from app.challenge5_sales.conversation_summarizer import (
    conversation_summarizer
)
from app.governance.audit_logger import audit_logger
from app.governance.content_filter import content_filter
from app.governance.prompt_versioning import prompt_versioning
from app.shared.llm_client import llm_client


class SalesService:
    """
    Main service for Challenge 5 - AI Sales Assistant.
    Orchestrates: intent → search → recommend → score → respond.
    """

    def __init__(self):
        self._conversations: Dict[str, Dict] = {}

    def _get_or_create_conversation(
        self,
        conversation_id: str,
        customer_name: Optional[str] = None,
        customer_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get or create conversation state."""
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = {
                "conversation_id": conversation_id,
                "customer_name": customer_name,
                "customer_email": customer_email,
                "history": [],
                "requirements": {},
                "message_count": 0,
                "lead_score": None,
                "recommendations": [],
                "escalated": False,
                "created_at": time.time()
            }
        return self._conversations[conversation_id]

    def _add_to_history(
        self,
        conversation_id: str,
        role: str,
        text: str
    ):
        """Add message to conversation history."""
        conv = self._conversations.get(conversation_id)
        if conv:
            conv["history"].append({
                "role": role,
                "text": text,
                "timestamp": time.time()
            })
            if role == "customer":
                conv["message_count"] += 1

    def _get_history_text(
        self,
        conversation_id: str
    ) -> str:
        """Get conversation history as text."""
        conv = self._conversations.get(conversation_id, {})
        history = conv.get("history", [])
        return "\n".join([
            f"{h['role'].title()}: {h['text']}"
            for h in history[-10:]
        ])

    async def process_message(
        self,
        conversation_id: str,
        message: str,
        customer_name: Optional[str] = None,
        customer_email: Optional[str] = None,
        db: Optional[Session] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main message processing pipeline.
        Returns complete sales response.
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())

        logger.info(
            f"Processing sales message: "
            f"conv={conversation_id}"
        )

        # Get conversation state
        conv = self._get_or_create_conversation(
            conversation_id=conversation_id,
            customer_name=customer_name,
            customer_email=customer_email
        )

        # Update customer info
        if customer_name:
            conv["customer_name"] = customer_name
        if customer_email:
            conv["customer_email"] = customer_email

        # Add customer message to history
        self._add_to_history(
            conversation_id, "customer", message
        )

        # Content filter
        content_status, _, _ = content_filter.check_input(
            message
        )

        # STEP 1: Extract intent from full conversation
        history_text = self._get_history_text(conversation_id)
        requirements = await intent_extractor.extract_all(
            message=message,
            conversation_history=history_text
        )

        # Merge with existing requirements
        existing_req = conv.get("requirements", {})
        for key, value in requirements.items():
            if value:
                existing_req[key] = value
        conv["requirements"] = existing_req

        # STEP 2: Handle objections first
        objections = existing_req.get("objections", [])
        objection_response = None
        if objections:
            objection_response = objection_handler.detect_and_handle(
                message=message,
                objections=objections
            )

        # STEP 3: Search for products
        recommendations = []
        if existing_req.get("budget_max") or existing_req.get("category_interest"):
            search_results = await recommender.get_recommendations(
                requirements=existing_req,
                top_k=3
            )
            recommendations = search_results
            conv["recommendations"] = recommendations

        # STEP 4: Score lead
        score_result = lead_scorer.calculate_score(
            requirements=existing_req,
            customer_name=conv.get("customer_name"),
            customer_email=conv.get("customer_email"),
            message_count=conv.get("message_count", 1)
        )
        conv["lead_score"] = score_result

        # STEP 5: Check escalation
        should_escalate, escalate_reason = (
            escalation_manager.should_escalate(
                lead_score=score_result,
                conversation_turns=conv.get("message_count", 1),
                requirements=existing_req,
                message=message
            )
        )

        escalation_data = None
        if should_escalate and not conv.get("escalated"):
            conv["escalated"] = True
            escalation_data = (
                await escalation_manager.prepare_handoff(
                    conversation_id=conversation_id,
                    conversation_history=history_text,
                    requirements=existing_req,
                    lead_score=score_result,
                    escalation_reason=escalate_reason,
                    customer_name=conv.get("customer_name")
                )
            )

        # STEP 6: Generate AI response
        if objection_response:
            ai_response = objection_response
        elif should_escalate:
            ai_response = escalation_manager.get_escalation_message(
                reason=escalate_reason,
                customer_name=conv.get("customer_name")
            )
        elif recommendations:
            ai_response = (
                await recommender.format_recommendations_response(
                    recommendations=recommendations,
                    requirements=existing_req
                )
            )
        else:
            ai_response = await self._generate_general_response(
                message=message,
                history_text=history_text,
                customer_name=conv.get("customer_name")
            )

        # Add AI response to history
        self._add_to_history(
            conversation_id, "assistant", ai_response
        )

        # STEP 7: Generate follow-up content
        followup_email = None
        followup_whatsapp = None
        if (
            recommendations and
            score_result.get("category") in ["hot", "warm"]
        ):
            followup_data = await followup_generator.generate_both(
                customer_name=conv.get("customer_name"),
                recommendations=recommendations,
                requirements=existing_req,
                lead_score=score_result
            )
            followup_email = followup_data.get("email")
            followup_whatsapp = followup_data.get("whatsapp")

        elapsed_ms = (time.time() - start_time) * 1000

        # STEP 8: Audit log
        prompt_version = prompt_versioning.get_version(
            "challenge5_sales"
        )
        audit_logger.log_ai_decision(
            db=db,
            request_id=request_id,
            challenge="challenge5",
            user_id=user_id,
            session_id=conversation_id,
            input_summary=message[:100],
            model_used="groq-llama-3.3-70b",
            model_version="3.3-70b",
            prompt_version=prompt_version,
            output_summary=(
                f"recommendations={len(recommendations)} "
                f"lead_score={score_result['total_score']} "
                f"escalated={should_escalate}"
            ),
            confidence_score=0.85,
            processing_time_ms=elapsed_ms,
            governance_status=content_status,
            metadata={
                "lead_category": score_result.get("category"),
                "escalated": should_escalate
            }
        )

        # Format product recommendations for response
        formatted_recommendations = []
        for rec in recommendations[:3]:
            metadata = rec.get("metadata", {})
            try:
                price = float(
                    metadata.get("price", "0")
                )
            except (ValueError, TypeError):
                price = 0.0

            formatted_recommendations.append({
                "product_id": rec.get(
                    "document", ""
                )[:36],
                "name": metadata.get("name", ""),
                "brand": metadata.get("brand"),
                "category": metadata.get("category"),
                "price": price,
                "currency": "USD",
                "final_price": price,
                "short_description": rec.get(
                    "document", ""
                )[:100],
                "features": [],
                "rating": None,
                "in_stock": metadata.get(
                    "in_stock"
                ) == "True",
                "match_score": rec.get("match_score", 0.5),
                "match_reasons": rec.get("match_reasons", []),
                "explanation": rec.get("explanation", "")
            })

        result = {
            "conversation_id": conversation_id,
            "message": ai_response,
            "recommendations": formatted_recommendations,
            "requirements": {
                "budget_min": existing_req.get("budget_min"),
                "budget_max": existing_req.get("budget_max"),
                "required_features": existing_req.get(
                    "required_features", []
                ),
                "preferred_brands": existing_req.get(
                    "preferred_brands", []
                ),
                "avoided_brands": existing_req.get(
                    "avoided_brands", []
                ),
                "category_interest": existing_req.get(
                    "category_interest"
                ),
                "urgency": existing_req.get(
                    "urgency", "normal"
                ),
                "objections": existing_req.get(
                    "objections", []
                )
            },
            "lead_score": score_result,
            "followup_email": followup_email,
            "followup_whatsapp": followup_whatsapp,
            "escalate_to_human": should_escalate,
            "escalation_reason": (
                escalate_reason if should_escalate else None
            ),
            "escalation_data": escalation_data,
            "processing_time_ms": elapsed_ms,
            "model_used": "groq-llama-3.3-70b",
            "governance_status": content_status
        }

        logger.info(
            f"Sales response ready: "
            f"recs={len(recommendations)} "
            f"score={score_result['total_score']} "
            f"time={elapsed_ms:.0f}ms"
        )

        return result

    async def _generate_general_response(
        self,
        message: str,
        history_text: str,
        customer_name: Optional[str] = None
    ) -> str:
        """Generate general sales response."""
        name_ctx = (
            f"Customer name: {customer_name}" if customer_name
            else ""
        )

        prompt = f"""You are a helpful AI sales assistant.

{name_ctx}
Recent conversation:
{history_text[-500:]}

Customer's latest message: {message}

Respond helpfully by:
1. Acknowledging what they said
2. Asking clarifying questions about their needs
3. Gathering budget and feature requirements
4. Being friendly and professional

Keep response to 2-3 sentences."""

        try:
            response = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "You are a helpful, friendly sales assistant. "
                    "Help customers find the right products. "
                    "Ask targeted questions to understand needs."
                ),
                max_tokens=200,
                temperature=0.6
            )
            return response.strip()

        except Exception as e:
            logger.warning(f"General response failed: {e}")
            name = customer_name or "there"
            return (
                f"Hi {name}! I'd love to help you find "
                f"the perfect product. "
                f"Could you tell me more about what you're "
                f"looking for and your budget range?"
            )

    async def start_conversation(
        self,
        customer_name: Optional[str] = None,
        customer_email: Optional[str] = None,
        initial_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a new sales conversation."""
        conversation_id = str(uuid.uuid4())
        conv = self._get_or_create_conversation(
            conversation_id=conversation_id,
            customer_name=customer_name,
            customer_email=customer_email
        )

        name = customer_name or "there"
        welcome = (
            f"Hi {name}! Welcome! I'm your AI shopping "
            f"assistant. I'm here to help you find the "
            f"perfect product. "
            f"What are you looking for today?"
        )

        if initial_message:
            return await self.process_message(
                conversation_id=conversation_id,
                message=initial_message,
                customer_name=customer_name,
                customer_email=customer_email
            )

        return {
            "conversation_id": conversation_id,
            "message": welcome,
            "recommendations": [],
            "requirements": {},
            "lead_score": None,
            "escalate_to_human": False,
            "processing_time_ms": 0,
            "model_used": "none",
            "governance_status": "passed"
        }


# Singleton
sales_service = SalesService()
