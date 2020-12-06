# pylint: disable=eval-used
"""
This rule trigger responds to events on the OSGi EventAdmin event bus.
"""
scriptExtension.importPreset("RuleSimple")
scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleFactories")

import core
from core.osgi.events import OsgiEventAdmin, event_dict, OSGI_TRIGGERS
from core.log import logging, LOG_PREFIX, log_traceback

try:
    from org.openhab.core.automation.handler import TriggerHandler
except:
    from org.eclipse.smarthome.automation.handler import TriggerHandler

LOG = logging.getLogger("{}.core.OsgiEventTrigger".format(LOG_PREFIX))
core.OSGI_TRIGGER_ID = "jsr223.OsgiEventTrigger"


class OsgiEventTriggerHandlerFactory(TriggerHandlerFactory):

    def __init__(self):
        self.handlers = []

    class Handler(TriggerHandler):

        def __init__(self, factory, runtime_trigger):
            TriggerHandler.__init__(self)
            self.rule_engine_callback = None
            self.factory = factory
            self.trigger = OSGI_TRIGGERS.get(runtime_trigger.id, runtime_trigger)
            self.filter = getattr(self.trigger, "event_filter", None)
            self.transformer = getattr(self.trigger, "event_transformer", None)
            LOG.warn("Creating trigger handler for '{}' ('{}'), filter={}, transformer={}".format(type(self.trigger).__name__, self.trigger.id, self.filter, self.transformer))

        def setCallback(self, callback):
            LOG.warn("setCallback")
            self.rule_engine_callback = callback

        def dispose(self):
            LOG.warn("Disposing '{}' (module '{}')".format(self, self.trigger.id))
            self.factory.handlers.remove(self)
            OsgiEventAdmin.remove_listener(self.on_event)
            if self.trigger.id in OSGI_TRIGGERS:
                del OSGI_TRIGGERS[self.trigger.id]

        @log_traceback
        def on_event(self, event):
            LOG.warn("on_event")
            if self.rule_engine_callback and event.getProperty('source') != 'RuleRegistryImpl':
                event = event_dict(event)
                if self.filter is not None and not self.filter(event):
                    return
                inputs = self.transformer and self.transformer(event) or {'event': event}
                self.rule_engine_callback.triggered(self.trigger, inputs)

    def get(self, trigger):
        LOG.warn("get")
        handler = OsgiEventTriggerHandlerFactory.Handler(self, trigger)
        self.handlers.append(handler)
        OsgiEventAdmin.add_listener(handler.on_event)
        return handler


def scriptLoaded(script):
    automationManager.addTriggerHandler(core.OSGI_TRIGGER_ID, OsgiEventTriggerHandlerFactory())
    LOG.info("TriggerHandler added '{}'".format(core.OSGI_TRIGGER_ID))

    automationManager.addTriggerType(TriggerType(
        core.OSGI_TRIGGER_ID, None,
        "an OSGI event is published",
        "Triggers when an OSGi event is published",
        None, Visibility.VISIBLE, None))
    LOG.info("TriggerType added '{}'".format(core.OSGI_TRIGGER_ID))


def scriptUnloaded():
    automationManager.removeHandler(core.OSGI_TRIGGER_ID)
    automationManager.removeModuleType(core.OSGI_TRIGGER_ID)
    LOG.info("TriggerType and TriggerHandler removed '{}'".format(core.OSGI_TRIGGER_ID))
