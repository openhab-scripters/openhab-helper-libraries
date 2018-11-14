from org.eclipse.smarthome.automation import Visibility
from org.eclipse.smarthome.automation.handler import TriggerHandler

import core

from core.jsr223 import scope
scope.scriptExtension.importPreset("RuleSupport")
scope.scriptExtension.importPreset("RuleFactories")

class _ShutdownTriggerHandlerFactory(scope.TriggerHandlerFactory):
        
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
    scope.automationManager.addTriggerHandler(
        core.SHUTDOWN_MODULE_ID, 
        _ShutdownTriggerHandlerFactory())

    scope.automationManager.addTriggerType(scope.TriggerType(
        core.SHUTDOWN_MODULE_ID, [],
        "the rule is activated", 
        "Triggers when a rule is activated the first time",
        set(), Visibility.VISIBLE, []))
    
def scriptUnloaded():
    scope.automationManager.removeHandler(core.SHUTDOWN_MODULE_ID)
    scope.automationManager.removeModuleType(core.SHUTDOWN_MODULE_ID)
