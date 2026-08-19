# Subject Types
SUBJECT_MATH = "mathematics"
SUBJECT_SCIENCE = "science"
SUBJECT_ENGLISH = "english"
SUBJECT_GENERAL = "general"

VALID_SUBJECTS = [
    SUBJECT_MATH,
    SUBJECT_SCIENCE,
    SUBJECT_ENGLISH,
    SUBJECT_GENERAL
]

# Difficulty Levels
DIFFICULTY_EASY = "easy"
DIFFICULTY_MEDIUM = "medium"
DIFFICULTY_HARD = "hard"
DIFFICULTY_MIXED = "mixed"

VALID_DIFFICULTIES = [
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    DIFFICULTY_HARD,
    DIFFICULTY_MIXED
]

# Question Types
QUESTION_MCQ = "mcq"
QUESTION_SHORT = "short"
QUESTION_LONG = "long"
QUESTION_NUMERICAL = "numerical"

VALID_QUESTION_TYPES = [
    QUESTION_MCQ,
    QUESTION_SHORT,
    QUESTION_LONG,
    QUESTION_NUMERICAL
]

# Score Ranges
SCORE_MAX = 100
SCORE_MIN = 0

# Grade thresholds
GRADE_A_PLUS = 90
GRADE_A = 80
GRADE_B = 70
GRADE_C = 60
GRADE_D = 50

def get_grade(score: float) -> str:
    """Get letter grade from score."""
    if score >= GRADE_A_PLUS:
        return "A+"
    elif score >= GRADE_A:
        return "A"
    elif score >= GRADE_B:
        return "B"
    elif score >= GRADE_C:
        return "C"
    elif score >= GRADE_D:
        return "D"
    else:
        return "F"

# Lead Score Categories
LEAD_HOT = "hot"
LEAD_WARM = "warm"
LEAD_COOL = "cool"
LEAD_COLD = "cold"

def get_lead_category(score: int) -> str:
    """Get lead category from score."""
    if score >= 80:
        return LEAD_HOT
    elif score >= 60:
        return LEAD_WARM
    elif score >= 40:
        return LEAD_COOL
    else:
        return LEAD_COLD

# File Types
ALLOWED_DOC_TYPES = [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"]
ALLOWED_DATA_TYPES = [".csv", ".json", ".xlsx"]

# Voice Tutor
VAD_THRESHOLD = 0.5
SILENCE_DURATION_MS = 1500
MAX_AUDIO_DURATION_S = 30
MIN_AUDIO_DURATION_S = 0.5

# Governance
CONTENT_BLOCKED = "blocked"
CONTENT_FLAGGED = "flagged"
CONTENT_PASSED = "passed"

# Cache TTL (seconds)
CACHE_TTL_SHORT = 300       # 5 minutes
CACHE_TTL_MEDIUM = 3600     # 1 hour
CACHE_TTL_LONG = 86400      # 24 hours

# Supported Languages
SUPPORTED_LANGUAGES = ["en", "hi", "ar"]
DEFAULT_LANGUAGE = "en"

# LLM Models
LLM_PRIMARY = "llama-3.3-70b-versatile"
LLM_FALLBACK1 = "gemini-1.5-flash"
LLM_FALLBACK2 = "meta-llama/Llama-3-70b-chat-hf"
LLM_LOCAL = "llama3"

# Providers
PROVIDER_GROQ = "groq"
PROVIDER_GEMINI = "gemini"
PROVIDER_TOGETHER = "together"
PROVIDER_OLLAMA = "ollama"
