import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # APP
    APP_NAME: str = "EduMind AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # DATABASE
    DATABASE_URL: str = "sqlite:///./edumind.db"

    # REDIS
    REDIS_URL: str = "redis://localhost:6379"

    # SECURITY
    SECRET_KEY: str = "edumind-secret-key-2024"
    JWT_SECRET: str = "edumind-jwt-secret-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080

    # LLM
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama3-70b-8192"
    GROQ_WHISPER_MODEL: str = "whisper-large-v3"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    TOGETHER_API_KEY: str = ""
    TOGETHER_MODEL: str = "meta-llama/Llama-3-70b-chat-hf"
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return ["http://localhost:3000", "http://localhost:5173"]
            if v.startswith("["):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [
                o.strip().strip('"').strip("'")
                for o in v.split(",")
                if o.strip()
            ]
        return ["http://localhost:3000", "http://localhost:5173"]

    # FILES
    MAX_UPLOAD_SIZE: int = 20971520
    MAX_FILE_SIZE_MB: int = 20
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: List[str] = [
        "pdf", "docx", "doc", "jpg",
        "jpeg", "png", "csv", "json", "xlsx", "txt"
    ]

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_extensions(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [e.strip() for e in v.split(",") if e.strip()]
        return ["pdf", "docx", "jpg", "jpeg", "png", "csv", "json", "xlsx", "txt"]

    # EMBEDDING
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # CHROMADB — all possible attribute names
    CHROMA_DB_PATH: str = "./chroma_db"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    CHROMA_COLLECTION_QUESTIONS: str = "exam_questions"
    CHROMA_COLLECTION_PRODUCTS: str = "products_catalogue"

    # SPACY
    SPACY_MODEL: str = "en_core_web_sm"

    # RATE LIMITING
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 5000

    # TTS
    TTS_VOICE: str = "en-US-AriaNeural"
    TTS_RATE: str = "+0%"
    TTS_VOLUME: str = "+0%"

    # VAD
    VAD_THRESHOLD: float = 0.5
    VAD_SAMPLING_RATE: int = 16000

    # GOVERNANCE
    CONFIDENCE_THRESHOLD: float = 0.6
    FLAG_LOW_CONFIDENCE: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 90
    ENABLE_BIAS_DETECTION: bool = True
    ENABLE_CONTENT_FILTER: bool = True

    # EVALUATOR
    MAX_SCORE: int = 10
    SIMILARITY_WEIGHT: float = 0.4
    LLM_WEIGHT: float = 0.6

    # GENERATOR
    MAX_QUESTIONS_PER_REQUEST: int = 50
    DEDUP_SIMILARITY_THRESHOLD: float = 0.85

    # SALES
    MAX_RECOMMENDATIONS: int = 3
    MIN_LEAD_SCORE_FOR_ESCALATION: int = 75


settings = Settings()
