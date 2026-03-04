"""Logging configuration for ADO MCP."""
import logging
import os
import re


class RedactSecretsFilter(logging.Filter):
    """Redact common credential patterns from log messages."""

    _patterns = [
        re.compile(r"(ADO_PAT=)([^\s,;]+)", re.IGNORECASE),
        re.compile(r"(Authorization:\s*Bearer\s+)([^\s,;]+)", re.IGNORECASE),
        re.compile(r"(token=)([^\s,;]+)", re.IGNORECASE),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pattern in self._patterns:
            msg = pattern.sub(r"\1***REDACTED***", msg)
        record.msg = msg
        record.args = ()
        return True


def setup_logging():
    """Configure logging for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    root = logging.getLogger()
    for handler in root.handlers:
        handler.addFilter(RedactSecretsFilter())

    return logging.getLogger(__name__)
