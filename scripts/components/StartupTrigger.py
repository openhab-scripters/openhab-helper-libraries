from org.eclipse.smarthome.automation import Visibility
from org.eclipse.smarthome.automation.handler import TriggerHandler


from openhab.jsr223 import scope
scope.ScriptExtension.importPreset("RuleSupport")
scope.ScriptExtension.importPreset("RuleFactories")

class _StartupTriggerHandlerFactory(scope.TriggerHandlerFactory):    
        
    class Handler(TriggerHandler):
        def __init__(self, trigger):
            self.trigger = trigger
            
        def setRuleEngineCallback(self, rule_engine_callback):
            rule_engine_callback.triggered(self.trigger, {})
            
        def dispose(self):
            pass
        
    def get(self, trigger):
        return _StartupTriggerHandlerFactory.Handler(trigger)
    
    def ungetHandler(self, module, ruleUID, handler):
        pass
    
    def dispose(self):
        pass
    
STARTUP_MODULE_ID = "jsr223.StartupTrigger"

scope.HandlerRegistry.addTriggerType(scope.TriggerType(
    STARTUP_MODULE_ID, [],
    "the rule is activated", 
    "Triggers when a rule is activated the first time",
    set(), Visibility.VISIBLE, []))

scope.HandlerRegistry.addTriggerHandler(STARTUP_MODULE_ID, _StartupTriggerHandlerFactory())