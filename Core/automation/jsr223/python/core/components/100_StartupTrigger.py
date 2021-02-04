"""
Defines a rule trigger that triggers a rule when the script loads, including
system startup.
"""
scriptExtension.importPreset("RuleSimple")
scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleFactories")

import core
from core.log import getLogger

try:
    from org.openhab.core.automation.handler import TriggerHandler
except:
    from org.eclipse.smarthome.automation.handler import TriggerHandler

LOG = getLogger("core.StartupTrigger")

core.STARTUP_MODULE_ID = "jsr223.StartupTrigger"


class _StartupTriggerHandlerFactory(TriggerHandlerFactory):

    class Handler(TriggerHandler):

        def __init__(self, trigger):
            self.trigger = trigger

        def setCallback(self, callback):
            from threading import Timer
            start_timer = Timer(1, lambda: callback.triggered(self.trigger, {'startup': True}))
            start_timer.start()

        def dispose(self):
            pass

    def get(self, trigger):
        return self.Handler(trigger)

    def ungetHandler(self, module, rule_uid, handler):
        pass

    def dispose(self):
        pass


def scriptLoaded(script):
    automationManager.addTriggerHandler(core.STARTUP_MODULE_ID, _StartupTriggerHandlerFactory())
    LOG.info("TriggerHandler added '{}'".format(core.STARTUP_MODULE_ID))

    automationManager.addTriggerType(TriggerType(
        core.STARTUP_MODULE_ID, None,
        "System started or rule saved",
        "Triggers when the rule is added, which occurs when the system has started or the rule has been saved",
        None, Visibility.VISIBLE, None))
    LOG.info("TriggerType added '{}'".format(core.STARTUP_MODULE_ID))


def scriptUnloaded():
    automationManager.removeHandler(core.STARTUP_MODULE_ID)
    automationManager.removeModuleType(core.STARTUP_MODULE_ID)
    LOG.info("TriggerType and TriggerHandler removed")
