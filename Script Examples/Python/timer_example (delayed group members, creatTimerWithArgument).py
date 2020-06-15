"""
This is an example rule that iterates through members of a group and creates
timers for each, spaced five seconds apart.
"""
from org.joda.time import DateTime

from core.rules import rule
from core.triggers import when
from core.actions import ScriptExecution


def timer_function(item_name):
    events.sendCommand(item_name, "announce")


@rule("Query Shelly Status")
@when("System started")
@when("Time cron 0 0/5 * * * ?") #every 5 minutes
def query_shelly_status(event):
    index = 0
    for shelly in itemRegistry.getItem("gShellyGeneralCommands").members:
        ScriptExecution.createTimerWithArgument(DateTime.now().plusSeconds(5 * index), shelly.name, timer_function)
        index += 1
