# logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from colorama import Fore, Style, init

init(autoreset=True)


class ColorFormatter(logging.Formatter):
    """Custom colorized log formatter."""

    COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, "")
        levelname = f"{log_color}{record.levelname:<8}{Style.RESET_ALL}"
        log_fmt = f"[%(asctime)s] [%(name)s] {levelname} %(message)s"
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


def setup_logger(
    name: str = "app",
    log_level: str = "INFO",
    log_file: str | None = None,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(log_level.upper())

    # Avoid duplicate handlers if re-imported
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColorFormatter())
    logger.addHandler(console_handler)

    # Create log file if it does not exist
    if log_file and not Path(log_file).is_file():
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        Path(log_file).touch(exist_ok=True)

    # Optional file handler
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_fmt = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)

    logger.info(f"Logger '{name}' initialized with level {log_level.upper()}")
    return logger
