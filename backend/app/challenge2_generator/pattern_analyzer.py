from typing import List, Dict, Any, Optional
from collections import Counter
from app.core.logger import logger
from app.shared.llm_client import llm_client


class PatternAnalyzer:
    """
    Analyze patterns in source exam papers.
    Identifies topic frequency, difficulty distribution,
    question type distribution, and recurring themes.
    """

    def analyze_topic_frequency(
        self,
        questions: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Count how often each topic appears."""
        topics = [q.get("topic", "general") for q in questions]
        return dict(Counter(topics))

    def analyze_difficulty_distribution(
        self,
        questions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze difficulty distribution as both
        counts and percentages.
        """
        difficulties = [
            q.get("difficulty", "medium") for q in questions
        ]
        counts = dict(Counter(difficulties))
        total = len(questions) or 1

        percentages = {
            level: round(count / total * 100, 1)
            for level, count in counts.items()
        }

        return {
            "counts": counts,
            "percentages": percentages,
            "dominant": (
                max(counts, key=counts.get)
                if counts else "medium"
            )
        }

    def analyze_question_types(
        self,
        questions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze distribution of question types."""
        types = [q.get("type", "short") for q in questions]
        counts = dict(Counter(types))
        total = len(questions) or 1

        percentages = {
            qtype: round(count / total * 100, 1)
            for qtype, count in counts.items()
        }

        return {
            "counts": counts,
            "percentages": percentages,
            "dominant": (
                max(counts, key=counts.get)
                if counts else "short"
            )
        }

    def analyze_marks_distribution(
        self,
        questions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze marks distribution across questions."""
        marks = [q.get("marks", 5) for q in questions]

        if not marks:
            return {
                "min": 0,
                "max": 0,
                "average": 0,
                "total": 0
            }

        return {
            "min": min(marks),
            "max": max(marks),
            "average": round(sum(marks) / len(marks), 1),
            "total": sum(marks),
            "distribution": dict(Counter(marks))
        }

    def find_recurring_topics(
        self,
        questions: List[Dict[str, Any]],
        threshold: int = 2
    ) -> List[str]:
        """
        Find topics that appear more than threshold times.
        These are high-priority topics for generation.
        """
        topic_freq = self.analyze_topic_frequency(questions)
        recurring = [
            topic for topic, count in topic_freq.items()
            if count >= threshold
        ]
        # Sort by frequency
        recurring.sort(
            key=lambda t: topic_freq[t],
            reverse=True
        )
        return recurring

    def get_recommended_focus(
        self,
        questions: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Get recommended topics to focus on for new paper.
        Based on frequency analysis of source papers.
        """
        topic_freq = self.analyze_topic_frequency(questions)

        # Sort by frequency descending
        sorted_topics = sorted(
            topic_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top 5 topics
        return [topic for topic, _ in sorted_topics[:5]]

    async def analyze_with_llm(
        self,
        raw_text: str,
        subject: str
    ) -> Dict[str, Any]:
        """
        Use LLM to extract deeper patterns from paper text.
        Identifies themes, key concepts, and question styles.
        """
        prompt = f"""Analyze this {subject} exam paper and identify:
1. Main topics covered (list 5-10 topics)
2. Cognitive levels tested (remember/understand/apply/analyze)
3. Common question styles used
4. Key concepts that appear frequently

Paper text (first 2000 chars):
{raw_text[:2000]}

Respond with JSON:
{{
    "main_topics": ["topic1", "topic2"],
    "cognitive_levels": {{"remember": 30, "understand": 40, "apply": 20, "analyze": 10}},
    "question_styles": ["style1", "style2"],
    "key_concepts": ["concept1", "concept2"],
    "difficulty_assessment": "easy/medium/hard/mixed"
}}"""

        try:
            result = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "You are an expert educational assessment analyst. "
                    "Analyze exam papers and identify patterns. "
                    "Respond with valid JSON only."
                ),
                max_tokens=600,
                temperature=0.2
            )

            import json
            import re
            json_match = re.search(r'\{.+\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            logger.warning(f"LLM pattern analysis failed: {e}")

        return {
            "main_topics": [],
            "cognitive_levels": {},
            "question_styles": [],
            "key_concepts": [],
            "difficulty_assessment": "mixed"
        }

    def build_generation_context(
        self,
        questions: List[Dict[str, Any]],
        llm_analysis: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Build context dict for question generation.
        Summarizes all patterns for the generator to use.
        """
        topic_freq = self.analyze_topic_frequency(questions)
        difficulty_dist = self.analyze_difficulty_distribution(
            questions
        )
        type_dist = self.analyze_question_types(questions)
        marks_dist = self.analyze_marks_distribution(questions)
        recurring = self.find_recurring_topics(questions)
        focus = self.get_recommended_focus(questions)

        context = {
            "source_question_count": len(questions),
            "topic_frequency": topic_freq,
            "difficulty_distribution": difficulty_dist,
            "question_type_distribution": type_dist,
            "marks_distribution": marks_dist,
            "recurring_topics": recurring,
            "recommended_focus": focus
        }

        if llm_analysis:
            context["llm_insights"] = llm_analysis

        return context


# Singleton
pattern_analyzer = PatternAnalyzer()
