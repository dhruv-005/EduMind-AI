# EduMind AI Governance Policy

Version: 1.0.0 | Date: 2024

## Overview

EduMind AI operates under a 7-pillar governance framework ensuring safe, fair, transparent, and accountable AI operations.

## The 7 Pillars

### Pillar 1: Content Safety
- All inputs filtered for harmful content
- All outputs scanned before delivery
- Prompt injection detection active
- Jailbreak attempt detection active

### Pillar 2: Audit Trail
- Every AI decision logged with unique request ID
- Logs retained for 90 days
- Input data hashed for privacy
- Model version tracked for every call

### Pillar 3: Human Oversight
- Low-confidence evaluations flagged for teacher review
- Hot leads (score >= 85) notify human sales rep
- Student distress signals escalate to counselor
- Admin dashboard for review queue management

### Pillar 4: Bias Detection
- Gender bias checking on all outputs
- Cultural bias detection active
- Stereotype detection enabled
- Evaluation score fairness monitoring

### Pillar 5: Rate Limiting
- Per-IP: 100 requests/hour
- Per-User: 500 requests/day
- Burst protection: 10 requests/second max
- Auto-block suspicious patterns

### Pillar 6: Data Privacy
- Voice audio deleted after transcription
- PDF documents deleted after processing
- Student answers not stored permanently
- GDPR-inspired data retention policies

### Pillar 7: Model Versioning and Fallback
- Primary: Groq LLaMA 3.3 70B
- Fallback 1: Google Gemini 1.5 Flash
- Fallback 2: Together AI LLaMA
- Fallback 3: Local Ollama
- All model switches logged in audit trail

## Incident Response

If an AI governance violation is detected:
1. Request is blocked or flagged
2. Incident logged to audit trail
3. Admin notified if severity is high
4. Human review queue updated
5. Incident reviewed within 24 hours

## Contact

For governance concerns: governance@edumind.ai
