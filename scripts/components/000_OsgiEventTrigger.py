import java.util
import traceback
import uuid
import traceback

from org.eclipse.smarthome.automation import Visibility
from org.eclipse.smarthome.config.core import Configuration
from org.eclipse.smarthome.automation.handler import TriggerHandler

import openhab
scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleFactories")

from openhab.log import logging
log = logging.getLogger("jython.openhab.triggers.OsgiEventTrigger")

from openhab.osgi.events import OsgiEventAdmin, event_dict, osgi_triggers

class OsgiEventTriggerHandlerFactory(TriggerHandlerFactory):
    def __init__(self):
        self.handlers = []
        
    class Handler(TriggerHandler):
        def __init__(self, factory, runtime_trigger):
            try:
                self.rule_engine_callback = None
                self.factory = factory
                self.trigger = osgi_triggers.get(runtime_trigger.id, runtime_trigger)
                self.filter = getattr(self.trigger, "event_filter", None)
                self.transformer = getattr(self.trigger, "event_transformer", None)
                log.debug("creating trigger handler for %s(%s), filter=%s, transformer=%s", 
                          type(self.trigger).__name__, self.trigger.id, self.filter, self.transformer)
            except:
                log.error(traceback.format_exc())
            
        def setRuleEngineCallback(self, rule_engine_callback):
            self.rule_engine_callback = rule_engine_callback
            
        def dispose(self):
            log.debug("disposing %s (module %s)", self, self.trigger.id)
            self.factory.handlers.remove(self)             
            OsgiEventAdmin.remove_listener(self.on_event)
            if self.trigger.id in osgi_triggers:
                del(osgi_triggers[self.trigger.id])              
                 
        def on_event(self, event):
            try:
                if self.rule_engine_callback and event.getProperty('source') != 'RuleRegistryImpl':
                    event = event_dict(event)
                    if self.filter is not None and not self.filter(event):
                        return
                    inputs = self.transformer and self.transformer(event) or {'event': event}
                    self.rule_engine_callback.triggered(self.trigger, inputs)
            except:
                 log.error(traceback.format_exc())
            
    def get(self, trigger):
        handler = OsgiEventTriggerHandlerFactory.Handler(self, trigger)
        self.handlers.append(handler)
        OsgiEventAdmin.add_listener(handler.on_event)       
        return handler

openhab.OSGI_TRIGGER_ID = "jsr223.OsgiEventTrigger"

def scriptLoaded(*args):
    automationManager.addTriggerHandler(openhab.OSGI_TRIGGER_ID, OsgiEventTriggerHandlerFactory())    
    automationManager.addTriggerType(TriggerType(openhab.OSGI_TRIGGER_ID, [],
        "an OSGI event is published", 
        "Triggers when an OSGI event is published",
        set(), Visibility.VISIBLE, []))
    log.info("%s trigger type and handler defined", openhab.OSGI_TRIGGER_ID)
    
def scriptUnloaded():
    automationManager.removeHandler(openhab.OSGI_TRIGGER_ID)
    automationManager.removeModuleType(openhab.OSGI_TRIGGER_ID)
    log.info("trigger handler removed")

