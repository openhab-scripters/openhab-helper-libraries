from org.eclipse.smarthome.automation import Visibility
from org.eclipse.smarthome.automation.handler import TriggerHandler

import core
from core.jsr223 import scope
from core.log import logging, LOG_PREFIX

log = logging.getLogger(LOG_PREFIX + ".ShutdownTrigger")

scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleFactories")

class _ShutdownTriggerHandlerFactory(TriggerHandlerFactory):
        
    class Handler(TriggerHandler):
        def __init__(self, trigger):
            self.trigger = trigger
            
        def setRuleEngineCallback(self, rule_engine_callback):
            rule_engine_callback.triggered(self.trigger, {'shutdown': True})
            
        def dispose(self):
            pass
        
    def get(self, trigger):
        return _ShutdownTriggerHandlerFactory.Handler(trigger)
    
    def ungetHandler(self, module, ruleUID, handler):
        pass
    
    def dispose(self):
        pass
    
core.SHUTDOWN_MODULE_ID = "jsr223.ShutdownTrigger"

def scriptLoaded(*args):
    automationManager.addTriggerHandler(
        core.SHUTDOWN_MODULE_ID, 
        _ShutdownTriggerHandlerFactory())
    log.info("TriggerHandler added [{}]".format(core.SHUTDOWN_MODULE_ID))

    automationManager.addTriggerType(TriggerType(
        core.SHUTDOWN_MODULE_ID,
        [],
        "the rule is activated", 
        "Triggers when a rule is activated the first time",
        set(),
        Visibility.VISIBLE,
        []))
    log.info("TriggerType added [{}]".format(core.SHUTDOWN_MODULE_ID))

def scriptUnloaded():
    automationManager.removeHandler(core.SHUTDOWN_MODULE_ID)
    automationManager.removeModuleType(core.SHUTDOWN_MODULE_ID)
    log.info("TriggerType and TriggerHandler removed [{}]".format(core.SHUTDOWN_MODULE_ID))