from org.eclipse.smarthome.automation import Visibility
from org.eclipse.smarthome.automation.handler import TriggerHandler

import openhab

from openhab.jsr223 import scope
scope.scriptExtension.importPreset("RuleSupport")
scope.scriptExtension.importPreset("RuleFactories")

class _StartupTriggerHandlerFactory(scope.TriggerHandlerFactory):
        
    class Handler(TriggerHandler):
        def __init__(self, trigger):
            self.trigger = trigger
            
        def setRuleEngineCallback(self, rule_engine_callback):
            rule_engine_callback.triggered(self.trigger, {'startup': True})
            
        def dispose(self):
            pass
        
    def get(self, trigger):
        return _StartupTriggerHandlerFactory.Handler(trigger)
    
    def ungetHandler(self, module, ruleUID, handler):
        pass
    
    def dispose(self):
        pass
    

openhab.STARTUP_MODULE_ID = "jsr223.StartupTrigger"

def scriptLoaded(*args):
    scope.automationManager.addTriggerHandler(
        openhab.STARTUP_MODULE_ID, 
        _StartupTriggerHandlerFactory())

    scope.automationManager.addTriggerType(scope.TriggerType(
        openhab.STARTUP_MODULE_ID, [],
        "the rule is activated", 
        "Triggers when a rule is activated the first time",
        set(), Visibility.VISIBLE, []))
    
def scriptUnloaded():
    scope.automationManager.removeHandler(openhab.STARTUP_MODULE_ID)
    scope.automationManager.removeModuleType(openhab.STARTUP_MODULE_ID)
