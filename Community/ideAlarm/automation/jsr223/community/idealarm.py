from core.rules import rule
from idealarm import ideAlarm
from core.utils import hasReloadFinished

@rule("Example ideAlarm rule")
class ideAlarmTrigger(object):

    """Make ideAlarm trigger on item changes"""
    def getEventTriggers(self):
        return ideAlarm.getTriggers()

    def execute(self, modules, inputs):
        if not hasReloadFinished(True): return
        ideAlarm.execute(self, modules, inputs)
