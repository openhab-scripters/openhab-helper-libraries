# pylint: disable=wrong-import-position, invalid-name
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
import uuid
import traceback

import java.util

from org.osgi.service.event import EventHandler, EventConstants#, EventAdmin

from core.jsr223.scope import scriptExtension
scriptExtension.importPreset("RuleSupport")
from core.jsr223.scope import Trigger, TriggerBuilder, Configuration
from core.osgi import BUNDLE_CONTEXT
from core.log import getLogger

LOG = getLogger(u"core.osgi.events")


def hashtable(*key_values):
    """
    Creates a Hashtable from 2-tuples of key/value pairs.

    Args:
        key_values (2-tuples): the key/value pairs to add to the Hashtable

    Returns:
        java.util.Hashtable: initialized Hashtable
    """
    _hashtable = java.util.Hashtable()
    for key, value in key_values:
        _hashtable.put(key, value)
    return _hashtable


class OsgiEventAdmin(object):

    _event_handler = None
    event_listeners = []
    log = getLogger(u"core.osgi.events.OsgiEventAdmin")

    # Singleton
    class OsgiEventHandler(EventHandler):

        def __init__(self):
            self.log = getLogger("core.osgi.events.OsgiEventHandler")
            self.registration = BUNDLE_CONTEXT.registerService(
                EventHandler, self, hashtable((EventConstants.EVENT_TOPIC, ["*"])))
            self.log.info("Registered openHAB OSGi event listener service")
            self.log.debug("Registration: [{}]".format(self.registration))

        def handleEvent(self, event):
            self.log.critical("Handling event: [{}]".format(event))
            for listener in OsgiEventAdmin.event_listeners:
                try:
                    listener(event)
                except:
                    self.log.error("Listener failed: '{}'".format(traceback.format_exc()))

        def dispose(self):
            self.registration.unregister()

    @classmethod
    def add_listener(class_, listener):
        class_.log.debug("Adding listener admin: '{} {}'".format(id(class_), listener))
        class_.event_listeners.append(listener)
        if len(class_.event_listeners) == 1:
            if class_._event_handler is None:
                class_._event_handler = class_.OsgiEventHandler()

    @classmethod
    def remove_listener(class_, listener):
        class_.log.debug("Removing listener: '{}'".format(listener))
        if listener in class_.event_listeners:
            class_.event_listeners.remove(listener)
        if not class_.event_listeners:
            if class_._event_handler is not None:
                class_.log.info("Unregistering openHAB OSGi event listener service")
                class_._event_handler.dispose()
                class_._event_handler = None


# The OH / JSR223 design does not allow trigger handlers to access
# the original trigger instance. The trigger information is copied into a
# RuntimeTrigger and then provided to the trigger handler. Therefore, there
# is no way AFAIK to access the original trigger from the trigger handler.
# Another option is to pass trigger information in the configuration, but
# OSGi doesn't support passing Jython-related objects. To work around these
# issues, the following dictionary provides a side channel for obtaining the original
# trigger.
OSGI_TRIGGERS = {}

class OsgiEventTrigger(Trigger):

    def __init__(self, filter_predicate=None):
        """
        The filter_predicate is a predicate taking an event argument and
        returning True (keep) or False (drop).
        """
        self.filter = filter_predicate or (lambda event: True)
        trigger_name = type(self).__name__ + "-" + uuid.uuid1().hex
        self.trigger = TriggerBuilder.create().withId(trigger_name).withTypeUID("jsr223.OsgiEventTrigger").withConfiguration(Configuration()).build()
        LOG.warn("self.trigger.id: {}".format(self.trigger.id))
        LOG.warn("trigger_name: {}".format(trigger_name))
        OSGI_TRIGGERS[trigger_name] = self.trigger
        #OSGI_TRIGGERS[self.id] = self
        #OSGI_TRIGGERS[self.trigger.id] = self

    def event_filter(self, event):
        return self.filter(event)

    def event_transformer(self, event):
        return event


def log_event(event):
    LOG.info("OSGi event: '{} ({})'".format(event, type(event).__name__))
    if isinstance(event, dict):
        for name in event:
            value = event[name]
            LOG.info("  '{}': {} ({})".format(name, value, type(value)))
    else:
        for name in event.propertyNames:
            value = event.getProperty(name)
            LOG.info("  '{}': {} ({})".format(name, value, type(value)))


def event_dict(event):
    return {key: event.getProperty(key) for key in event.getPropertyNames()}
