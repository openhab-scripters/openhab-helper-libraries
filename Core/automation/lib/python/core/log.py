"""
This module bridges the `Python standard logging module <https://docs.python.org/2/library/logging.html>`_
with the slf4j library used by openHAB. The ``configuration`` module provides
a ``LOG_PREFIX`` variable that is used as the default logger throughout the
core modules and scripts.
"""
__all__ = [
    "LOG_PREFIX",
    "logging",
    "getLogger",
    "log_traceback"
]

try:
    import typing as t
except:
    pass

import logging
import traceback
from functools import wraps

from org.slf4j import Logger, LoggerFactory

try:
    import configuration
    LOG_PREFIX = configuration.LOG_PREFIX # type: str
except:
    LOG_PREFIX = "jython"
    LoggerFactory.getLogger("{}.core.log".format(LOG_PREFIX)).warn("The 'configuration.py' file is missing from the python.path!")

TRACE = 5

class Slf4jHandler(logging.Handler):
    def emit(self, record):
        message = self.format(record)
        logger_name = record.name
        if record.name == "root":
            logger_name = Logger.ROOT_LOGGER_NAME
        logger = LoggerFactory.getLogger(logger_name)
        level = record.levelno
        if level == logging.CRITICAL:
            logger.error(message)
        elif level == logging.ERROR:
            logger.error(message)
        elif level == logging.DEBUG:
            logger.debug(message)
        elif level == logging.WARNING:
            logger.warn(message)
        elif level == logging.INFO:
            logger.info(message)
        elif level == TRACE:
            logger.trace(message)

class Slf4jLogger(logging.Logger):
    def trace(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'TRACE'.
        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.
        logger.trace("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        if self.isEnabledFor(TRACE):
            self._log(TRACE, msg, args, **kwargs)


HANDLER = Slf4jHandler()
logging.addLevelName(TRACE, "TRACE")
logging.setLoggerClass(Slf4jLogger)
logging.root.setLevel(TRACE)
logging.root.handlers = [HANDLER]


def getLogger(name, prefix=None):
    # type: (t.Optional[str], str) -> Slf4jLogger
    if not prefix and name:
        prefix = LOG_PREFIX
    if name:
        name = u"{}.{}".format(prefix.strip("."), name.strip("."))
    return logging.getLogger(name)


def log_traceback(function):
    """
    Decorator to provide better Jython stack traces

    Essentially, the decorated function/class/method is wrapped in a try/except
    and will log a traceback for exceptions. If openHAB Cloud Connector is
    installed, exceptions will be sent as a notification. If the
    configuration.adminEmail variable is populated, the notification will be
    sent to that address. Otherwise, a broadcast notification will be sent.
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            rule_name = None
            if hasattr(function, 'log'):
                function.log.warn(traceback.format_exc())
                rule_name = function.name
            elif args and hasattr(args[0], 'log'):
                args[0].log.warn(traceback.format_exc())
                rule_name = args[0].name
            else:
                logging.getLogger(LOG_PREFIX).warn(traceback.format_exc())
            import core.actions
            if hasattr(core.actions, 'NotificationAction'):
                try:
                    import configuration
                    if hasattr(configuration, 'admin_email') and configuration.admin_email != "admin_email@some_domain.com":
                        core.actions.NotificationAction.sendNotification(configuration.admin_email, "Exception: {}: [{}]".format(rule_name, traceback.format_exc()))
                except:
                    core.actions.NotificationAction.sendBroadcastNotification("Exception: {}: [{}]".format(rule_name, traceback.format_exc()))
    return wrapper
