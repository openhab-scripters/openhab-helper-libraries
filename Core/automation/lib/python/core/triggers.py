import inspect
import json
import uuid

import java.util
from java.nio.file.StandardWatchEventKinds import ENTRY_CREATE, ENTRY_DELETE, ENTRY_MODIFY

from org.eclipse.smarthome.automation.core.util import TriggerBuilder
from org.eclipse.smarthome.automation import Trigger
from org.eclipse.smarthome.config.core import Configuration
from org.eclipse.smarthome.core.thing import ChannelUID, ThingUID, ThingStatus
from org.eclipse.smarthome.core.thing.type import ChannelKind
from org.eclipse.smarthome.core.types import TypeParser

import core
from core.jsr223 import scope
from core.osgi.events import OsgiEventTrigger
from core.log import logging, LOG_PREFIX

from org.quartz.CronExpression import isValidExpression

log = logging.getLogger(LOG_PREFIX + ".triggers")

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
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID(core.STARTUP_MODULE_ID).withConfiguration(Configuration()).build()

class ShutdownTrigger(Trigger):
    def __init__(self, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID(core.SHUTDOWN_MODULE_ID).withConfiguration(Configuration()).build()

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
        self.trigger = TriggerBuilder.create().withId(triggerId).withTypeUID(core.DIRECTORY_TRIGGER_MODULE_ID).withConfiguration(Configuration(config)).build()

# Function decorator trigger support

def when(target, target_type=None, trigger_type=None, old_state=None, new_state=None, event_types=None, trigger_name=None):
    try:
        def item_trigger(function):
            if not hasattr(function, 'triggers'):
                function.triggers = []
            item = scope.itemRegistry.getItem(trigger_target)
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
                log.debug("when: Created item_trigger: [{}]".format(trigger_name))
            return function

        def cron_trigger(function):
            if not hasattr(function, 'triggers'):
                function.triggers = []
            trigger_name = "Cron-{}-{}".format(function.__name__, uuid.uuid1().hex)
            function.triggers.append(CronTrigger(trigger_type, triggerName=trigger_name).trigger)
            log.debug("when: Created cron_trigger: [{}]".format(trigger_name))
            return function

        def system_trigger(function):
            if not hasattr(function, 'triggers'):
                function.triggers = []
            if trigger_target == "started":
                function.triggers.append(StartupTrigger(triggerName=trigger_name).trigger)
            else:
                function.triggers.append(ShutdownTrigger(triggerName=trigger_name).trigger)
            log.debug("when: Created system_trigger: [{}]".format(trigger_name))
            return function

        def channel_trigger(function):
            if not hasattr(function, 'triggers'):
                function.triggers = []
            function.triggers.append(ChannelEventTrigger(trigger_target, event=new_state, triggerName=trigger_name).trigger)
            log.debug("when: Created channel_trigger: [{}]".format(trigger_name))
            return function

        def thing_trigger(function):
            if not hasattr(function, 'triggers'):
                function.triggers = []
            event_types = "ThingStatusInfoChangedEvent" if (trigger_type == "changed") else "ThingStatusInfoEvent"
            function.triggers.append(ThingEventTrigger(trigger_target, event_types, triggerName=trigger_name).trigger)
            log.debug("when: Created thing_trigger: [{}]".format(trigger_name))
            return function
        
        trigger_target = None
        if isValidExpression(target):
            target_type = "Time"
            trigger_target = "cron"
            trigger_type = target
        else:
            trigger_name = trigger_name or (target.replace(":","_").replace("#","_").replace(" ","-"))
            inputList = target.split(" ")
            if len(inputList) > 1:
                # target_type target [trigger_type] [from] [old_state] [to] [new_state]
                while len(inputList) > 0:
                    if target_type is None:
                        if " ".join(inputList[0:2]) in ["Member of", "Descendent of"]:
                            target_type = " ".join(inputList[0:2])
                            inputList = inputList[2:]
                        else:
                            target_type = inputList.pop(0)
                    elif trigger_target is None:
                        if target_type == "System" and len(inputList) > 1:
                            if " ".join(inputList[0:2]) == "shuts down":
                                trigger_target = "shuts down"
                        else:
                            trigger_target = inputList.pop(0)
                    elif trigger_type is None:
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
                            else:
                                raise ValueError("when: \"{}\" could not be parsed. \"triggered\" is invalid for target_type \"{}\"".format(target, target_type))
                        elif trigger_target == "cron":
                            if target_type == "Time":
                                if isValidExpression(" ".join(inputList)):
                                    trigger_type = " ".join(inputList)
                                    del inputList[:]
                                else:
                                    raise ValueError("when: \"{}\" could not be parsed. \"{}\" is not a valid cron expression. See http://www.quartz-scheduler.org/documentation/quartz-2.1.x/tutorials/tutorial-lesson-06".format(target, " ".join(inputList)))
                            else:
                                raise ValueError("when: \"{}\" could not be parsed. \"cron\" is invalid for target_type \"{}\"".format(target, target_type))
                        else:
                            raise ValueError("when: \"{}\" could not be parsed because the trigger_type {}".format(target, "is missing" if inputList[0] is None else "\"{}\" is invalid".format(inputList[0])))
                    else:
                        if old_state is None and trigger_type == "changed" and inputList[0] == "from":
                            inputList.pop(0)
                            old_state = inputList.pop(0)
                        elif new_state is None and trigger_type == "changed" and inputList[0] == "to":
                            inputList.pop(0)
                            new_state = inputList.pop(0)
                        elif new_state is None and (trigger_type == "received update" or trigger_type == "received command"):
                            new_state = inputList.pop(0)
                        elif new_state is None and target_type == "Channel":
                            new_state = inputList.pop(0)
                        elif len(inputList) > 0:# there are no more possible combinations, but there is more data
                            raise ValueError("when: \"{}\" could not be parsed. \"{}\" is invalid for \"{} {} {}\"".format(target, inputList, target_type, trigger_target, trigger_type))

            else:# a simple Item target was used, so add default target_type and trigger_type (Item XXXXX changed)
                if target_type is None:
                    target_type = "Item"
                if trigger_target is None:
                    trigger_target = target
                if trigger_type is None:
                    trigger_type = "changed"

        # validate the inputs, and if anything isn't populated correctly throw an exception
        if target_type is None or target_type not in ["Item", "Member of", "Descendent of", "Thing", "Channel", "System", "Time"]:
            raise ValueError("when: \"{}\" could not be parsed. target_type is missing or invalid. Valid target_type values are: Item, Member of, Descendent of, Thing, Channel, System, and Time.".format(target))
        elif trigger_type is None:
            raise ValueError("when: \"{}\" could not be parsed because trigger_type cannot be None".format(target)) 
        elif target_type in ["Item", "Member of", "Descendent of"] and scope.itemRegistry.getItem(trigger_target) is None:# throws ItemNotFoundException if item does not exist
            raise ValueError("when: \"{}\" could not be parsed because Item \"{}\" is not in the itemRegistry".format(target, trigger_target))
        elif target_type in ["Member of", "Descendent of"] and scope.itemRegistry.getItem(trigger_target).type != "Group":
            raise ValueError("when: \"{}\" could not be parsed because \"{}\" was specified, but \"{}\" is not a group".format(target, target_type, trigger_target))
        elif target_type == "Item" and old_state is not None and trigger_type == "changed" and not TypeParser.parseState(scope.itemRegistry.getItem(trigger_target).acceptedDataTypes, old_state):
            raise ValueError("when: \"{}\" could not be parsed because \"{}\" is not a valid state for \"{}\"".format(target, old_state, trigger_target))
        elif target_type == "Item" and new_state is not None and (trigger_type == "changed" or trigger_type == "received update") and not TypeParser.parseState(scope.itemRegistry.getItem(trigger_target).acceptedDataTypes, new_state):
            raise ValueError("when: \"{}\" could not be parsed because \"{}\" is not a valid state for \"{}\"".format(target, new_state, trigger_target))
        elif target_type == "Item" and new_state is not None and trigger_type == "received command" and not TypeParser.parseState(scope.itemRegistry.getItem(trigger_target).acceptedCommandTypes, new_state):
            raise ValueError("when: \"{}\" could not be parsed because \"{}\" is not a valid command for \"{}\"".format(target, new_state, trigger_target))
        elif target_type == "Channel" and scope.things.getChannel(ChannelUID(trigger_target)) is None:# returns null if Channel does not exist
            raise ValueError("when: \"{}\" could not be parsed because Channel \"{}\" does not exist".format(target, trigger_target))
        elif target_type == "Channel" and scope.things.getChannel(ChannelUID(trigger_target)).kind != ChannelKind.TRIGGER:
            raise ValueError("when: \"{}\" could not be parsed because Channel \"{}\" is not a trigger".format(target, trigger_target))
        elif target_type == "Thing" and scope.things.get(ThingUID(trigger_target)) is None:# returns null if Thing does not exist
            raise ValueError("when: \"{}\" could not be parsed because Thing \"{}\" is not in the thingRegistry".format(target, trigger_target))
        elif target_type == "Thing" and old_state and not hasattr(ThingStatus, old_state):
            raise ValueError("when: \"{}\" is not a valid Thing status".format(old_state))
        elif target_type == "Thing" and new_state and not hasattr(ThingStatus, new_state):
            raise ValueError("when: \"{}\" is not a valid Thing status".format(new_state))   
        elif target_type == "Thing" and (old_state is not None or new_state is not None):# there is only an event trigger for Things, so old_state and new_state can't be used yet *****TO BE REMOVED*****
            raise ValueError("when: \"{}\" could not be parsed because rule triggers do not currently support checking the from/to status for Things".format(target))
        elif target_type == "System" and trigger_target != "started" and trigger_target != "shuts down":
            raise ValueError("when: \"{}\" could not be parsed. trigger_target \"{}\" is invalid for target_type \"System\". Valid trigger_type values are \"started\" and \"shuts down\"".format(target, target_type))
        #elif target_type == "System":# 'System shuts down' is not currently supported, and the 'System started' trigger needs to be reworked for the update API *****TO BE REMOVED*****
        #    raise ValueError("when: \"{}\" could not be parsed because rule triggers do not currently support target_type \"System\"".format(target))

        log.debug("when: target=[{}], target_type={}, trigger_target={}, trigger_type={}, old_state={}, new_state={}".format(target, target_type, trigger_target, trigger_type, old_state, new_state))

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
