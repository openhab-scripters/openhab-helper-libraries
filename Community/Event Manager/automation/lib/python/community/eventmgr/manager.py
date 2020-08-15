# -*- coding: utf-8 -*-

import traceback 

from core.jsr223 import scope
from core.jsr223.scope import ir, DateTimeType
from core.log import log_traceback
from core.actions import ScriptExecution
from core.date import to_joda_datetime
from core.rules import addRule
from core.triggers import ChannelEventTrigger, CronTrigger, ItemStateChangeTrigger, ItemStateUpdateTrigger
from core.items import add_item, remove_item
from core.links import add_link
from core.metadata import set_metadata, get_key_value

from community.eventmgr import EVENTMANAGER_LIB_VERSION
from community.eventmgr.base import EventBase
from community.eventmgr.event import TimeEvent, TimeOfDayEvent
from community.eventmgr.exception import ConfigErrorException
from community.eventmgr.rule import EventHandlerRule
from community.eventmgr.state import CronStateProxy, ItemStateProxy, TimeOfDayStateProxy

from configuration import eventmgr_configuration as configuration


from org.joda.time import DateTime



class EventSubscription(EventBase):

    @log_traceback
    def __init__(self, EventId, CallbackKey, Callback):
        EventBase.__init__(self)

        self.Logger().debug("[EventSubscription] Subscribe to event Id='{}', CallbackKey='{}'".format(EventId, CallbackKey))
        self.eventId = EventId
        self.callback = Callback
        self.callbackKey = CallbackKey

