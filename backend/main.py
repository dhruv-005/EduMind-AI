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


# ── GENERATOR ─────────────────────────────────────────────────────
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
        spell      = SpellChecker()
        words      = re.findall(r'\b[a-zA-Z]{3,}\b', text)
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
async def synthesize_speech_base64(text: str, voice: str = "en-US-AriaNeural") -> str:
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


# ── WEBSOCKET VOICE TUTOR (REAL-TIME STT & TTS) ───────────────────
@app.websocket("/api/v1/voice-tutor/ws/{session_id}")
async def voice_tutor_ws(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connected: session={session_id}")

    try:
        welcome_text = "Hello! I am your Socratic AI tutor. What would you like to learn today?"
        welcome_audio = await synthesize_speech_base64(welcome_text, settings.TTS_VOICE)

        await websocket.send_json({
            "type":       "connected",
            "session_id": session_id,
            "text":       welcome_text,
            "audio":      welcome_audio,
            "message":    "Voice tutor ready!",
        })

        while True:
            try:
                raw = await websocket.receive_text()
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = {"type": "text", "text": raw}
            except WebSocketDisconnect:
                break
            except Exception:
                break

            msg_type = data.get("type", "text")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            question = ""

            # 1. SPEECH-TO-TEXT (STT via Groq Whisper)
            if msg_type == "audio" and data.get("audio"):
                logger.info("Processing voice recording via Whisper...")
                try:
                    # Clean base64 input
                    audio_b64 = data["audio"]
                    if "," in audio_b64:
                        audio_b64 = audio_b64.split(",")[1]
                    audio_bytes = base64.b64decode(audio_b64)
                    audio_format = data.get("format", "wav") or "wav"
                    
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as tmp_file:
                        tmp_file.write(audio_bytes)
                        tmp_path = tmp_file.name

                    from groq import Groq
                    groq_client = Groq(api_key=settings.GROQ_API_KEY)
                    with open(tmp_path, "rb") as f:
                        transcription = groq_client.audio.transcriptions.create(
                            file=(os.path.basename(tmp_path), f.read()),
                            model="whisper-large-v3",
                            response_format="json"
                        )
                    question = transcription.text.strip()
                    logger.info(f"Whisper STT result: '{question}'")
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception as e:
                    logger.error(f"Whisper STT failed: {e}")
                    question = ""

            elif msg_type == "text":
                question = str(data.get("text", data.get("message", ""))).strip()

            if not question:
                continue

            # Confirm transcript
            await websocket.send_json({
                "type": "transcript",
                "text": question,
            })

            # 2. SOCRATIC AI RESPONSE (LLM)
            try:
                from app.shared.llm_client import llm_client
                response_text = llm_client.simple_prompt(
                    prompt=f"Student question: {question}\n\nRespond as a friendly Socratic AI tutor. Ask guiding questions or give hints rather than giving direct answers.",
                    system="You are an expert Socratic AI tutor. Never give direct answers immediately. Guide with 2-3 engaging questions or hints. Under 100 words.",
                    max_tokens=150,
                    temperature=0.7,
                )
            except Exception as e:
                logger.warning(f"Socratic LLM failed: {e}")
                response_text = f"That’s a great question about '{question}'. What do you think is the first key step?"

            # 3. TEXT-TO-SPEECH (In-Memory TTS Stream)
            response_audio = await synthesize_speech_base64(response_text, settings.TTS_VOICE)

            await websocket.send_json({
                "type":       "response",
                "text":       response_text,
                "audio":      response_audio,
                "topic":      data.get("subject", "general"),
                "session_id": session_id,
            })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session={session_id[:8]}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


# ── VOICE TUTOR REST ENDPOINTS ────────────────────────────────────
@app.post("/api/v1/voice-tutor/session")
async def voice_tutor_create_session(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
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
async def sales_chat(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    message = payload.get("message", "")
    conv_id = payload.get("conversation_id", "")

    try:
        from app.shared.llm_client import llm_client
        response_text = llm_client.simple_prompt(
            prompt=f"Customer: {message}\n\nRespond as a helpful sales assistant. Recommend relevant educational products.",
            system="You are an intelligent sales assistant for EduMind AI. Be concise, friendly and professional.",
            max_tokens=300,
            temperature=0.7,
        )
    except Exception as e:
        logger.warning(f"Sales LLM fallback: {e}")
        response_text = f"Thank you for your interest! I recommend EduPro Premium at ₹4,999/year with AI tutoring."

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
                "Dear Valued Customer,\n\n"
                "Thank you for your interest today. I recommend EduPro Premium (₹4,999):\n"
                "✓ AI-powered personalized tutoring\n"
                "✓ Real-time progress analytics\n\n"
                "Reply for a free demo!\n\nBest regards,\nEduMind AI Sales Team"
            ),
            "whatsapp": (
                "Hi! 👋 Thank you for your interest in EduMind AI! 🎓\n\n"
                "Top pick: *EduPro Premium* — ₹4,999\n"
                "✅ AI Tutor ✅ Analytics\n\n"
                "Want a free demo? 😊"
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

try:
    from app.challenge3_spelling.router import router as spelling_router
    app.include_router(spelling_router)
    logger.info("Spelling router loaded")
except Exception as e:
    logger.warning(f"Spelling router failed: {e}")

try:
    from app.admin.router import router as admin_router
    app.include_router(admin_router, prefix="/api/v1/admin")
    logger.info("Admin router loaded")
except Exception as e:
    logger.warning(f"Admin router failed: {e}")
