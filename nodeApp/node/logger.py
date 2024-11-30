
import logging
from logging.config import dictConfig

LOG_LEVEL_COLORS = {
    "INFO": "\033[34m",     # Blue for INFO
    "ERROR": "\033[31m",    # Red for ERROR
    "ACCESS": "\033[32m",   # Green for ACCESS
}

GRAY = "\033[37m"  # Gray for date and time
RESET = "\033[0m"   # Reset color

class ColorFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'asctime'):
            record.asctime = self.formatTime(record, self.datefmt)

        record.asctime = GRAY + record.asctime + RESET

        levelname = record.levelname
        if levelname == "INFO":
            record.levelname = LOG_LEVEL_COLORS["INFO"] + "[INFO]" + RESET
        elif levelname == "ERROR":
            record.levelname = LOG_LEVEL_COLORS["ERROR"] + "[ERROR]" + RESET
        elif levelname == "ACCESS":
            record.levelname = LOG_LEVEL_COLORS["ACCESS"] + "[ACCESS]" + RESET

        return super().format(record)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "generic": {
            "format": "%(asctime)s %(levelname)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "()": ColorFormatter,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
        },
    },
    "loggers": {
        "sanic.root": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "sanic.error": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "sanic.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)

class NodeLogger:
    def __init__(self):
        """Node logger."""
        self.root_logger = logging.getLogger("sanic.root")
        self.error_logger = logging.getLogger("sanic.error")
        self.access_logger = logging.getLogger("sanic.access")

    def info(self, message, **kwargs):
        self.root_logger.info(message, **kwargs)

    def error(self, message, **kwargs):
        self.error_logger.error(message, **kwargs)

    def access(self, message, **kwargs):
        self.access_logger.info(message, **kwargs)


logger = NodeLogger()
"""Node logger."""
