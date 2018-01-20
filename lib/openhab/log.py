import logging
import functools
import traceback

from org.apache.logging.log4j import Logger, LogManager

LOG_PREFIX = "sboh2j"

def log_traceback(fn):
    """Decorator to provide better Jython stack traces"""
    functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as ex:
            if len(args) > 0 and hasattr(args[0], "log"):
                args[0].log.error(traceback.format_exc())
            else:
                logger = LogManager.getLogger(LOG_PREFIX)
                logger.error(traceback.format_exc())
            raise # Re-raise the exception (allowing a caller to see and handle the exception as well)
    return wrapper

class Log4j2Handler(logging.Handler):
    def emit(self, record):
        message = self.format(record)
        logger_name = record.name
        if record.name == "root":
            logger = LogManager.getLogger(LOG_PREFIX)
        else:
            logger = LogManager.getLogger(logger_name)
        level = record.levelno
        if level == logging.DEBUG:
            logger.debug(message)
        elif level == logging.INFO:
            logger.info(message)
        elif level == logging.WARN:
            logger.warn(message)
        elif level in [logging.ERROR, logging.CRITICAL]:
            logger.error(message)

handler = Log4j2Handler()
logging.root.setLevel(logging.DEBUG)
logging.root.handlers = [handler]
