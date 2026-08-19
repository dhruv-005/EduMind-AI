# Version: 1.0.0
# English-specific evaluation prompts

ENGLISH_EVALUATION_PROMPT = """Evaluate this English answer:

Question: {question}
Reference: {reference_answer}
Student: {student_answer}
Grade Level: {grade_level}

Score criteria (0.0-1.0):
- correctness: Content/interpretation correct
- relevance: Addresses the specific question
- completeness: All points covered with evidence
- clarity: Grammar correct + well-structured argument

JSON response only."""
