import logging
import functools
import traceback

from org.slf4j import Logger, LoggerFactory

LOG_PREFIX = "org.eclipse.smarthome.automation.rules"

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
                print traceback.format_exc()
    return wrapper

class Slf4jHandler(logging.Handler):
    def emit(self, record):
        message = self.format(record)
        logger_name = record.name
        if record.name == "root":
            logger_name = Logger.ROOT_LOGGER_NAME
        logger = LoggerFactory.getLogger(logger_name)
        level = record.levelno
        if level == logging.DEBUG:
            logger.debug(message)
        elif level == logging.INFO:
            logger.info(message)
        elif level == logging.WARN:
            logger.warn(message)
        elif level in [logging.ERROR, logging.CRITICAL] :
            logger.error(message)
            
handler = Slf4jHandler()
logging.root.setLevel(logging.DEBUG)
logging.root.handlers = [handler]

