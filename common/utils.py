import logging
import logging.config
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from django.utils import timezone


def set_default_log(log_level: str = None):
    """
    log_level:string
        choice:
        DEBUG INFO WARNING ERROR CRITICAL
    """
    if not log_level:
        log_level = os.environ.get("LOG_LEVEL", "INFO")
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(levelname)s\t%(asctime)s\t|%(filename)s|%(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": log_level,
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {"handlers": ["console"], "level": log_level, "propagate": False}
        },
    }
    logging.config.dictConfig(LOGGING_CONFIG)
    log = logging.getLogger(__name__)
    return log
