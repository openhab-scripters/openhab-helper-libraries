
# Requires 000_DirectoryTrigger.py component

from core.log import logging
from core.triggers import DirectoryEventTrigger, ENTRY_CREATE     
from core.rules import rule

scriptExtension.importPreset("RuleSupport")
    
@rule
class DirectoryWatcherExampleRule(object):
    def getEventTriggers(self):
        return [ DirectoryEventTrigger("/tmp", event_kinds=[ENTRY_CREATE]) ]
    
    def execute(self, module, inputs):
        logging.info("detected new file: %s", inputs['path'])

automationManager.addRule(DirectoryWatcherExampleRule())

