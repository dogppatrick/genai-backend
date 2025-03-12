import logging
import logging.config
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from django.utils import timezone


def empty_wraper(func):
    def do_nothing(*args, **kwargs):
        result = func(*args, **kwargs)
        return result

    return do_nothing


def add_tzinfo(post_modeified: datetime):
    return post_modeified.replace(tzinfo=datetime.timezone.utc)


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


def log_timer(func):
    def timed(*args, **kwargs):
        import timeit

        logger = set_default_log()
        logger.info(f"==={func.__name__} START ===")
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        end_time = timeit.default_timer()
        elapsed_time = end_time - start_time
        logger.info(f"==={func.__name__} END >>>>|{elapsed_time:.3f}s|")
        return result

    return timed


def get_tw_now(with_tz: bool = True) -> datetime:
    taipei_timezone = ZoneInfo("Asia/Taipei")
    result = timezone.localtime(timezone.now(), timezone=taipei_timezone)
    return result if with_tz else result.replace(tzinfo=None)
