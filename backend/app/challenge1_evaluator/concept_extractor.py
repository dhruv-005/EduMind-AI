import re
from typing import List, Dict, Any, Optional
from app.core.logger import logger
from app.shared.llm_client import llm_client


class ConceptExtractor:
    """
    Extract key concepts from answers using NLP + LLM.
    Used to identify what concepts a student did/didn't cover.
    """

    def __init__(self):
        self._nlp = None

    def _get_nlp(self):
        """Load spaCy model lazily."""
        if self._nlp is None:
            try:
                import spacy
                try:
                    self._nlp = spacy.load("en_core_web_sm")
                    logger.info("spaCy model loaded: en_core_web_sm")
                except OSError:
                    logger.warning(
                        "spaCy model not found. "
                        "Run: python -m spacy download en_core_web_sm"
                    )
                    self._nlp = None
            except ImportError:
                logger.warning("spaCy not installed")
                self._nlp = None
        return self._nlp

    def extract_keywords_simple(self, text: str) -> List[str]:
        """
        Simple keyword extraction without spaCy.
        Fallback when spaCy not available.
        """
        if not text:
            return []

        # Remove punctuation and lowercase
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text_clean.split()

        # Common stop words to filter
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on',
            'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is',
            'are', 'was', 'were', 'be', 'been', 'being', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can',
            'that', 'this', 'these', 'those', 'it', 'its',
            'which', 'who', 'what', 'when', 'where', 'how', 'why',
            'also', 'as', 'so', 'if', 'then', 'than', 'not',
            'no', 'nor', 'yet', 'both', 'either'
        }

        # Filter stop words and short words
        keywords = [
            w for w in words
            if w not in stop_words and len(w) > 3
        ]

        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords[:20]

    def extract_with_spacy(self, text: str) -> List[str]:
        """Extract concepts using spaCy NLP."""
        nlp = self._get_nlp()
        if not nlp or not text:
            return self.extract_keywords_simple(text)

        try:
            doc = nlp(text[:1000])  # Limit for performance
            concepts = []

            # Extract noun chunks (key phrases)
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower().strip()
                if len(chunk_text) > 2:
                    concepts.append(chunk_text)

            # Extract named entities
            for ent in doc.ents:
                ent_text = ent.text.lower().strip()
                if (
                    ent_text not in concepts and
                    len(ent_text) > 2
                ):
                    concepts.append(ent_text)

            # Extract key verbs and nouns
            for token in doc:
                if (
                    token.pos_ in ["NOUN", "PROPN"] and
                    not token.is_stop and
                    len(token.text) > 3
                ):
                    token_text = token.lemma_.lower()
                    if token_text not in concepts:
                        concepts.append(token_text)

            return concepts[:20]

        except Exception as e:
            logger.warning(f"spaCy extraction failed: {e}")
            return self.extract_keywords_simple(text)

    async def extract_concepts_llm(
        self,
        text: str,
        subject: str = "general"
    ) -> List[str]:
        """
        Extract concepts using LLM for better accuracy.
        Returns list of key concepts.
        """
        if not text.strip():
            return []

        prompt = f"""Extract the key concepts and facts from this {subject} answer.
Return ONLY a Python list of short concept phrases (2-5 words each).
No explanations, just the list.

Answer: {text[:800]}

Format: ["concept 1", "concept 2", "concept 3"]
"""
        try:
            result = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "You are an expert at identifying key "
                    "educational concepts from student answers. "
                    "Return only a valid Python list."
                ),
                max_tokens=300,
                temperature=0.1
            )

            # Parse the list from LLM response
            concepts = self._parse_concept_list(result)
            return concepts

        except Exception as e:
            logger.warning(f"LLM concept extraction failed: {e}")
            return self.extract_with_spacy(text)

    def _parse_concept_list(self, text: str) -> List[str]:
        """Parse a Python list from LLM response text."""
        try:
            # Find list pattern in response
            match = re.search(r'\[([^\]]+)\]', text)
            if match:
                list_str = match.group(0)
                # Safe evaluation
                import ast
                concepts = ast.literal_eval(list_str)
                if isinstance(concepts, list):
                    return [
                        str(c).lower().strip()
                        for c in concepts
                        if c and len(str(c)) > 2
                    ]
        except Exception as e:
            logger.warning(f"Failed to parse concept list: {e}")

        # Fallback: extract quoted strings
        concepts = re.findall(r'"([^"]+)"', text)
        if not concepts:
            concepts = re.findall(r"'([^']+)'", text)

        return [c.lower().strip() for c in concepts if len(c) > 2]

    def compare_concepts(
        self,
        reference_concepts: List[str],
        student_concepts: List[str]
    ) -> Dict[str, Any]:
        """
        Compare student concepts vs reference concepts.
        Returns what's correct, missing, and wrong.
        """
        ref_set = set(c.lower() for c in reference_concepts)
        student_set = set(c.lower() for c in student_concepts)

        # Find exact matches
        correct = list(ref_set & student_set)

        # Find missing (in reference but not in student)
        missing = list(ref_set - student_set)

        # Find wrong (in student but not in reference)
        wrong = list(student_set - ref_set)

        # Calculate coverage
        coverage = (
            len(correct) / len(ref_set) * 100
            if ref_set else 0
        )

        return {
            "correct_concepts": correct,
            "missing_concepts": missing[:10],
            "wrong_concepts": wrong[:5],
            "total_expected": len(ref_set),
            "total_found": len(correct),
            "coverage_percentage": round(coverage, 1)
        }

    async def full_concept_analysis(
        self,
        reference_answer: str,
        student_answer: str,
        subject: str = "general"
    ) -> Dict[str, Any]:
        """
        Full concept analysis combining spaCy + LLM.
        Returns comprehensive concept comparison.
        """
        # Extract from reference (use both methods)
        ref_spacy = self.extract_with_spacy(reference_answer)
        ref_llm = await self.extract_concepts_llm(
            reference_answer, subject
        )
        reference_concepts = list(set(ref_spacy + ref_llm))

        # Extract from student answer
        student_spacy = self.extract_with_spacy(student_answer)
        student_llm = await self.extract_concepts_llm(
            student_answer, subject
        )
        student_concepts = list(set(student_spacy + student_llm))

        # Compare
        comparison = self.compare_concepts(
            reference_concepts,
            student_concepts
        )

        return comparison


# Singleton
concept_extractor = ConceptExtractor()
