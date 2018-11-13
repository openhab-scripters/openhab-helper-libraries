import traceback
import uuid

from org.osgi.framework import FrameworkUtil
from org.osgi.service.event import EventHandler, EventConstants, EventAdmin
from org.osgi.service.cm import ManagedService

from org.eclipse.smarthome.config.core import Configuration
from org.eclipse.smarthome.automation.handler import TriggerHandler

import openhab
from openhab.jsr223 import scope
scope.scriptExtension.importPreset("RuleSupport")

from openhab.osgi import bundle_context
from openhab.log import logging

import uuid
import java.util

log = logging.getLogger("jython.openhab.osgi.events")

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
    log = logging.getLogger("jython.openhab.osgi.events.OsgiEventAdmin")
    
    _event_handler = None
    _event_listeners = []
    
    # Singleton
    class OsgiEventHandler(EventHandler):
        def __init__(self):
            self.log = logging.getLogger("jython.openhab.osgi.events.OsgiEventHandler")
            self.registration = bundle_context.registerService(
                EventHandler, self, hashtable((EventConstants.EVENT_TOPIC, ["*"])))
            self.log.info("Registered openHAB OSGI event listener service")
            self.log.debug("registration=%s", self.registration)
            
        def handleEvent(self, event):
            self.log.debug("handling event %s", event)
            for listener in OsgiEventAdmin._event_listeners:
                try:
                    listener(event)
                except:
                    self.log.error("Listener failed: %s", traceback.format_exc())
        
        def dispose(self):
            self.registration.unregister()

    @classmethod
    def add_listener(cls, listener):
        cls.log.debug("adding listener admin=%s %s", id(cls), listener)
        cls._event_listeners.append(listener)
        if len(cls._event_listeners) == 1:
            if cls._event_handler is None:
                cls._event_handler = cls.OsgiEventHandler()
            
    @classmethod
    def remove_listener(cls, listener):
        cls.log.debug("removing listener %s", listener)
        if listener in cls._event_listeners:
            cls._event_listeners.remove(listener)
        if len(cls._event_listeners) == 0:
            if cls._event_handler is not None:
                cls.log.info("Unregistering openHAB OSGI event listener service")
                cls._event_handler.dispose()
                cls._event_handler = None

    
# The ESH / JSR223 design does not allow trigger handlers to access
# the original trigger instance. The trigger information is copied into a
# RuntimeTrigger and then provided to the trigger handler. Therefore, there
# is no way AFAIK to access the original trigger from the trigger handler.
# Another option is to pass trigger information in the configuration, but
# OSGi doesn't support passing Jython-related objects. To work around these
# issues, the following dictionary provides a side channel for obtaining the original
# trigger.
osgi_triggers = {}

class OsgiEventTrigger(scope.Trigger):
    """Filter is a predicate taking an event argument and returning True (keep) or False (drop)"""
    def __init__(self, filter=None):
        self.filter = filter or (lambda event: True)
        triggerId = type(self).__name__ + "-" + uuid.uuid1().hex
        config = Configuration()
        scope.Trigger.__init__(self, triggerId, openhab.OSGI_TRIGGER_ID, config)
        global osgi_triggers
        osgi_triggers[self.id] = self
        
    def event_filter(self, event):
        return self.filter(event)
    
    def event_transformer(self, event):
        return event
    
def log_event(event):
    log.info("OSGI event: %s (%s)", event, type(event).__name__)
    if isinstance(event, dict):
        for name in event:
            value = event[name]
            log.info("  '{}': {} ({})".format(name, value, type(value)))
    else:
        for name in event.propertyNames:
            value = event.getProperty(name)
            log.info("  '{}': {} ({})".format(name, value, type(value)))
        
def event_dict(event):
    return { key: event.getProperty(key) for key in event.getPropertyNames() }


    