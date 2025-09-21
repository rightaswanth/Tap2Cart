import sys
from datetime import datetime
from pathlib import Path
from loguru import logger

# Create a logs directory inside the system temp folder
LOG_DIR = Path("/var/log/tap2cart")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Log file path with current date
LOG_FILE = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"

# Remove default logger
logger.remove()

# Add file logger
logger.add(
    LOG_FILE,
    rotation="1 day",         # New log file every day
    retention="10 days",      # Keep logs for 10 days
    compression="zip",        # Compress old logs
    enqueue=True,             # Safe for multi-thread/multi-process
    serialize=True,           # JSON format for structured logging
    level="INFO",             # Default log level
)

# Optional: console logging for dev environment
# logger.add(
#     sys.stdout,
#     colorize=True,
#     format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
#            "<level>{level}</level> | "
#            "<cyan>{module}</cyan>:<cyan>{line}</cyan> - "
#            "<level>{message}</level>",
#     level="DEBUG",
# )

# Example usage
# logger.info("Logger initialized")
