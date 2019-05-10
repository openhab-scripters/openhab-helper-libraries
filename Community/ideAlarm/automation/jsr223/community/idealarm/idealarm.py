from core.rules import rule
from community.idealarm import ideAlarm

@rule("ideAlarm main rule", description="Make ideAlarm trigger on item changes. Do not alter.")
@ideAlarm.getTriggers()
def ideAlarmMainRule(event):
    ideAlarm.execute(event)
