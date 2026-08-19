# Version: 1.0.0
# General evaluation prompts

GENERAL_EVALUATION_PROMPT = """Evaluate this answer:

Question: {question}
Reference: {reference_answer}
Student: {student_answer}
Grade Level: {grade_level}

Score criteria (0.0-1.0):
- correctness: Key facts correct
- relevance: Relevant to question
- completeness: All key points covered
- clarity: Clearly and logically presented

JSON response only."""
