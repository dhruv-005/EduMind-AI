# Version: 1.0.0
# Prompts for extracting questions from source papers

EXTRACTION_SYSTEM_PROMPT = """You are an expert exam paper analyst.
Extract and categorize questions from exam paper text.
Always respond with valid JSON."""

EXTRACTION_PROMPT = """Extract all questions from this exam paper text.

Subject: {subject}
Paper Text: {text}

For each question identify:
- question number
- question text
- marks
- question type (mcq/short/long/numerical)
- difficulty (easy/medium/hard)
- topic

Return JSON array of questions."""

PATTERN_ANALYSIS_PROMPT = """Analyze this exam paper and identify patterns.

Subject: {subject}
Paper Text: {text}

Identify:
1. Most frequent topics
2. Difficulty distribution
3. Question type distribution
4. Total marks

Return JSON with analysis."""
