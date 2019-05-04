# -*- coding: utf-8 -*-
import random
import time

import configuration
from core.log import logging, LOG_PREFIX
from core.jsr223 import scope

from org.joda.time import DateTime
from org.joda.time.format import DateTimeFormat

log = logging.getLogger(LOG_PREFIX + '.core.utils')

def isActive(item):
    '''
    Tries to determine if a device is active (tripped) from the perspective of an alarm system.
    A door lock is special in the way that when it's locked its contacts are OPEN, hence
    the value needs to be inverted for the alarm system to determine if it's 'active'
    '''
    active = False
    if item.state in [scope.ON, scope.OPEN]:
        active = True
    active = not active if configuration.customGroupNames['lockDevice'] in item.groupNames else active
    return active

def kw(dict, search):
    '''Get key by value in dictionary'''
    for k, v in dict.iteritems():
        if v == search:
            return k

def iround(x):
    """iround(number) -> integer. Round a float to the nearest integer."""
    y = round(x) - .5
    return int(y) + (y > 0)

def getItemValue(itemName, defVal):
    '''
    Returns the Item's value if the Item is initialized, otherwise return the default value.
    itemRegistry.getItem will return an object also for uninitialized items but it has less methods.
    '''
    item = scope.itemRegistry.getItem(itemName)
    if type(defVal) is int:
        return item.state.intValue() if item.state not in [scope.NULL, scope.UNDEF] else defVal
    elif type(defVal) is float:
        return item.state.floatValue() if item.state not in [scope.NULL, scope.UNDEF] else defVal
    elif defVal in [scope.ON, scope.OFF, scope.OPEN, scope.CLOSED]:
        return item.state if item.state not in [scope.NULL, scope.UNDEF] else defVal
    elif type(defVal) is str:
        return item.state.toFullString() if item.state not in [scope.NULL, scope.UNDEF] else defVal
    elif type(defVal) is DateTime:
        # We return a org.joda.time.DateTime from a org.eclipse.smarthome.core.library.types.DateTimeType
        return DateTime(item.state.calendar.timeInMillis) if item.state not in [scope.NULL, scope.UNDEF] else defVal
    else:
        log.warn("The type of the passed default value is not handled")
        return None

def getLastUpdate(pe, item):
    '''
    Returns the Item's last update datetime as a 'org.joda.time.DateTime',
    http://joda-time.sourceforge.net/apidocs/org/joda/time/DateTime.html
    '''
    try:
        if pe.lastUpdate(item) is None:
            log.warning("No existing lastUpdate data for item: [{}], returning 1970-01-01T00:00:00Z".format(item.name))
            return DateTime(0)
        return pe.lastUpdate(item).toDateTime()
    except:
        # I have an issue with OH file changes being detected (StartupTrigger only) before the file
        # is completely written. The first read breaks because of a partial file write and the second read succeeds.
        log.warning("Exception when getting lastUpdate data for item: [{}], returning 1970-01-01T00:00:00Z".format(item.name))
        return DateTime(0)

def sendCommand(itemName, newValue):
    '''
    Sends a command to an item regerdless of it's current state
    '''
    events.sendCommand(itemName, str(newValue))

def postUpdate(itemName, newValue):
    '''
    Posts an update to an item regerdless of it's current state
    '''
    events.postUpdate(itemName, str(newValue))

def postUpdateCheckFirst(itemName, newValue, sendACommand=False, floatPrecision=None):
    '''
    newValue must be of a type supported by the item

    Checks if the current state of the item is different than the desired new state.
    If the target state is the same, no update is posted.
    sendCommand vs postUpdate:
    If you want to tell something to change, (turn a light on, change the thermostat
    to a new temperature, start raising the blinds, etc.), then you want to send
    a command to an item using sendCommand.
    If your items' states are not being updated by a binding, the autoupdate feature
    or something else external, you will probably want to update the state in a rule
    using postUpdate.
    '''
    compareValue = None
    item = scope.itemRegistry.getItem(itemName)

    if item.state not in [scope.NULL, scope.UNDEF]:
        if type(newValue) is int:
            compareValue = scope.itemRegistry.getItem(itemName).state.intValue()
        elif type(newValue) is float:
            '''
            Unfortunately, most decimal fractions cannot be represented exactly as binary fractions.
            A consequence is that, in general, the decimal floating-point numbers you enter are only
            approximated by the binary floating-point numbers actually stored in the machine.
            Therefore, comparing the stored value with the new value will most likely always result in a difference.
            You can supply the named argument floatPrecision to round the value before comparing
            '''
            if floatPrecision is None:
                compareValue = scope.itemRegistry.getItem(itemName).state.floatValue()
            else:
                compareValue = round(scope.itemRegistry.getItem(itemName).state.floatValue(), floatPrecision)
        elif newValue in [scope.ON, scope.OFF, scope.OPEN, scope.CLOSED]:
            compareValue = scope.itemRegistry.getItem(itemName).state
        elif type(newValue) is str:
            compareValue = scope.itemRegistry.getItem(itemName).state.toString()
        else:
            log.warn("Can not set [{}] to the unsupported type [{}]. Value: [{}]".format(itemName, type(newValue), newValue))
    if (compareValue is not None and compareValue != newValue) or item.state in [scope.NULL, scope.UNDEF]:
        if sendACommand:
            log.debug("New sendCommand value for [{}] is [{}]".format(itemName, newValue))
            sendCommand(itemName, newValue)
        else:
            log.debug("New postUpdate value for [{}] is [{}]".format(itemName, newValue))
            postUpdate(itemName, newValue)
        return True
    else:
        return False

def sendCommandCheckFirst(itemName, newValue, floatPrecision=None):
    ''' See postUpdateCheckFirst '''
    return postUpdateCheckFirst(itemName, newValue, sendACommand=True, floatPrecision=floatPrecision)

def isBright():
    '''Returns true when light level is bright'''
    return getItemValue(configuration.customItemNames['sysLightLevel'], LIGHT_LEVEL['BRIGHT']) == LIGHT_LEVEL['BRIGHT']

def isShady():
    '''Returns true when shady or darker than shady'''
    return getItemValue(configuration.customItemNames['sysLightLevel'], LIGHT_LEVEL['BRIGHT']) <= LIGHT_LEVEL['SHADY']

def isDark():
    '''Returns true when dark or darker than dark'''
    return getItemValue(configuration.customItemNames['sysLightLevel'], LIGHT_LEVEL['BRIGHT']) <= LIGHT_LEVEL['DARK']

def isBlack():
    '''Returns true if black, otherwise false'''
    return getItemValue(configuration.customItemNames['sysLightLevel'], LIGHT_LEVEL['BRIGHT']) <= LIGHT_LEVEL['BLACK']

'''
				 Safety pig has arrived!
				
				  _._ _..._ .-',     _.._(`))
				 '-. `     '  /-._.-'    ',/
				    )         \            '.
				   / _    _    |             \
				  |  a    a    /              |
				  \   .-.                     ;  
				   '-('' ).-'       ,'       ;
				      '-;           |      .'
				         \           \    /
				         | 7  .__  _.-\   \
				         | |  |  ``/  /`  /
				        /,_|  |   /,_/   /
				           /,_/      '`-'
'''
