"""Debug logger — crash-safe diagnostic logging for sprint execution.

Provides structured, flush-on-write logging that survives subprocess crashes.
When ``config.debug=False`` (default), a NullHandler is attached and all calls
are zero-overhead no-ops.

Log format per line::

    2026-03-04T19:00:00.123 DEBUG [executor] poll_tick pid=1234 elapsed=5.2

Version header (first line when enabled)::

    # debug-log-version: 1.0
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import SprintConfig

DEBUG_LOG_VERSION = "1.0"
LOGGER_NAME = "superclaude.sprint.debug"


class _FlushHandler(logging.FileHandler):
    """File handler that flushes after every emit for crash safety.

    If the process crashes or is killed, all previously emitted records
    are guaranteed to be on disk because each ``emit()`` call flushes
    the underlying stream before returning.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            super().emit(record)
            self.flush()
        except Exception:
            # Suppress I/O errors so logging never disrupts the sprint
            self.handleError(record)


class _DebugFormatter(logging.Formatter):
    """Structured formatter producing ``timestamp LEVEL [component] message``.

    Timestamps are ISO 8601 with millisecond precision.  The component
    is extracted from the logger name's last segment (e.g.
    ``superclaude.sprint.debug.executor`` → ``executor``).
    """

    def format(self, record: logging.LogRecord) -> str:
        # ISO 8601 with milliseconds
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        ts = dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{int(record.msecs):03d}"

        # Component: last segment of logger name, or "root" if no dots
        parts = record.name.split(".")
        component = parts[-1] if len(parts) > 1 else "root"

        # Level: uppercase, padded to 8 chars for alignment
        level = record.levelname.ljust(8)

        return f"{ts} {level} [{component}] {record.getMessage()}"


def setup_debug_logger(config: SprintConfig) -> logging.Logger:
    """Create and configure the debug logger.

    When ``config.debug`` is True, attaches a :class:`_FlushHandler`
    writing to ``config.debug_log_path`` with the structured formatter
    and writes the version header as the first line.

    When ``config.debug`` is False, attaches only a ``NullHandler``
    for zero-overhead no-op logging.

    Returns:
        A ``logging.Logger`` named ``superclaude.sprint.debug`` with
        ``propagate=False``.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.propagate = False

    # Clear any pre-existing handlers (e.g. from a previous call)
    logger.handlers.clear()

    if config.debug:
        log_path = config.debug_log_path
        log_path.parent.mkdir(parents=True, exist_ok=True)

        handler = _FlushHandler(str(log_path), mode="w", encoding="utf-8")
        handler.setFormatter(_DebugFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        # Write version header as first line (not via logger, to keep it
        # outside the structured log format)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"# debug-log-version: {DEBUG_LOG_VERSION}\n")

        # Re-open handler after writing header so it appends
        handler.close()
        logger.handlers.clear()
        handler = _FlushHandler(str(log_path), mode="a", encoding="utf-8")
        handler.setFormatter(_DebugFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    else:
        logger.addHandler(logging.NullHandler())
        logger.setLevel(logging.CRITICAL + 1)  # effectively disabled

    return logger


def debug_log(logger: logging.Logger, event: str, **kwargs) -> None:
    """Emit a structured debug event.

    Produces log entries like: ``poll_tick pid=1234 elapsed=5.2``

    When the logger is disabled (NullHandler only), returns immediately
    with negligible overhead — the ``isEnabledFor`` check short-circuits
    before any string formatting occurs.

    Args:
        logger: The debug logger from :func:`setup_debug_logger`.
        event: Event name (e.g. ``"poll_tick"``, ``"PHASE_BEGIN"``).
        **kwargs: Key-value pairs appended as ``k=v``.
    """
    if not logger.isEnabledFor(logging.DEBUG):
        return

    if kwargs:
        pairs = " ".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        logger.debug(f"{event} {pairs}")
    else:
        logger.debug(event)
