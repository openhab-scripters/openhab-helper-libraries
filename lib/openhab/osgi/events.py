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
    
    # Singleton
    class OsgiEventHandler(EventHandler):
        def __init__(self):
            log.info("Registering openHAB OSGI event listener service")
            self.registration = bundle_context.registerService(
                EventHandler, self, hashtable((EventConstants.EVENT_TOPIC, ["*"])))
            
        def handleEvent(self, event):
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
                cls._event_handler = OsgiEventAdmin.OsgiEventHandler()
            
    @classmethod
    def remove_listener(cls, listener):
        if listener in cls._event_listeners:
            cls._event_listeners.remove(listener)
        if len(cls._event_listeners) == 0:
            if cls._event_handler is not None:
                log.info("Unregistering openHAB OSGI event listener service")
                cls._event_handler.dispose()
                cls._event_handler = None

trigger_filters = {}

class OsgiEventTrigger(scope.Trigger):
    """Filter is a predicate taking an event argument and returning True (keep) or False (drop)"""
    def __init__(self, event_filter=None):
        triggerName = uuid.uuid1().hex
        config = Configuration()
        if event_filter is not None:
            # openHAB/OSGI forces this side channel :-(
            filter_id = str(uuid.uuid4())
            global trigger_filters
            trigger_filters[filter_id] = event_filter
            config.put('filter_id', filter_id)
        scope.Trigger.__init__(self, triggerName, openhab.OSGI_TRIGGER_ID, config)
        
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


    