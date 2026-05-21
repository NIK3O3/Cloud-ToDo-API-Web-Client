import logging
import sys

from pythonjsonlogger import json

from app.core.config import get_settings

LOG_FORMAT = " ".join(
    [
        "%(asctime)s",
        "%(levelname)s",
        "%(name)s",
        "%(message)s",
        "%(request_id)s",
        "%(method)s",
        "%(path)s",
        "%(status_code)s",
        "%(duration_ms)s",
    ]
)


def configure_logging() -> None:
    settings = get_settings()
    handler = logging.StreamHandler(sys.stdout)
    formatter = json.JsonFormatter(fmt=LOG_FORMAT)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())
