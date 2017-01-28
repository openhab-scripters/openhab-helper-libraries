import java.util
import traceback
import uuid

from org.osgi.framework import FrameworkUtil
from org.osgi.service.event import EventHandler, EventConstants, EventAdmin
from org.osgi.service.cm import ManagedService

from org.eclipse.smarthome.automation import Visibility
from org.eclipse.smarthome.config.core import Configuration

from openhab.log import logging
log = logging.getLogger("OsgiEventAdmin")

from org.eclipse.smarthome.automation.handler import TriggerHandler

from openhab.jsr223 import scope
scope.ScriptExtension.importPreset("RuleSupport")
scope.ScriptExtension.importPreset("RuleFactories")

from openhab.osgi import bundle_context

def hashtable(*key_values):
    """
    :param key_values: 2-tuples of (key, value)
    :return: initialized Hashtable
    """
    ht = java.util.Hashtable()
    for k, v in key_values:
        ht.put(k, v)
    return ht

class OsgiEventAdmin(object):
    _event_handler = None
    _event_listeners = []
    
    class OsgiEventHandler(EventHandler):
        def __init__(self):
            self.registration = bundle_context.registerService(
                EventHandler, self, hashtable((EventConstants.EVENT_TOPIC, ["*"])))

        def _log_event(self, event):
            log.info("OSGI event: %s", event)
            for name in event.propertyNames:
                log.info("  '{}': {}".format(name, event.getProperty(name)))
            
        def handleEvent(self, event):
            #self._log_event(event)
            for listener in OsgiEventAdmin._event_listeners:
                try:
                    listener(event)
                except:
                    log.error("Listener failed: %s", traceback.format_exc())
        
        def dispose(self):
            self.registration.unregister()

    @classmethod
    def add_listener(cls, listener):
        cls._event_listeners.append(listener)
        if len(cls._event_listeners) == 1:
            if cls._event_handler is None:
                log.info("Registering OSGI event listener")
                cls._event_handler = OsgiEventAdmin.OsgiEventHandler()
            
    @classmethod
    def remove_listener(cls, listener):
        if listener in cls._event_listeners:
            cls._event_listeners.remove(listener)
        if len(cls._event_listeners) == 0:
            if cls._event_handler is not None:
                log.info("Unregistering OSGI event listener")
                cls._event_handler.dispose()
                cls._event_handler = None

    
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
        try:
            handler = OsgiEventTriggerHandlerFactory.Handler(self, trigger)
            self.handlers.append(handler)
            OsgiEventAdmin.add_listener(handler.on_event)       
            return handler
        except:
            print traceback.format_exc()
    
    def ungetHandler(self, module, ruleUID, handler):
        self.handlers.remove(handler)
        OsgiEventAdmin.remove_listener(handler.on_event)

TRIGGER_MODULE_ID = "jsr223.OsgiEventTrigger"

scope.HandlerRegistry.addTriggerType(scope.TriggerType(TRIGGER_MODULE_ID, [],
    "an OSGI event is published", 
    "Triggers when an OSGI event is published",
    set(), Visibility.VISIBLE, []))

scope.HandlerRegistry.addTriggerHandler(TRIGGER_MODULE_ID, OsgiEventTriggerHandlerFactory())

class OsgiEventTrigger(scope.Trigger):
    def __init__(self):
        triggerName = uuid.uuid1().hex
        config = { }
        scope.Trigger.__init__(self, triggerName, "jsr223.OsgiEventTrigger", Configuration(config))

    