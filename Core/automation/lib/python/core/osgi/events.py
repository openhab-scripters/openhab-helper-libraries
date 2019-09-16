"""
This module provides an OSGi EventAdmin event monitor and rule trigger. This
can trigger off any OSGi event. Rule manager events are filtered to avoid
circular loops in the rule execution.

.. code-block::

    class ExampleRule(SimpleRule):
        def __init__(self):
            self.triggers = [ core.osgi.events.OsgiEventTrigger() ]

        def execute(self, module, inputs):
            event = inputs['event']
            # do something with event
"""
from core.jsr223.scope import scriptExtension
scriptExtension.importPreset("RuleSupport")
from core.jsr223.scope import Trigger, TriggerBuilder, Configuration

import uuid
import java.util
import traceback

from org.osgi.framework import FrameworkUtil
from org.osgi.service.event import EventHandler, EventConstants, EventAdmin
from org.osgi.service.cm import ManagedService

import core
from core.osgi import bundle_context
from core.log import logging, LOG_PREFIX

log = logging.getLogger("{}.core.osgi.events".format(LOG_PREFIX))

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
            self.log = logging.getLogger("jsr223.jython.core.osgi.events.OsgiEventHandler")
            self.registration = bundle_context.registerService(
                EventHandler, self, hashtable((EventConstants.EVENT_TOPIC, ["*"])))
            self.log.info("Registered openHAB OSGi event listener service")
            self.log.debug("Registration: [{}]".format(self.registration))

        def handleEvent(self, event):
            self.log.debug("Handling event: [{}]".format(event))
            for listener in OsgiEventAdmin._event_listeners:
                try:
                    listener(event)
                except:
                    self.log.error("Listener failed: [{}]".format(traceback.format_exc()))

        def dispose(self):
            self.registration.unregister()

    @classmethod
    def add_listener(cls, listener):
        cls.log.debug("Adding listener admin: [{} {}]".format(id(cls), listener))
        cls._event_listeners.append(listener)
        if len(cls._event_listeners) == 1:
            if cls._event_handler is None:
                cls._event_handler = cls.OsgiEventHandler()

    @classmethod
    def remove_listener(cls, listener):
        cls.log.debug("Removing listener: [{}]".format(listener))
        if listener in cls._event_listeners:
            cls._event_listeners.remove(listener)
        if len(cls._event_listeners) == 0:
            if cls._event_handler is not None:
                cls.log.info("Unregistering openHAB OSGi event listener service")
                cls._event_handler.dispose()
                cls._event_handler = None


# The OH / JSR223 design does not allow trigger handlers to access
# the original trigger instance. The trigger information is copied into a
# RuntimeTrigger and then provided to the trigger handler. Therefore, there
# is no way AFAIK to access the original trigger from the trigger handler.
# Another option is to pass trigger information in the configuration, but
# OSGi doesn't support passing Jython-related objects. To work around these
# issues, the following dictionary provides a side channel for obtaining the original
# trigger.
osgi_triggers = {}

class OsgiEventTrigger(Trigger):
    """Filter is a predicate taking an event argument and returning True (keep) or False (drop)"""
    def __init__(self, filter=None):
        self.filter = filter or (lambda event: True)
        triggerName = type(self).__name__ + "-" + uuid.uuid1().hex
        self.trigger = TriggerBuilder.create().withId(triggerName).withTypeUID("jsr223.OsgiEventTrigger").withConfiguration(Configuration()).build()
        global osgi_triggers
        osgi_triggers[triggerName] = self

    def event_filter(self, event):
        return self.filter(event)

    def event_transformer(self, event):
        return event

def log_event(event):
    log.info("OSGI event: [{} ({})]".format(event, type(event).__name__))
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
