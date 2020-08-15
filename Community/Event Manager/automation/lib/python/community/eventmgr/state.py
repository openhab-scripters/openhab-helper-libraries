
import traceback 
from abc import abstractmethod

from org.joda.time import DateTime

from core.log import log_traceback
from core.jsr223.scope import itemRegistry, DateTimeType

from community.eventmgr.base import EventBase
from community.eventmgr.event import TimeOfDayEvent


class StateProxy(EventBase):
    """Abstract class used to hold state of underlying data.

    The primary task of this internal base class is to ensure that states can be handled the same way for all kinds of events.

    Attributes:
        eventId: A String with the Id of the event that caused the state change.
    """

    @log_traceback
    def __init__(self, eventId):
        EventBase.__init__(self)
        self._eventId = eventId
    
    @log_traceback
    def getEventId(self):
        return self._eventId
    
    @abstractmethod
    def getState(self):
        pass
    


class ItemStateProxy(StateProxy):
    """Proxy class representing state for Items, used on Channel Events and Item State Changed.

    This class reads the Item State from openHAB Itemregistry.

    Attributes:
        eventId: A String with the Id of the event that caused the state change.
        itemName: Name of item.
    """
    @log_traceback
    def __init__(self, eventId, itemName):
        StateProxy.__init__(self, eventId)
        self._itemName = itemName

    @log_traceback
    def getState(self):
        return itemRegistry.getItem(self._itemName).state

    @log_traceback
    def getStateAsJoda(self):
        return DateTime(itemRegistry.getItem(self._itemName).state.toString())



class CronStateProxy(StateProxy):
    """Proxy class representing state for a CronEvent.

    This class holds the time that a Cron Job should fire and constructs a DateTime when querying state.

    Attributes:
        eventId: A String with the Id of the event that caused the state change.
        hour: Hour of Cron Job
        minute: Minute of Cron Job
        second: Second of Cron Job (Not used)
    """
    @log_traceback
    def __init__(self, eventId, hour, minute, second):
        StateProxy.__init__(self, eventId)
        self._hour = hour
        self._minute = minute
        self._second = second
        
    @log_traceback
    def getState(self):
        return DateTimeType( DateTime.now().withTime(self._hour, self._minute, self._second, 0).toString() )
    
    @log_traceback
    def getStateAsJoda(self):
        return DateTime.now().withTime(self._hour, self._minute, self._second, 0)
        


class TimeOfDayStateProxy(StateProxy):
    @log_traceback
    def __init__(self, todRuleId, timeOfDayEvents, initState):
        StateProxy.__init__(self, todRuleId)
        self._timeOfDayEvents = timeOfDayEvents
        self.state = initState
        
    @log_traceback
    def getState(self):
        return self.state


    @log_traceback
    def callback(self, eventData):
        self.Logger().debug(" [callback] id='{}', key='{}', state='{}'".format(eventData.getId(), eventData.getUserKey(), eventData.getState()))
        ruleId = eventData.getUserKey()
        eventId = eventData.getId()

        self.state = eventData.getState()
        self.Logger().info("[callback] State was changed to '{}'".format(eventData.getState()))

        timeOfDayEvents = self._timeOfDayEvents
        
        # Perform callback to all TimeOfDay event subscribers
        for subscription in self.dictTimeOfDaySubscriptions[ruleId]:
            try:
                self.Logger().debug("[callback] Id='{}', TimeOfDay='{}'".format(ruleId, subscription))    
                subscription.callback( TimeOfDayEvent(ruleId, eventId, timeOfDayEvents[eventId]) )
            except:
                self.Logger().error(traceback.format_exc())


