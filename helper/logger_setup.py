
import logging
import asyncio
from helper.report_error import report_error

class ErrorReportingHandler(logging.Handler):
    def __init__(self, app):
        super().__init__(level=logging.ERROR)
        self.app = app

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            # Use self.format(record) to get the full formatted message including traceback
            full_log_message = self.format(record)
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(report_error(self.app, full_log_message))
            except RuntimeError:
                # If no loop is running, run it just for this task
                asyncio.run(report_error(self.app, full_log_message))

def init_logger(app, name=__name__, level=logging.INFO):
    """Initializes the logger with console and custom error reporting handlers."""
    # Set up global logging format and level
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Suppress info logs from pyrogram
    logging.getLogger("pyrogram").setLevel(logging.ERROR)

    # Attach error reporting handler to the root logger, so all errors are caught
    root_logger = logging.getLogger()
    
    # Avoid adding the handler multiple times if the logger is re-initialized
    if not any(isinstance(h, ErrorReportingHandler) for h in root_logger.handlers):
        root_logger.addHandler(ErrorReportingHandler(app))

    # Return your app's logger
    return logging.getLogger(name)
