import uuid
import time
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.core.logger import logger
from app.challenge2_generator.schemas import GeneratorConfig
from app.challenge2_generator.paper_parser import paper_parser
from app.challenge2_generator.pattern_analyzer import pattern_analyzer
from app.challenge2_generator.question_generator import question_generator
from app.challenge2_generator.deduplicator import deduplicator
from app.challenge2_generator.answer_generator import answer_generator
from app.challenge2_generator.pdf_exporter import pdf_exporter
from app.governance.audit_logger import audit_logger
from app.governance.prompt_versioning import prompt_versioning
from app.models.question import GeneratedQuestion, SourcePaper


class GeneratorService:
    """
    Main service for Challenge 2 - Question Generator.
    Orchestrates: parse → analyze → generate → deduplicate → export.
    """

    async def process_source_paper(
        self,
        file_path: str,
        filename: str,
        subject: str,
        db: Optional[Session] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an uploaded source paper.
        Extract questions and patterns.
        """
        paper_id = str(uuid.uuid4())

        try:
            # Parse the file
            parsed = paper_parser.parse_file(
                file_path=file_path,
                subject=subject
            )

            # Analyze patterns with LLM
            llm_insights = await pattern_analyzer.analyze_with_llm(
                raw_text=parsed["raw_text"],
                subject=subject
            )

            # Save to database
            if db:
                source_paper = SourcePaper(
                    id=paper_id,
                    user_id=user_id,
                    filename=filename,
                    file_path=file_path,
                    subject=subject,
                    raw_text=parsed["raw_text"][:5000],
                    question_count=parsed["question_count"],
                    topics_detected=parsed["topics"],
                    difficulty_distribution=parsed[
                        "difficulty_distribution"
                    ],
                    is_processed=True
                )
                db.add(source_paper)
                db.commit()

            logger.info(
                f"Source paper processed: {filename} "
                f"({parsed['question_count']} questions found)"
            )

            return {
                "paper_id": paper_id,
                "filename": filename,
                "subject": subject,
                "question_count": parsed["question_count"],
                "topics_detected": parsed["topics"],
                "difficulty_distribution": parsed[
                    "difficulty_distribution"
                ],
                "llm_insights": llm_insights,
                "is_processed": True,
                "message": (
                    f"Successfully extracted "
                    f"{parsed['question_count']} questions"
                )
            }

        except Exception as e:
            logger.error(f"Paper processing failed: {e}")
            raise

    async def generate_questions(
        self,
        config: GeneratorConfig,
        db: Optional[Session] = None,
        user_id: Optional[str] = None,
        source_paper_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main generation pipeline.
        Generate, deduplicate, enrich with answers.
        """
        start_time = time.time()
        batch_id = str(uuid.uuid4())
        request_id = str(uuid.uuid4())

        logger.info(
            f"Starting generation: "
            f"subject={config.subject} "
            f"count={config.num_questions} "
            f"batch={batch_id}"
        )

        try:
            # Get pattern context from source papers
            pattern_context = None
            source_questions = []

            if (
                source_paper_id and
                config.use_source_patterns and
                db
            ):
                paper = db.query(SourcePaper).filter(
                    SourcePaper.id == source_paper_id
                ).first()

                if paper:
                    logger.info(
                        f"Using source paper patterns: "
                        f"{source_paper_id}"
                    )
                    # Build context from stored data
                    pattern_context = {
                        "recurring_topics": (
                            paper.topics_detected or []
                        ),
                        "difficulty_distribution": (
                            paper.difficulty_distribution or {}
                        )
                    }

            # Generate questions
            generated = await question_generator.generate_all(
                config=config,
                pattern_context=pattern_context
            )

            if not generated:
                raise Exception(
                    "Question generation returned no results"
                )

            # Deduplicate
            clean_questions, duplicates_removed = (
                deduplicator.remove_duplicates(generated)
            )

            # If we removed duplicates, generate more
            if (
                duplicates_removed > 0 and
                len(clean_questions) < config.num_questions
            ):
                extra_needed = (
                    config.num_questions - len(clean_questions)
                )
                logger.info(
                    f"Generating {extra_needed} extra questions "
                    f"to replace duplicates"
                )
                extra = await question_generator.generate_batch(
                    config=config,
                    pattern_context=pattern_context,
                    batch_size=extra_needed + 2
                )
                # Deduplicate extras against existing
                existing_texts = [
                    q["question_text"] for q in clean_questions
                ]
                for q in extra:
                    is_dup, _ = deduplicator.is_duplicate_of_existing(
                        q["question_text"],
                        existing_texts
                    )
                    if not is_dup:
                        clean_questions.append(q)
                        existing_texts.append(q["question_text"])

            # Take only requested number
            final_questions = clean_questions[:config.num_questions]

            # Generate answers if requested
            if config.include_answers:
                final_questions = (
                    await answer_generator.batch_generate_answers(
                        questions=final_questions,
                        subject=config.subject,
                        grade_level=config.grade_level
                    )
                )

            # Save to database
            if db:
                self._save_questions(
                    db=db,
                    questions=final_questions,
                    batch_id=batch_id,
                    user_id=user_id,
                    config=config
                )

            # Build statistics
            elapsed_ms = (time.time() - start_time) * 1000
            from collections import Counter
            topic_coverage = dict(Counter(
                q.get("topic", "general")
                for q in final_questions
            ))
            difficulty_dist = dict(Counter(
                q.get("difficulty", "medium")
                for q in final_questions
            ))
            type_dist = dict(Counter(
                q.get("question_type", "short")
                for q in final_questions
            ))

            # Get model info from first question
            model_used = "groq"
            provider = "groq"
            if final_questions:
                model_used = final_questions[0].get(
                    "model_used", "llama-3.3-70b"
                )
                provider = final_questions[0].get(
                    "provider", "groq"
                )

            # Audit log
            prompt_version = prompt_versioning.get_version(
                "challenge2_generation"
            )
            audit_logger.log_ai_decision(
                db=db,
                request_id=request_id,
                challenge="challenge2",
                user_id=user_id,
                session_id=None,
                input_summary=(
                    f"subject={config.subject} "
                    f"count={config.num_questions}"
                ),
                model_used=model_used,
                model_version="3.3-70b",
                prompt_version=prompt_version,
                output_summary=(
                    f"generated={len(final_questions)} "
                    f"duplicates_removed={duplicates_removed}"
                ),
                confidence_score=0.85,
                processing_time_ms=elapsed_ms,
                governance_status="passed",
                metadata={
                    "batch_id": batch_id,
                    "duplicates_removed": duplicates_removed
                }
            )

            result = {
                "batch_id": batch_id,
                "request_id": request_id,
                "subject": config.subject,
                "topic": config.topic,
                "total_generated": len(final_questions),
                "duplicates_removed": duplicates_removed,
                "questions": final_questions,
                "topic_coverage": topic_coverage,
                "difficulty_distribution": difficulty_dist,
                "question_type_distribution": type_dist,
                "processing_time_ms": elapsed_ms,
                "model_used": model_used,
                "provider": provider,
                "governance_status": "passed"
            }

            logger.info(
                f"Generation complete: "
                f"batch={batch_id} "
                f"count={len(final_questions)} "
                f"time={elapsed_ms:.0f}ms"
            )

            return result

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Generation failed: batch={batch_id} error={e}"
            )
            raise

    def _save_questions(
        self,
        db: Session,
        questions: List[Dict[str, Any]],
        batch_id: str,
        user_id: Optional[str],
        config: GeneratorConfig
    ):
        """Save generated questions to database."""
        try:
            for q in questions:
                gq = GeneratedQuestion(
                    id=q.get("id", str(uuid.uuid4())),
                    batch_id=batch_id,
                    user_id=user_id,
                    question_text=q["question_text"],
                    question_type=q.get("question_type", "short"),
                    subject=config.subject,
                    topic=q.get("topic"),
                    difficulty=q.get("difficulty", "medium"),
                    marks=q.get("marks", 5),
                    grade_level=config.grade_level,
                    options=q.get("options"),
                    correct_option=q.get("correct_option"),
                    model_answer=q.get("model_answer"),
                    marking_scheme=q.get("marking_scheme"),
                    key_points=q.get("key_points"),
                    is_duplicate=q.get("is_duplicate", False),
                    model_used=q.get("model_used", "groq"),
                    provider=q.get("provider", "groq"),
                    prompt_version=prompt_versioning.get_version(
                        "challenge2_generation"
                    )
                )
                db.add(gq)

            db.commit()
            logger.info(
                f"Saved {len(questions)} questions to DB"
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save questions: {e}")

    async def export_pdf(
        self,
        batch_id: str,
        title: str,
        institution: Optional[str],
        include_answers: bool,
        db: Optional[Session] = None
    ) -> str:
        """Export questions from a batch as PDF."""
        questions = []

        if db:
            db_questions = db.query(GeneratedQuestion).filter(
                GeneratedQuestion.batch_id == batch_id
            ).all()
            questions = [q.to_dict() for q in db_questions]

        if not questions:
            raise Exception(
                f"No questions found for batch: {batch_id}"
            )

        file_path = pdf_exporter.export(
            questions=questions,
            title=title,
            institution=institution,
            include_answers=include_answers,
            batch_id=batch_id,
            subject=questions[0].get("subject", "General")
            if questions else "General"
        )

        return file_path


# Singleton
generator_service = GeneratorService()
