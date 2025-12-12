import logging
import asyncio
import os
from helper.report_error import report_error

# Ensure logs directory exists
if not os.path.exists("logs"):
    os.makedirs("logs")

class ErrorReportingHandler(logging.Handler):
    def __init__(self, app):
        super().__init__(level=logging.ERROR)
        self.app = app

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            full_log_message = self.format(record)
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(report_error(self.app, full_log_message))
            except RuntimeError:
                asyncio.run(report_error(self.app, full_log_message))

def init_logger(app, name=__name__, level=logging.INFO):
    """Initializes logger with Console, File, and Telegram reporting."""
    
    # 1. Basic Config - Logs to Console
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 2. File Handler - Saves errors to logs/error.log
    file_handler = logging.FileHandler("logs/error.log")
    file_handler.setLevel(logging.ERROR) # Only save Errors and Critical bugs
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # Add handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

    # 3. Suppress noisy libraries
    logging.getLogger("pyrogram").setLevel(logging.ERROR)

    # 4. Telegram Error Reporter
    if not any(isinstance(h, ErrorReportingHandler) for h in root_logger.handlers):
        root_logger.addHandler(ErrorReportingHandler(app))

    return logging.getLogger(name)
