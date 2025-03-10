import logging
from logging.handlers import RotatingFileHandler
import pathlib
from config import path_to_logs, api_logs_filename, zomboid_logs_filename, log_file_max_size, discord_logs_filename

log_file_size = (log_file_max_size * 1024) * 1024

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

api_logger = logging.getLogger("api")
api_logger.setLevel(logging.DEBUG)

api_file_rotator = RotatingFileHandler(
    pathlib.Path(path_to_logs, api_logs_filename), maxBytes=log_file_size, backupCount=10, encoding="utf-8",
)
api_file_rotator.setFormatter(formatter)

api_logger.addHandler(api_file_rotator)

zomboid_logger = logging.getLogger("zomboid")
zomboid_logger.setLevel(logging.DEBUG)

zomboid_file_rotator = RotatingFileHandler(
    pathlib.Path(path_to_logs, zomboid_logs_filename), maxBytes=log_file_size, backupCount=10, encoding="utf-8",
)
zomboid_file_rotator.setFormatter(formatter)

zomboid_logger.addHandler(zomboid_file_rotator)

discord_bot_logger = logging.getLogger("discord")
discord_bot_logger.setLevel(logging.DEBUG)

discord_bot_file_rotator = RotatingFileHandler(
    pathlib.Path(path_to_logs, discord_logs_filename), maxBytes=log_file_size, backupCount=10, encoding="utf-8",
)
discord_bot_file_rotator.setFormatter(formatter)

discord_bot_logger.addHandler(discord_bot_file_rotator)
