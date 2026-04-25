"""Structured audit logging setup.

Logs every scoring request as a JSON line to both stdout and `audit.log`
(in the backend working directory). We intentionally avoid logging anything
that could be considered sensitive — only the inputs needed to reproduce
the score, plus the score and reason codes.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

LOG_FILE = Path(__file__).resolve().parent.parent / "audit.log"

_logger: logging.Logger | None = None


def get_logger() -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    logger = logging.getLogger("saakhsetu.audit")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter("%(message)s")

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    try:
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        # Fall back to stdout only if the file isn't writable (e.g. in tests)
        pass

    _logger = logger
    return logger


def log_scoring_event(
    request_id: str,
    inputs: Dict[str, Any],
    score: float,
    reason_codes: list[str],
) -> None:
    """Emit one structured audit log entry for a scoring request."""
    payload = {
        "event": "score_computed",
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "inputs": inputs,
        "score": score,
        "reason_codes": reason_codes,
    }
    get_logger().info(json.dumps(payload, sort_keys=True))
