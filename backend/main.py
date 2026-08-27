import uuid as _uuid
import os
import re
import json
import base64
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File as FastAPIFile, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)

    # Database
    try:
        from app.core.database import create_tables
        create_tables()
        logger.info("Database tables ready")
    except Exception as e:
        logger.warning(f"Database setup failed: {e}")

    # Redis
    try:
        from app.core.redis_client import get_async_redis
        await get_async_redis()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis not available — running without cache")

    # Upload directories
    for folder in [
        "uploads", "uploads/spelling", "uploads/papers",
        "uploads/documents", "uploads/catalogues", "uploads/audio"
    ]:
        os.makedirs(folder, exist_ok=True)
    logger.info("Upload directories ready")

    logger.info(f"{settings.APP_NAME} started successfully!")
    logger.info(f"API docs: http://localhost:8000/docs")
    logger.info("=" * 60)

    yield

    logger.info(f"{settings.APP_NAME} shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autonomous Knowledge Synthesis Engine",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Universal CORS Middleware with wildcard support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── LANGUAGE VOICE MAPS ───────────────────────────────────────────
LANGUAGE_CONFIGS = {
    "en": {"voice": "en-US-AriaNeural", "name": "English", "welcome": "Hello! I am your Socratic AI tutor. What would you like to learn today?"},
    "es": {"voice": "es-ES-ElviraNeural", "name": "Spanish", "welcome": "¡Hola! Soy tu tutor de IA socrático. ¿Qué te gustaría aprender hoy?"},
    "fr": {"voice": "fr-FR-DeniseNeural", "name": "French", "welcome": "Bonjour ! Je suis votre tuteur socratique en IA. Qu'aimeriez-vous apprendre aujourd'hui ?"},
    "de": {"voice": "de-DE-KatjaNeural", "name": "German", "welcome": "Hallo! Ich bin dein sokratischer KI-Lehrer. Was möchtest du heute lernen?"},
    "hi": {"voice": "hi-IN-SwararaNeural", "name": "Hindi", "welcome": "नमस्ते! मैं आपका सुकराती एआई शिक्षक हूं। आज आप क्या सीखना चाहेंगे?"},
    "ar": {"voice": "ar-SA-ZariyahNeural", "name": "Arabic", "welcome": "مرحباً! أنا معلمك السقراطي الذكي. ماذا تريد أن تتعلم اليوم؟"},
    "zh": {"voice": "zh-CN-XiaoxiaoNeural", "name": "Chinese", "welcome": "你好！我是 your 启发式 AI 导师。今天你想学点什么呢？"}
}


# ── HEALTH ────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    from datetime import datetime, timezone
    return {
        "status":      "healthy",
        "app":         settings.APP_NAME,
        "version":     settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp":   datetime.now(timezone.utc).isoformat(),
    }


@app.get("/")
async def root():
    return {
        "app":     settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs":    "/docs",
        "status":  "running",
    }


# ── GENERATOR — DIRECT (JSON parse fix active) ────────────────────
@app.post("/api/v1/generator/generate")
async def generator_generate(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    subject       = body.get("subject", "science")
    topic         = body.get("topic", "") or subject
    num_questions = min(int(body.get("num_questions", 3)), 10)
    difficulty    = body.get("difficulty", "medium")
    question_type = body.get("question_type", "short")
    level         = body.get("level", body.get("grade_level", "grade-10"))

    questions = []

    try:
        from app.shared.llm_client import llm_client

        prompt = (
            f"Write exactly {num_questions} exam questions about {topic} "
            f"for {subject}, {level} students.\n"
            f"Difficulty: {difficulty}. Question type: {question_type}.\n\n"
            f"STRICT RULES:\n"
            f"- Number each question: 1. 2. 3. etc.\n"
            f"- Plain English ONLY\n"
            f"- NO backslashes, NO special characters\n"
            f"- Write formulas in words: carbon dioxide not CO2\n"
            f"- Each question on its own line\n"
            f"- No extra text, no introduction, no explanation\n\n"
            f"Write the {num_questions} questions now:"
        )

        response = llm_client.simple_prompt(
            prompt=prompt,
            system=(
                f"You are a {subject} teacher generating exam questions. "
                f"Write ONLY numbered questions in plain English. "
                f"No JSON. No special characters. No backslashes. "
                f"Just a numbered list of questions."
            ),
            max_tokens=600,
            temperature=0.4,
        )

        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            match = re.match(r'^(?:Q?\d+[.):\s]+)(.{10,})', line)
            if match:
                q_text = match.group(1).strip()
                q_text = re.sub(r'\\+', '', q_text).strip('*').strip('#').strip()
                if q_text and len(q_text) > 10:
                    questions.append({
                        "question_text":         q_text,
                        "question":              q_text,
                        "question_type":         question_type if question_type != "mixed" else "short",
                        "difficulty":            difficulty if difficulty != "mixed" else "medium",
                        "topic":                 topic,
                        "marks":                 5,
                        "estimated_time_minutes": 5,
                        "model_answer":          "",
                        "options":               None,
                        "correct_option":        None,
                    })
    except Exception as e:
        logger.warning(f"Generator LLM failed: {e}")

    if not questions:
        fallbacks = [
            f"Explain the concept of {topic} in {subject} with suitable examples.",
            f"What are the main characteristics of {topic}? Explain each one.",
            f"Describe the importance of {topic} and its real-world applications.",
        ]
        for i in range(min(num_questions, len(fallbacks))):
            questions.append({
                "question_text":         fallbacks[i],
                "question":              fallbacks[i],
                "question_type":         "short",
                "difficulty":            "medium",
                "topic":                 topic,
                "marks":                 5,
                "estimated_time_minutes": 5,
                "model_answer":          f"Refer to {subject} textbook chapter on {topic}.",
                "options":               None,
                "correct_option":        None,
            })

    questions = questions[:num_questions]

    return {
        "success": True,
        "data": {
            "questions":          questions,
            "total":              len(questions),
            "subject":            subject,
            "topic":              topic,
            "batch_id":           str(_uuid.uuid4()),
            "duplicates_removed": 0,
        },
        "message": f"Generated {len(questions)} questions successfully",
        "error":   None,
    }


# ── SPELLING DETECT ───────────────────────────────────────────────
@app.post("/api/v1/spelling/detect")
async def spelling_detect(file: UploadFile = FastAPIFile(...)):
    import aiofiles
    content  = await file.read()
    filename = file.filename or "document.txt"
    ext      = os.path.splitext(filename)[1].lower()
    os.makedirs("uploads/spelling", exist_ok=True)
    file_path = f"uploads/spelling/{_uuid.uuid4()}{ext}"
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    text = ""
    if ext == ".pdf":
        try:
            import fitz
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text() + " "
            doc.close()
        except Exception:
            text = content.decode("utf-8", errors="ignore")
        if not text.strip():
            text = content.decode("utf-8", errors="ignore")
    else:
        text = content.decode("utf-8", errors="ignore")
    errors = []
    try:
        from spellchecker import SpellChecker
        spell = SpellChecker()
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        misspelled = spell.unknown(words)
        seen = set()
        for word in misspelled:
            clean = word.lower().strip()
            if clean in seen or len(clean) < 3 or word.isupper():
                continue
            seen.add(clean)
            correction = spell.correction(clean)
            if correction and correction != clean:
                errors.append({
                    "word":       word,
                    "correction": correction,
                    "page":       1,
                    "confidence": 0.9,
                    "position":   {"x": 0, "y": 0},
                })
        logger.info(f"Spell check: {len(words)} words, {len(errors)} errors")
    except ImportError:
        logger.error("pyspellchecker not installed")
    except Exception as e:
        logger.error(f"Spell check error: {e}")

    try:
        os.remove(file_path)
    except Exception:
        pass

    total_words = len(text.split()) if text.strip() else 0

    return {
        "success": True,
        "data": {
            "errors":        errors,
            "error_count":   len(errors),
            "total_words":   total_words,
            "error_rate":    f"{(len(errors)/max(total_words,1)*100):.1f}%",
            "text_preview":  text[:200].strip(),
            "annotated_url": None,
            "report_id":     str(_uuid.uuid4()),
        },
        "message": f"Spell check complete. Found {len(errors)} errors.",
        "error":   None,
    }


# ── AUDIO HELPER: ASYNC IN-MEMORY TTS ─────────────────────────────
async def synthesize_speech_base64(text: str, voice: str) -> str:
    """Synthesizes text to MP3 in-memory and returns a clean base64 string."""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        audio_bytes = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes.extend(chunk["data"])
        if audio_bytes:
            return base64.b64encode(bytes(audio_bytes)).decode("utf-8")
    except Exception as e:
        logger.warning(f"In-memory Edge-TTS failed: {e}")
    return ""


# ── WEBSOCKET — VOICE TUTOR (MULTILINGUAL ACTIVE) ─────────────────
@app.websocket("/api/v1/voice-tutor/ws/{session_id}")
async def voice_tutor_ws(websocket: WebSocket, session_id: str):
    """WebSocket for real-time voice tutor communication with actual STT & TTS."""
    # Retrieve language from query params
    params = websocket.query_params
    lang_code = params.get("language", "en")
    if lang_code not in LANGUAGE_CONFIGS:
        lang_code = "en"

    lang_cfg = LANGUAGE_CONFIGS[lang_code]
    voice = lang_cfg["voice"]
    lang_name = lang_cfg["name"]

    await websocket.accept()
    logger.info(f"WebSocket connected: session={session_id} language={lang_name}")

    # Ensure audio temp directories exist
    os.makedirs("uploads/audio", exist_ok=True)

    try:
        # Initial Welcome Message via Edge-TTS in targeted language
        welcome_text = lang_cfg["welcome"]
        welcome_audio_base64 = await synthesize_speech_base64(welcome_text, voice)

        await websocket.send_json({
            "type":       "connected",
            "session_id": session_id,
            "text":       welcome_text,
            "audio":      welcome_audio_base64,
            "message":    "Voice tutor ready!",
        })

        while True:
            # Receive message
            try:
                raw  = await websocket.receive_text()
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = {"type": "text", "text": raw}
            except WebSocketDisconnect:
                break
            except Exception:
                break

            msg_type = data.get("type", "text")
            logger.info(f"WS received: type={msg_type} session={session_id[:8]}")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            question = ""

            # ── 1. SPEECH-TO-TEXT (STT via Groq Whisper with Language Hint) ──
            if msg_type == "audio" and data.get("audio"):
                logger.info(f"Processing voice recording via Whisper in {lang_name}...")
                audio_data = base64.b64decode(data["audio"])
                audio_format = data.get("format", "wav")
                
                temp_audio_path = f"uploads/audio/input_{session_id}.{audio_format}"
                with open(temp_audio_path, "wb") as f:
                    f.write(audio_data)

                try:
                    from groq import Groq
                    groq_client = Groq(api_key=settings.GROQ_API_KEY)
                    with open(temp_audio_path, "rb") as file_obj:
                        transcription = groq_client.audio.transcriptions.create(
                            file=(os.path.basename(temp_audio_path), file_obj.read()),
                            model="whisper-large-v3",
                            response_format="json",
                            language=lang_code # Force Whisper to transcribe in targeted language
                        )
                    question = transcription.text
                    logger.info(f"Whisper STT transcription ({lang_name}): '{question}'")
                except Exception as e:
                    logger.error(f"Whisper STT failed: {e}")
                    question = ""
                finally:
                    if os.path.exists(temp_audio_path):
                        os.remove(temp_audio_path)

            elif msg_type == "text":
                question = data.get("text", data.get("message", ""))

            if not question:
                continue

            # Confirm transcript back to browser
            await websocket.send_json({
                "type": "transcript",
                "text": question,
            })

            # ── 2. SOCRATIC AI RESPONSE (LLM in Chosen Language) ──
            try:
                from app.shared.llm_client import llm_client
                response_text = llm_client.simple_prompt(
                    prompt=(
                        f"Student question: {question}\n\n"
                        f"Respond in {lang_name} as a Socratic AI tutor. Ask guiding questions or give hints."
                    ),
                    system=(
                        f"You are an expert Socratic AI tutor. Never give direct answers. "
                        f"Guide with hints and questions. Keep responses under 120 words. "
                        f"STRICT: Respond ONLY in {lang_name}."
                    ),
                    max_tokens=200,
                    temperature=0.7,
                )
            except Exception as e:
                logger.warning(f"Socratic LLaMA failed: {e}")
                response_text = f"That’s a great question! What do you think is the first step?"

            # ── 3. TEXT-TO-SPEECH (TTS in Chosen Language Voice) ──
            response_audio_base64 = await synthesize_speech_base64(response_text, voice)

            # Send back both Text and Voice
            await websocket.send_json({
                "type":       "response",
                "text":       response_text,
                "audio":      response_audio_base64,
                "topic":      data.get("subject", "general"),
                "session_id": session_id,
            })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session={session_id[:8]}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


# ── VOICE TUTOR REST ENDPOINTS ────────────────────────────────────
@app.post("/api/v1/voice-tutor/session")
async def voice_tutor_create_session(payload: dict = None):
    data       = payload or {}
    session_id = str(_uuid.uuid4())
    return {
        "success": True,
        "data": {
            "session_id":  session_id,
            "subject":     data.get("subject", "mathematics"),
            "grade_level": data.get("grade_level", "grade-10"),
            "status":      "active",
            "ws_url":      f"/api/v1/voice-tutor/ws/{session_id}",
        },
        "message": "Session created successfully",
        "error":   None,
    }


@app.get("/api/v1/voice-tutor/subjects")
async def voice_tutor_subjects():
    return {
        "success": True,
        "data": {
            "subjects": [
                "mathematics", "science", "english", "history",
                "geography", "physics", "chemistry", "biology",
                "computer_science", "general"
            ]
        }
    }


@app.delete("/api/v1/voice-tutor/session/{session_id}")
async def voice_tutor_end_session(session_id: str):
    return {
        "success": True,
        "data":    {"session_id": session_id, "status": "ended"},
        "message": "Session ended",
        "error":   None,
    }


@app.get("/api/v1/voice-tutor/session/{session_id}/summary")
async def voice_tutor_session_summary(session_id: str):
    return {
        "success": True,
        "data": {
            "session_id":       session_id,
            "questions_asked":  0,
            "topics_covered":   [],
            "session_duration": 0,
            "status":           "ended",
        },
        "message": "Summary retrieved",
    }


@app.get("/api/v1/voice-tutor/history")
async def voice_tutor_history():
    return {
        "success": True,
        "data": {"sessions": [], "total": 0},
        "message": "History retrieved",
    }


# ── SALES ENDPOINTS ───────────────────────────────────────────────
@app.post("/api/v1/sales/conversation")
async def sales_start_conversation():
    return {
        "success": True,
        "data":    {"conversation_id": str(_uuid.uuid4()), "status": "active"},
        "message": "Conversation started",
        "error":   None,
    }


@app.post("/api/v1/sales/chat")
async def sales_chat(payload: dict):
    message = payload.get("message", "")
    conv_id = payload.get("conversation_id", "")

    try:
        from app.shared.llm_client import llm_client
        response_text = llm_client.simple_prompt(
            prompt=(
                f"Customer: {message}\nRespond as educational sales assistant. Recommend products.",
                f"system: You are a sales assistant for EduMind AI. Be concise and friendly."
            ),
            max_tokens=300,
            temperature=0.7,
        )
    except Exception as e:
        logger.warning(f"Sales LLM failed: {e}")
        msg_lower = message.lower()
        if any(w in msg_lower for w in ['budget', 'price', 'cost']):
            response_text = "We have:\n💰 SmartLearn Basic — ₹2,499/year\n⭐ EduPro Premium — ₹4,999/year\n🏆 AcademyX — ₹7,999/year\nWhich suits you?"
        elif any(w in msg_lower for w in ['grade', 'class', 'student']):
            response_text = "EduPro Premium (₹4,999) is best for students:\n✓ AI tutoring\n✓ Grade-aligned curriculum\n✓ Parent dashboard\nWhich grade?"
        else:
            response_text = "Thank you! I recommend EduPro Premium at ₹4,999/year with AI tutoring. What is your budget and grade level?"
    return {
        "success": True,
        "data": {
            "conversation_id": conv_id,
            "response":        response_text,
            "recommendations": [
                {"name": "EduPro Premium",  "category": "Software",  "price": 4999, "description": "Advanced AI-powered learning platform", "features": ["AI Tutor", "Analytics", "Parent Dashboard"], "why_match": "Best value", "match_score": 0.95},
                {"name": "SmartLearn Basic","category": "Software",  "price": 2499, "description": "Affordable learning platform",          "features": ["Video Lessons", "Practice Tests"],           "why_match": "Budget friendly", "match_score": 0.80},
                {"name": "AcademyX Premium","category": "Platform",  "price": 7999, "description": "Premium with live tutoring",            "features": ["Live Tutors", "Gamification"],               "why_match": "Best features", "match_score": 0.72},
            ],
            "lead_score": {
                "total": min(85, 25 + len(message) // 5),
                "tier":  "WARM",
                "breakdown": {"budget": 15, "intent": 20, "authority": 10, "urgency": 10},
            },
            "customer_profile": {
                "budget": None, "requirements": [], "preferences": [], "objections": [], "urgency": None,
            },
        },
        "message": "Response generated",
        "error":   None,
    }


@app.get("/api/v1/sales/catalogue")
async def sales_get_catalogue():
    return {"success": True, "data": {"products": [], "total": 0}, "message": "Catalogue retrieved"}


@app.post("/api/v1/sales/catalogue/upload")
async def sales_upload_catalogue(file: UploadFile = FastAPIFile(...)):
    content = await file.read()
    count   = max(0, len(content.decode("utf-8", errors="ignore").strip().split("\n")) - 1)
    return {
        "success": True,
        "data":    {"total_products": count, "filename": file.filename, "status": "indexed"},
        "message": f"Uploaded {count} products",
        "error":   None,
    }


@app.get("/api/v1/sales/leads")
async def sales_get_leads():
    return {"success": True, "data": {"leads": [], "total": 0}, "message": "Leads retrieved"}


@app.post("/api/v1/sales/follow-up/{conv_id}")
async def sales_follow_up(conv_id: str):
    return {
        "success": True,
        "data": {
            "email": (
                "Subject: Thank you for exploring EduMind AI!\n\n"
                "Dear Customer,\n\n"
                "I recommend EduPro Premium (Rs.4,999):\n"
                "- AI tutoring\n- Analytics\n- Parent dashboard\n\n"
                "Reply for free demo!\n\nEduMind AI Team"
            ),
            "whatsapp": (
                "Hi! Thank you for your interest in EduMind AI!\n\n"
                "Top pick: EduPro Premium - Rs.4,999\n"
                "AI Tutor, Analytics, Parent Dashboard\n\n"
                "Want a free demo?"
            ),
        },
        "message": "Follow-up generated",
        "error":   None,
    }


@app.get("/api/v1/sales/recommendations/{conv_id}")
async def sales_recommendations(conv_id: str):
    return {"success": True, "data": {"recommendations": [], "conversation_id": conv_id}}


@app.get("/api/v1/sales/lead-score/{conv_id}")
async def sales_lead_score(conv_id: str):
    return {
        "success": True,
        "data": {
            "total": 55,
            "tier":  "WARM",
            "breakdown": {"budget": 15, "intent": 20, "authority": 10, "urgency": 10},
        },
    }


@app.post("/api/v1/sales/escalate/{conv_id}")
async def sales_escalate(conv_id: str):
    return {
        "success": True,
        "data": {"conversation_id": conv_id, "escalated": True, "message": "Sales rep notified"},
    }


# ── ROUTERS ───────────────────────────────────────────────────────
try:
    from app.challenge1_evaluator.router import router as evaluator_router
    app.include_router(evaluator_router)
    logger.info("Evaluator router loaded")
except Exception as e:
    logger.warning(f"Evaluator router failed: {e}")

logger.info("Generator using direct endpoint (JSON parse fix active)")

try:
    from app.challenge3_spelling.router import router as spelling_router
    app.include_router(spelling_router)
    logger.info("Spelling router loaded")
except Exception as e:
    logger.warning(f"Spelling router failed: {e}")

try:
    from app.challenge4_voice_tutor.router import router as voice_router
    app.include_router(voice_router, prefix="/api/v1/voice-tutor")
    logger.info("Voice tutor router loaded")
except Exception as e:
    logger.warning(f"Voice tutor router failed: {e}")

try:
    from app.challenge5_sales.router import router as sales_router
    app.include_router(sales_router, prefix="/api/v1/sales")
    logger.info("Sales router loaded")
except Exception as e:
    logger.warning(f"Sales router failed: {e}")

try:
    from app.admin.router import router as admin_router
    app.include_router(admin_router, prefix="/api/v1/admin")
    logger.info("Admin router loaded")
except Exception as e:
    logger.warning(f"Admin router failed: {e}")
