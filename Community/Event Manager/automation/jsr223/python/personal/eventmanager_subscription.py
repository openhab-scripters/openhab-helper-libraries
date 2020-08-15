
import traceback 

from core.log import log_traceback, logging, LOG_PREFIX
logger = logging.getLogger("{}.eventmgr".format(LOG_PREFIX))
try:
    from community.eventmgr.manager import EventManager
    from community.eventmgr.event import TimeEvent
    from community.eventmgr.exception import ConfigErrorException
except:
    logger.error(traceback.format_exc())

#Callback method
def callbackEvent(astroData):
    logger.info("[callbackEvent] id='{}', key='{}', data='{}'".format(astroData.getId(), astroData.getUserKey() , astroData.getState()))

def callbackTimeOfDay(todEvent):
    logger.info("[callbackTimeOfDay] RuleId='{}', EventId='{}', TimeOfDay='{}'".format(todEvent.getRuleId(), todEvent.getEventId(), todEvent.getState()))



#Class with Callback methods
class MyCallback(object):
    def __init__(self):
        self.logger = logging.getLogger("{}.astro.MyCallback".format(LOG_PREFIX))
    
    def callbackEvent(self, astroData):
        self.logger.info("[callbackEvent] id='{}', key='{}', data='{}'".format(astroData.getId(), astroData.getUserKey() , astroData.getState()))

    def callbackTimeOfDay(self, todEvent):
        self.logger.info("[callbackTimeOfDay] RuleId='{}', EventId='{}', TimeOfDay='{}'".format(todEvent.getRuleId(), todEvent.getEventId(), todEvent.getState()))




def scriptLoaded(*args):
    logger = logging.getLogger("{}.eventmgr".format(LOG_PREFIX))
    
    myCallback =  MyCallback()
    EventManager.subscribeEvent('Sunrise', callbackEvent, "SunriseMethodCallback")
    EventManager.subscribeEvent('Sunrise', myCallback.callbackEvent, "SunriseClassCallback")
    EventManager.subscribeEvent('Sunset', myCallback.callbackEvent)
    try:
        EventManager.subscribeEvent('Sunset1', myCallback.callbackEvent)    #Subscription to non existing event will fail
    except ConfigErrorException as ce:
        logger.error(ce)
        
    
    EventManager.subscribeTimeOfDayEvent('AstroTimeOfDay', callbackTimeOfDay, "TimeOfDay Method Callback")
    EventManager.subscribeTimeOfDayEvent('AlarmTimeOfDay', myCallback.callbackTimeOfDay, "TimeOfDay ClassMethod Callback")
    
    try:
        EventManager.subscribeTimeOfDayEvent('AstroTimeOfDay2', myCallback.callbackTimeOfDay) #Subscription to non existing event will fail
    except ConfigErrorException as ce:
        logger.error(ce)
    
    

def scriptUnloaded(*args):
    pass