"""Structured (JSON-lines) logging for the whole app.

Use `logger.info("msg", extra={"ctx": {...}})` to attach structured context.
Never put secrets or raw résumé text in log context — résumés are PII.
"""
import json
import logging
import sys


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        ctx = getattr(record, "ctx", None)
        if isinstance(ctx, dict):
            payload.update(ctx)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(debug: bool = False) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.DEBUG if debug else logging.INFO)
    # Keep third-party chatter down at default level.
    for noisy in ("uvicorn.access", "httpx", "openai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
