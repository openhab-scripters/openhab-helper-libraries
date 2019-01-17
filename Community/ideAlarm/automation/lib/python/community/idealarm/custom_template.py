# -*- coding: utf-8 -*-
'''
Custom ideAlarm functions library.
Edit this file to suit your needs.
'''
from org.eclipse.smarthome.core.types import UnDefType
from org.eclipse.smarthome.core.library.types import OnOffType, OpenClosedType
from core.log import logging, LOG_PREFIX
from logging import DEBUG, INFO, WARNING, ERROR
from core.utils import kw
log = logging.getLogger(LOG_PREFIX + '.ideAlarm.custom')
# Get direct access to the JSR223 scope types and objects (for Jython modules imported into scripts)
from core.jsr223.scope import events, itemRegistry

NULL = UnDefType.NULL
UNDEF = UnDefType.UNDEF
ON = OnOffType.ON
OFF = OnOffType.OFF
OPEN = OpenClosedType.OPEN
CLOSED = OpenClosedType.CLOSED

ZONESTATUS = {'NORMAL': 0, 'ALERT': 1, 'ERROR': 2, 'TRIPPED': 3, 'ARMING': 4}
ARMINGMODE = {'DISARMED': 0, 'ARMED_HOME': 1, 'ARMED_AWAY': 2}

def onArmingModeChange(zone, newArmingMode, oldArmingMode):
    '''
    This function will be called when there is a change of arming mode for a zone.
    oldArmingMode is None when initializing.
    '''
    if zone.zoneNumber == 1:
        if oldArmingMode is not None:
            pass

        if newArmingMode == ARMINGMODE['DISARMED']:
            pass
        elif newArmingMode == ARMINGMODE['ARMED_HOME']:
            pass

        if newArmingMode != ARMINGMODE['DISARMED']:
            pass

    log.debug('Custom function: onArmingModeChange: '+zone.name.decode('utf-8')+' ---> '+kw(ARMINGMODE, newArmingMode))

def onZoneStatusChange(zone, newZoneStatus, oldZoneStatus, errorMessage=None):
    '''
    This function will be called when there is a change of zone status.
    oldZoneStatus is None when initializing.
    '''
    log.info('Custom function: onZoneStatusChange: '+zone.name.decode('utf-8')+' ---> '+kw(ZONESTATUS, newZoneStatus))

    if newZoneStatus == ZONESTATUS['ERROR']:
        pass
    elif newZoneStatus == ZONESTATUS['ALERT']:
        # Get all sensors that have been tripped since 2 minutes regardless of their current state
        # considering that an intruder might have closed a tripped door already when this is running
        if zone.alarmTestMode:
            pass
        else:
            pass
    elif newZoneStatus == ZONESTATUS['TRIPPED']:
        if zone.zoneNumber == 1:
            pass
    elif newZoneStatus == ZONESTATUS['ARMING']:
        if zone.zoneNumber == 1:
            pass

def onArmingWithOpenSensors(zone, armingMode):
    '''
    There might be open sensors when trying to arm. If so, this function gets called.
    (That doesn't necessarily need to be an error condition).
    However if the zone has been configured not to allow opened sensors during arming, 
    the zone status onZoneStatusChange will be called with status ERROR.
    '''
    return

def onNagTimer(zone, nagSensors):
    '''
    You should do something about the open doors!
    '''
    return
