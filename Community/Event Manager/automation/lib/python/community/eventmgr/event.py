
from core.log import log_traceback 
from core.jsr223 import scope

from community.eventmgr.base import EventBase


class TimeEvent(EventBase):
    """Class used in event callbacks for Time Events.

    The primary task of this base class is to ensure logging is done in an uniform way

    Attributes:
        id: A String with the EventId that was fired.
        userKey: User defined Key when subscribing
        state: DateTimeType indicating the state of the event that was fired
    """
    @log_traceback
    def __init__(self, id, userKey, state):
        EventBase.__init__(self)
        self.id = id
        self.userKey = userKey
        self.state = state

    @log_traceback
    def getId(self):
        """
        Get method for the id

        Args:

        Returns:
            Id
        """
        return self.id

    @log_traceback
    def getUserKey(self):
        """
        Get method for the User defined key

        Args:

        Returns:
            UserKey
        """
        return self.userKey

    
    @log_traceback
    def getState(self):
        """
        Get method for the State

        Args:

        Returns:
            State
        """
        return self.state
    

class TimeOfDayEvent(EventBase):
    """Class used in event callbacks for TimeOfDay Events.

    The primary task of this base class is to ensure logging is done in an uniform way

    Attributes:
        ruleId: A String with the Id of the TimeOfDay Rule that changed state.
        eventId: A String with the Id of the event that caused the state change.
        userKey: User defined Key when subscribing
        state: String defined in config, indicating the current state
    """
    
    @log_traceback
    def __init__(self, ruleId, eventId, eventName):
        EventBase.__init__(self)
        self.ruleId = ruleId
        self.eventId = eventId
        self.eventName = eventName

    @log_traceback
    def getRuleId(self):
        """
        Get method for the RuleId

        Args:

        Returns:
            RuleId as String for
        """
        return self.ruleId

    @log_traceback
    def getEventId(self):
        """
        Get method for the EventId

        Args:

        Returns:
            EventId as String that triggered the state change
        """
        return self.eventId

    @log_traceback
    def getEventName(self):
        return self.eventName

    @log_traceback
    def getState(self):
        """
        Get method for the State

        Args:

        Returns:
            State as String (defined in Configuration) for the new state of TimeOfDay.
        """
        return self.eventName

