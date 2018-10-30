import inspect
import json
import uuid

import java.util
from java.nio.file.StandardWatchEventKinds import ENTRY_CREATE, ENTRY_DELETE, ENTRY_MODIFY

from org.eclipse.smarthome.automation.core.util import TriggerBuilder
from org.eclipse.smarthome.automation import Trigger
from org.eclipse.smarthome.automation.handler import TriggerHandler
from org.eclipse.smarthome.automation.type import TriggerType
from org.eclipse.smarthome.config.core import Configuration
from org.eclipse.smarthome.core.thing import ChannelUID
from org.eclipse.smarthome.core.thing import ThingUID
from org.eclipse.smarthome.core.types import TypeParser
#from org.eclipse.smarthome.core.thing import ThingStatus

import openhab
from openhab.jsr223 import scope
from openhab.osgi.events import OsgiEventTrigger
from openhab.log import logging, LOG_PREFIX

from org.slf4j import Logger, LoggerFactory

from org.quartz.CronExpression import isValidExpression

scope.scriptExtension.importPreset("RuleSimple")
scope.scriptExtension.importPreset("RuleSupport")
scope.scriptExtension.importPreset("RuleFactories")

log = LoggerFactory.getLogger("org.eclipse.smarthome.automation.core.internal.RuleEngineImpl")

