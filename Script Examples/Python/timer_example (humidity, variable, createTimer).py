"""
This is an example rule that turns a fan ON/OFF based on a humidity sensor and
using ScriptExecution.createTimer.
"""
from org.joda.time import DateTime

from core.rules import rule
from core.triggers import when
from core.actions import ScriptExecution

fan_timer = None


def scriptUnloaded():
    # This function is called when each script is unloaded and is a nice way to cleanup timers
    if fan_timer is not None and not fan_timer.hasTerminated():
        fan_timer.cancel()


@rule("Bathroom fan adjustment")
@when("Item Humidity_Sensor changed")
def adjust_fan_based_on_humidity(event):
    global fan_timer
    if event.itemState >= DecimalType(90):
        # The conditions have been met to turn on the fan
        adjust_fan_based_on_humidity.log.debug("Conditions met to turn off fan")
        if fan_timer is not None and not fan_timer.hasTerminated():
            # If the timer is running, cancel it
            fan_timer.cancel()
            adjust_fan_based_on_humidity.log.debug("Timer stopped")
        if items["Bathroom_Fan"] == OFF:
            # The fan is OFF, so turn it ON
            events.sendCommand("Bathroom_Fan", "ON")
    elif items["Bathroom_Fan"] == ON and event.itemState < DecimalType(90):
        # The conditions have been met to turn OFF the fan
        adjust_fan_based_on_humidity.log.debug("Conditions met to turn on fan")
        if fan_timer is None or fan_timer.hasTerminated():
            # A timer does not exist, so create one
            fan_timer = ScriptExecution.createTimer(DateTime.now().plusMinutes(5), lambda: events.sendCommand("Bathroom_Fan", "OFF"))
            adjust_fan_based_on_humidity.log.debug("Timer started")
