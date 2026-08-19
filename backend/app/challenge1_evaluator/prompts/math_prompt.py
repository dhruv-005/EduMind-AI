# Version: 1.0.0
# Math-specific evaluation prompts

MATH_EVALUATION_PROMPT = """Evaluate this mathematics answer:

Question: {question}
Reference: {reference_answer}
Student: {student_answer}
Grade Level: {grade_level}

Score criteria (0.0-1.0):
- correctness: Final answer correct + formula correct
- relevance: Right method/approach used
- completeness: All steps shown + units included
- clarity: Work clearly presented

JSON response only."""

MATH_FEEDBACK_PROMPT = """As a math teacher, give feedback for score {score}/10:
- What was done correctly (formulas, steps)
- What was wrong or missing
- How to improve
Keep it encouraging and specific."""
