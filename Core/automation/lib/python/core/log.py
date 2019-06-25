'''
This module bridges the `Python standard ``logging`` module
<https://docs.python.org/2/library/logging.html>` with openHAB logging. The
``configuration`` module also provides a `LOG_PREFIX` variable, which is used
as the default logger. This is used throughout the core modules and scripts,
including the ``log`` module. LOG_PREFIX can be modified based on personal
preference.

If openHAB Cloud Connector is installed, exceptions will be sent as a
notification. If the configuration.adminEmail variable is populated, the
notification will be sent to that person. Otherwise, a broadcast notification
will be sent.
'''

import logging
import functools
import traceback

from org.slf4j import Logger, LoggerFactory

from configuration import LOG_PREFIX

class Slf4jHandler(logging.Handler):
    def emit(self, record):
        message = self.format(record)
        logger_name = record.name
        if record.name == "root":
            logger_name = Logger.ROOT_LOGGER_NAME
        logger = LoggerFactory.getLogger(logger_name)
        level = record.levelno
        if level == logging.CRITICAL:
            logger.trace(message)
        elif level == logging.ERROR:
            logger.error(message)
        elif level == logging.DEBUG:
            logger.debug(message)
        elif level == logging.WARNING:
            logger.warn(message)
        elif level == logging.INFO:
            logger.info(message)
            
handler = Slf4jHandler()
logging.root.setLevel(logging.DEBUG)
logging.root.handlers = [handler]

def log_traceback(fn):
    """Decorator to provide better Jython stack traces"""
    functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except:
            rule_name = None
            if hasattr(fn, 'log'):
                fn.log.error(traceback.format_exc())
                rule_name = fn.name
            elif len(args) > 0 and hasattr(args[0], 'log'):
                args[0].log.error(traceback.format_exc())
                rule_name = args[0].name
            else:
                logging.getLogger(LOG_PREFIX).error(traceback.format_exc())
            import core.actions
            if hasattr(core.actions, 'NotificationAction'):
                import configuration
                if hasattr(configuration, 'admin_email') and configuration.admin_email != "admin_email@some_domain.com":
                    core.actions.NotificationAction.sendNotification(configuration.admin_email, "Exception: {}: [{}]".format(rule_name, traceback.format_exc()))
                else:
                    core.actions.NotificationAction.sendBroadcastNotification("Exception: {}: [{}]".format(rule_name, traceback.format_exc()))
    return wrapper
