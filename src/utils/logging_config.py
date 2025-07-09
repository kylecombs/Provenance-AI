import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path


def setup_logging(
    log_dir: str = "logs",
    log_level: str = "INFO",
    log_to_console: bool = True,
    log_to_file: bool = True
):
    """
    Set up logging configuration for the artwork identifier application.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_console: Whether to log to console
        log_to_file: Whether to log to file
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Generate timestamped log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"artwork_identifier_{timestamp}.log"
    
    # Define logging configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {},
        "loggers": {
            "": {  # Root logger
                "handlers": [],
                "level": log_level,
                "propagate": False
            },
            "artwork_identifier": {
                "handlers": [],
                "level": log_level,
                "propagate": False
            }
        }
    }
    
    # Add console handler if requested
    if log_to_console:
        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        }
        config["loggers"][""]["handlers"].append("console")
        config["loggers"]["artwork_identifier"]["handlers"].append("console")
    
    # Add file handler if requested
    if log_to_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "detailed",
            "filename": str(log_file),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        }
        config["loggers"][""]["handlers"].append("file")
        config["loggers"]["artwork_identifier"]["handlers"].append("file")
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log initial message
    logger = logging.getLogger("artwork_identifier")
    logger.info(f"Logging initialized. Log file: {log_file if log_to_file else 'None'}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__ from the calling module)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"artwork_identifier.{name}")


# Example usage in other modules:
# from src.utils.logging_config import get_logger
# logger = get_logger(__name__)
# logger.info("Module initialized")