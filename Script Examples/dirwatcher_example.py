
# Requires 000_DirectoryTrigger.py component

from core.triggers import DirectoryEventTrigger, ENTRY_CREATE     
from core.rules import rule
from core.log import logging, LOG_PREFIX

@rule("Directory watcher example")
class DirectoryWatcherExampleRule(object):
    def getEventTriggers(self):
        return [ DirectoryEventTrigger("/tmp", event_kinds=[ENTRY_CREATE]) ]
    
    def execute(self, module, inputs):
        logging.getLogger(LOG_PREFIX + ".directory_watcher_example").info("Detected new file: [{}]".format(inputs['path']))