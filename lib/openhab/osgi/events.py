import traceback
import uuid

from org.osgi.framework import FrameworkUtil
from org.osgi.service.event import EventHandler, EventConstants, EventAdmin
from org.osgi.service.cm import ManagedService

from org.eclipse.smarthome.config.core import Configuration
from org.eclipse.smarthome.automation.handler import TriggerHandler

from openhab.jsr223 import scope
scope.ScriptExtension.importPreset("RuleSupport")

from openhab.osgi import bundle_context
from openhab.log import logging

log = logging.getLogger("OsgiEventAdmin")

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

class OsgiEventTrigger(scope.Trigger):
    def __init__(self):
        triggerName = uuid.uuid1().hex
        config = { }
        scope.Trigger.__init__(self, triggerName, "jsr223.OsgiEventTrigger", Configuration(config))

    