from typing import Dict, Any, Optional
from datetime import datetime
from app.core.logger import logger


# Prompt version registry
PROMPT_VERSIONS: Dict[str, Dict[str, Any]] = {
    "challenge1_evaluation": {
        "version": "1.0.0",
        "created_at": "2024-01-01",
        "description": "Main evaluation prompt for answer scoring",
        "changelog": "Initial version"
    },
    "challenge1_math": {
        "version": "1.0.0",
        "created_at": "2024-01-01",
        "description": "Math-specific evaluation prompt",
        "changelog": "Initial version"
    },
    "challenge1_science": {
        "version": "1.0.0",
        "created_at": "2024-01-01",
        "description": "Science-specific evaluation prompt",
        "changelog": "Initial version"
    },
    "challenge1_english": {
        "version": "1.0.0",
        "created_at": "2024-01-01",
        "description": "English-specific evaluation prompt",
        "changelog": "Initial version"
    },
    "challenge2_extraction": {
        "version": "1.0.0",
        "created_at": "2024-01-01",
        "description": "Question extraction from papers",
        "changelog": "Initial version"
    },
    "challenge2_generation": {
        "version": "1.0.0",
        "created_at": "2024-01-01",
        "description": "New question generation prompt",
        "changelog": "Initial version"
    },
    "challenge4_tutor": {
        "version": "1.0.0",
        "created_at": "2024-01-01",
        "description": "Voice tutor system prompt",
        "changelog": "Initial version"
    },
    "challenge5_sales": {
        "version": "1.0.0",
        "created_at": "2024-01-01",
        "description": "Sales assistant system prompt",
        "changelog": "Initial version"
    }
}


class PromptVersionManager:
    """Track and manage prompt versions for governance."""

    def get_version(self, prompt_key: str) -> str:
        """Get current version of a prompt."""
        prompt_info = PROMPT_VERSIONS.get(prompt_key, {})
        return prompt_info.get("version", "unknown")

    def get_prompt_info(self, prompt_key: str) -> Dict[str, Any]:
        """Get full prompt metadata."""
        return PROMPT_VERSIONS.get(prompt_key, {
            "version": "unknown",
            "created_at": "unknown",
            "description": "Prompt not registered",
            "changelog": ""
        })

    def register_prompt(
        self,
        prompt_key: str,
        version: str,
        description: str,
        changelog: str = ""
    ) -> bool:
        """Register or update a prompt version."""
        PROMPT_VERSIONS[prompt_key] = {
            "version": version,
            "created_at": datetime.utcnow().strftime("%Y-%m-%d"),
            "description": description,
            "changelog": changelog,
            "updated_at": datetime.utcnow().isoformat()
        }
        logger.info(f"Prompt registered: {prompt_key} v{version}")
        return True

    def list_all_versions(self) -> Dict[str, Any]:
        """List all registered prompt versions."""
        return {
            key: {
                "version": info.get("version"),
                "description": info.get("description"),
                "created_at": info.get("created_at")
            }
            for key, info in PROMPT_VERSIONS.items()
        }

    def log_prompt_usage(
        self,
        prompt_key: str,
        model_used: str,
        success: bool
    ):
        """Log prompt usage for tracking."""
        version = self.get_version(prompt_key)
        logger.info(
            f"PROMPT_USED | key={prompt_key} | "
            f"version={version} | model={model_used} | "
            f"success={success}"
        )

    def get_audit_info(self, prompt_key: str) -> Dict[str, Any]:
        """Get audit-ready prompt information."""
        info = self.get_prompt_info(prompt_key)
        return {
            "prompt_key": prompt_key,
            "prompt_version": info.get("version", "unknown"),
            "prompt_description": info.get("description", ""),
            "prompt_created": info.get("created_at", "")
        }


# Singleton
prompt_versioning = PromptVersionManager()
