import inspect
import json
import uuid
from functools import wraps

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
from openhab.jsr223 import scope, get_automation_manager
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

class ItemEventTrigger(Trigger):
    def __init__(self, eventSource, eventTypes, eventTopic="smarthome/items/*", triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID("core.GenericEventTrigger").withConfiguration(Configuration({
            "eventTopic": eventTopic,
            "eventSource": "smarthome/items/{}/".format(eventSource),
            "eventTypes": eventTypes
        })).build()

class ChannelEventTrigger(Trigger):
    def __init__(self, channelUID, event=None, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        config = { "channelUID": channelUID }
        if event is not None:
            config["event"] = event
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID("core.ChannelEventTrigger").withConfiguration(Configuration(config)).build()

'''
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

'''
# ShutdownTrigger is not ready yet
class ShutdownTrigger(Trigger):
    def __init__(self, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID("openhab.SHUTDOWN_MODULE_ID").withConfiguration(Configuration()).build()
'''

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

class _FunctionRule(scope.SimpleRule):
    def __init__(self, callback, triggers, name=None):#extended=False):
        self.triggers = triggers
        self.callback = callback
        #self.extended = extended
        if name is None and hasattr(callback, '__name__'):
            name = callback.__name__
        self.name = name
        #log.debug("_FunctionRule: test: rule name=[{}]".format(name))
        #log.debug("_FunctionRule: test: callback.__name__=[{}]".format(callback.__name__))
        self.log = logging.getLogger(LOG_PREFIX + ("" if name is None else ("." + name)))
        
    def execute(self, module, inputs):
        try:
            #log.error("rule: execute [{}]: extended=[{}]".format(self.name, self.extended))
            #self.callback(module, inputs) if self.extended else self.callback()
            self.callback(inputs.get('event'))
        except:
            import traceback
            self.log.error(traceback.format_exc())

def rule(name, *triggers):
    try:
        def rule_decorator(function):
            all_triggers = [ trigger for sublist in list(triggers) for trigger in sublist ]
            newRule = _FunctionRule(function, all_triggers, name=name)
            get_automation_manager().addRule(newRule)
            return function
        return rule_decorator
    except Exception as e:
        import traceback
        log.error("rule: Exception [{}]: [{}]".format(e, traceback.format_exc()))

def when(target, trigger_type=None, member_of=False, descendent_of=False, old_state=None, new_state=None, changed=False, received_update=False, received_command=False, event_types=None):#, result_item_name=None):
    try:
        triggers = []
        def item_trigger():
            def create_event_trigger(item_name):
                if received_update:
                    triggers.append(ItemEventTrigger(item_name, "ItemStateEvent", triggerName=trigger_name).trigger)
                elif received_command:
                    triggers.append(ItemEventTrigger(item_name, "ItemCommandEvent", triggerName=trigger_name).trigger)
                else:
                    triggers.append(ItemEventTrigger(item_name, "GroupItemStateChangedEvent", triggerName=trigger_name).trigger)
            def create_composite_trigger(item_name):
                if received_update:
                    triggers.append(ItemStateUpdateTrigger(item_name, state=new_state, triggerName=trigger_name).trigger)
                elif received_command:
                    triggers.append(ItemCommandTrigger(item_name, command=new_state, triggerName=trigger_name).trigger)
                else:
                    triggers.append(ItemStateChangeTrigger(item_name, previousState=old_state, state=new_state, triggerName=trigger_name).trigger)

            group_members = []
            item = scope.itemRegistry.getItem(target)
            if item.type == "Group" and (member_of or descendent_of):
                if descendent_of:
                    group_members = item.getAllMembers()
                else:
                    group_members = item.getMembers()
            else:
                group_members = [ item ]
            for member in group_members:
                trigger_name = "{}-{}{}{}".format(member.name,"received-update" if received_update else ("received-command" if received_command else "changed"), "-from-{}".format(old_state) if old_state else "", "-to-{}".format(new_state) if new_state else "")
                if member.type == "Group":
                    create_event_trigger(member.name)
                else:
                    create_composite_trigger(member.name)
                log.debug("Created item_trigger: [{}]".format(trigger_name))
            return triggers

        def cron_trigger():
            #trigger_name = "Cron-{}-{}".format(function.__name__, uuid.uuid1().hex)
            #trigger_name = "Cron-{}-{}".format(__name__, uuid.uuid1().hex)
            trigger_name = "Cron-{}".format(uuid.uuid1().hex)
            triggers.append(CronTrigger(target, triggerName=trigger_name).trigger)
            log.debug("Created cron_trigger: [{}]".format(trigger_name))
            return triggers

        def system_trigger():
            trigger_name = "System-{}".format(target.replace(" ","-"))
            if target == "started":
                triggers.append(StartupTrigger(triggerName=trigger_name).trigger)
            '''
            # ShutdownTrigger is not ready yet
            else:
                triggers.append(ShutdownTrigger(triggerName=trigger_name).trigger)
            '''
            log.debug("Created system_trigger: [{}]".format(trigger_name))
            return triggers

        def channel_trigger():
            trigger_name = "Channel-{}-was-triggered{}".format(target.replace(":","_").replace("#","_"),"-with-event-{}".format(new_state) if new_state is not None else "")
            triggers.append(ChannelEventTrigger(target, event=new_state, triggerName=trigger_name).trigger)
            log.debug("Created channel_trigger: [{}]".format(trigger_name))
            return triggers

        def thing_trigger():
            trigger_name = "{}-{}".format(target.replace(":","_"),"received-update" if received_update else "changed")
            event_types = "ThingStatusInfoChangedEvent" if changed else "ThingStatusInfoEvent"
            triggers.append(ThingEventTrigger(target, event_types, triggerName=trigger_name).trigger)
            log.debug("Created thing_trigger: [{}]".format(trigger_name))
            return triggers

        if isValidExpression(target):
            trigger_type = "Cron"
        else: 
            inputList = target.split(" ")
            if len(inputList) > 1:
                while len(inputList) > 0:
                    if trigger_type is None:
                        if inputList[0] in ["Item", "Thing", "Channel"]:
                            trigger_type = inputList.pop(0)
                            target = inputList.pop(0)
                        elif " ".join(inputList[0:2]) == "Member of":
                            inputList = inputList[2:]
                            trigger_type = "Item"
                            member_of = True
                            target = inputList.pop(0)
                        elif " ".join(inputList[0:2]) == "Descendent of":
                            inputList = inputList[2:]
                            trigger_type = "Item"
                            descendent_of = True
                            target = inputList.pop(0)
                        elif inputList[0] == "System":
                            trigger_type = inputList.pop(0)
                            if inputList[0] == "started":
                                target = inputList.pop(0)
                            '''
                            # ShutdownTrigger is not ready yet
                            elif " ".join(inputList[0:2]) == "shuts down":
                                inputList = inputList[2:]
                                target = "shuts down"
                            '''
                        else:
                            raise ValueError("when: \"{}\" could not be parsed. trigger_type \"{}\" is invalid. Valid trigger_type values are: Cron, Member of, Descendent of, Item, Thing, Channel, System.".format(target, inputList[0]))
                    else:
                        if " ".join(inputList[0:2]) == "received update":
                            if trigger_type in ["Item", "Thing"]:
                                inputList = inputList[2:]
                                received_update = True
                            else:
                                raise ValueError("when: \"{}\" could not be parsed. \"received update\" is invalid for trigger_type \"{}\"".format(target, trigger_type))
                        elif " ".join(inputList[0:2]) == "received command":
                            if trigger_type == "Item":
                                inputList = inputList[2:]
                                received_command = True
                            else:
                                raise ValueError("when: \"{}\" could not be parsed. \"received command\" is invalid for trigger_type \"{}\"".format(target, trigger_type))
                        elif inputList[0] == "changed":
                            if trigger_type in ["Item", "Thing"]:
                                inputList.pop(0)
                                changed = True
                            else:
                                raise ValueError("when: \"{}\" could not be parsed. \"changed\" is invalid for trigger_type \"{}\"".format(target, trigger_type))
                        elif inputList[0] == "triggered":
                            if trigger_type == "Channel":
                                inputList.pop(0)
                                if len(inputList) > 0:
                                    new_state = inputList.pop(0)
                            else:
                                raise ValueError("when: \"{}\" could not be parsed. \"triggered\" is invalid for trigger_type \"{}\"".format(target, trigger_type))
                        else:#if len(inputList) > 0:
                            if changed and inputList[0] == "from":
                                inputList.pop(0)
                                old_state = inputList.pop(0)
                                if inputList[0] == "to":
                                    inputList.pop(0)
                                    new_state = inputList.pop(0)
                                else:
                                    raise ValueError("when: \"{}\" could not be parsed. old_state specified, but new_state is missing.".format(target))
                            elif changed and inputList[0] == "to":
                                inputList.pop(0)
                                new_state = inputList.pop(0)
                            elif received_update or received_command:
                                new_state = inputList.pop(0)
                            if len(inputList) > 0:
                                raise ValueError("when: \"{}\" could not be parsed. \"{}\" is invalid for trigger_type \"{}\"".format(target, inputList[0], trigger_type))
            else:# add default values for simple item targets (Item XXXXX changed)
                if trigger_type is None:
                    trigger_type = "Item"
                if not received_update and not received_command and not changed:
                    changed = True

        # validate the inputs, and if anything isn't populated correctly throw an exception
        if trigger_type == "Item" and not scope.itemRegistry.getItem(target):# throws ItemNotFoundException if item does not exist
            raise ValueError("when: Item \"{}\" is not in the itemRegistry".format(target))
        elif trigger_type == "Item" and old_state and changed and not TypeParser.parseState(scope.itemRegistry.getItem(target).acceptedDataTypes, old_state):
            raise ValueError("when: \"{}\" not a valid state for \"{}\"".format(old_state, target))
        elif trigger_type == "Item" and new_state and (changed or received_update) and not TypeParser.parseState(scope.itemRegistry.getItem(target).acceptedDataTypes, new_state):
            raise ValueError("when: \"{}\" not a valid state for \"{}\"".format(new_state, target))
        elif trigger_type == "Item" and received_command and new_state and not TypeParser.parseState(scope.itemRegistry.getItem(target).acceptedCommandTypes, new_state):
            raise ValueError("when: \"{}\" not a valid command for \"{}\"".format(new_state, target))
        elif (member_of or descendent_of) and scope.itemRegistry.getItem(target).type != "Group":
            raise ValueError("when: \"{}\" specified, but \"{}\" is not a group".format("Member of" if member_of else "Descendent of", target))
        elif trigger_type == "Channel" and not scope.things.getChannel(ChannelUID(target)):# returns null if Channel does not exist
            raise ValueError("when: Channel \"{}\" does not exist".format(target))
        elif trigger_type == "Thing" and not scope.things.get(ThingUID(target)):# returns null if Thing does not exist
            raise ValueError("when: Thing \"{}\" is not in the thingRegistry".format(target))
        elif trigger_type == "Thing" and (old_state or new_state):# There is only an event trigger for Things, so old_state and new_state can't be used yet
            raise ValueError("when: Rule triggers do not currently support checking the status for Thing \"{}\"".format(target))
        #elif trigger_type == "Thing" and old_state and not hasattr(ThingStatus, old_state):# There is only an event trigger for Things, so this can't be used yet
        #    raise ValueError("when: \"{}\" is not a valid Thing status".format(old_state))
        #elif trigger_type == "Thing" and new_state and not hasattr(ThingStatus, new_state):# There is only an event trigger for Things, so this can't be used yet
        #    raise ValueError("when: \"{}\" is not a valid Thing status".format(new_state))            

        log.info("when: trigger_type={}, target={}, member_of={}, descendent_of={}, changed={}, received_update={}, received_command={}, old_state={}, new_state={}".format(trigger_type, target, member_of, descendent_of, changed, received_update, received_command, old_state, new_state))

        if trigger_type == "Item":
            return item_trigger()
        elif trigger_type == "Thing":
            return thing_trigger()
        elif trigger_type == "Channel":
            return channel_trigger()
        elif trigger_type == "System":
            return system_trigger()
        elif trigger_type == "Cron":
            return cron_trigger()

    except Exception as e:
        import traceback
        log.error("when: Exception [{}]: [{}]".format(e, traceback.format_exc()))

def time_triggered(cron_expression, trigger_name=None):
    def decorator(fn):
        rule = _FunctionRule(fn, [CronTrigger(cron_expression)], name=trigger_name)
        get_automation_manager().addRule(rule)
        return fn
    return decorator

GROUP_CHANGE = "GroupItemStateChangedEvent"
ITEM_CHANGE = "ItemStateChangedEvent"
ITEM_UPDATE = "ItemStateEvent"
ITEM_COMMAND = "ItemCommandEvent"

# this decorator has been deprecated
def item_triggered(item_name, event_types=None, result_item_name=None, trigger_name=None):
    event_types = event_types or [ITEM_CHANGE]
    event_bus = scope.events
    if hasattr(event_types, '__iter__'):
        event_types = ",".join(event_types)
    def decorator(fn):
        nargs = len(inspect.getargspec(fn).args)
        def callback(module, inputs):
            fn_args = []
            event = inputs.get('event')
            if event and nargs == 1:
                fn_args.append(event)
            result_value = fn(*fn_args)
            if result_item_name:
                event_bus.postUpdate(result_item_name, unicode(result_value))
        rule = _FunctionRule(callback, [ItemEventTrigger(item_name, event_types)], 
                             extended=True, name=trigger_name)
        get_automation_manager().addRule(rule)
        return fn
    return decorator

# this decorator has been deprecated
def item_group_triggered(group_name, event_types=None, result_item_name=None, trigger_name=None):
    event_types = event_types or [ITEM_CHANGE]
    event_bus = scope.events
    if hasattr(event_types, '__iter__'):
        event_types = ",".join(event_types)
    def decorator(fn):
        nargs = len(inspect.getargspec(fn).args)
        def callback(module, inputs):
            fn_args = []
            event = inputs.get('event')
            if event and nargs == 1:
                fn_args.append(event)
            result_value = fn(*fn_args)
            if result_item_name:
                event_bus.postUpdate(result_item_name, unicode(result_value))
        group_triggers = []
        group = scope.itemRegistry.getItem(group_name)
        for i in group.getAllMembers():
            group_triggers.append(ItemEventTrigger(i.name, event_types))
        rule = _FunctionRule(callback, group_triggers, extended=True, name=trigger_name)
        get_automation_manager().addRule(rule)
        return fn
    return decorator