# Version: 2.0.0
# Prompts for question generation — fixed for clean JSON output

GENERATION_SYSTEM_PROMPT = """You are an expert exam paper setter with 20 years of experience.

CRITICAL RULES — FOLLOW EXACTLY:
1. Return ONLY a valid JSON array
2. Start your response with [ and end with ]
3. Never use markdown, backticks, or code blocks
4. Never add explanations before or after the JSON
5. Use only double quotes for strings
6. Never use backslash in question text — write words in full
7. No trailing commas
8. No comments inside JSON
9. Keep question text clean — no special escape characters"""

GENERATION_PROMPT = """Generate exactly {num_questions} {subject} exam questions.

Grade Level: {grade_level}
Topic: {topic}
Difficulty: {difficulty}
Question Type: {question_type}
Marks per question: {marks}

RULES FOR JSON OUTPUT:
- Write question text naturally without backslashes
- Use plain English — avoid LaTeX or special symbols
- If you need subscript write it in words: CO2 not CO\\2
- If you need superscript write it: x squared not x\\2

Return ONLY this JSON format — nothing else:
[
  {{
    "question_text": "Write the complete question here in plain English",
    "question_type": "short",
    "difficulty": "medium",
    "topic": "specific topic name",
    "marks": 5,
    "estimated_time_minutes": 5,
    "model_answer": "Write the complete model answer here"
  }}
]"""

GENERATION_PROMPT_MCQ = """Generate exactly {num_questions} {subject} MCQ questions.

Grade Level: {grade_level}
Topic: {topic}
Difficulty: {difficulty}
Marks per question: {marks}

RULES FOR JSON OUTPUT:
- Write question text naturally without backslashes
- Use plain English only
- All 4 options must be plausible

Return ONLY this JSON format — nothing else:
[
  {{
    "question_text": "Write the complete question here",
    "question_type": "mcq",
    "difficulty": "medium",
    "topic": "specific topic name",
    "marks": {marks},
    "estimated_time_minutes": 3,
    "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
    "correct_option": 0,
    "model_answer": "The correct answer is A because..."
  }}
]"""

GENERATION_PROMPT_LONG = """Generate exactly {num_questions} {subject} long answer questions.

Grade Level: {grade_level}
Topic: {topic}
Difficulty: {difficulty}
Marks per question: {marks}

RULES FOR JSON OUTPUT:
- Write question text naturally without backslashes
- Use plain English only

Return ONLY this JSON format — nothing else:
[
  {{
    "question_text": "Write the complete detailed question here",
    "question_type": "long",
    "difficulty": "hard",
    "topic": "specific topic name",
    "marks": {marks},
    "estimated_time_minutes": 20,
    "model_answer": "Write the complete detailed model answer covering all key points"
  }}
]"""

GENERATION_PROMPT_NUMERICAL = """Generate exactly {num_questions} {subject} numerical questions.

Grade Level: {grade_level}
Topic: {topic}
Difficulty: {difficulty}
Marks per question: {marks}

RULES FOR JSON OUTPUT:
- Write numbers and formulas in plain text
- Use words instead of symbols where possible
- No backslashes or LaTeX

Return ONLY this JSON format — nothing else:
[
  {{
    "question_text": "Write the complete numerical problem here in plain text",
    "question_type": "numerical",
    "difficulty": "medium",
    "topic": "specific topic name",
    "marks": {marks},
    "estimated_time_minutes": 10,
    "model_answer": "Step 1: ... Step 2: ... Final answer: ..."
  }}
]"""

DEDUP_CHECK_PROMPT = """Are these two questions essentially the same?
Question 1: {q1}
Question 2: {q2}
Answer only: YES or NO"""

ANSWER_GENERATION_PROMPT = """Generate a detailed model answer for this {subject} question.

Question: {question}
Grade Level: {grade_level}
Marks: {marks}

Requirements:
- Complete and accurate answer
- Appropriate detail for marks available
- Clear step-by-step for numerical questions
- Key points for long answers

Return ONLY this JSON:
{{
  "model_answer": "Complete answer here",
  "key_points": ["point 1", "point 2", "point 3"],
  "marking_scheme": "How marks are awarded"
}}"""

PATTERN_ANALYSIS_PROMPT = """Analyze these exam questions and identify patterns.

Questions:
{questions}

Identify:
1. Most common topics
2. Difficulty distribution
3. Question types used
4. Marks distribution

Return ONLY this JSON:
{{
  "recurring_topics": ["topic1", "topic2", "topic3"],
  "difficulty_distribution": {{"easy": 30, "medium": 50, "hard": 20}},
  "question_types": {{"mcq": 40, "short": 35, "long": 15, "numerical": 10}},
  "avg_marks": 5,
  "total_questions_analyzed": 0
}}"""


def get_generation_prompt(config) -> str:
    """Get the appropriate prompt based on question type."""
    question_type = getattr(config, 'question_type', 'mixed')
    num_questions = getattr(config, 'num_questions', 5)
    subject       = getattr(config, 'subject', 'general')
    grade_level   = getattr(config, 'grade_level', 'grade-10')
    topic         = getattr(config, 'topic', '') or subject
    difficulty    = getattr(config, 'difficulty', 'medium')
    marks         = getattr(config, 'marks_per_question', 5)

    params = {
        'num_questions': num_questions,
        'subject':       subject,
        'grade_level':   grade_level,
        'topic':         topic,
        'difficulty':    difficulty,
        'marks':         marks,
    }

    if question_type == 'mcq':
        return GENERATION_PROMPT_MCQ.format(**params)
    elif question_type == 'long':
        return GENERATION_PROMPT_LONG.format(**params)
    elif question_type == 'numerical':
        return GENERATION_PROMPT_NUMERICAL.format(**params)
    else:
        return GENERATION_PROMPT.format(**params)
