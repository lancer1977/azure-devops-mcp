"""Configuration module for ADO MCP."""
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Application settings."""
    ado_org: str
    ado_project: str
    ado_pat: str
    ado_api_version: str = "7.1-preview.3"
    port: int = 8080
    log_level: str = "INFO"
    ado_allow_writes: bool = False
    ado_allowed_work_item_types: str = "Task,Bug,User Story"


def get_settings() -> Settings:
    """Load and validate settings from environment variables."""
    ado_org = os.getenv("ADO_ORG")
    if not ado_org:
        raise ValueError("ADO_ORG environment variable is required")

    ado_project = os.getenv("ADO_PROJECT")
    if not ado_project:
        raise ValueError("ADO_PROJECT environment variable is required")

    ado_pat = os.getenv("ADO_PAT")
    if not ado_pat:
        raise ValueError("ADO_PAT environment variable is required")

    ado_api_version = os.getenv("ADO_API_VERSION", "7.1-preview.3")
    port = int(os.getenv("PORT", "8080"))
    log_level = os.getenv("LOG_LEVEL", "INFO")
    ado_allow_writes = os.getenv("ADO_ALLOW_WRITES", "false").lower() in {"1", "true", "yes", "on"}
    ado_allowed_work_item_types = os.getenv("ADO_ALLOWED_WORK_ITEM_TYPES", "Task,Bug,User Story")

    return Settings(
        ado_org=ado_org,
        ado_project=ado_project,
        ado_pat=ado_pat,
        ado_api_version=ado_api_version,
        port=port,
        log_level=log_level,
        ado_allow_writes=ado_allow_writes,
        ado_allowed_work_item_types=ado_allowed_work_item_types,
    )
