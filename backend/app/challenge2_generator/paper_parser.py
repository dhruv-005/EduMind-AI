import re
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from app.core.logger import logger
from app.core.exceptions import FileProcessingException


class PaperParser:
    """
    Parse uploaded exam papers (PDF/Word/Image).
    Extract questions, marks, topics from source papers.
    """

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file.
        Tries PyMuPDF first, then pdfplumber as fallback.
        """
        text = ""

        # Try PyMuPDF first
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()

            if text.strip():
                logger.info(
                    f"PDF text extracted with PyMuPDF: "
                    f"{len(text)} chars"
                )
                return text
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {e}")

        # Fallback to pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            if text.strip():
                logger.info(
                    f"PDF text extracted with pdfplumber: "
                    f"{len(text)} chars"
                )
                return text
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")

        # Try OCR as last resort
        logger.info("Trying OCR for PDF...")
        return self._ocr_pdf(file_path)

    def _ocr_pdf(self, file_path: str) -> str:
        """OCR a PDF by converting to images first."""
        try:
            from pdf2image import convert_from_path
            import pytesseract
            from PIL import Image

            images = convert_from_path(file_path, dpi=200)
            text = ""
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(
                    image,
                    config='--psm 6'
                )
                text += page_text + "\n"
                logger.debug(f"OCR page {i+1}: {len(page_text)} chars")

            return text
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""

    def extract_text_from_image(self, file_path: str) -> str:
        """Extract text from image using OCR."""
        try:
            import pytesseract
            from PIL import Image
            import cv2
            import numpy as np

            # Preprocess image for better OCR
            img = cv2.imread(file_path)
            if img is None:
                raise FileProcessingException(
                    f"Cannot read image: {file_path}"
                )

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray)

            # Threshold
            _, thresh = cv2.threshold(
                denoised, 0, 255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

            # Convert to PIL
            pil_image = Image.fromarray(thresh)

            # OCR
            text = pytesseract.image_to_string(
                pil_image,
                config='--psm 6 --oem 3'
            )

            logger.info(
                f"Image OCR completed: {len(text)} chars"
            )
            return text

        except Exception as e:
            logger.error(f"Image OCR failed: {e}")
            raise FileProcessingException(
                f"Failed to extract text from image: {str(e)}"
            )

    def extract_questions(
        self,
        text: str
    ) -> List[Dict[str, Any]]:
        """
        Extract individual questions from raw text.
        Returns list of question dicts with text, marks, number.
        """
        questions = []

        # Pattern 1: Numbered questions (1. 2. 3.)
        pattern1 = re.compile(
            r'(?:^|\n)\s*(\d+)[.)]\s+(.+?)(?=\n\s*\d+[.)]|\Z)',
            re.DOTALL | re.MULTILINE
        )

        # Pattern 2: Q1, Q2, Q3 format
        pattern2 = re.compile(
            r'(?:^|\n)\s*[Qq]\.?\s*(\d+)[.):]?\s+(.+?)'
            r'(?=\n\s*[Qq]\.?\s*\d+|\Z)',
            re.DOTALL | re.MULTILINE
        )

        # Try pattern 1 first
        matches = pattern1.findall(text)
        if not matches:
            matches = pattern2.findall(text)

        for num, content in matches:
            content = content.strip()
            if len(content) < 10:
                continue

            # Extract marks if present
            marks = self._extract_marks(content)

            # Clean content
            clean_content = re.sub(
                r'\[?\d+\s*marks?\]?',
                '',
                content,
                flags=re.IGNORECASE
            ).strip()

            if clean_content:
                questions.append({
                    "number": int(num),
                    "text": clean_content,
                    "marks": marks,
                    "raw": content
                })

        logger.info(
            f"Extracted {len(questions)} questions from text"
        )
        return questions

    def _extract_marks(self, text: str) -> int:
        """Extract marks from question text."""
        patterns = [
            r'\[(\d+)\s*marks?\]',
            r'\((\d+)\s*marks?\)',
            r'(\d+)\s*marks?',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 5  # Default marks

    def detect_question_type(self, text: str) -> str:
        """Detect question type from text."""
        text_lower = text.lower()

        # MCQ indicators
        if re.search(
            r'\b(a\)|b\)|c\)|d\)|\(a\)|\(b\)|\(c\)|\(d\))',
            text_lower
        ):
            return "mcq"

        # Numerical indicators
        if re.search(
            r'\b(calculate|compute|find the value|solve|'
            r'evaluate|determine the|how many|how much)\b',
            text_lower
        ):
            return "numerical"

        # Long answer indicators
        if re.search(
            r'\b(explain|describe|discuss|analyze|compare|'
            r'evaluate|elaborate|justify|critically)\b',
            text_lower
        ):
            return "long"

        # Short answer
        return "short"

    def detect_difficulty(self, text: str, marks: int) -> str:
        """Detect difficulty level from question text and marks."""
        text_lower = text.lower()

        # Hard indicators
        if marks >= 10 or re.search(
            r'\b(analyze|critically|evaluate|justify|'
            r'compare and contrast|prove)\b',
            text_lower
        ):
            return "hard"

        # Easy indicators
        if marks <= 2 or re.search(
            r'\b(define|state|list|name|identify|what is)\b',
            text_lower
        ):
            return "easy"

        return "medium"

    def detect_topic(self, text: str, subject: str) -> str:
        """Detect topic from question text."""
        text_lower = text.lower()

        topic_keywords = {
            "mathematics": {
                "algebra": ["equation", "variable", "polynomial", "linear"],
                "geometry": ["triangle", "circle", "angle", "area", "perimeter"],
                "calculus": ["derivative", "integral", "limit", "differentiate"],
                "statistics": ["probability", "mean", "median", "mode", "variance"],
                "trigonometry": ["sine", "cosine", "tangent", "angle"]
            },
            "science": {
                "photosynthesis": ["photosynthesis", "chlorophyll", "glucose"],
                "forces": ["force", "newton", "gravity", "friction"],
                "atoms": ["atom", "electron", "proton", "neutron"],
                "cells": ["cell", "mitosis", "membrane", "organelle"],
                "electricity": ["current", "voltage", "resistance", "circuit"]
            },
            "english": {
                "grammar": ["grammar", "sentence", "verb", "noun", "adjective"],
                "literature": ["poem", "novel", "character", "theme", "plot"],
                "writing": ["essay", "paragraph", "argument", "evidence"]
            }
        }

        subject_topics = topic_keywords.get(subject.lower(), {})
        for topic, keywords in subject_topics.items():
            if any(kw in text_lower for kw in keywords):
                return topic

        return "general"

    def parse_file(
        self,
        file_path: str,
        subject: str = "general"
    ) -> Dict[str, Any]:
        """
        Main method: parse a file and extract all question data.
        Returns structured data ready for pattern analysis.
        """
        file_ext = Path(file_path).suffix.lower()

        # Extract text
        if file_ext == ".pdf":
            raw_text = self.extract_text_from_pdf(file_path)
        elif file_ext in [".jpg", ".jpeg", ".png"]:
            raw_text = self.extract_text_from_image(file_path)
        else:
            raise FileProcessingException(
                f"Unsupported file type: {file_ext}"
            )

        if not raw_text.strip():
            raise FileProcessingException(
                "Could not extract text from file. "
                "Please ensure the file is readable."
            )

        # Extract questions
        raw_questions = self.extract_questions(raw_text)

        # Enrich with metadata
        questions = []
        for q in raw_questions:
            q_type = self.detect_question_type(q["text"])
            difficulty = self.detect_difficulty(
                q["text"], q["marks"]
            )
            topic = self.detect_topic(q["text"], subject)

            questions.append({
                "number": q["number"],
                "text": q["text"],
                "marks": q["marks"],
                "type": q_type,
                "difficulty": difficulty,
                "topic": topic
            })

        # Build summary stats
        topics = list(set(q["topic"] for q in questions))
        difficulty_dist = {
            "easy": sum(
                1 for q in questions if q["difficulty"] == "easy"
            ),
            "medium": sum(
                1 for q in questions if q["difficulty"] == "medium"
            ),
            "hard": sum(
                1 for q in questions if q["difficulty"] == "hard"
            )
        }

        return {
            "raw_text": raw_text,
            "questions": questions,
            "question_count": len(questions),
            "topics": topics,
            "difficulty_distribution": difficulty_dist,
            "subject": subject
        }


# Singleton
paper_parser = PaperParser()
