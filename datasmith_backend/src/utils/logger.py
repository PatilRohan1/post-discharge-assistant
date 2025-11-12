import traceback
from loguru import logger
from datetime import datetime
from src.constants.environment_constants import EnvironmentConstants


class Logger:
    def __init__(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        folder_path = EnvironmentConstants.LOG_FOLDER_PATH.value
        app_mode = EnvironmentConstants.APP_MODE.value

        if app_mode == "production":
            logger.remove()
            logger.add(
                f"{folder_path}/{current_date}/file_info.log",
                level="INFO",
                filter=lambda record: record["level"].name in ["INFO"],
                backtrace=False,
                diagnose=False,
                enqueue=True,
            )
            logger.add(
                f"{folder_path}/{current_date}/file_error.log",
                level="ERROR",
                backtrace=False,
                diagnose=False,
                enqueue=True,
            )
        else:
            logger.add(
                f"{folder_path}/{current_date}/file_info.log",
                level="INFO",
                filter=lambda record: record["level"].name in ["INFO"],
            )
            logger.add(f"{folder_path}/{current_date}/file_error.log", level="ERROR")

    @staticmethod
    def log_info_message(log_message):
        """
        get info logs across application
        """
        logger.info(log_message)

    @staticmethod
    def log_error_message(ex, log_message=""):
        """
        get error logs across application
        """
        logger.error(log_message)

        # use traceback for the stack frame in our code which we are interested in.
        tb_str_full = "".join(traceback.format_exception(type(ex), ex, ex.__traceback__))
        logger.error(f"Full traceback:\n{tb_str_full}")

        # use logger.error() for full traceback including libraries
        # logger.error(ex)
