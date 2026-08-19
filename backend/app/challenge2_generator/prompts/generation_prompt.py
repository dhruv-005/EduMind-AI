# Version: 1.0.0
# Prompts for question generation

GENERATION_SYSTEM_PROMPT = """You are an expert exam paper setter
with 20 years of experience creating educational assessments.
Generate high-quality, fair, and educationally valid questions.
Always respond with valid JSON array."""

GENERATION_PROMPT = """Generate {num_questions} {subject} exam questions.

Grade Level: {grade_level}
Topic: {topic}
Difficulty: {difficulty}
Question Type: {question_type}
Marks per question: {marks}

Requirements:
- Clear and unambiguous questions
- Appropriate for grade level
- Cover different aspects
- No repetition

Return JSON array only."""

DEDUP_CHECK_PROMPT = """Are these two questions essentially the same question?
Question 1: {q1}
Question 2: {q2}
Answer only: YES or NO"""
