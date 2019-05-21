from core.rules import rule
from core.triggers import when

# Example using Python threading.Time
from threading import Timer
chargerTimer1 = None

'''
Possible timer states:
NEW - instantiated
RUNNABLE - defined
TIMED_WAITING - timer is running (slight delay after timer is stopped)
TERMINATED - timer completed or stopped
'''

@rule("Example rule using python threading.timer")
@when("Item Outlet9_Power changed")
def batteryChargingMonitor1(event):
    #log.debug("Battery charging monitor: {}: start".format(event.itemState))
    global chargerTimer1
    if items["Outlet9"] == ON and event.itemState <= DecimalType(8) and event.oldItemState <= DecimalType(8):
        if chargerTimer1 is None or str(chargerTimer1.getState()) == "TERMINATED":
            chargerTimer1 = Timer(600, lambda: events.sendCommand("Outlet9","OFF"))# 600 seconds = 5 minutes
            chargerTimer1.start()
            batteryChargingMonitor1.log.info("Battery charging monitor: Started battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState, event.oldItemState))
    elif chargerTimer1 is not None and str(chargerTimer1.getState()) == "TIMED_WAITING":
        chargerTimer1.stop()
        batteryChargingMonitor1.log.info("Battery charging monitor: Cancelled battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState, event.oldItemState))

# Example using the createTimer Action
from core.actions import ScriptExecution
from org.joda.time import DateTime
chargerTimer2 = None

@rule("Example rule using createTimer")
@when("Item Outlet9_Power changed")
def batteryChargingMonitor2(event):
    #log.debug("Battery charging monitor: {}: start".format(event.itemState))
    global chargerTimer2
    if items["Outlet9"] == ON and event.itemState <= DecimalType(8) and event.oldItemState <= DecimalType(8):
        if chargerTimer2 is None or chargerTimer2.hasTerminated():
            chargerTimer2 = ScriptExecution.createTimer(DateTime.now().plusMinutes(5), lambda: events.sendCommand("Outlet9","OFF"))
            batteryChargingMonitor2.log.info("Battery charging monitor: Started battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState, event.oldItemState))
    elif chargerTimer2 is not None and not chargerTimer2.hasTerminated():
        chargerTimer2.cancel()
        batteryChargingMonitor2.log.info("Battery charging monitor: Cancelled battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState, event.oldItemState))
