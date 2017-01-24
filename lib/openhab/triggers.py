import uuid
from org.eclipse.smarthome.automation import Trigger
from org.eclipse.smarthome.config.core import Configuration
from org.eclipse.smarthome.automation.handler import TriggerHandler
from org.eclipse.smarthome.automation.type import TriggerType


from openhab.jsr223 import scope
scope.ScriptExtension.importPreset("RuleFactories")
scope.ScriptExtension.importPreset("RuleSupport")
scope.ScriptExtension.importPreset("RuleSimple")

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
        Trigger.__init__(self, triggerName, "core.ItemStateChangeTrigger", Configuration(config))

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

class _StartupTriggerHandlerFactory(scope.TriggerHandlerFactory):    
        
    class Handler(TriggerHandler):
        def __init__(self, trigger):
            self.trigger = trigger
            
        def setRuleEngineCallback(self, rule_engine_callback):
            rule_engine_callback.triggered(self.trigger, {})
            
    def get(self, trigger):
        return StartupTriggerHandlerFactory.Handler(trigger)
    
    def ungetHandler(self, module, ruleUID, handler):
        pass
    
    def dispose(self):
        pass
    
STARTUP_MODULE_ID = "jsr223.StartupTrigger"
scope.HandlerRegistry.addTriggerType(TriggerType(STARTUP_MODULE_ID, [], []))
scope.HandlerRegistry.addTriggerHandler(STARTUP_MODULE_ID, _StartupTriggerHandlerFactory())

class StartupTrigger(Trigger):
    def __init__(self, triggerName=None):
        triggerName = triggerName or uuid.uuid1().hex
        Trigger.__init__(self, triggerName, STARTUP_MODULE_ID, Configuration())
    
        
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
        scope.HandlerRegistry.addRule(rule)
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
        scope.HandlerRegistry.addRule(rule)
        return fn
    return decorator

