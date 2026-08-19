import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from app.core.logger import logger
from app.core.config import settings
from app.core.exceptions import FileProcessingException


class ImageAnnotator:
    """
    Annotate images with spelling error boxes.
    Uses OpenCV to draw colored rectangles and labels.
    """

    # Colors (BGR format for OpenCV)
    ERROR_COLOR = (0, 0, 255)       # Red
    CORRECTION_COLOR = (0, 200, 0)  # Green
    BOX_THICKNESS = 2
    FONT_SCALE = 0.5

    def _get_output_path(self, original_path: str) -> str:
        """Get output path for annotated image."""
        output_dir = Path(settings.UPLOAD_DIR) / "annotated"
        output_dir.mkdir(parents=True, exist_ok=True)
        ext = Path(original_path).suffix
        stem = Path(original_path).stem
        return str(
            output_dir /
            f"{stem}_annotated_{uuid.uuid4().hex[:8]}{ext}"
        )

    def annotate_image(
        self,
        image_path: str,
        errors: List[Dict[str, Any]],
        show_corrections: bool = True
    ) -> str:
        """
        Draw annotation boxes on image for spelling errors.
        Returns path to annotated image.
        """
        try:
            import cv2
            import numpy as np

            img = cv2.imread(image_path)
            if img is None:
                raise FileProcessingException(
                    f"Cannot read image: {image_path}"
                )

            annotated_count = 0

            for error in errors:
                x = error.get("x")
                y = error.get("y")
                w = error.get("width")
                h = error.get("height")
                word = error.get("word", "")
                correction = error.get("correction", "")

                if None in [x, y, w, h]:
                    continue

                # Convert to int
                x, y, w, h = int(x), int(y), int(w), int(h)

                # Draw error rectangle (red)
                cv2.rectangle(
                    img,
                    (x, y),
                    (x + w, y + h),
                    self.ERROR_COLOR,
                    self.BOX_THICKNESS
                )

                # Draw correction label above box
                if show_corrections and correction:
                    label = f"→ {correction}"
                    label_x = x
                    label_y = max(y - 5, 15)

                    # Background for text
                    (text_w, text_h), baseline = (
                        cv2.getTextSize(
                            label,
                            cv2.FONT_HERSHEY_SIMPLEX,
                            self.FONT_SCALE,
                            1
                        )
                    )

                    cv2.rectangle(
                        img,
                        (label_x, label_y - text_h - 4),
                        (label_x + text_w + 4, label_y + 2),
                        (255, 255, 255),
                        -1
                    )

                    # Draw text
                    cv2.putText(
                        img,
                        label,
                        (label_x + 2, label_y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        self.FONT_SCALE,
                        self.CORRECTION_COLOR,
                        1,
                        cv2.LINE_AA
                    )

                annotated_count += 1

            output_path = self._get_output_path(image_path)
            cv2.imwrite(output_path, img)

            logger.info(
                f"Image annotated: {annotated_count} boxes "
                f"drawn → {output_path}"
            )
            return output_path

        except ImportError:
            logger.error(
                "OpenCV not installed. "
                "Run: pip install opencv-python"
            )
            raise FileProcessingException(
                "OpenCV not installed"
            )
        except Exception as e:
            logger.error(f"Image annotation failed: {e}")
            raise FileProcessingException(
                f"Failed to annotate image: {str(e)}"
            )

    def draw_summary_panel(
        self,
        image_path: str,
        error_count: int,
        total_words: int
    ) -> str:
        """
        Add a summary panel to annotated image.
        Shows total errors and error rate.
        """
        try:
            import cv2
            import numpy as np

            img = cv2.imread(image_path)
            if img is None:
                return image_path

            height, width = img.shape[:2]

            # Create panel at bottom
            panel_height = 50
            panel = np.ones(
                (panel_height, width, 3),
                dtype=np.uint8
            ) * 240  # Light gray

            error_rate = (
                error_count / max(total_words, 1) * 100
            )

            summary_text = (
                f"Spelling Errors: {error_count} | "
                f"Total Words: {total_words} | "
                f"Error Rate: {error_rate:.1f}%"
            )

            cv2.putText(
                panel,
                summary_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (30, 30, 30),
                1,
                cv2.LINE_AA
            )

            # Append panel to image
            combined = np.vstack([img, panel])
            cv2.imwrite(image_path, combined)

            return image_path

        except Exception as e:
            logger.warning(f"Summary panel failed: {e}")
            return image_path

    def create_error_legend(
        self,
        image_path: str
    ) -> str:
        """Add color legend to annotated image."""
        try:
            import cv2
            import numpy as np

            img = cv2.imread(image_path)
            if img is None:
                return image_path

            # Draw legend in top-right corner
            legend_x = img.shape[1] - 200
            legend_y = 10

            # Background
            cv2.rectangle(
                img,
                (legend_x - 5, legend_y - 5),
                (img.shape[1] - 5, legend_y + 50),
                (255, 255, 255),
                -1
            )

            # Red box = error
            cv2.rectangle(
                img,
                (legend_x, legend_y + 5),
                (legend_x + 20, legend_y + 20),
                self.ERROR_COLOR,
                -1
            )
            cv2.putText(
                img,
                "Spelling Error",
                (legend_x + 25, legend_y + 17),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 0, 0),
                1
            )

            # Green text = correction
            cv2.putText(
                img,
                "→ Green = Correction",
                (legend_x, legend_y + 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                self.CORRECTION_COLOR,
                1
            )

            cv2.imwrite(image_path, img)
            return image_path

        except Exception as e:
            logger.warning(f"Legend creation failed: {e}")
            return image_path


# Singleton
image_annotator = ImageAnnotator()