class ItemStateUpdateTrigger(Trigger):
    def __init__(self, itemName, state=None, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        config = { "itemName": itemName }
        if state is not None:
            config["state"] = state
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID("core.ItemStateUpdateTrigger").withConfiguration(Configuration(config)).build()

class ItemStateChangeTrigger(Trigger):
    def __init__(self, itemName, previousState=None, state=None, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        config = { "itemName": itemName }
        if state is not None:
            config["state"] = state
        if previousState is not None:
            config["previousState"] = previousState
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID("core.ItemStateChangeTrigger").withConfiguration(Configuration(config)).build()

class ItemCommandTrigger(Trigger):
    def __init__(self, itemName, command=None, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        config = { "itemName": itemName }
        if command is not None:
            config["command"] = command
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID("core.ItemCommandTrigger").withConfiguration(Configuration(config)).build()

class ChannelEventTrigger(Trigger):
    def __init__(self, channelUID, event=None, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        config = { "channelUID": channelUID }
        if event is not None:
            config["event"] = event
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID("core.ChannelEventTrigger").withConfiguration(Configuration(config)).build()

class GenericEventTrigger(Trigger):
    def __init__(self, eventSource, eventTypes, eventTopic="smarthome/*", triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID("core.GenericEventTrigger").withConfiguration(Configuration({
            "eventTopic": eventTopic,
            "eventSource": "smarthome/{}/".format(eventSource),
            "eventTypes": eventTypes
        })).build()

'''
Item event types:
ITEM_UPDATE = "ItemStateEvent"
ITEM_COMMAND = "ItemCommandEvent"
ITEM_CHANGE = "ItemStateChangedEvent"
GROUP_CHANGE = "GroupItemStateChangedEvent"
'''
class ItemEventTrigger(Trigger):
    def __init__(self, eventSource, eventTypes, eventTopic="smarthome/items/*", triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID("core.GenericEventTrigger").withConfiguration(Configuration({
            "eventTopic": eventTopic,
            "eventSource": "smarthome/items/{}/".format(eventSource),
            "eventTypes": eventTypes
        })).build()

'''
Thing event types:
"ThingAddedEvent"
"ThingRemovedEvent"
"ThingStatusInfoChangedEvent"
"ThingStatusInfoEvent"
"ThingUpdatedEvent"
'''
class ThingEventTrigger(Trigger):
    def __init__(self, thingUID, eventTypes, eventTopic="smarthome/things/*", triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID("core.GenericEventTrigger").withConfiguration(Configuration({
            "eventTopic": eventTopic,
            "eventSource": "smarthome/things/{}/".format(thingUID),
            "eventTypes": eventTypes
        })).build()

EVERY_SECOND = "0/1 * * * * ?"
EVERY_MINUTE = "0 * * * * ?"
EVERY_HOUR = "0 0 * * * ?"

class CronTrigger(Trigger):
    def __init__(self, cronExpression, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID("timer.GenericCronTrigger").withConfiguration(Configuration({"cronExpression": cronExpression})).build()

class StartupTrigger(Trigger):
    def __init__(self, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID("openhab.STARTUP_MODULE_ID").withConfiguration(Configuration()).build()

class ShutdownTrigger(Trigger):
    def __init__(self, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID("openhab.SHUTDOWN_MODULE_ID").withConfiguration(Configuration()).build()

# Item Registry Triggers

class ItemRegistryTrigger(OsgiEventTrigger):
    def __init__(self, event_name):
        OsgiEventTrigger.__init__(self)
        self.event_name = event_name
        
    def event_filter(self, event):
        return event.get('type') == self.event_name
    
    def event_transformer(self, event):
        return json.loads(event['payload'])

class ItemAddedTrigger(ItemRegistryTrigger):
    def __init__(self):
        ItemRegistryTrigger.__init__(self, "ItemAddedEvent")
        
class ItemRemovedTrigger(ItemRegistryTrigger):
     def __init__(self):
        ItemRegistryTrigger.__init__(self, "ItemRemovedEvent")

class ItemUpdatedTrigger(ItemRegistryTrigger):
    def __init__(self):
        ItemRegistryTrigger.__init__(self, "ItemUpdatedEvent")
        
# Directory watcher trigger

class DirectoryEventTrigger(Trigger):
    def __init__(self, path, event_kinds=[ENTRY_CREATE, ENTRY_DELETE, ENTRY_MODIFY], watch_subdirectories=False):
        triggerId = type(self).__name__ + "-" + uuid.uuid1().hex
        config = {
            'path': path,
            'event_kinds': str(event_kinds),
            'watch_subdirectories': watch_subdirectories,
        }
        self.trigger = TriggerBuilder.create().withId(triggerId).withTypeUID("openhab.DIRECTORY_TRIGGER_MODULE_ID").withConfiguration(Configuration(config)).build()

# Function decorator trigger support

def when(target, target_type=None, trigger_type=None, old_state=None, new_state=None, event_types=None):
    try:
        def item_trigger(function):
            if not hasattr(function, 'triggers'):
                function.triggers = []
            item = scope.itemRegistry.getItem(target)
            group_members = []
            if target_type == "Member of":
                group_members = item.getMembers()
            elif target_type == "Descendent of":
                group_members = item.getAllMembers()
            else:
                group_members = [ item ]
            for member in group_members:
                trigger_name = "Item-{}-{}{}{}".format(member.name, trigger_type.replace(" ","-"), "-from-{}".format(old_state) if old_state else "", "-to-{}".format(new_state) if new_state else "")
                if trigger_type == "received update":
                    function.triggers.append(ItemStateUpdateTrigger(member.name, state=new_state, triggerName=trigger_name).trigger)
                elif trigger_type == "received command":
                    function.triggers.append(ItemCommandTrigger(member.name, command=new_state, triggerName=trigger_name).trigger)
                else:
                    function.triggers.append(ItemStateChangeTrigger(member.name, previousState=old_state, state=new_state, triggerName=trigger_name).trigger)
                log.debug("Created item_trigger: [{}]".format(trigger_name))
            return function

        def cron_trigger(function):
            if not hasattr(function, 'triggers'):
                function.triggers = []
            trigger_name = "Cron-{}-{}".format(function.__name__, uuid.uuid1().hex)
            function.triggers.append(CronTrigger(target, triggerName=trigger_name).trigger)
            log.debug("Created cron_trigger: [{}]".format(trigger_name))
            return function

        def system_trigger(function):
            if not hasattr(function, 'triggers'):
                function.triggers = []
            if trigger_type == "started":
                function.triggers.append(StartupTrigger(triggerName=trigger_name).trigger)
            else:
                function.triggers.append(ShutdownTrigger(triggerName=trigger_name).trigger)
            log.debug("Created system_trigger: [{}]".format(trigger_name))
            return function

        def channel_trigger(function):
            if not hasattr(function, 'triggers'):
                function.triggers = []
            function.triggers.append(ChannelEventTrigger(target, event=new_state, triggerName=trigger_name).trigger)
            log.debug("Created channel_trigger: [{}]".format(trigger_name))
            return function

        def thing_trigger(function):
            if not hasattr(function, 'triggers'):
                function.triggers = []
            event_types = "ThingStatusInfoChangedEvent" if (trigger_type == "changed") else "ThingStatusInfoEvent"
            function.triggers.append(ThingEventTrigger(target, event_types, triggerName=trigger_name).trigger)
            log.debug("Created thing_trigger: [{}]".format(trigger_name))
            return function
        
        original_target = target
        if isValidExpression(target):
            target_type = "Time"
            trigger_type = "cron"
        else:
            trigger_name = target.replace(":","_").replace("#","_").replace(" ","-")
            inputList = target.split(" ")
            if len(inputList) > 1:
                while len(inputList) > 0:
                    if target_type is None:
                        if inputList[0] in ["Item", "Thing", "Channel"]:
                            target_type = inputList.pop(0)
                            target = inputList.pop(0)
                        elif " ".join(inputList[0:2]) == "Member of":
                            inputList = inputList[2:]
                            target_type = "Member of"
                            target = inputList.pop(0)
                        elif " ".join(inputList[0:2]) == "Descendent of":
                            inputList = inputList[2:]
                            target_type = "Descendent of"
                            target = inputList.pop(0)
                        elif inputList[0] == "System":
                            target_type = inputList.pop(0)
                            if inputList[0] == "started":
                                trigger_type = inputList.pop(0)
                            elif " ".join(inputList[0:2]) == "shuts down":
                                del inputList[:]
                                trigger_type = "shuts down"
                            else:
                                raise ValueError("when: \"{}\" could not be parsed. trigger_type \"{}\" is invalid for target_type \"System\". Valid trigger_type values are \"started\" and \"shuts down\"".format(original_target, inputList[0]))
                        elif inputList[0] == "Time":
                            target_type = inputList.pop(0)
                            if inputList[0] == "cron":
                                trigger_type = inputList.pop(0)
                                if isValidExpression(" ".join(inputList)):
                                    target = " ".join(inputList)
                                    del inputList[:]
                                else:
                                    raise ValueError("when: \"{}\" could not be parsed. \"{}\" is not a valid cron expression. See http://www.quartz-scheduler.org/documentation/quartz-2.1.x/tutorials/tutorial-lesson-06".format(original_target, " ".join(inputList)))
                            else:
                                raise ValueError("when: \"{}\" could not be parsed. trigger_type \"{}\" is invalid. The only valid trigger_type value is \"cron\" (i.e, \"Time cron 0 55 5 * * ?\")".format(original_target, inputList[0]))
                        else:
                            raise ValueError("when: \"{}\" could not be parsed. target_type \"{}\" is invalid. Valid target_type values are: Item, Member of, Descendent of, Thing, Channel, System, and Time.".format(target, inputList[0]))
                    else:
                        if " ".join(inputList[0:2]) == "received update":
                            if target_type in ["Item", "Thing", "Member of", "Descendent of"]:
                                inputList = inputList[2:]
                                trigger_type = "received update"
                            else:
                                raise ValueError("when: \"{}\" could not be parsed. \"received update\" is invalid for target_type \"{}\"".format(target, target_type))
                        elif " ".join(inputList[0:2]) == "received command":
                            if target_type in ["Item", "Member of", "Descendent of"]:
                                inputList = inputList[2:]
                                trigger_type = "received command"
                            else:
                                raise ValueError("when: \"{}\" could not be parsed. \"received command\" is invalid for target_type \"{}\"".format(target, target_type))
                        elif inputList[0] == "changed":
                            if target_type in ["Item", "Thing", "Member of", "Descendent of"]:
                                inputList.pop(0)
                                trigger_type = "changed"
                            else:
                                raise ValueError("when: \"{}\" could not be parsed. \"changed\" is invalid for target_type \"{}\"".format(target, target_type))
                        elif inputList[0] == "triggered":
                            if target_type == "Channel":
                                trigger_type = inputList.pop(0)
                                if len(inputList) > 0:
                                    new_state = inputList.pop(0)
                            else:
                                raise ValueError("when: \"{}\" could not be parsed. \"triggered\" is invalid for target_type \"{}\"".format(target, target_type))
                        else:#if len(inputList) > 0:
                            if trigger_type == "changed" and inputList[0] == "from":
                                inputList.pop(0)
                                old_state = inputList.pop(0)
                                if inputList[0] == "to":
                                    inputList.pop(0)
                                    new_state = inputList.pop(0)
                                else:
                                    raise ValueError("when: \"{}\" could not be parsed. old_state specified, but new_state is missing.".format(target))
                            elif trigger_type == "changed" and inputList[0] == "to":
                                inputList.pop(0)
                                new_state = inputList.pop(0)
                            elif trigger_type == "received update" or trigger_type == "received command":
                                new_state = inputList.pop(0)
                            if len(inputList) > 0:
                                raise ValueError("when: \"{}\" could not be parsed. \"{}\" is invalid for target_type \"{}\"".format(target, inputList[0], target_type))
            else:# add default values for simple item targets (Item XXXXX changed)
                if target_type is None:
                    target_type = "Item"
                if trigger_type is None:
                    trigger_type == "changed"

        # validate the inputs, and if anything isn't populated correctly throw an exception
        if trigger_type is None:
            raise ValueError("when: \"{}\" could not be parsed because the trigger_type is missing".format(original_target))
        elif target_type in ["Item", "Member of", "Descendent of"] and not scope.itemRegistry.getItem(target):# throws ItemNotFoundException if item does not exist
            raise ValueError("when: \"{}\" could not be parsed because Item \"{}\" is not in the itemRegistry".format(original_target, target))
        elif target_type == "Item" and old_state and trigger_type == "changed" and not TypeParser.parseState(scope.itemRegistry.getItem(target).acceptedDataTypes, old_state):
            raise ValueError("when: \"{}\" could not be parsed because \"{}\" not a valid state for \"{}\"".format(original_target, old_state, target))
        elif target_type == "Item" and new_state and (trigger_type == "changed" or trigger_type == "received update") and not TypeParser.parseState(scope.itemRegistry.getItem(target).acceptedDataTypes, new_state):
            raise ValueError("when: \"{}\" could not be parsed because \"{}\" not a valid state for \"{}\"".format(original_target, new_state, target))
        elif target_type == "Item" and trigger_type == "received command" and new_state and not TypeParser.parseState(scope.itemRegistry.getItem(target).acceptedCommandTypes, new_state):
            raise ValueError("when: \"{}\" could not be parsed because \"{}\" not a valid command for \"{}\"".format(original_target, new_state, target))
        elif target_type in ["Member of", "Descendent of"] and scope.itemRegistry.getItem(target).type != "Group":
            raise ValueError("when: \"{}\" could not be parsed because \"{}\" was specified, but \"{}\" is not a group".format(original_target, target_type, target))
        elif target_type == "Channel" and not scope.things.getChannel(ChannelUID(target)):# returns null if Channel does not exist
            raise ValueError("when: \"{}\" could not be parsed because Channel \"{}\" does not exist".format(original_target, target))
        elif target_type == "Thing" and not scope.things.get(ThingUID(target)):# returns null if Thing does not exist
            raise ValueError("when: \"{}\" could not be parsed because Thing \"{}\" is not in the thingRegistry".format(original_target, target))
        elif target_type == "Thing" and (old_state or new_state):# There is only an event trigger for Things, so old_state and new_state can't be used yet
            raise ValueError("when: \"{}\" could not be parsed because rule triggers do not currently support checking the status for Things".format(original_target))
        elif target_type == "System":
            raise ValueError("when: \"{}\" could not be parsed because rule triggers do not currently support target_type \"System\"".format(original_target))
        #elif target_type == "Thing" and old_state and not hasattr(ThingStatus, old_state):# There is only an event trigger for Things, so this can't be used yet
        #    raise ValueError("when: \"{}\" is not a valid Thing status".format(old_state))
        #elif target_type == "Thing" and new_state and not hasattr(ThingStatus, new_state):# There is only an event trigger for Things, so this can't be used yet
        #    raise ValueError("when: \"{}\" is not a valid Thing status".format(new_state))            
        
        log.debug("when: original_target=[{}], target_type={}, target={}, trigger_type={}, old_state={}, new_state={}".format(original_target, target_type, target, trigger_type, old_state, new_state))
        
        if target_type in ["Item", "Member of", "Descendent of"]:
            return item_trigger
        elif target_type == "Thing":
            return thing_trigger
        elif target_type == "Channel":
            return channel_trigger
        elif target_type == "System":
            return system_trigger
        elif target_type == "Time":
            return cron_trigger

    except Exception as e:
        import traceback
        log.error("when: Exception [{}]: [{}]".format(e, traceback.format_exc()))
