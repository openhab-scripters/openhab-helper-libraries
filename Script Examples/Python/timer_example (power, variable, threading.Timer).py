"""
This is an example rule that turns an outlet ON/OFF based on a power meter
using threading.Timer.
"""
from threading import Timer

from core.rules import rule
from core.triggers import when

charger_timer = None

'''
Possible timer states:
NEW - instantiated
RUNNABLE - defined
TIMED_WAITING - timer is running (slight delay after timer is stopped)
TERMINATED - timer completed or stopped
'''


def scriptUnloaded():
    # This function is called when each script is unloaded and is a nice way to cleanup timers
    if charger_timer is not None and charger_timer.isAlive():
        charger_timer.stop()


@rule("Example rule using python threading.timer")
@when("Item Outlet9_Power changed")
def battery_charging_monitor(event):
    battery_charging_monitor.log.debug("Battery charging monitor: {}: start".format(event.itemState))
    global charger_timer
    if items["Outlet9"] == ON and event.itemState <= DecimalType(8) and event.oldItemState <= DecimalType(8):
        if charger_timer is None or not charger_timer.isAlive():
            charger_timer = Timer(600, lambda: events.sendCommand("Outlet9","OFF"))# 600 seconds = 5 minutes
            charger_timer.start()
            battery_charging_monitor.log.info("Battery charging monitor: Started battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState, event.oldItemState))
    elif charger_timer is not None and charger_timer.isAlive():
        charger_timer.stop()
        battery_charging_monitor.log.info("Battery charging monitor: Canceled battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState, event.oldItemState))

