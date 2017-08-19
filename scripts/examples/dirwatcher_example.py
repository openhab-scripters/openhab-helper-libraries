
# Requires 000_DirectoryTrigger.py component

from openhab.log import logging
from openhab.triggers import DirectoryEventTrigger, ENTRY_CREATE     
from openhab.rules import rule

scriptExtension.importPreset("RuleSupport")
    
@rule
class DirectoryWatcherExampleRule(object):
    def getEventTriggers(self):
        return [ DirectoryEventTrigger("/tmp", event_kinds=[ENTRY_CREATE]) ]
    
    def execute(self, module, inputs):
        logging.info("detected new file: %s", inputs['path'])

automationManager.addRule(DirectoryWatcherExampleRule())

