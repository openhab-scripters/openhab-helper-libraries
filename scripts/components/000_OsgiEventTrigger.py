import java.util
import traceback
import uuid

from org.eclipse.smarthome.automation import Visibility
from org.eclipse.smarthome.config.core import Configuration
from org.eclipse.smarthome.automation.handler import TriggerHandler

import openhab
scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleFactories")

from openhab.osgi.events import OsgiEventAdmin, event_dict, trigger_filters

class OsgiEventTriggerHandlerFactory(TriggerHandlerFactory):
    def __init__(self):
        self.handlers = []
        
    class Handler(TriggerHandler):
        def __init__(self, factory, trigger):
            try:
                self.rule_engine_callback = None
                self.factory = factory
                self.trigger = trigger
                trigger_config = trigger.getConfiguration()
                if trigger_config.containsKey("filter_id"):
                    self.filter_id = trigger_config.get("filter_id")
                    self.filter = trigger_filters.get(self.filter_id)
                else:
                    self.filter_id = None
                    self.filter = None
            except:
                import traceback
                print traceback.format_exc()
            
        def setRuleEngineCallback(self, rule_engine_callback):
            self.rule_engine_callback = rule_engine_callback
            
        def dispose(self):
            self.factory.handlers.remove(self)             
            OsgiEventAdmin.remove_listener(self.on_event)
            if self.filter_id:
                del(trigger_filters[self.filter_id])              
                 
        def on_event(self, event):
            try:
                if self.rule_engine_callback and event.getProperty('source') != 'RuleRegistryImpl':
                    event = event_dict(event)
                    if self.filter is not None and not self.filter(event):
                        return
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

openhab.OSGI_TRIGGER_ID = "jsr223.OsgiEventTrigger"

def scriptLoaded(*args):
    automationManager.addTriggerHandler(openhab.OSGI_TRIGGER_ID, OsgiEventTriggerHandlerFactory())    
    automationManager.addTriggerType(TriggerType(openhab.OSGI_TRIGGER_ID, [],
        "an OSGI event is published", 
        "Triggers when an OSGI event is published",
        set(), Visibility.VISIBLE, []))
    
def scriptUnloaded():
    automationManager.removeHandler(openhab.OSGI_TRIGGER_ID)
    automationManager.removeModuleType(openhab.OSGI_TRIGGER_ID)

