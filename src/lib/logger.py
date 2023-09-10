import logging
import os
from datetime import datetime

now = datetime.utcnow()
date = now.strftime("%Y-%m-%d")


def generate_logger(logger_name, level=logging.INFO):
    """
    The generate_logger function creates a logger object that can be used to log messages.
    The function takes two arguments:
        - logger_name: The name of the logger, which will be used as the filename for logs.
        - level: The logging level (defaults to INFO). This is passed directly into setLevel().

    :param logger_name: Name the logger and set the log file name
    :param level: Set the logging level for the logger
    :return: A logger object
    """
    log_path = None
    home_dir = os.path.expanduser("~")
    system_log_path = f"/var/log/{logger_name}"
    backup_log_path = f"{home_dir}/.logs/{logger_name}"
    if not os.path.exists(system_log_path):
        try:
            os.makedirs(system_log_path)
            log_path = system_log_path
        except PermissionError:
            if not os.path.exists(backup_log_path):
                os.makedirs(backup_log_path)
            else:
                log_path = backup_log_path
    else:
        log_path = backup_log_path
    # Create a logger
    logger = logging.getLogger(logger_name)

    # Set the logging level (you can adjust this as needed)
    logger.setLevel(level)

    # Create a formatter to include timestamp, function, and line number
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - '
                                  '%(message)s')

    # Create a file handler to log to a file
    if log_path is None:
        print(f"Failed to setup logging")
        exit(255)
    file_handler = logging.FileHandler(f'{log_path}/{date}.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Create a stream handler to log to stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger
