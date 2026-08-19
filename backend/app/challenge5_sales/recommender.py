from typing import List, Dict, Any, Optional
from app.core.logger import logger
from app.shared.llm_client import llm_client
from app.challenge5_sales.catalogue_manager import (
    catalogue_manager
)


class Recommender:
    """
    Product recommender using RAG pipeline.
    Semantic search + LLM explanation.
    ZERO hallucination: only uses catalogue data.
    """

    async def get_recommendations(
        self,
        requirements: Dict[str, Any],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get top product recommendations.
        Uses semantic search + requirement filtering.
        Returns top_k products with explanations.
        """
        # Build search query from requirements
        query = self._build_search_query(requirements)
        logger.info(f"Search query: {query[:100]}")

        # Search in ChromaDB
        search_results = await catalogue_manager.search_products(
            query=query,
            budget_max=requirements.get("budget_max"),
            category=requirements.get("category_interest"),
            in_stock_only=True,
            top_k=top_k * 3
        )

        if not search_results:
            logger.warning("No products found in search")
            return []

        # Score and rank results
        scored = self._score_results(
            results=search_results,
            requirements=requirements
        )

        # Take top_k
        top_results = scored[:top_k]

        # Generate explanations using LLM
        enriched = await self._generate_explanations(
            products=top_results,
            requirements=requirements
        )

        return enriched

    def _build_search_query(
        self,
        requirements: Dict[str, Any]
    ) -> str:
        """Build semantic search query from requirements."""
        parts = []

        category = requirements.get("category_interest")
        if category:
            parts.append(category)

        features = requirements.get("required_features", [])
        if features:
            parts.extend(features[:5])

        brands = requirements.get("preferred_brands", [])
        if brands:
            parts.append(f"brand: {', '.join(brands)}")

        budget_max = requirements.get("budget_max")
        if budget_max:
            parts.append(f"under ${budget_max}")

        specific = requirements.get("specific_requirements")
        if specific:
            parts.append(specific)

        return " ".join(parts) if parts else "popular products"

    def _score_results(
        self,
        results: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Score and rank search results based on requirements.
        Higher score = better match.
        """
        budget_max = requirements.get("budget_max")
        preferred_brands = [
            b.lower()
            for b in requirements.get("preferred_brands", [])
        ]
        avoided_brands = [
            b.lower()
            for b in requirements.get("avoided_brands", [])
        ]
        required_features = [
            f.lower()
            for f in requirements.get("required_features", [])
        ]

        scored = []

        for result in results:
            metadata = result.get("metadata", {})
            similarity = result.get("similarity", 0.5)

            score = similarity

            # Budget fit bonus
            price_str = metadata.get("price", "0")
            try:
                price = float(price_str)
                if budget_max:
                    if price <= budget_max:
                        budget_fit = (
                            1.0 - (price / budget_max) * 0.3
                        )
                        score += budget_fit * 0.2
                    else:
                        score -= 0.3
            except (ValueError, TypeError):
                pass

            # Brand preference
            brand = metadata.get("brand", "").lower()
            if brand in preferred_brands:
                score += 0.15
            if brand in avoided_brands:
                score -= 0.5

            # Feature matching
            doc_text = result.get("document", "").lower()
            feature_matches = sum(
                1 for f in required_features
                if f in doc_text
            )
            if required_features:
                score += (
                    feature_matches /
                    len(required_features) * 0.2
                )

            # In stock bonus
            if metadata.get("in_stock") == "True":
                score += 0.05

            scored.append({
                **result,
                "match_score": round(
                    max(0.0, min(1.0, score)), 3
                )
            })

        scored.sort(
            key=lambda x: x["match_score"],
            reverse=True
        )

        # Filter avoided brands completely
        scored = [
            r for r in scored
            if r.get("metadata", {}).get(
                "brand", ""
            ).lower() not in avoided_brands
        ]

        return scored

    async def _generate_explanations(
        self,
        products: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized explanations for each product.
        Uses ONLY catalogue data - no hallucination.
        """
        enriched = []

        for product in products:
            metadata = product.get("metadata", {})
            doc_text = product.get("document", "")

            # Build prompt using ONLY catalogue data
            prompt = f"""Based ONLY on this product information, 
explain why it matches the customer's needs.

Product: {metadata.get('name', 'Unknown')}
Brand: {metadata.get('brand', 'Unknown')}
Category: {metadata.get('category', 'Unknown')}
Price: ${metadata.get('price', 'Unknown')}
Details: {doc_text[:300]}

Customer needs:
- Budget: up to ${requirements.get('budget_max', 'flexible')}
- Features needed: {', '.join(requirements.get('required_features', ['not specified']))}
- Urgency: {requirements.get('urgency', 'normal')}

Write 2-3 sentences explaining why this product fits.
ONLY use the product information provided above.
Do NOT invent features not mentioned."""

            try:
                explanation = await llm_client.simple_prompt_async(
                    prompt=prompt,
                    system=(
                        "You are a helpful sales assistant. "
                        "Explain product matches accurately. "
                        "NEVER invent or hallucinate features. "
                        "Only use provided product data."
                    ),
                    max_tokens=150,
                    temperature=0.3
                )

                match_reasons = self._extract_match_reasons(
                    doc_text=doc_text,
                    requirements=requirements,
                    metadata=metadata
                )

                enriched.append({
                    **product,
                    "explanation": explanation.strip(),
                    "match_reasons": match_reasons,
                    "product_name": metadata.get("name"),
                    "product_brand": metadata.get("brand"),
                    "product_category": metadata.get("category"),
                    "product_price": metadata.get("price"),
                    "product_in_stock": metadata.get(
                        "in_stock"
                    ) == "True"
                })

            except Exception as e:
                logger.warning(
                    f"Explanation generation failed: {e}"
                )
                enriched.append({
                    **product,
                    "explanation": (
                        "This product matches your requirements."
                    ),
                    "match_reasons": [],
                    "product_name": metadata.get("name"),
                    "product_brand": metadata.get("brand"),
                    "product_category": metadata.get("category"),
                    "product_price": metadata.get("price"),
                    "product_in_stock": metadata.get(
                        "in_stock"
                    ) == "True"
                })

        return enriched

    def _extract_match_reasons(
        self,
        doc_text: str,
        requirements: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[str]:
        """Extract specific reasons why product matches."""
        reasons = []
        doc_lower = doc_text.lower()

        budget_max = requirements.get("budget_max")
        price_str = metadata.get("price", "0")
        try:
            price = float(price_str)
            if budget_max and price <= budget_max:
                reasons.append(
                    f"Within budget (${price:.0f})"
                )
        except (ValueError, TypeError):
            pass

        features = requirements.get("required_features", [])
        for feature in features[:3]:
            if feature.lower() in doc_lower:
                reasons.append(
                    f"Has {feature}"
                )

        brands = requirements.get("preferred_brands", [])
        brand = metadata.get("brand", "")
        if brand and brand.lower() in [
            b.lower() for b in brands
        ]:
            reasons.append(f"Preferred brand: {brand}")

        if metadata.get("in_stock") == "True":
            reasons.append("In stock and available")

        return reasons[:4]

    async def format_recommendations_response(
        self,
        recommendations: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> str:
        """
        Format recommendations as natural language response.
        """
        if not recommendations:
            return (
                "I couldn't find products matching your "
                "exact requirements. Could you tell me more "
                "about what you're looking for? For example, "
                "your budget range or specific features needed."
            )

        budget_ctx = ""
        if requirements.get("budget_max"):
            budget_ctx = (
                f"under ${requirements['budget_max']:.0f}"
            )

        products_text = "\n".join([
            f"{i+1}. {p.get('product_name', 'Product')} "
            f"(${p.get('product_price', 'N/A')}) - "
            f"{p.get('explanation', '')}"
            for i, p in enumerate(recommendations[:3])
        ])

        prompt = f"""You are a helpful sales assistant.
Present these {len(recommendations)} product recommendations 
naturally and persuasively to the customer.

Customer budget: {budget_ctx or 'flexible'}
Customer needs: {', '.join(requirements.get('required_features', ['general use']))}

Products found:
{products_text}

Write a helpful, conversational response (3-4 sentences) that:
1. Acknowledges their needs
2. Highlights the best match
3. Mentions key benefits
4. Asks if they want more details

Keep it friendly and helpful. Don't repeat all product details."""

        try:
            response = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "You are a friendly, knowledgeable "
                    "sales assistant. Be helpful and honest. "
                    "Only mention features from the provided "
                    "product data."
                ),
                max_tokens=250,
                temperature=0.5
            )
            return response.strip()

        except Exception as e:
            logger.warning(
                f"Response formatting failed: {e}"
            )
            names = [
                p.get("product_name", "product")
                for p in recommendations[:3]
            ]
            return (
                f"Based on your requirements, I recommend: "
                f"{', '.join(names)}. "
                f"Would you like more details on any of these?"
            )


# Singleton
recommender = Recommender()
