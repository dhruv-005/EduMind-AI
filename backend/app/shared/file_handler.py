import os
import uuid
import shutil
from typing import Optional, List, Tuple
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from app.core.logger import logger
from app.core.constants import ALLOWED_DOC_TYPES, ALLOWED_DATA_TYPES
from app.core.exceptions import FileProcessingException


class FileHandler:
    """Handle file uploads, validation, and cleanup."""

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        """Create upload directory if it doesn't exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Upload directory ready: {self.upload_dir}")

    def validate_file(
        self,
        file: UploadFile,
        allowed_types: Optional[List[str]] = None
    ) -> Tuple[bool, str]:
        """
        Validate uploaded file.
        Returns: (is_valid, error_message)
        """
        if not file.filename:
            return False, "No filename provided"

        extension = Path(file.filename).suffix.lower()
        allowed = allowed_types or ALLOWED_DOC_TYPES

        if extension not in allowed:
            return False, (
                f"File type '{extension}' not allowed. "
                f"Allowed: {', '.join(allowed)}"
            )

        return True, ""

    async def save_upload(
        self,
        file: UploadFile,
        subfolder: str = "",
        allowed_types: Optional[List[str]] = None
    ) -> Tuple[str, str]:
        """
        Save uploaded file to disk.
        Returns: (file_path, original_filename)
        """
        is_valid, error = self.validate_file(file, allowed_types)
        if not is_valid:
            raise FileProcessingException(error)

        extension = Path(file.filename).suffix.lower()
        unique_name = f"{uuid.uuid4().hex}{extension}"

        save_dir = self.upload_dir / subfolder if subfolder else self.upload_dir
        save_dir.mkdir(parents=True, exist_ok=True)

        file_path = save_dir / unique_name

        try:
            content = await file.read()

            if len(content) > self.max_size_bytes:
                raise FileProcessingException(
                    f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
                )

            with open(file_path, "wb") as f:
                f.write(content)

            logger.info(
                f"File saved: {file_path} "
                f"({len(content)/1024:.1f}KB)"
            )

            return str(file_path), file.filename

        except FileProcessingException:
            raise
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise FileProcessingException(f"Failed to save file: {str(e)}")

    def delete_file(self, file_path: str) -> bool:
        """Delete a file from disk."""
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False

    def get_file_info(self, file_path: str) -> dict:
        """Get file information."""
        path = Path(file_path)
        if not path.exists():
            return {"exists": False}

        stat = path.stat()
        return {
            "exists": True,
            "name": path.name,
            "extension": path.suffix.lower(),
            "size_bytes": stat.st_size,
            "size_kb": round(stat.st_size / 1024, 2),
            "path": str(path)
        }

    def cleanup_old_files(
        self,
        subfolder: str = "",
        max_age_hours: int = 24
    ) -> int:
        """Clean up files older than max_age_hours. Returns count deleted."""
        import time
        cleanup_dir = (
            self.upload_dir / subfolder if subfolder else self.upload_dir
        )
        deleted = 0
        cutoff = time.time() - (max_age_hours * 3600)

        try:
            for file_path in cleanup_dir.iterdir():
                if (
                    file_path.is_file() and
                    file_path.stat().st_mtime < cutoff
                ):
                    file_path.unlink()
                    deleted += 1

            if deleted:
                logger.info(
                    f"Cleaned up {deleted} old files from {cleanup_dir}"
                )
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

        return deleted

    def read_file_bytes(self, file_path: str) -> bytes:
        """Read file as bytes."""
        try:
            with open(file_path, "rb") as f:
                return f.read()
        except Exception as e:
            raise FileProcessingException(
                f"Cannot read file {file_path}: {str(e)}"
            )

    def is_pdf(self, file_path: str) -> bool:
        """Check if file is a PDF."""
        return Path(file_path).suffix.lower() == ".pdf"

    def is_image(self, file_path: str) -> bool:
        """Check if file is an image."""
        return Path(file_path).suffix.lower() in [".jpg", ".jpeg", ".png"]


# Singleton
file_handler = FileHandler()
