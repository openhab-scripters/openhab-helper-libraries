import java.util
import traceback
import uuid

from org.eclipse.smarthome.automation import Visibility
from org.eclipse.smarthome.config.core import Configuration
from org.eclipse.smarthome.automation.handler import TriggerHandler

from openhab.jsr223 import scope
scope.ScriptExtension.importPreset("RuleSupport")
scope.ScriptExtension.importPreset("RuleFactories")

from openhab.osgi.events import OsgiEventAdmin

class OsgiEventTriggerHandlerFactory(scope.TriggerHandlerFactory):    
    def __init__(self):
        self.handlers = []
        
    class Handler(TriggerHandler):
        def __init__(self, factory, trigger):
            self.factory = factory
            self.trigger = trigger
            self.rule_engine_callback = None
            
        def setRuleEngineCallback(self, rule_engine_callback):
            self.rule_engine_callback = rule_engine_callback
            
        def dispose(self):
            self.factory.handlers.remove(self)
            if len(self.factory.handlers):
                OsgiEventAdmin.stop()
                 
        def on_event(self, event):
            try:
                if self.rule_engine_callback and event.getProperty('source') != 'RuleRegistryImpl':
                    self.rule_engine_callback.triggered(self.trigger, {'event': event})
            except:
                import traceback
                print traceback.format_exc()
            
    def get(self, trigger):
        handler = OsgiEventTriggerHandlerFactory.Handler(self, trigger)
        self.handlers.append(handler)
        OsgiEventAdmin.add_listener(handler.on_event)       
        return handler
    
    def ungetHandler(self, module, ruleUID, handler):
        self.handlers.remove(handler)
        OsgiEventAdmin.remove_listener(handler.on_event)

MODULE_ID = "jsr223.OsgiEventTrigger"

scope.HandlerRegistry.addTriggerType(scope.TriggerType(MODULE_ID, [],
    "an OSGI event is published", 
    "Triggers when an OSGI event is published",
    set(), Visibility.VISIBLE, []))

scope.HandlerRegistry.addTriggerHandler(MODULE_ID, OsgiEventTriggerHandlerFactory())