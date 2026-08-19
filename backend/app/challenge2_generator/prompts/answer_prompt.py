# Version: 1.0.0
# Prompts for answer and marking scheme generation

ANSWER_SYSTEM_PROMPT = """You are an expert teacher creating
model answers and marking schemes for exam questions.
Answers should be comprehensive and appropriate for the grade level."""

ANSWER_PROMPT = """Generate a model answer for this question:

Subject: {subject}
Grade Level: {grade_level}
Question: {question}
Marks: {marks}
Difficulty: {difficulty}

Provide:
1. Complete model answer
2. Key marking points
3. Marking scheme

Format:
MODEL_ANSWER: [answer]
KEY_POINTS:
- [point 1 - X marks]
MARKING_SCHEME: [distribution]"""

MCQ_OPTIONS_PROMPT = """Generate 4 MCQ options for:
Question: {question}
Correct Answer: {correct_answer}

Make 3 plausible distractors.
Format:
A) [correct]
B) [distractor 1]
C) [distractor 2]
D) [distractor 3]
CORRECT: A"""
