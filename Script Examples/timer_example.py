from core.rules import rule
from core.triggers import when
from core.log import logging, LOG_PREFIX
log = logging.getLogger(LOG_PREFIX + ".timer_example")

# Example timer rule using Jython
from threading import Timer
chargerTimer1 = None

'''
Possible timer states:
NEW - instantiated
RUNNABLE - defined
TIMED_WAITING - timer is running (slight delay after timer is stopped)
TERMINATED - timer completed or stopped
'''
@rule("Example 1 timer rule)
@when("Item Outlet9_Power changed")
def batteryChargingMonitor1(event):
    #log.debug("Battery charging monitor: {}: start".format(event.itemState))
    global chargerTimer1
    if items["Outlet9"] == OnOffType.ON and event.itemState <= DecimalType(8) and event.oldItemState <= DecimalType(8):
        if chargerTimer1 is None or str(chargerTimerAttached.getState()) == "TERMINATED":
            chargerTimer1 = Timer(600, lambda: events.sendCommand("Outlet9","OFF"))
            chargerTimer1.start()
            log.info("Battery charging monitor: Started battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState,event.oldItemState))
    elif chargerTimer1 is not None and str(chargerTimer1.getState()) == "TIMED_WAITING":
        chargerTimer1.stop()
        log.info("Battery charging monitor: Cancelled battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState,event.oldItemState))

# Example using the createTimer Action
from org.eclipse.smarthome.model.script.actions.Timer import *
from org.eclipse.smarthome.model.script.actions.ScriptExecution import createTimer
from org.joda.time import DateTime
chargerTimer2 = None

@rule("Example 2 timer rule)
@when("Item Outlet9_Power changed")
def batteryChargingMonitor2(event):
    #log.debug("Battery charging monitor: {}: start".format(event.itemState))
    global chargerTimer2
    if items["Outlet9"] == OnOffType.ON and event.itemState <= DecimalType(8) and event.oldItemState <= DecimalType(8):
        if chargerTimer2 is None or chargerTimer2.hasTerminated():
            chargerTimer2 = creatTimer(DateTime.now().plusMinutes(5), lambda: events.sendCommand("Outlet9","OFF"))
            log.info("Battery charging monitor: Started battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState,event.oldItemState))
    elif chargerTimer2 is not None and not chargerTimer2.hasTerminated():
        chargerTimer2.cancel()
        log.info("Battery charging monitor: Cancelled battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState,event.oldItemState))
