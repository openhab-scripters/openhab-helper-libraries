from core.rules import rule
from community.idealarm import ideAlarm

@rule("Example ideAlarm rule", description="Make ideAlarm trigger on item changes")
@ideAlarm.getTriggers()
def exampleIdealarmRule(event):
    ideAlarm.execute(event)