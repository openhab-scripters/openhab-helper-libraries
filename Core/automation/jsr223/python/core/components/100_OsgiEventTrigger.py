"""
This rule trigger responds to events on the OSGI EventAdmin event bus.
"""

scriptExtension.importPreset(None)

import java.util
import traceback
import uuid

try:
    from org.openhab.core.automation.handler import TriggerHandler
except:
    from org.eclipse.smarthome.automation.handler import TriggerHandler

import core
from core.osgi.events import OsgiEventAdmin, event_dict, osgi_triggers
from core.log import logging, LOG_PREFIX

log = logging.getLogger("{}.core.OsgiEventTrigger".format(LOG_PREFIX))

scriptExtension.importPreset("RuleSimple")
scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleFactories")

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
                log.debug("Creating trigger handler for {} ({}), filter={}, transformer={}".format(type(self.trigger).__name__, self.trigger.id, self.filter, self.transformer))
            except:
                log.error(traceback.format_exc())

        def setRuleEngineCallback(self, rule_engine_callback):
            self.rule_engine_callback = rule_engine_callback

        def dispose(self):
            log.debug("Disposing {} (module {})".format(self, self.trigger.id))
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
        handler = OsgiEventTriggerHandlerFactory.Handler(trigger)
        self.handlers.append(handler)
        OsgiEventAdmin.add_listener(handler.on_event)
        return handler

core.OSGI_TRIGGER_ID = "jsr223.OsgiEventTrigger"

def scriptLoaded(*args):
    automationManager.addTriggerHandler(core.OSGI_TRIGGER_ID, OsgiEventTriggerHandlerFactory())
    log.info("TriggerHandler added [{}]".format(core.OSGI_TRIGGER_ID))

    automationManager.addTriggerType(TriggerType(core.OSGI_TRIGGER_ID, None,
        "an OSGI event is published",
        "Triggers when an OSGI event is published",
        None, Visibility.VISIBLE, None))
    log.info("TriggerType added [{}]".format(core.OSGI_TRIGGER_ID))

def scriptUnloaded():
    automationManager.removeHandler(core.OSGI_TRIGGER_ID)
    automationManager.removeModuleType(core.OSGI_TRIGGER_ID)
    log.info("TriggerType and TriggerHandler removed [{}]".format(core.OSGI_TRIGGER_ID))
