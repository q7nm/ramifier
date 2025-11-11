import logging
import sys

logger = logging.getLogger("ramifier")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[%(levelname)s] [%(prefix)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def log_info(message: str, prefix: str ="ramifier"):
    logger.info(message, extra={"prefix": prefix})


def log_warning(message: str, prefix: str ="ramifier"):
    logger.warning(message, extra={"prefix": prefix})


def log_error(message: str, prefix: str ="ramifier"):
    logger.error(message, extra={"prefix": prefix})
