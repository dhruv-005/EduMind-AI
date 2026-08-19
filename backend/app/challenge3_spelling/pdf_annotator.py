import os
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.core.logger import logger
from app.core.config import settings
from app.core.exceptions import FileProcessingException


class PDFAnnotator:
    """
    Annotate PDFs with spelling error highlights.
    Uses PyMuPDF to add highlight annotations at exact coordinates.
    """

    def _get_output_path(self, original_path: str) -> str:
        """Get output path for annotated PDF."""
        output_dir = Path(settings.UPLOAD_DIR) / "annotated"
        output_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(original_path).stem
        return str(output_dir / f"{stem}_annotated_{uuid.uuid4().hex[:8]}.pdf")

    def annotate_pdf(
        self,
        pdf_path: str,
        errors: List[Dict[str, Any]],
        highlight_color: tuple = (1, 0, 0)
    ) -> str:
        """
        Add highlight annotations to PDF for spelling errors.
        Returns path to annotated PDF.
        """
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(pdf_path)
            output_path = self._get_output_path(pdf_path)

            # Group errors by page
            errors_by_page = {}
            for error in errors:
                page_num = error.get("page", 1) - 1
                if page_num not in errors_by_page:
                    errors_by_page[page_num] = []
                errors_by_page[page_num].append(error)

            annotated_count = 0

            for page_idx in range(len(doc)):
                page = doc[page_idx]
                page_errors = errors_by_page.get(page_idx, [])

                for error in page_errors:
                    word = error.get("word", "")
                    correction = error.get("correction", "")

                    if not word:
                        continue

                    # Search for word on page
                    try:
                        instances = page.search_for(word)

                        for rect in instances:
                            # Add highlight annotation
                            highlight = page.add_highlight_annot(
                                rect
                            )
                            highlight.set_colors(
                                stroke=highlight_color
                            )

                            # Add tooltip with correction
                            highlight.set_info(
                                title="Spelling Error",
                                content=(
                                    f"Error: '{word}'\n"
                                    f"Correction: '{correction}'"
                                )
                            )
                            highlight.update()
                            annotated_count += 1
                            break  # Only annotate first instance

                    except Exception as e:
                        logger.debug(
                            f"Could not annotate '{word}': {e}"
                        )

                    # Try coordinate-based annotation if search fails
                    if (
                        error.get("x") is not None and
                        error.get("y") is not None
                    ):
                        try:
                            x = error["x"]
                            y = error["y"]
                            w = error.get("width", 50)
                            h = error.get("height", 15)

                            rect = fitz.Rect(x, y, x + w, y + h)
                            highlight = page.add_highlight_annot(
                                rect
                            )
                            highlight.set_colors(
                                stroke=(1, 0.5, 0)
                            )
                            highlight.set_info(
                                title="Spelling Error",
                                content=(
                                    f"'{word}' → '{correction}'"
                                )
                            )
                            highlight.update()
                            annotated_count += 1

                        except Exception as e:
                            logger.debug(
                                f"Coordinate annotation failed: {e}"
                            )

            doc.save(output_path)
            doc.close()

            logger.info(
                f"PDF annotated: {annotated_count} highlights "
                f"added to {output_path}"
            )
            return output_path

        except ImportError:
            logger.error(
                "PyMuPDF not installed. "
                "Run: pip install PyMuPDF"
            )
            raise FileProcessingException(
                "PyMuPDF library not installed"
            )
        except Exception as e:
            logger.error(f"PDF annotation failed: {e}")
            raise FileProcessingException(
                f"Failed to annotate PDF: {str(e)}"
            )

    def extract_text_with_positions(
        self,
        pdf_path: str
    ) -> List[Dict[str, Any]]:
        """
        Extract text from PDF with word positions.
        Used for text-layer PDFs (not scanned).
        """
        try:
            import fitz

            doc = fitz.open(pdf_path)
            all_words = []

            for page_num, page in enumerate(doc, 1):
                # Get words with bounding boxes
                words = page.get_text("words")

                for w in words:
                    x0, y0, x1, y1, word, block, line, word_n = w
                    if word.strip():
                        all_words.append({
                            "word": word.strip(),
                            "x": x0,
                            "y": y0,
                            "width": x1 - x0,
                            "height": y1 - y0,
                            "page": page_num,
                            "block": block,
                            "line": line
                        })

            doc.close()
            logger.info(
                f"Extracted {len(all_words)} words "
                f"from PDF with positions"
            )
            return all_words

        except ImportError:
            logger.warning("PyMuPDF not available")
            return []
        except Exception as e:
            logger.error(
                f"PDF text extraction failed: {e}"
            )
            return []

    def has_text_layer(self, pdf_path: str) -> bool:
        """Check if PDF has a text layer (vs scanned)."""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            for page in doc:
                text = page.get_text().strip()
                if len(text) > 50:
                    doc.close()
                    return True
            doc.close()
            return False
        except Exception:
            return False

    def get_page_count(self, pdf_path: str) -> int:
        """Get number of pages in PDF."""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            count = len(doc)
            doc.close()
            return count
        except Exception:
            return 1


# Singleton
pdf_annotator = PDFAnnotator()
