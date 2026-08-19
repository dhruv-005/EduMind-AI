import re
from typing import List, Dict, Any, Set, Tuple
from app.core.logger import logger

# Known abbreviations to skip
KNOWN_ABBREVIATIONS = {
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr",
    "etc", "eg", "ie", "vs", "dept", "approx",
    "avg", "max", "min", "std", "qty", "ref",
    "no", "vol", "pg", "pp", "ed", "rev",
    "jan", "feb", "mar", "apr", "jun", "jul",
    "aug", "sep", "oct", "nov", "dec",
    "mon", "tue", "wed", "thu", "fri", "sat", "sun",
    "am", "pm", "bc", "ad", "phd", "mba", "llb",
    "usa", "uk", "eu", "un", "nato", "nasa"
}

# Technical terms by domain
TECHNICAL_TERMS = {
    "mathematics": {
        "cosine", "sine", "tangent", "polynomial",
        "determinant", "eigenvalue", "parallelogram",
        "rhombus", "trapezoid", "hypotenuse",
        "pythagorean", "logarithm", "exponent",
        "coefficient", "quadratic", "binomial",
        "permutation", "combinatorics", "stochastic"
    },
    "science": {
        "photosynthesis", "mitosis", "meiosis",
        "chromosome", "ribosomes", "mitochondria",
        "centriole", "vacuole", "chloroplast",
        "glycolysis", "cytoplasm", "nucleotide",
        "oxidation", "reduction", "electrolysis",
        "thermodynamics", "entropy", "wavelength",
        "frequency", "amplitude", "refraction",
        "diffraction", "osmosis", "diffusion"
    },
    "general_technical": {
        "algorithm", "blockchain", "cryptocurrency",
        "api", "html", "css", "javascript", "python",
        "database", "software", "hardware",
        "bandwidth", "latency", "protocol"
    }
}

# Flatten all technical terms
ALL_TECHNICAL_TERMS: Set[str] = set()
for domain_terms in TECHNICAL_TERMS.values():
    ALL_TECHNICAL_TERMS.update(domain_terms)


class SmartFilter:
    """
    Intelligent filter to reduce false positives
    in spell checking results.
    Skips: names, abbreviations, technical terms, ALL CAPS.
    """

    def __init__(self):
        self._nlp = None
        self._custom_dict: Set[str] = set()

    def _get_nlp(self):
        """Load spaCy for NER lazily."""
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy NER loaded for smart filter")
            except Exception as e:
                logger.warning(
                    f"spaCy not available for smart filter: {e}"
                )
                self._nlp = None
        return self._nlp

    def add_to_custom_dict(self, words: List[str]):
        """Add words to custom dictionary (skip these)."""
        self._custom_dict.update(
            w.lower() for w in words
        )

    def is_proper_noun(self, word: str, context: str) -> bool:
        """Check if word is a proper noun using spaCy NER."""
        nlp = self._get_nlp()
        if not nlp:
            # Fallback: check if word starts with capital
            # in middle of sentence
            return (
                word[0].isupper() and
                len(word) > 1
            )

        try:
            doc = nlp(context[:200])
            named_entities = {
                ent.text.lower() for ent in doc.ents
                if ent.label_ in [
                    "PERSON", "ORG", "GPE", "LOC",
                    "PRODUCT", "EVENT", "FAC"
                ]
            }
            return word.lower() in named_entities
        except Exception:
            return False

    def is_abbreviation(self, word: str) -> bool:
        """Check if word is a known abbreviation."""
        word_lower = word.lower()

        # Known abbreviations list
        if word_lower in KNOWN_ABBREVIATIONS:
            return True

        # All uppercase (likely abbreviation)
        if word.isupper() and len(word) <= 6:
            return True

        # Contains dots (e.g., U.S.A.)
        if re.match(r'^[A-Z](\.[A-Z])+\.?$', word):
            return True

        return False

    def is_technical_term(
        self,
        word: str,
        domain: str = "general"
    ) -> bool:
        """Check if word is a technical term."""
        word_lower = word.lower()

        # Check all technical terms
        if word_lower in ALL_TECHNICAL_TERMS:
            return True

        # Check domain-specific terms
        domain_terms = TECHNICAL_TERMS.get(domain, set())
        if word_lower in domain_terms:
            return True

        return False

    def is_in_custom_dict(self, word: str) -> bool:
        """Check if word is in custom dictionary."""
        return word.lower() in self._custom_dict

    def is_number_or_mixed(self, word: str) -> bool:
        """Check if word contains numbers."""
        return bool(re.search(r'\d', word))

    def is_too_short(
        self,
        word: str,
        min_length: int = 2
    ) -> bool:
        """Check if word is too short to spell check."""
        return len(word) <= min_length

    def should_skip(
        self,
        word: str,
        context: str = "",
        domain: str = "general",
        skip_proper_nouns: bool = True,
        skip_technical: bool = True
    ) -> Tuple[bool, str]:
        """
        Main filter method.
        Returns (should_skip, reason).
        """
        # Skip very short words
        if self.is_too_short(word):
            return True, "too_short"

        # Skip words with numbers
        if self.is_number_or_mixed(word):
            return True, "contains_numbers"

        # Skip abbreviations
        if self.is_abbreviation(word):
            return True, "abbreviation"

        # Skip ALL CAPS words
        if word.isupper():
            return True, "all_caps"

        # Skip technical terms
        if skip_technical and self.is_technical_term(
            word, domain
        ):
            return True, "technical_term"

        # Skip custom dictionary words
        if self.is_in_custom_dict(word):
            return True, "custom_dictionary"

        # Skip proper nouns
        if skip_proper_nouns and context:
            if self.is_proper_noun(word, context):
                return True, "proper_noun"

        return False, ""

    def filter_errors(
        self,
        errors: List[Dict[str, Any]],
        full_text: str = "",
        domain: str = "general",
        skip_proper_nouns: bool = True,
        skip_technical: bool = True
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Filter error list to remove false positives.
        Returns (filtered_errors, skipped_words).
        """
        filtered = []
        skipped = []

        for error in errors:
            word = error.get("word", "")
            if not word:
                continue

            should_skip, reason = self.should_skip(
                word=word,
                context=full_text,
                domain=domain,
                skip_proper_nouns=skip_proper_nouns,
                skip_technical=skip_technical
            )

            if should_skip:
                skipped.append(word)
                logger.debug(
                    f"Skipped '{word}': {reason}"
                )
            else:
                filtered.append(error)

        logger.info(
            f"Smart filter: "
            f"{len(filtered)} real errors, "
            f"{len(skipped)} skipped"
        )

        return filtered, skipped

    def get_skip_stats(
        self,
        original: List[Dict],
        filtered: List[Dict],
        skipped: List[str]
    ) -> Dict[str, Any]:
        """Get statistics about filtering."""
        return {
            "original_error_count": len(original),
            "real_error_count": len(filtered),
            "skipped_count": len(skipped),
            "false_positive_rate": round(
                len(skipped) / max(len(original), 1) * 100,
                1
            )
        }


# Singleton
smart_filter = SmartFilter()
