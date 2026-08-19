from typing import Dict, Any
from app.core.logger import logger
from app.core.constants import get_lead_category


class LeadScorer:
    """
    Score sales leads using BANT framework:
    Budget + Authority + Need + Timeline (Urgency)
    Total score: 0-100, category: hot/warm/cool/cold
    """

    def score_budget(
        self,
        requirements: Dict[str, Any]
    ) -> int:
        """
        Score budget clarity (0-25 points).
        Clear budget = higher score.
        """
        budget_max = requirements.get("budget_max")
        budget_min = requirements.get("budget_min")

        if budget_max and budget_min:
            return 25  # Clear budget range
        elif budget_max:
            return 20  # Has max budget
        elif budget_min:
            return 15  # Has min budget only
        else:
            # Check for implied budget
            purchase_intent = requirements.get(
                "purchase_intent", "medium"
            )
            if purchase_intent == "high":
                return 10
            return 5  # No budget info

    def score_intent(
        self,
        requirements: Dict[str, Any],
        message_count: int = 1
    ) -> int:
        """
        Score purchase intent (0-25 points).
        Strong intent = higher score.
        """
        intent = requirements.get("purchase_intent", "medium")
        features = requirements.get("required_features", [])
        objections = requirements.get("objections", [])

        base_score = {
            "high": 20,
            "medium": 12,
            "low": 5
        }.get(intent, 12)

        # More features = more specific intent
        if len(features) >= 3:
            base_score += 3
        elif len(features) >= 1:
            base_score += 1

        # Objections reduce intent score
        if len(objections) >= 3:
            base_score -= 5
        elif len(objections) >= 1:
            base_score -= 2

        # More messages = more engaged
        if message_count >= 5:
            base_score += 2
        elif message_count >= 3:
            base_score += 1

        return max(0, min(25, base_score))

    def score_authority(
        self,
        requirements: Dict[str, Any],
        customer_name: str = None,
        customer_email: str = None
    ) -> int:
        """
        Score decision-making authority (0-25 points).
        Provided contact info = more authority signals.
        """
        score = 10  # Base score

        # Has name = real person
        if customer_name:
            score += 5

        # Has email = serious buyer
        if customer_email:
            score += 8

        # Authority keywords
        message = requirements.get("specific_requirements", "")
        authority_keywords = [
            "i will", "i want to buy", "i need",
            "for my business", "our company",
            "i can decide", "i'm the buyer"
        ]
        if any(
            kw in message.lower()
            for kw in authority_keywords
        ):
            score += 2

        return min(25, score)

    def score_urgency(
        self,
        requirements: Dict[str, Any]
    ) -> int:
        """
        Score purchase urgency/timeline (0-25 points).
        High urgency = higher score.
        """
        urgency = requirements.get("urgency", "normal")

        urgency_scores = {
            "high": 22,
            "normal": 12,
            "low": 5
        }

        score = urgency_scores.get(urgency, 12)

        # Objections reduce urgency score
        objections = requirements.get("objections", [])
        if "not_sure" in objections:
            score -= 5
        if "need_to_compare" in objections:
            score -= 3

        return max(0, min(25, score))

    def calculate_score(
        self,
        requirements: Dict[str, Any],
        customer_name: str = None,
        customer_email: str = None,
        message_count: int = 1
    ) -> Dict[str, Any]:
        """
        Calculate complete lead score.
        Returns score breakdown and category.
        """
        budget_score = self.score_budget(requirements)
        intent_score = self.score_intent(
            requirements, message_count
        )
        authority_score = self.score_authority(
            requirements, customer_name, customer_email
        )
        urgency_score = self.score_urgency(requirements)

        total_score = (
            budget_score +
            intent_score +
            authority_score +
            urgency_score
        )

        category = get_lead_category(total_score)

        # Generate explanation
        explanation = self._build_explanation(
            total_score=total_score,
            category=category,
            budget_score=budget_score,
            intent_score=intent_score,
            urgency_score=urgency_score
        )

        # Recommend next action
        next_action = self._get_next_action(
            category=category,
            urgency=requirements.get("urgency", "normal"),
            has_email=bool(customer_email)
        )

        result = {
            "total_score": total_score,
            "budget_score": budget_score,
            "intent_score": intent_score,
            "authority_score": authority_score,
            "urgency_score": urgency_score,
            "category": category,
            "explanation": explanation,
            "next_action": next_action
        }

        logger.info(
            f"Lead scored: {total_score}/100 "
            f"category={category}"
        )

        return result

    def _build_explanation(
        self,
        total_score: int,
        category: str,
        budget_score: int,
        intent_score: int,
        urgency_score: int
    ) -> str:
        """Build human-readable score explanation."""
        strength = []
        weakness = []

        if budget_score >= 20:
            strength.append("clear budget")
        else:
            weakness.append("unclear budget")

        if intent_score >= 18:
            strength.append("strong intent")
        elif intent_score >= 10:
            strength.append("moderate interest")
        else:
            weakness.append("low purchase intent")

        if urgency_score >= 18:
            strength.append("urgent need")
        elif urgency_score <= 6:
            weakness.append("no urgency")

        strengths_text = (
            f"Strong signals: {', '.join(strength)}. "
            if strength else ""
        )
        weakness_text = (
            f"Weak signals: {', '.join(weakness)}. "
            if weakness else ""
        )

        return (
            f"{category.upper()} lead ({total_score}/100). "
            f"{strengths_text}{weakness_text}"
        )

    def _get_next_action(
        self,
        category: str,
        urgency: str,
        has_email: bool
    ) -> str:
        """Get recommended next action for sales team."""
        actions = {
            "hot": (
                "Contact immediately! High-value lead ready to buy. "
                "Schedule a demo or call within 1 hour."
            ),
            "warm": (
                "Send personalized follow-up within 24 hours. "
                "Include product comparison and special offer."
            ),
            "cool": (
                "Add to nurture campaign. "
                "Send educational content and check back in 1 week."
            ),
            "cold": (
                "Add to general newsletter. "
                "Re-engage with promotional offers in 2-4 weeks."
            )
        }

        action = actions.get(
            category,
            "Monitor and engage when appropriate."
        )

        if has_email and category in ["hot", "warm"]:
            action += " Send follow-up email."

        return action


# Singleton
lead_scorer = LeadScorer()
