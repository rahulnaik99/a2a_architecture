"""
Centralised logging configuration for the multi-agent orchestrator.

Import and call setup_logging() once at app startup (main.py).
All other modules just use: logger = logging.getLogger(__name__)
"""

import logging
import sys
from datetime import datetime, timezone


class _ColourFormatter(logging.Formatter):
    """ANSI colour codes for terminal readability."""

    COLOURS = {
        logging.DEBUG:    "\033[36m",   # cyan
        logging.INFO:     "\033[32m",   # green
        logging.WARNING:  "\033[33m",   # yellow
        logging.ERROR:    "\033[31m",   # red
        logging.CRITICAL: "\033[35m",   # magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        colour = self.COLOURS.get(record.levelno, "")
        record.levelname = f"{colour}{record.levelname:<8}{self.RESET}"
        return super().format(record)


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure root logger with:
    - Coloured console output
    - Structured format: timestamp | level | logger_name | message
    """
    fmt = "%(asctime)s | %(levelname)s | %(name)-45s | %(message)s"
    datefmt = "%H:%M:%S"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_ColourFormatter(fmt=fmt, datefmt=datefmt))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # quiet noisy third-party loggers
    for noisy in ("httpx", "httpcore", "openai", "urllib3", "multipart"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    logging.getLogger("litellm").setLevel(logging.WARNING)

    logging.info("Logging configured | level=%s", logging.getLevelName(level))
