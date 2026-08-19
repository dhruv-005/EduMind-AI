import uuid
import time
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.logger import logger
from app.challenge3_spelling.ocr_engine import ocr_engine
from app.challenge3_spelling.spell_detector import spell_detector
from app.challenge3_spelling.smart_filter import smart_filter
from app.challenge3_spelling.pdf_annotator import pdf_annotator
from app.challenge3_spelling.image_annotator import image_annotator
from app.challenge3_spelling.report_generator import report_generator
from app.governance.audit_logger import audit_logger
from app.governance.human_oversight import human_oversight
from app.models.spelling_report import SpellingReport


class SpellingService:
    """
    Main service for Challenge 3 - Spelling Error Detection.
    Orchestrates: extract → detect → filter → annotate → report.
    """

    def _is_pdf(self, file_path: str) -> bool:
        return Path(file_path).suffix.lower() == ".pdf"

    def _is_image(self, file_path: str) -> bool:
        return Path(file_path).suffix.lower() in [
            ".jpg", ".jpeg", ".png"
        ]

    def _count_words(self, text: str) -> int:
        """Count words in text."""
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        return len(words)

    async def check_document(
        self,
        file_path: str,
        filename: str,
        language: str = "en",
        skip_proper_nouns: bool = True,
        skip_technical: bool = True,
        domain: str = "general",
        db: Optional[Session] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main spell check pipeline for uploaded documents.
        Returns complete report with annotations.
        """
        start_time = time.time()
        report_id = str(uuid.uuid4())
        request_id = str(uuid.uuid4())

        logger.info(
            f"Starting spell check: "
            f"file={filename} "
            f"report_id={report_id}"
        )

        # Determine file type
        file_type = (
            "pdf" if self._is_pdf(file_path)
            else "image"
        )

        ocr_used = False
        ocr_confidence = None
        words_with_boxes = []
        full_text = ""
        page_count = 1

        try:
            # STEP 1: Extract text and word positions
            if self._is_pdf(file_path):
                page_count = pdf_annotator.get_page_count(
                    file_path
                )

                if pdf_annotator.has_text_layer(file_path):
                    # Text PDF - extract directly
                    logger.info("PDF has text layer - direct extraction")
                    words_with_boxes = (
                        pdf_annotator.extract_text_with_positions(
                            file_path
                        )
                    )
                    full_text = " ".join(
                        w["word"] for w in words_with_boxes
                    )
                else:
                    # Scanned PDF - use OCR
                    logger.info("Scanned PDF - using OCR")
                    ocr_used = True
                    words_with_boxes = (
                        ocr_engine.extract_from_pdf_pages(
                            file_path,
                            lang=language
                        )
                    )
                    full_text = " ".join(
                        w["word"] for w in words_with_boxes
                    )
                    ocr_confidence = (
                        ocr_engine.get_overall_confidence(
                            words_with_boxes
                        )
                    )

            elif self._is_image(file_path):
                # Image file - always use OCR
                logger.info("Image file - using OCR")
                ocr_used = True
                words_with_boxes = (
                    ocr_engine.extract_text_with_boxes(
                        file_path,
                        lang=language
                    )
                )
                full_text = " ".join(
                    w["word"] for w in words_with_boxes
                )
                ocr_confidence = (
                    ocr_engine.get_overall_confidence(
                        words_with_boxes
                    )
                )

            if not full_text.strip():
                raise Exception(
                    "No text could be extracted from the file"
                )

            total_words = self._count_words(full_text)
            logger.info(
                f"Extracted {total_words} words, "
                f"OCR used: {ocr_used}"
            )

            # STEP 2: Detect spelling errors
            raw_errors = await spell_detector.detect_all(
                text=full_text,
                words_with_boxes=words_with_boxes,
                use_llm=True
            )
            logger.info(
                f"Raw errors detected: {len(raw_errors)}"
            )

            # STEP 3: Smart filter
            filtered_errors, skipped_words = (
                smart_filter.filter_errors(
                    errors=raw_errors,
                    full_text=full_text,
                    domain=domain,
                    skip_proper_nouns=skip_proper_nouns,
                    skip_technical=skip_technical
                )
            )
            logger.info(
                f"After filtering: {len(filtered_errors)} errors"
            )

            # STEP 4: Annotate document
            annotated_path = None
            try:
                if self._is_pdf(file_path):
                    annotated_path = pdf_annotator.annotate_pdf(
                        pdf_path=file_path,
                        errors=filtered_errors
                    )
                elif self._is_image(file_path):
                    annotated_path = image_annotator.annotate_image(
                        image_path=file_path,
                        errors=filtered_errors
                    )
                    if annotated_path and filtered_errors:
                        image_annotator.draw_summary_panel(
                            annotated_path,
                            len(filtered_errors),
                            total_words
                        )
                        image_annotator.create_error_legend(
                            annotated_path
                        )

            except Exception as e:
                logger.warning(
                    f"Annotation failed (non-critical): {e}"
                )

            # STEP 5: Check governance - human oversight
            should_review, review_reason = (
                human_oversight.should_trigger_review(
                    challenge="challenge3",
                    metadata={
                        "ocr_confidence": (
                            ocr_confidence or 1.0
                        )
                    }
                )
            )
            if should_review:
                human_oversight.add_to_review_queue(
                    challenge="challenge3",
                    request_id=request_id,
                    reason=review_reason,
                    content={
                        "filename": filename,
                        "ocr_confidence": ocr_confidence
                    },
                    priority="normal",
                    user_id=user_id
                )

            # STEP 6: Build report
            elapsed_ms = (time.time() - start_time) * 1000

            report = report_generator.build_report(
                errors=filtered_errors,
                skipped_words=skipped_words,
                total_words=total_words,
                original_filename=filename,
                file_type=file_type,
                page_count=page_count,
                ocr_used=ocr_used,
                ocr_confidence=ocr_confidence,
                processing_time_ms=elapsed_ms,
                report_id=report_id,
                request_id=request_id,
                annotated_file_path=annotated_path
            )

            # STEP 7: Save to database
            if db:
                self._save_report(
                    db=db,
                    report=report,
                    user_id=user_id,
                    file_path=file_path
                )

            # STEP 8: Audit log
            audit_logger.log_ai_decision(
                db=db,
                request_id=request_id,
                challenge="challenge3",
                user_id=user_id,
                session_id=None,
                input_summary=f"file={filename}",
                model_used="pyspellchecker+languagetool+llm",
                model_version="1.0",
                prompt_version="1.0.0",
                output_summary=(
                    f"errors={len(filtered_errors)} "
                    f"words={total_words} "
                    f"ocr={ocr_used}"
                ),
                confidence_score=(
                    ocr_confidence if ocr_used else 1.0
                ),
                processing_time_ms=elapsed_ms,
                governance_status="passed",
                metadata={
                    "ocr_used": ocr_used,
                    "human_review": should_review
                }
            )

            logger.info(
                f"Spell check complete: "
                f"errors={len(filtered_errors)} "
                f"time={elapsed_ms:.0f}ms"
            )

            return report

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Spell check failed: "
                f"file={filename} error={e}"
            )
            raise

    def _save_report(
        self,
        db: Session,
        report: Dict[str, Any],
        user_id: Optional[str],
        file_path: str
    ):
        """Save spelling report to database."""
        try:
            sr = SpellingReport(
                id=str(uuid.uuid4()),
                request_id=report["request_id"],
                user_id=user_id,
                original_filename=report["original_filename"],
                file_type=report["file_type"],
                file_path=file_path,
                annotated_file_path=report.get(
                    "annotated_file_path"
                ),
                page_count=report["summary"]["pages_checked"],
                total_words=report["summary"]["total_words"],
                total_errors=report["summary"]["total_errors"],
                error_rate=report["summary"]["error_rate"],
                errors=report["errors"][:100],
                skipped_words=report["skipped_words"],
                skipped_count=report["summary"]["skipped_count"],
                ocr_used=report["summary"]["ocr_used"],
                ocr_confidence=report["summary"]["ocr_confidence"],
                processing_time_ms=report["metadata"][
                    "processing_time_ms"
                ],
                governance_status=report["metadata"][
                    "governance_status"
                ],
                human_verification_required=report["metadata"][
                    "human_verification_required"
                ]
            )
            db.add(sr)
            db.commit()
            logger.info(
                f"Spelling report saved: {sr.id}"
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save report: {e}")

    async def check_text(
        self,
        text: str,
        language: str = "en",
        skip_proper_nouns: bool = True,
        skip_technical: bool = True
    ) -> Dict[str, Any]:
        """Quick spell check for plain text input."""
        report_id = str(uuid.uuid4())
        start_time = time.time()

        raw_errors = await spell_detector.detect_all(
            text=text,
            use_llm=True
        )

        filtered, skipped = smart_filter.filter_errors(
            errors=raw_errors,
            full_text=text,
            skip_proper_nouns=skip_proper_nouns,
            skip_technical=skip_technical
        )

        total_words = self._count_words(text)
        elapsed_ms = (time.time() - start_time) * 1000

        return {
            "report_id": report_id,
            "total_words": total_words,
            "total_errors": len(filtered),
            "error_rate": self._count_words(text) and
                len(filtered) / total_words or 0,
            "errors": filtered,
            "skipped_words": skipped,
            "processing_time_ms": elapsed_ms
        }


# Singleton
spelling_service = SpellingService()
