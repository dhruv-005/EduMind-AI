# Version: 1.0.0
# Hint generation prompts

BROAD_HINT_PROMPT = """Give a broad hint for this question.
Ask a guiding question. Do NOT give the answer.
Be encouraging. Max 2 sentences.

Question: {question}
Student attempt: {attempt}"""

SPECIFIC_HINT_PROMPT = """Give a specific hint.
Point to the exact concept or formula.
Still don't reveal the full answer.
Max 3 sentences.

Question: {question}
Student attempt: {attempt}"""

DIRECT_ANSWER_PROMPT = """The student has tried multiple times.
Now explain the complete answer clearly.
Show steps and explain why. Be encouraging.
Max 5 sentences.

Question: {question}"""

SOCRATIC_QUESTION_PROMPT = """Generate ONE Socratic follow-up question.
Build on what the student said.
Deepen their understanding.
Be curious and encouraging.

Student said: {student_response}
Topic: {topic}"""
