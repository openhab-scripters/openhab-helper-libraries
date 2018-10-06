from java.nio.file.StandardWatchEventKinds import ENTRY_CREATE, ENTRY_DELETE, ENTRY_MODIFY

from org.eclipse.smarthome.automation.handler import TriggerHandler
from org.eclipse.smarthome.automation.type import TriggerType
from org.eclipse.smarthome.config.core import Configuration
from org.eclipse.smarthome.core.service import AbstractWatchService

import openhab
from openhab.log import log_traceback
from openhab.jsr223 import scope
scope.scriptExtension.importPreset("RuleFactories")

class JythonDirectoryWatcher(AbstractWatchService):
    def __init__(self, path, event_kinds=[ENTRY_CREATE, ENTRY_DELETE, ENTRY_MODIFY], watch_subdirectories=False):
        AbstractWatchService.__init__(self, path)
        self.event_kinds = event_kinds
        self.watch_subdirectories = watch_subdirectories
        self.callback = None
        
    def getWatchEventKinds(self, path):
        return self.event_kinds
    
    def watchSubDirectories(self):
        return self.watch_subdirectories
    
    @log_traceback
    def processWatchEvent(self, event, kind, path):
        if self.callback is not None:
            self.callback(event, kind, path)
    

class _DirectoryEventTriggerHandlerFactory(scope.TriggerHandlerFactory):
        
    class Handler(TriggerHandler):
        @log_traceback
        def __init__(self, trigger):
            scope.TriggerHandler.__init__(self)
            self.rule_engine_callback = None
            self.trigger = trigger
            config = trigger.configuration
            self.watcher = JythonDirectoryWatcher(
                config.get('path'), eval(config.get('event_kinds')),
                watch_subdirectories=config.get('watch_subdirectories'))
            self.watcher.callback = self.handle_directory_event
            self.watcher.activate()
            
        def setRuleEngineCallback(self, rule_engine_callback):
            self.rule_engine_callback = rule_engine_callback
          
        @log_traceback  
        def handle_directory_event(self, event, kind, path):
            self.rule_engine_callback.triggered(self.trigger, {
                'event': event,
                'kind': kind,
                'path': path
            })
            
        def dispose(self):
            self.watcher.deactivate()
            self.watcher = None
        
    def get(self, trigger):
        return _DirectoryEventTriggerHandlerFactory.Handler(trigger)
    

openhab.DIRECTORY_TRIGGER_MODULE_ID = "jsr223.DirectoryTrigger"

def scriptLoaded(*args):
    scope.automationManager.addTriggerHandler(
        openhab.DIRECTORY_TRIGGER_MODULE_ID, 
        _DirectoryEventTriggerHandlerFactory())

    scope.automationManager.addTriggerType(TriggerType(
        openhab.DIRECTORY_TRIGGER_MODULE_ID, [],
        "a directory change event is detected.", 
        "Triggers when a directory change event is detected.",
        set(), Visibility.VISIBLE, []))
    
def scriptUnloaded():
    scope.automationManager.removeHandler(openhab.DIRECTORY_TRIGGER_MODULE_ID)
    scope.automationManager.removeModuleType(openhab.DIRECTORY_TRIGGER_MODULE_ID)
