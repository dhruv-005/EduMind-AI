import re
from typing import List, Dict, Any, Tuple, Optional, Set
from app.core.logger import logger


class SpellDetector:
    """
    Multi-layer spell detection pipeline.
    Layer 1: PySpellChecker (fast)
    Layer 2: LanguageTool (context-aware)
    Layer 3: LLM verification (confirm real errors)
    """

    def __init__(self):
        self._spell_checker = None
        self._lang_tool = None

    def _get_spell_checker(self):
        """Load PySpellChecker lazily."""
        if self._spell_checker is None:
            try:
                from spellchecker import SpellChecker
                self._spell_checker = SpellChecker(language='en')
                logger.info("PySpellChecker loaded")
            except ImportError:
                logger.warning(
                    "pyspellchecker not installed. "
                    "Run: pip install pyspellchecker"
                )
        return self._spell_checker

    def _get_lang_tool(self):
        """Load LanguageTool lazily."""
        if self._lang_tool is None:
            try:
                import language_tool_python
                self._lang_tool = (
                    language_tool_python.LanguageTool('en-US')
                )
                logger.info("LanguageTool loaded")
            except ImportError:
                logger.warning(
                    "language_tool_python not installed. "
                    "Run: pip install language-tool-python"
                )
            except Exception as e:
                logger.warning(f"LanguageTool failed to load: {e}")
        return self._lang_tool

    def tokenize_text(self, text: str) -> List[Dict[str, Any]]:
        """Tokenize text into words with position info."""
        words = []
        pattern = re.compile(r'\b[a-zA-Z]+\b')

        for line_num, line in enumerate(text.split('\n'), 1):
            for match in pattern.finditer(line):
                words.append({
                    "word": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "line": line_num
                })

        return words

    def check_with_pyspellchecker(
        self,
        words: List[str]
    ) -> Dict[str, str]:
        """Check words with PySpellChecker."""
        checker = self._get_spell_checker()
        if not checker:
            return {}

        try:
            alpha_words = [
                w for w in words
                if w.isalpha() and len(w) > 2
            ]

            if not alpha_words:
                return {}

            misspelled = checker.unknown(alpha_words)

            corrections = {}
            for word in misspelled:
                correction = checker.correction(word)
                if correction and correction != word:
                    corrections[word] = correction

            logger.debug(
                f"PySpellChecker: {len(corrections)} errors "
                f"in {len(alpha_words)} words"
            )
            return corrections

        except Exception as e:
            logger.warning(f"PySpellChecker failed: {e}")
            return {}

    def check_with_languagetool(
        self,
        text: str
    ) -> List[Dict[str, Any]]:
        """Check text with LanguageTool for contextual errors."""
        tool = self._get_lang_tool()
        if not tool:
            return []

        try:
            matches = tool.check(text[:5000])
            errors = []

            for match in matches:
                if match.ruleId.startswith('MORFOLOGIK'):
                    error_word = text[
                        match.offset:match.offset + match.errorLength
                    ]
                    correction = (
                        match.replacements[0]
                        if match.replacements else error_word
                    )
                    errors.append({
                        "word": error_word,
                        "correction": correction,
                        "offset": match.offset,
                        "length": match.errorLength,
                        "rule_id": match.ruleId,
                        "message": match.message,
                        "alternatives": match.replacements[:5],
                        "source": "languagetool"
                    })

            logger.debug(
                f"LanguageTool: {len(errors)} errors found"
            )
            return errors

        except Exception as e:
            logger.warning(f"LanguageTool check failed: {e}")
            return []

    async def verify_with_llm(
        self,
        suspected_errors: List[Dict[str, Any]],
        context_text: str
    ) -> List[Dict[str, Any]]:
        """Use LLM to verify suspected spelling errors."""
        if not suspected_errors:
            return []

        to_verify = suspected_errors[:20]

        error_list = "\n".join([
            f"- '{e['word']}' (suggested: '{e['correction']}')"
            for e in to_verify
        ])

        prompt = f"""Review these suspected spelling errors in the context below.
For each error, confirm if it is genuinely misspelled.

Context (first 500 chars):
{context_text[:500]}

Suspected errors:
{error_list}

For each word, respond YES (genuine error) or NO (not an error).
Format:
word1: YES/NO
word2: YES/NO"""

        try:
            from app.shared.llm_client import llm_client
            response = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "You are a spelling expert. "
                    "Confirm genuine spelling errors only. "
                    "Consider context carefully."
                ),
                max_tokens=300,
                temperature=0.1
            )

            confirmed = []
            lines = response.strip().split('\n')

            for i, error in enumerate(to_verify):
                word = error['word'].lower()
                for line in lines:
                    if word in line.lower() and ':' in line:
                        verdict = line.split(':')[-1].strip()
                        if 'YES' in verdict.upper():
                            confirmed.append(error)
                        break
                else:
                    confirmed.append(error)

            logger.info(
                f"LLM verification: "
                f"{len(confirmed)}/{len(to_verify)} "
                f"confirmed as real errors"
            )
            return confirmed

        except Exception as e:
            logger.warning(f"LLM verification failed: {e}")
            return suspected_errors

    def merge_results(
        self,
        pyspell_errors: Dict[str, str],
        langtool_errors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge results from both spell checkers."""
        merged = {}

        for word, correction in pyspell_errors.items():
            word_lower = word.lower()
            merged[word_lower] = {
                "word": word,
                "correction": correction,
                "source": "pyspellchecker",
                "confidence": 0.85
            }

        for error in langtool_errors:
            word_lower = error["word"].lower()
            if word_lower not in merged:
                merged[word_lower] = {
                    "word": error["word"],
                    "correction": error["correction"],
                    "source": "languagetool",
                    "confidence": 0.90,
                    "alternatives": error.get("alternatives", [])
                }
            else:
                merged[word_lower]["source"] = "both"
                merged[word_lower]["confidence"] = 0.95

        return list(merged.values())

    async def detect_all(
        self,
        text: str,
        words_with_boxes: Optional[List[Dict]] = None,
        use_llm: bool = True
    ) -> List[Dict[str, Any]]:
        """Run full spell detection pipeline."""
        if not text.strip():
            return []

        word_list = re.findall(r'\b[a-zA-Z]+\b', text)

        pyspell_errors = self.check_with_pyspellchecker(word_list)
        logger.info(
            f"Layer 1 (PySpell): {len(pyspell_errors)} errors"
        )

        langtool_errors = self.check_with_languagetool(text)
        logger.info(
            f"Layer 2 (LangTool): {len(langtool_errors)} errors"
        )

        merged = self.merge_results(pyspell_errors, langtool_errors)

        if use_llm and merged:
            merged = await self.verify_with_llm(merged, text)
            logger.info(
                f"Layer 3 (LLM): {len(merged)} confirmed errors"
            )

        if words_with_boxes:
            merged = self._enrich_with_positions(
                merged, words_with_boxes
            )

        return merged

    def _enrich_with_positions(
        self,
        errors: List[Dict[str, Any]],
        words_with_boxes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Add position info to errors from OCR box data."""
        box_lookup = {}
        for w in words_with_boxes:
            word_lower = w["word"].lower()
            if word_lower not in box_lookup:
                box_lookup[word_lower] = w

        enriched = []
        for error in errors:
            word_lower = error["word"].lower()
            box = box_lookup.get(word_lower, {})
            error_with_pos = {
                **error,
                "x": box.get("x"),
                "y": box.get("y"),
                "width": box.get("width"),
                "height": box.get("height"),
                "page": box.get("page", 1),
                "line": box.get("line")
            }
            enriched.append(error_with_pos)

        return enriched


# Singleton
spell_detector = SpellDetector()
