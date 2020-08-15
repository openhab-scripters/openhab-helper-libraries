import traceback
from abc import abstractmethod

from core.log import log_traceback, logging
from community.eventmgr import LOG_CONTEXTNAME


class EventBase(object):
    """Shared abstract class for all EventHandler JSR223 classes.

    The primary task of this base class is to ensure logging is done in an uniform way

    Attributes:
        name: A String that can hold an additional name added to the LogContext if given.
        log: Log context
    """
    
    @abstractmethod
    @log_traceback
    def __init__(self, name = None):
        self.Name = name
        if name=="" or name is None:
            self.log = logging.getLogger(u"{}.{}".format(LOG_CONTEXTNAME,  self.__class__.__name__))
        else:
            self.log = logging.getLogger(u"{}.{}.{}".format(LOG_CONTEXTNAME,  self.__class__.__name__, self.Name.decode('utf8')))


    def Logger(self):
        """
        Access to Logger instance for that class

        Args:

        Returns:
            An instance of the logger for the class
        """
        return self.log

    def getName(self):
        """
        Get Additional Name if set, else None

        Args:

        Returns:
            String representing the Name or None if not set
        """
        return self.Name

