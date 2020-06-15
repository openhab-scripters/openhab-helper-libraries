"""
This is an example rule that turns an outlet ON/OFF based on a power meter
using a dictionary and ScriptExecution.createTimer.
"""
from org.joda.time import DateTime

from core.rules import rule
from core.triggers import when
from core.actions import ScriptExecution

MY_TIMERS = {}


def scriptUnloaded():
    # This function is called when each script is unloaded and is a nice way to cleanup timers
    for timer in MY_TIMERS.keys():
        if MY_TIMERS.get(timer) is not None and not MY_TIMERS[timer].hasTerminated():
            MY_TIMERS[timer].cancel()


@rule("Example rule using createTimer")
@when("Item Outlet9_Power changed")
def battery_charging_monitor(event):
    battery_charging_monitor.log.debug("Battery charging monitor: {}: start".format(event.itemState))
    if items["Outlet9"] == ON and event.itemState <= DecimalType(8) and event.oldItemState <= DecimalType(8):
        if MY_TIMERS.get("charger_timer") is None or MY_TIMERS["charger_timer"].hasTerminated():
            MY_TIMERS["charger_timer"] = ScriptExecution.createTimer(DateTime.now().plusMinutes(5), lambda: events.sendCommand("Outlet9","OFF"))
            battery_charging_monitor.log.info("Battery charging monitor: Started battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState, event.oldItemState))
    elif MY_TIMERS.get("charger_timer") is not None and not MY_TIMERS["charger_timer"].hasTerminated():
        MY_TIMERS.get("charger_timer").cancel()
        battery_charging_monitor.log.info("Battery charging monitor: Canceled battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState, event.oldItemState))
