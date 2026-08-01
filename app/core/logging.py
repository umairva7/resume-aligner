import logging
import sys
from app.core.config import settings

def setup_logging():
    """Configure structured application logging."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Root Logger setup
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Prevent duplicate handlers if re-initialized
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)

    return logging.getLogger("resume_aligner")

logger = setup_logging()
