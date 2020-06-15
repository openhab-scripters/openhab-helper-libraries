"""
This is an example rule that turns a fan ON/OFF based on a humidity sensor
using a dictionary and threading.Timer.
"""
from threading import Timer

from core.rules import rule
from core.triggers import when

MY_TIMERS = {}


def scriptUnloaded():
    # This function is called when each script is unloaded and is a nice way to cleanup timers
    for timer in MY_TIMERS.keys():
        if MY_TIMERS.get(timer) is not None and MY_TIMERS[timer].isAlive():
            MY_TIMERS[timer].cancel()


def timer_function():
    events.sendCommand("Bathroom_Fan", "OFF")
    test_timer_rule.log.debug("Timer has executed")


@rule("Bathroom fan adjustment")
@when("Item Humidity_Sensor changed")
def test_timer_rule(event):
    if event.itemState >= DecimalType(90):
        # The conditions have been met to turn on the fan
        test_timer_rule.log.debug("Conditions met to turn off fan")
        if MY_TIMERS.get("fan_timer") is not None and MY_TIMERS["fan_timer"].isAlive():
            # If the timer is running, cancel it
            MY_TIMERS["fan_timer"].cancel()
            test_timer_rule.log.debug("Timer stopped")
        if items["Bathroom_Fan"] == OFF:
            # The fan is OFF, so turn it ON
            events.sendCommand("Bathroom_Fan", "ON")
    elif items["Bathroom_Fan"] == ON and event.itemState < DecimalType(90):
        # The conditions have been met to turn OFF the fan
        test_timer_rule.log.debug("Conditions met to turn on fan")
        if MY_TIMERS.get("fan_timer") is None or not MY_TIMERS["fan_timer"].isAlive():
            # A timer does not exist, so create one
            MY_TIMERS["fan_timer"] = Timer(600, lambda: timer_function())
            MY_TIMERS["fan_timer"].start()
            test_timer_rule.log.debug("Timer started")
