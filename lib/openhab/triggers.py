import java.util
from java.nio.file.StandardWatchEventKinds import ENTRY_CREATE, ENTRY_DELETE, ENTRY_MODIFY

import inspect
import json
import uuid

from org.eclipse.smarthome.automation import Trigger
from org.eclipse.smarthome.automation.handler import TriggerHandler
from org.eclipse.smarthome.automation.type import TriggerType
from org.eclipse.smarthome.config.core import Configuration

import openhab
from openhab.jsr223 import scope, get_automation_manager
scope.scriptExtension.importPreset("RuleSimple")

from openhab.osgi.events import OsgiEventTrigger
from openhab.log import logging, LOG_PREFIX

class ItemStateUpdateTrigger(Trigger):
    def __init__(self, itemName, state=None, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        config = { "itemName": itemName }
        if state is not None:
            config["state"] = state
        Trigger.__init__(self, triggerName, "core.ItemStateUpdateTrigger", Configuration(config))

class ItemStateChangeTrigger(Trigger):
    def __init__(self, itemName, state=None, triggerName=None, previousState=None):
        triggerName = triggerName or uuid.uuid1().hex
        config = { "itemName": itemName }
        if state is not None:
            config["state"] = state
        if previousState is not None:
            config["previousState"] = previousState
        Trigger.__init__(self, triggerName, "core.ItemStateChangeTrigger", Configuration(config))

class ItemCommandTrigger(Trigger):
    def __init__(self, itemName, command=None, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        config = { "itemName": itemName }
        if command is not None:
            config["command"] = command
        Trigger.__init__(self, triggerName, "core.ItemCommandTrigger", Configuration(config))

class ChannelEventTrigger(Trigger):
    def __init__(self, channelUID, event, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        #self.log.debug("Trigger: " + triggerName + "; channel: " + channelUID)
        config = { "channelUID": channelUID }
        config["event"] = event
        Trigger.__init__(self, triggerName, "core.ChannelEventTrigger", Configuration(config))
        self.setLabel(triggerName)

EVERY_SECOND = "0/1 * * * * ?"
EVERY_MINUTE = "0 * * * * ?"
EVERY_HOUR = "0 0 * * * ?"

class CronTrigger(Trigger):
    def __init__(self, cronExpression, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        Trigger.__init__(self, triggerName, "timer.GenericCronTrigger", Configuration({
                "cronExpression": cronExpression
                }))

class ItemEventTrigger(Trigger):
    def __init__(self, eventSource, eventTypes, eventTopic="smarthome/items/*", triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        Trigger.__init__(self, triggerName, "core.GenericEventTrigger", Configuration({
                "eventTopic": eventTopic,
                "eventSource": "smarthome/items/{}/".format(eventSource),
                "eventTypes": eventTypes
                }))

class StartupTrigger(Trigger):
    def __init__(self, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        Trigger.__init__(self, triggerName, openhab.STARTUP_MODULE_ID, Configuration())
    
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
        config = Configuration({
            'path': path,
            'event_kinds': str(event_kinds),
            'watch_subdirectories': watch_subdirectories,
        })
        Trigger.__init__(self, triggerId, openhab.DIRECTORY_TRIGGER_MODULE_ID, config)

# Function decorator trigger support

class _FunctionRule(scope.SimpleRule):
    def __init__(self, callback, triggers, extended=False, name=None):
        self.triggers = triggers
        self.callback = callback
        self.extended = extended
        if name is None and hasattr(callback, '__name__'):
            name = callback.__name__
        self.log = logging.getLogger(LOG_PREFIX + ("" if name is None else ("." + name)))
        
    def execute(self, module, inputs):
        try:
            self.callback(module, inputs) if self.extended else self.callback()
        except:
            import traceback
            self.log.error(traceback.format_exc())

def time_triggered(cron_expression, trigger_name=None):
    def decorator(fn):
        rule = _FunctionRule(fn, [CronTrigger(cron_expression)], name=trigger_name)
        get_automation_manager().addRule(rule)
        return fn
    return decorator

ITEM_CHANGE = "ItemStateChangedEvent"
ITEM_UPDATE = "ItemStateEvent"
ITEM_COMMAND = "ItemCommandEvent"

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
