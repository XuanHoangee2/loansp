import os
import logging
from datetime import datetime
import structlog

class CustomLogger:
    def __init__(self, log_dir = "logs"):
        #ensure log directory exists
        self.log_dir = os.path.join(os.getcwd(), log_dir)
        os.makedirs(self.log_dir, exist_ok=True)

        #timestamp for log file
        log_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

        self.log_path_file = os.path.join(self.log_dir, log_file)

    def get_logger(self):
        logger_name = os.path.basename(self.log_path_file)

        #config logging for console + file 
        file_handler = logging.FileHandler(self.log_path_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[file_handler, console_handler],
        )

        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="ISO", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer(),
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        return structlog.get_logger(logger_name)
    
logger = CustomLogger().get_logger()
# logger.info("App started")
# logger.error("Something went wrong", error="File not found")