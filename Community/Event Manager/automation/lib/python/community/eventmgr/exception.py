
from core.log import log_traceback 

from community.eventmgr.base import EventBase


class ConfigErrorException(EventBase, Exception):
    """Class used when raising exception for Configuration Errors.

    Attributes:
        message: The Error message
    """
    
    def __init__(self, message):
    
         # Call the base class constructor with the parameters it needs
        Exception.__init__(self, message)
