from core.rules import rule
from community.idealarm import ideAlarm

@rule("ideAlarm main rule", description="Make ideAlarm trigger on item changes. Do not alter.")
@ideAlarm.get_triggers()
def ideAlarm_main_rule(event):
    ideAlarm.execute(event)
