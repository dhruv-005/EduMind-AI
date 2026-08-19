# Version: 1.0.0
# Science-specific evaluation prompts

SCIENCE_EVALUATION_PROMPT = """Evaluate this science answer:

Question: {question}
Reference: {reference_answer}
Student: {student_answer}
Grade Level: {grade_level}

Score criteria (0.0-1.0):
- correctness: Scientific facts accurate
- relevance: Correct principles applied
- completeness: Cause-effect explained + all parts addressed
- clarity: Correct terminology + logical structure

JSON response only."""
