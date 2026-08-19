import os
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from app.core.logger import logger
from app.core.exceptions import FileProcessingException


class OCREngine:
    """
    OCR engine for extracting text from images and scanned PDFs.
    Uses Tesseract with OpenCV preprocessing for best accuracy.
    """

    def __init__(self):
        self._tesseract_available = None

    def _check_tesseract(self) -> bool:
        """Check if Tesseract is available."""
        if self._tesseract_available is None:
            try:
                import pytesseract
                pytesseract.get_tesseract_version()
                self._tesseract_available = True
                logger.info("Tesseract OCR available")
            except Exception:
                self._tesseract_available = False
                logger.warning(
                    "Tesseract not available. "
                    "Install: sudo apt install tesseract-ocr"
                )
        return self._tesseract_available

    def preprocess_image(self, image_path: str):
        """
        Preprocess image for better OCR accuracy.
        Returns preprocessed image array.
        """
        try:
            import cv2
            import numpy as np

            img = cv2.imread(image_path)
            if img is None:
                raise FileProcessingException(
                    f"Cannot read image: {image_path}"
                )

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Resize if too small (min 300 DPI equivalent)
            height, width = gray.shape
            if width < 1000:
                scale = 1000 / width
                gray = cv2.resize(
                    gray,
                    None,
                    fx=scale,
                    fy=scale,
                    interpolation=cv2.INTER_CUBIC
                )

            # Denoise
            denoised = cv2.fastNlMeansDenoising(
                gray, h=10
            )

            # Increase contrast using CLAHE
            clahe = cv2.createCLAHE(
                clipLimit=2.0,
                tileGridSize=(8, 8)
            )
            contrasted = clahe.apply(denoised)

            # Binarize using Otsu thresholding
            _, binary = cv2.threshold(
                contrasted,
                0, 255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

            # Remove noise with morphological operations
            kernel = cv2.getStructuringElement(
                cv2.MORPH_RECT, (1, 1)
            )
            clean = cv2.morphologyEx(
                binary,
                cv2.MORPH_CLOSE,
                kernel
            )

            return clean

        except ImportError:
            logger.warning("OpenCV not installed")
            return None
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return None

    def extract_text_with_boxes(
        self,
        image_path: str,
        lang: str = "eng"
    ) -> List[Dict[str, Any]]:
        """
        Extract text with bounding box coordinates.
        Returns list of word dicts with position info.
        """
        if not self._check_tesseract():
            raise FileProcessingException(
                "Tesseract OCR not installed"
            )

        try:
            import pytesseract
            from PIL import Image
            import pandas as pd

            # Preprocess image
            preprocessed = self.preprocess_image(image_path)

            if preprocessed is not None:
                from PIL import Image as PILImage
                import numpy as np
                pil_img = PILImage.fromarray(preprocessed)
            else:
                pil_img = Image.open(image_path)

            # Get word-level data with boxes
            config = f'--oem 3 --psm 6 -l {lang}'
            data = pytesseract.image_to_data(
                pil_img,
                config=config,
                output_type=pytesseract.Output.DICT
            )

            words = []
            n_boxes = len(data['text'])

            for i in range(n_boxes):
                word = data['text'][i].strip()
                conf = int(data['conf'][i])

                if word and conf > 30:
                    words.append({
                        "word": word,
                        "x": data['left'][i],
                        "y": data['top'][i],
                        "width": data['width'][i],
                        "height": data['height'][i],
                        "confidence": conf / 100.0,
                        "page": 1,
                        "line": data['line_num'][i],
                        "block": data['block_num'][i]
                    })

            logger.info(
                f"OCR extracted {len(words)} words "
                f"from {image_path}"
            )
            return words

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise FileProcessingException(
                f"OCR failed: {str(e)}"
            )

    def extract_from_pdf_pages(
        self,
        pdf_path: str,
        lang: str = "eng"
    ) -> List[Dict[str, Any]]:
        """
        Extract text from scanned PDF by converting to images.
        Returns all words with page number and coordinates.
        """
        try:
            from pdf2image import convert_from_path
            import tempfile
            import uuid

            logger.info(
                f"Converting PDF to images for OCR: {pdf_path}"
            )

            # Convert PDF pages to images
            images = convert_from_path(
                pdf_path,
                dpi=200,
                fmt='PNG'
            )

            all_words = []

            for page_num, image in enumerate(images, 1):
                # Save temp image
                temp_dir = tempfile.mkdtemp()
                temp_path = os.path.join(
                    temp_dir,
                    f"page_{page_num}.png"
                )
                image.save(temp_path)

                # OCR the page
                try:
                    page_words = self.extract_text_with_boxes(
                        temp_path,
                        lang=lang
                    )
                    # Update page number
                    for w in page_words:
                        w["page"] = page_num
                    all_words.extend(page_words)

                except Exception as e:
                    logger.warning(
                        f"OCR failed for page {page_num}: {e}"
                    )
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

            logger.info(
                f"PDF OCR complete: "
                f"{len(all_words)} words from "
                f"{len(images)} pages"
            )
            return all_words

        except ImportError:
            logger.error(
                "pdf2image not installed. "
                "Run: pip install pdf2image"
            )
            raise FileProcessingException(
                "pdf2image library not installed"
            )
        except Exception as e:
            logger.error(f"PDF OCR failed: {e}")
            raise FileProcessingException(
                f"PDF OCR failed: {str(e)}"
            )

    def get_overall_confidence(
        self,
        words: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall OCR confidence from word list."""
        if not words:
            return 0.0

        confidences = [
            w.get("confidence", 0.0) for w in words
        ]
        return round(sum(confidences) / len(confidences), 3)

    def extract_plain_text(
        self,
        image_path: str,
        lang: str = "eng"
    ) -> Tuple[str, float]:
        """
        Extract plain text from image.
        Returns (text, confidence).
        """
        if not self._check_tesseract():
            return "", 0.0

        try:
            import pytesseract
            from PIL import Image

            preprocessed = self.preprocess_image(image_path)

            if preprocessed is not None:
                from PIL import Image as PILImage
                import numpy as np
                pil_img = PILImage.fromarray(preprocessed)
            else:
                pil_img = Image.open(image_path)

            config = f'--oem 3 --psm 6 -l {lang}'
            text = pytesseract.image_to_string(
                pil_img,
                config=config
            )

            # Get confidence
            data = pytesseract.image_to_data(
                pil_img,
                config=config,
                output_type=pytesseract.Output.DICT
            )
            confs = [
                int(c) for c in data['conf']
                if int(c) > 0
            ]
            avg_conf = (
                sum(confs) / len(confs) / 100.0
                if confs else 0.0
            )

            return text.strip(), round(avg_conf, 3)

        except Exception as e:
            logger.error(f"Plain text extraction failed: {e}")
            return "", 0.0


# Singleton
ocr_engine = OCREngine()
