import uuid
import java.util
from org.eclipse.smarthome.automation import Trigger
from org.eclipse.smarthome.automation.handler import TriggerHandler
from org.eclipse.smarthome.automation.type import TriggerType
from org.eclipse.smarthome.config.core import Configuration

import openhab
from openhab.jsr223 import scope, get_automation_manager
scope.scriptExtension.importPreset("RuleSimple")

class ItemStateUpdateTrigger(Trigger):
    def __init__(self, itemName, state=None, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        config = { "itemName": itemName }
        if state is not None:
            config["state"] = state
        Trigger.__init__(self, triggerName, "core.ItemStateUpdateTrigger", Configuration(config))

class ItemStateChangeTrigger(Trigger):
    def __init__(self, itemName, state=None, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        config = { "itemName": itemName }
        if state is not None:
            config["state"] = state
        Trigger.__init__(self, triggerName, "core.ItemStateChangeTrigger", Configuration(config))

class ItemCommandTrigger(Trigger):
    def __init__(self, itemName, command=None, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        config = { "itemName": itemName }
        if command is not None:
            config["command"] = command
        Trigger.__init__(self, triggerName, "core.ItemCommandTrigger", Configuration(config))

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
    def __init__(self, eventSource, eventTypes, eventTopic="smarthome/*", triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        Trigger.__init__(self, triggerName, "core.GenericEventTrigger", Configuration({
                "eventTopic": eventTopic,
                "eventSource": eventSource,
                "eventTypes": eventTypes
                }))

class StartupTrigger(Trigger):
    def __init__(self, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        Trigger.__init__(self, triggerName, openhab.STARTUP_MODULE_ID, Configuration())
    
        
class _FunctionRule(scope.SimpleRule):
    def __init__(self, callback, triggers, extended=False):
        self.triggers = triggers
        self.callback = callback
        self.extended = extended
        
    def execute(self, module, inputs):
        try:
            self.callback(module, inputs) if self.extended else self.callback()
        except:
            import traceback
            print traceback.format_exc()

def time_triggered(cron_expression):
    def decorator(fn):
        rule = _FunctionRule(fn, [CronTrigger(cron_expression)])
        get_automation_manager().addRule(rule)
        return fn
    return decorator

ITEM_CHANGE = "ItemStateChangedEvent"
ITEM_UPDATE = "ItemStateEvent"
ITEM_COMMAND = "ItemCommandEvent"

def item_triggered(item_name, event_types=None, result_item_name=None):
    event_types = event_types or [ITEM_CHANGE]
    if hasattr(event_types, '__iter__'):
        event_types = ",".join(event_types)
    def decorator(fn):
        def callback(module, inputs):
            result_value = fn()
            if result_item_name:
                scope.events.postUpdate(result_item_name, str(result_value))
        rule = _FunctionRule(callback, [ItemEventTrigger(item_name, event_types)], extended=True)
        get_automation_manager().addRule(rule)
        return fn
    return decorator


def item_group_triggered(group_name, event_types=None, result_item_name=None):
    event_types = event_types or [ITEM_CHANGE]
    if hasattr(event_types, '__iter__'):
        event_types = ",".join(event_types)
    def decorator(fn):
        def callback(module, inputs):
            result_value = fn()
            if result_item_name:
                scope.events.postUpdate(result_item_name, str(result_value))
        group_triggers = []
        #[ItemEventTrigger(item_name, event_types)]
        rule = _FunctionRule(callback, group_triggers, extended=True)
        get_automation_manager().addRule(rule)
        return fn
    return decorator