class EventManager(EventBase): 
    """
    Singleton Manager class 
    """
    _instance = None
    
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance
    
    @classmethod
    def getInstance(class_):
        if not isinstance(class_._instance, class_):
            class_._instance = EventManager()
        return class_._instance


    @log_traceback
    def __init__(self):
        
        EventBase.__init__(self)
        
        self.__version__ = EVENTMANAGER_LIB_VERSION
        self.__version_info__ = tuple([ int(num) for num in self.__version__.split('.')])

        self.Logger().info("Starting EventManager Version {}".format(self.__version__))

        try:
            self.dictEventSubscriptions = {}
            self.dictTimeOfDaySubscriptions = {}

            
            
            self.dictChannel2EventId = {}   # Translation from Channel to EventId
            
            
            self.dictCron2EventId = {}  # Translation from Cron JobId to EventId

            
            self.dictEventId2StateProxy = {}    # Dictionary of all state proxies for Events
            self.dictTimeOfDay2StateProxy = {}  # Dictionary of all state proxies for TimeOfDay
            
            self.RuleUID = None
            
            self._AstroJsr223MetadataKey = 'EventHandlerJSR223'
            self._MetadataEventKey = 'EventId'
            self._JSR223Tag = '#EventHandlerJSR223#'

            # Read configuration
            self._ruleName = configuration['RULENAME']
            self._itemPrefix = configuration['ITEM_PREFIX']
            self._EventConfig = configuration['EVENTS']
            self._TimeOfDay = configuration['TIME_OF_DAY']
            self._groupItemName = '{}_group'.format(self._itemPrefix)
            self._eventHandlerRule = EventHandlerRule(self, self._ruleName)
            
            self.cleanup()

            self.initialize()
            
            self.initializeTimeOfDay()

            self.Logger().debug("Initialized EventManager")
        except:
            self.Logger().error(traceback.format_exc())

    @classmethod
    def getEventState(cls, eventId):
        """
        Get Actual state of event 

        Args: 
            eventId: Id of the Event being queried

        Returns:
            String representing the State
        """
        return cls.getInstance()._getEventState(eventId)

    @classmethod
    def getTimeOfDayState(cls, timeOfDayId):
        """
        Get Actual state of TimeOfDay 

        Args: 
            timeOfDayId: Id of the TimeOfDay 

        Returns:
            String representing the State of the TimeOfDay
        """
        return cls.getInstance()._getTimeOfDayState(timeOfDayId)
        
    @classmethod
    def subscribeEvent(cls, eventId, callback, userKey = None ):
        """
        Called to subscribe to events

        Args: 
            eventId: Id of the TimeOfDay 
            callback: Method to callback when event is triggered
            userKey: User defined metadata (string) to return in callback

        Returns:
            None
        """
        cls.getInstance()._subscribeEvent(eventId, callback, userKey) 

    @classmethod
    def subscribeTimeOfDayEvent(cls, eventId, callback, userKey = None ):
        """
        Called to subscribe to events

        Args: 
            eventId: Id of the TimeOfDay 
            callback: Method to callback when event is triggered
            userKey: User defined metadata (string) to return in callback

        Returns:
            None
        """
        cls.getInstance()._subscribeTimeOfDayEvent(eventId, callback, userKey) 

    @log_traceback
    def _getEventState(self, eventId):
        if (self.dictEventId2StateProxy.has_key(eventId)):
            return self.dictEventId2StateProxy[eventId].getState()
        self.Logger().warn("[_getEventState] Event '{}' was not found. No state returned".format(eventId))
        return None

    @log_traceback
    def _getTimeOfDayState(self, timeOfDayId):
        if (self.dictTimeOfDay2StateProxy.has_key(timeOfDayId)):
            return self.dictTimeOfDay2StateProxy[timeOfDayId].getState()
        self.Logger().warn("[_getTimeOfDayState] TimeOfDay Rule '{}' was not found. No state returned".format(timeOfDayId))
        return None


    def _subscribeEvent(self, eventId, callback, userKey):
        if eventId in self.dictEventSubscriptions.keys():
            self.Logger().info("[_subscribeEvent] Create subscription to event '{}' with UserKey '{}'".format(eventId, userKey))
            self.dictEventSubscriptions[eventId].append( EventSubscription(eventId, userKey, callback) )

            if (self.dictEventId2StateProxy.has_key(eventId)):
                return self.dictEventId2StateProxy[eventId].getState()
            else:
                self.Logger().error("Cannot find current state of Event because eventid '{}' does not exist in dictionary.".format(eventId))

        else:
            message = "Cannot create Event subscription because eventid '{}' does not exist in configuration.".format(eventId)
            self.Logger().warn("[_subscribeEvent] {}".format(message))
            raise ConfigErrorException(message)

        return None

    
    def _subscribeTimeOfDayEvent(self, todRuleId, callback, userKey):
        if todRuleId in self.dictTimeOfDaySubscriptions.keys():
            self.Logger().info("[_subscribeTimeOfDayEvent] Create subscription to TimeOfDay event ruleId '{}' and userKey '{}'".format(todRuleId, userKey))
            self.dictTimeOfDaySubscriptions[todRuleId].append( EventSubscription(todRuleId, userKey, callback) )
        else:
            message = "Cannot create TimeOfDay subscription because TimeOfDay rule '{}' does not exist in configuration.".format(todRuleId)
            self.Logger().warn("[_subscribeTimeOfDayEvent] {}".format(message))
            raise ConfigErrorException(message)

    @log_traceback
    def cleanup(self):
        self.Logger().debug("[CLEANUP]: Performing cleanup (Removing all items)")
        if not scope.itemRegistry.getItems(self._groupItemName):
            self.Logger().debug("[CLEANUP]: No items found")
            return

        for item in scope.itemRegistry.getItem(self._groupItemName).members:
            self.Logger().debug("[CLEANUP]:  Removing item='{}'".format(item))
            remove_item(item.name)

        if scope.itemRegistry.getItem(self._groupItemName):
            self.Logger().debug("[CLEANUP]: Removing groupitem='{}'".format(self._groupItemName))
            remove_item(self._groupItemName)

    
    @log_traceback
    def initialize(self):
        if not scope.itemRegistry.getItems(self._groupItemName):
            self.log.debug("[INITIALIZE] Creating groupitem '{}'!".format(self._groupItemName))
            self.ensureItemCreated(self._groupItemName, 'Group', 'EventHandler JSR223 group', [self._JSR223Tag])

        for event in self._EventConfig:            #Extract Id and trigger from configuration
            eventId = event['id']
            eventTrigger = event['trigger']
            self.log.debug("[INITIALIZE] Processing config for id='{}' is '{}'".format(eventId, eventTrigger))

            self.generateTrigger(eventId, eventTrigger)
        
        newRule = addRule(self._eventHandlerRule)   # Activate Rule
        self.RuleUID = newRule.UID
        self.log.debug("EventHandlerRule created UID='{}'".format(self.RuleUID))


    @log_traceback
    def initializeTimeOfDay(self):
        self.Logger().debug("[initializeTimeOfDay] _TimeOfDay: '{}'".format(self._TimeOfDay))
        
        for ruleTimeOfDay in self._TimeOfDay:
            
            ruleId = ruleTimeOfDay['id']
            dictRules = ruleTimeOfDay['events']
            self.Logger().debug("[initializeTimeOfDay] Processing rule '{}' with states '{}'".format(ruleId, dictRules))

            dictInitValues = {}
            
            # ##################
            # Initialize
            # ##################
            now = DateTime.now()
            
            #Set to last state
            initialState = dictRules.items()[-1][1]
            objTimeOfDayProxy = None
            
            for idx1, (eventId, eventValue) in enumerate(dictRules.iteritems()):  # Find current/initial State
                if not self.dictEventId2StateProxy[eventId].getStateAsJoda().isBefore(now):
                    self.Logger().debug("[TimeOfDay] Initial state for TimeOfDay '{}' is '{}'".format(ruleId, initialState))
                    objTimeOfDayProxy = TimeOfDayStateProxy(ruleId, dictRules, initialState)
                    break
                initialState = eventValue


            # All are after now, => we are after last entry but on a new day (after midnight), and before states was updated
            if objTimeOfDayProxy is None:
                objTimeOfDayProxy = TimeOfDayStateProxy(ruleId, dictRules, dictRules.items()[-1][1])


            
            # Create subscriptions
            for idx1, (eventId, eventValue) in enumerate(dictRules.iteritems()):
                self.Logger().debug("[TimeOfDay] Create underlying Event Subscription for TimeOfDayEvent key='{}', TimeOfDay='{}' ruleId='{}'".format(eventId, eventValue, ruleId))
                self._subscribeEvent(eventId, self.callbackTimeOfDay, ruleId)
    
            # Add State Proxy to dictinary
            self.dictTimeOfDay2StateProxy[ruleId] = objTimeOfDayProxy
            
            # prepare for subscriptions
            self.dictTimeOfDaySubscriptions[ruleId] = []
    

    
                
    @log_traceback
    def ensureItemCreated(self, itemName, itemType, itemLabel = '', listTags = [], listGroups = []):
        """
        Ensure Group Item is created
        """
        self.log.debug("[ensureItemCreated] Ensure item '{}' is created".format(itemName))
        if scope.itemRegistry.getItems(itemName):
            remove_item(itemName)
        if not scope.itemRegistry.getItems(itemName):
            self.log.debug("[ensureItemCreated] Creating item '{}'!".format(itemName))
            add_item(itemName, item_type=itemType, label=itemLabel, groups=listGroups, tags=listTags)

    
               
    @log_traceback
    def addTrigger(self, objTrigger):
        """
        When adding a new trigger rule needs to be unrigistered
        """
        
        try:
            ruleRegistry.remove(self.RuleUID)   # Remove if exists
        except:
            pass

        self._eventHandlerRule.addTrigger(objTrigger)
        addRule(self._eventHandlerRule)
        


    @log_traceback
    def generateTrigger(self, eventId, trigger):

        try:
            self.Logger().debug("[generateTrigger] Trigger='{}'".format(trigger))
            
            #Create Astro Channel Trigger
            if trigger.has_key('astro'):
                self.Logger().debug("[generateTrigger] Astro Channel Trigger!")
                self.generateAstroChannelTrigger(eventId, trigger['astro'])
            
            #Create CronTrigger
            elif trigger.has_key('time'):
                self.generateCronTrigger(eventId, trigger['time'])
            
            else:
                self.Logger().error("[generateTrigger] Trigger type is unknown/unsupported, nothing will be created! => {}".format(trigger))
          
        except:
            self.Logger().error((traceback.format_exc()))

    @log_traceback
    def generateCronTrigger(self, eventId, triggerTime):
        """
        Validate and create CronTrigger event to subscription dictionary
        """
        try:
            self.Logger().debug("[generateCronTrigger] EventId='{}' Time='{}'".format(eventId, triggerTime))
            
            hour = triggerTime['hour']
            minute = triggerTime['minute']
            second = 0 
            if triggerTime.has_key('second'):
                second = 0
                self.Logger().warn("CronTrigger for event '{}' contains seconds, this is not supported for CronTriggers. Defaulting seconds to '00'".format(eventId))

            self.Logger().debug("[generateCronTrigger] Time Trigger! hour='{}', minute='{}', second='{}'".format(hour, minute, second))
            
            key = self.getCronTriggerKey(hour, minute, second)
            triggerName = 'CRON_{}'.format(key)
            
            cronJob = "{} {} {} * * ?".format(second, minute, hour)
            cronTrigger = CronTrigger(cronJob, trigger_name=triggerName)
            
            self.dictCron2EventId[key] = eventId    # Create mapping between Cron JobId and EventId
            
            self.dictEventId2StateProxy[eventId] = CronStateProxy(eventId, hour, minute, second)    #Create a State proxy and add to dictionary

            self._eventHandlerRule.addTrigger(cronTrigger)   # Add trigger to rule

            self.dictEventSubscriptions[eventId] = [] # Prepare entry in dictionary to subscribe to this event
 
            self.Logger().info("[generateCronTrigger] CronTrigger '{}' (CronJob='{}'), for event '{}' generated (dictionary key='{}')".format(triggerName, cronJob, eventId, key))
        except:
            self.Logger().error((traceback.format_exc()))



    @log_traceback
    def getCronTriggerKey(self, hour, minute, second = 0):
        return "{:02d}{:02d}{:02d}".format(hour, minute, second)


    @log_traceback
    def generateAstroChannelTrigger(self, eventId, channelName):
        '''
        Validate requested channel and generates Items to subscribe
        '''
        generatedItems = []

        # Lists to validate against
        supportedBindings = ['astro']
        supportedAstroThings = ['sun', 'moon']
        supportedSunEventGroups = ['rise', 'set', 'noon', 'night', 'morningNight', 'astroDawn', 'nauticDawn', 'civilDawn', 'astroDusk', 'nauticDusk', 'civilDusk', 'eveningNight', 'daylight']
        supportedMoonEventGroups = ['rise', 'set']
        supportedAstroEvents = ['start', 'end'] #, 'event']


        strLink = channelName.replace('#',':').split(':')
        triggerBinding = strLink[0]
        triggerThing = strLink[1]
        triggerThingContext = strLink[2]
        triggerEventGroup = strLink[3]
        triggerEvent = strLink[4]
        self.Logger().debug("[generateAstroChannelTrigger] - Binding='{}' Thing='{}' Context='{}', EventGroup='{}', Event='{}'".format(triggerBinding, triggerThing, triggerThingContext, triggerEventGroup, triggerEvent))
        try:
            # #######################
            # Validation
            # #######################
            if triggerThing not in supportedAstroThings:
                self.log.error("Requested Astro thing '{}' is not supported. Supported things is '{}'".format(triggerThing, supportedAstroThings))
                return None
            
            elif triggerThing=='sun' and triggerEventGroup not in supportedSunEventGroups:
                self.log.error("Requested Astro event context '{}' is not supported for 'sun' Thing. Supported event context is '{}'".format(triggerEventGroup, supportedSunEventGroups))
                return None

            elif triggerThing=='moon' and triggerEventGroup not in supportedMoonEventGroups:
                self.log.error("Requested Astro event context '{}' is not supported for 'moon' Thing. Supported event context is '{}'".format(triggerEventGroup, supportedMoonEventGroups))
                return None

            elif triggerEvent not in supportedAstroEvents:
                self.log.error("Requested Astro event '{}' is not supported. Supported events is '{}'".format(triggerEvent, supportedAstroEvents))
                return None
            
            
            # #######################
            # Create  items and triggers
            # #######################
            
            # Generate Item so that we always have actual state
            itemName = self.generateUniqueItem( triggerBinding, 
                                                triggerThing, 
                                                triggerThingContext, 
                                                triggerEventGroup, 
                                                triggerEvent, 
                                                channelName, 
                                                eventId)

            # Generate Channel Trigger so that we always get notified when event occurs
            channelTriggerName = ':'.join([triggerBinding, triggerThing, triggerThingContext, triggerEventGroup]) + '#event'
            triggerName = 'ASTRO_{}'.format(eventId)

            channelTrigger = ChannelEventTrigger(channelTriggerName, triggerEvent.upper(), trigger_name = triggerName)
            
                    
            self.dictEventId2StateProxy[eventId] = ItemStateProxy(eventId, itemName)
            self.dictChannel2EventId[channelName] = eventId

            # Add Channel Trigger
            self._eventHandlerRule.addTrigger(channelTrigger)
                
            # Prepare entry in dictionary to subscribe to this event
            self.dictEventSubscriptions[eventId] = []
            
            self.Logger().info("[generateAstroChannelTrigger] Trigger '{}' for channel '{}' with event='{}' generated (EventId='{}')".format(triggerName, channelTriggerName, triggerEvent.upper(), eventId))
        except:
            self.Logger().error(traceback.format_exc())                
        
    
    @log_traceback
    def generateUniqueItem(self, triggerBinding, triggerThing, triggerThingContext, triggerEventGroup, triggerEvent, triggerName, eventId):
        """
        Ensure that a unique name is generated for the Shadow Item being generated
        """
        #Create unique name for item
        joinedItemName = '_'.join([self._itemPrefix, triggerThing, triggerThingContext, triggerEventGroup, triggerEvent])
        itemName = joinedItemName.replace('-', '_')

        self.Logger().debug("[GENERATE] Item '{}' with trigger '{}'".format(itemName, triggerName))
         
        # Create Item and set Tag
        itemType= 'DateTime'
        itemLabel = '{} - ## DO NOT CHANGE USED BY EVENTHANDLERJSR223 ## [%s]'.format(itemName)
        listGroups = [self._groupItemName]
        listTags = [self._JSR223Tag]
        self.ensureItemCreated(itemName, itemType, itemLabel, listTags, listGroups)

        # Link item to channel
        add_link(itemName, triggerName)

        # Set Metadata on Item (EventId)
        set_metadata(itemName, self._AstroJsr223MetadataKey, { self._MetadataEventKey : eventId }, overwrite=True)
        return itemName


    @log_traceback
    def processEvent(self, module, inputs):
        """
        Event Handler method (Called from Rule Event handler)
        """
        
        self.Logger().info("[processEvent] module='{}', inputs='{}'".format(module, inputs))
        
        itemName = ''
        eventId = ''
        itemState = None
        
        try:
            
            if inputs.has_key('event'):
                self.Logger().info("[processEvent] event='{}'".format(inputs['event']))
                
                event = inputs['event']
                
                # It was triggered by a channel event
                if hasattr(event, 'channel'):
                    self.Logger().info("[processEvent] is a channel event channel='{}', event='{}'".format(event.channel, event.event))
                    channelName = str(event.channel)
                    eventName = str(event.event)
                    channelEventName = channelName.replace('#event', '#{}'.format(eventName.lower()))
                    self.Logger().debug("[processEvent] is a channel event channel='{}', event='{}' convert='{}'".format(event.channel, event.event, channelEventName))


                    if self.dictChannel2EventId.has_key(channelEventName):
                        eventId = self.dictChannel2EventId[channelEventName]
                    else:
                        self.Logger().error("No Event was found for channel '{}' when processing".format(channelEventName))
                        return
                    
                elif hasattr(event, 'itemName'):
                    self.Logger().debug("[processEvent] is an item triggered event")
                    itemName = inputs['event'].getItemName()
                    # Get EventId from Metadata
                    eventId = get_key_value(itemName, self._AstroJsr223MetadataKey, self._MetadataEventKey)
                    
            else:
                now = DateTime.now()
                #For now only use minutes
                key = self.getCronTriggerKey(now.getHourOfDay(), now.getMinuteOfHour(), 0)
                eventId = self.dictCron2EventId[key]
                self.Logger().debug("[processEvent] is an Cron triggered event TriggerKey='{}', EventId='{}'".format(key, eventId))


            if eventId != '':
                if self.dictEventId2StateProxy.has_key(eventId):
                    eventState = self.dictEventId2StateProxy[eventId].getState()
                else:
                    self.Logger().error("[processEvent] No StateProxy found for event '{}'. Subscribers will not get notified.".format(eventId))    
                    return

                self.Logger().debug("[processEvent] Id='{}', State='{}'".format(eventId, eventState))    

                # Perform callback to all Astro event subscribers
                for subscription in self.dictEventSubscriptions[eventId]:
                    
                    try:
                        self.Logger().info("[processEvent] SUBSCRIPTION='{}' - Sending event '{}' with state '{}' to subscriber".format(subscription, eventId, eventState)) 
                        subscription.callback(TimeEvent(eventId, subscription.callbackKey, eventState))
                    except:
                        self.Logger().error(traceback.format_exc())
            else:
                self.Logger().error("EventId was not found when processing event. Input='{}'".format(input))
                return
        except:
            self.Logger().error(traceback.format_exc())

        

    
    @log_traceback
    def callbackTimeOfDay(self, eventData):
        self.Logger().info("[TIMEOFDAY-CALLBACK] id='{}', key='{}', data='{}'".format(eventData.getId(), eventData.getUserKey(), eventData.getState()))
        #userKey = eventData.getUserKey()
        ruleId = eventData.getUserKey()
        eventId = eventData.getId()
        timeOfDay = self._TimeOfDay

        #Find affected rule
        timeOfDayRule = list(filter(lambda timeOfDayItem: timeOfDayItem['id'] in ruleId, timeOfDay))
        if len(timeOfDayRule)==0:
            self.Logger().error("[callbackTimeOfDay] Nothing found for TimeOfDay subscription for Rule with Id '{}'".format(ruleId))
            return

        timeOfDayEvents = timeOfDayRule[0]['events']

        # Perform callback to all TimeOfDay event subscribers
        for subscription in self.dictTimeOfDaySubscriptions[ruleId]:
            try:
                self.Logger().debug("[callbackTimeOfDay] Performing callback to subscriber with ruleId='{}', eventId='{}', TimeOfDay='{}'".format(ruleId, eventId, subscription))    
                subscription.callback( TimeOfDayEvent(ruleId, eventId, timeOfDayEvents[eventId]) )
            except:
                self.Logger().exception(traceback.format_exc())    
    
