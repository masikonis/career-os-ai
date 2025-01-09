import logging
import sys


def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """Get a logger instance with the specified name."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.setLevel(level)
        logger.propagate = False

    return logger
