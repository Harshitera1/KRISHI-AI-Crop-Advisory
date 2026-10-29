import json
import logging
import os
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        extra_fields = (
            "event",
            "request_id",
            "path",
            "method",
            "status_code",
            "duration_ms",
        )
        for field in extra_fields:
            value = getattr(record, field, None)
            if value is not None:
                log_data[field] = value

        return json.dumps(log_data)


def configure_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    root_logger = logging.getLogger()

    if root_logger.handlers:
        root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.setLevel(log_level)
    werkzeug_logger.handlers.clear()
    werkzeug_logger.addHandler(handler)
    werkzeug_logger.propagate = False
