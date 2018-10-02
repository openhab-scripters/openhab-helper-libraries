from org.slf4j import Logger, LoggerFactory
from openhab.triggers import item_triggered
from threading import Timer
log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")
chargerTimerAttached = None

'''
Possible timer states:
NEW - instantiated
RUNNABLE - defined
TIMED_WAITING - timer is running (slight delay after timer is stopped)
TERMINATED - timer completed or stopped
'''

@item_triggered("Outlet9_Power")
def batteryChargingMonitor(event):
    #log.debug("JSR223: Power: Battery charging monitor: {}: start".format(event.itemState))
    global chargerTimerAttached
    if items["Outlet9"] == OnOffType.ON and event.itemState <= DecimalType(8) and event.oldItemState <= DecimalType(8):
        if not chargerTimerAttached or str(chargerTimerAttached.getState()) == "TERMINATED":
            chargerTimerAttached = Timer(600, lambda: events.sendCommand("Outlet9","OFF"))
            chargerTimerAttached.start()
            log.debug("JSR223: Power: Battery charging monitor: Started battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState,event.oldItemState))
    elif chargerTimerAttached and str(chargerTimerAttached.getState()) == "TIMED_WAITING":
        chargerTimerAttached.stop()
        log.debug("JSR223: Power: Battery charging monitor: Cancelled battery charging turn off timer: Outlet9_Power=[{}], oldItemState=[{}]".format(event.itemState,event.oldItemState))
