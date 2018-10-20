from org.slf4j import Logger, LoggerFactory
from openhab.rules import rule
from openhab.triggers import when
log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Example timer rule using Jython
from threading import Timer
chargerTimerAttached1 = None

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
    #log.debug("JSR223: Power: Battery charging monitor: {}: start".format(event.itemState))
    global chargerTimerAttached1
    if items["Outlet9"] == OnOffType.ON and event.itemState <= DecimalType(8) and event.oldItemState <= DecimalType(8):
        if not chargerTimerAttached1 or str(chargerTimerAttached.getState()) == "TERMINATED":
            chargerTimerAttached1 = Timer(600, lambda: events.sendCommand("Outlet9","OFF"))
            chargerTimerAttached1.start()
            log.info("JSR223: Power: Battery charging monitor: Started battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState,event.oldItemState))
    elif chargerTimerAttached1 and str(chargerTimerAttached1.getState()) == "TIMED_WAITING":
        chargerTimerAttached1.stop()
        log.info("JSR223: Power: Battery charging monitor: Cancelled battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState,event.oldItemState))

# Example using the createTimer Action
from org.eclipse.smarthome.model.script.actions.Timer import *
from org.eclipse.smarthome.model.script.actions.ScriptExecution import createTimer
from org.joda.time import DateTime
chargerTimerAttached2 = None

@rule("Example 2 timer rule)
@when("Item Outlet9_Power changed")
def batteryChargingMonitor2(event):
    #log.debug("JSR223: Power: Battery charging monitor: {}: start".format(event.itemState))
    global chargerTimerAttached2
    if items["Outlet9"] == OnOffType.ON and event.itemState <= DecimalType(8) and event.oldItemState <= DecimalType(8):
        if npt chargerTimerAttached2 or chargerTimerAttached2.hasTerminated():
            chargerTimerAttached2 = creatTimer(DateTime.now().plusMinutes(5), lambda: events.sendCommand("Outlet9","OFF"))
            log.info("JSR223: Power: Battery charging monitor: Started battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState,event.oldItemState))
    elif chargerTimerAttached2 and not chargerTimerAttached2.hasTerminated():
        chargerTimerAttached2.cancel()
        log.info("JSR223: Power: Battery charging monitor: Cancelled battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState,event.oldItemState))
