
import logging
from logging.config import dictConfig

connection_LEVEL = 25
logging.addLevelName(connection_LEVEL, "CONNECTION")

LOG_LEVEL_COLORS = {
    "INFO": "\033[34m",     # Blue for INFO
    "ERROR": "\033[31m",    # Red for ERROR
    "CONNECTION": "\033[32m",   # Green for CONNECTION
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
            record.levelname = LOG_LEVEL_COLORS["INFO"] + "[INFO]  " + RESET
        elif levelname == "ERROR":
            record.levelname = LOG_LEVEL_COLORS["ERROR"] + "[ERROR] " + RESET
        elif levelname == "CONNECTION":
            record.levelname = LOG_LEVEL_COLORS["CONNECTION"] + "[CONN]  " + RESET

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
        "root": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "error": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "connection": {
            "level": "CONNECTION",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)

class NodeLogger:
    def __init__(self):
        """Node logger."""
        self.root_logger = logging.getLogger("root")
        self.error_logger = logging.getLogger("error")
        self.connection_logger = logging.getLogger("connection")

    def info(self, message, **kwargs):
        self.root_logger.info(message, **kwargs)

    def error(self, message, **kwargs):
        self.error_logger.error(message, **kwargs)

    def connection(self, message, **kwargs):
        self.connection_logger.log(connection_LEVEL, message, **kwargs)

logger = NodeLogger()
"""Node logger."""
