from org.eclipse.smarthome.core.types import UnDefType
from org.eclipse.smarthome.core.library.types import IncreaseDecreaseType, NextPreviousType, OnOffType, OpenClosedType, PlayPauseType, RewindFastforwardType, StopMoveType, UpDownType, DecimalType
import org.joda.time.DateTime as DateTime

import time
import random

from core.log import logging, LOG_PREFIX
log = logging.getLogger(LOG_PREFIX + '.utils')

import config
reload(config)
import config

from core.jsr223.scope import events, itemRegistry

NULL = UnDefType.NULL
UNDEF = UnDefType.UNDEF
ON = OnOffType.ON
OFF = OnOffType.OFF
OPEN = OpenClosedType.OPEN
CLOSED = OpenClosedType.CLOSED

def kw(dict, search):
    '''Get key by value in dictionary'''
    for k, v in dict.iteritems():
        if v == search:
            return k

def isActive(item):
    '''
    Tries to determine if a device is active (tripped) from the perspective of an alarm system.
    A door lock is special in the way that when it's locked its contacts are OPEN hence
    the value needs to be inverted for the alarm system to determine if it's 'active'
    '''
    active = False
    if item.state in [ON, OPEN]:
        active = True
    # active = not active if config.customGroupNames['lockDevice'] in item.groupNames else active
    return active

def getItemValue(itemName, defVal):
    '''
    Returns the items value if the item is initialized otherwise return the default value.
    itemRegistry.getItem will return an object also for uninitialized items but it has less methods.
    '''
    item = itemRegistry.getItem(itemName)
    if type(defVal) is int:
        return item.state.intValue() if item.state not in [NULL, UNDEF] else defVal
    elif type(defVal) is float:
        return item.state.floatValue() if item.state not in [NULL, UNDEF] else defVal
    elif defVal in [ON, OFF, OPEN, CLOSED]:
        return item.state if item.state not in [NULL, UNDEF] else defVal
    elif type(defVal) is str:
        return item.state.toFullString() if item.state not in [NULL, UNDEF] else defVal
    elif type(defVal) is DateTime:
        # We return a to a org.joda.time.DateTime from a org.eclipse.smarthome.core.library.types.DateTimeType
        return DateTime(item.state.calendar.timeInMillis) if item.state not in [NULL, UNDEF] else defVal
    else:
        log.error('The type of the passed default value is not handled')
        return None

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

def postUpdateCheckFirst(itemName, newValue, sendACommand=False, floatPrecision=-1):
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
    item = itemRegistry.getItem(itemName)

    if item.state not in [NULL, UNDEF]:
        if type(newValue) is int:
            compareValue = itemRegistry.getItem(itemName).state.intValue()
        elif type(newValue) is float:
            '''
            Unfortunately, most decimal fractions cannot be represented exactly as binary fractions.
            A consequence is that, in general, the decimal floating-point numbers you enter are only
            approximated by the binary floating-point numbers actually stored in the machine.
            Therefore, comparing the stored value with the new value will most likely always result in a difference.
            You can supply the named argument floatPrecision to round the value before comparing
            '''
            if floatPrecision == -1:
                compareValue = itemRegistry.getItem(itemName).state.floatValue()
            else:
                compareValue = round(itemRegistry.getItem(itemName).state.floatValue(), floatPrecision)
        elif newValue in [ON, OFF, OPEN, CLOSED]:
            compareValue = itemRegistry.getItem(itemName).state
        elif type(newValue) is str:
            compareValue = itemRegistry.getItem(itemName).state.toString()
        else:
            log.error('Can not set '+str(itemName)+' to the unsupported type '+str(type(newValue))+'. Value: '+str(newValue))
    if (compareValue is not None and compareValue != newValue) or item.state in [NULL, UNDEF]:
        if sendACommand:
            log.debug('New sendCommand value for '+itemName+' is '+str(newValue))
            sendCommand(itemName, newValue)
        else:
            log.debug('New postUpdate value for '+itemName+' is '+str(newValue))
            postUpdate(itemName, newValue)
        return True
    else:
        return False

def sendCommandCheckFirst(itemName, newValue, floatPrecision=-1):
    ''' See postUpdateCheckFirst '''
    return postUpdateCheckFirst(itemName, newValue, sendACommand=True, floatPrecision=floatPrecision)

def hasReloadFinished(exitScript=False):
    '''
    Sometimes scripts are running before all Items have finished loading.
    To prevent that, place an item, only for this purpose last in your last items file.(alphabetic order).
    The item must be persisted on change.
    We will check if this item has a specific value. Define the name of the item in your lucid config file.
    Name it whatever you like but it's better if it starts with the last letter in the alphabet.
    Example Item:
    String ZZZ_Test_Reload_Finished (G_PersistOnChange)
    '''
    HELLO = 'Hello'
    try:
        if itemRegistry.getItem(config.customItemNames['reloadFinished']).state.toString == HELLO:
            return True
    except:
        if exitScript: return False
        timeToSleep = 0.5+random.uniform(0, 1)
        time.sleep(timeToSleep)
        log.info('WAITING '+str(timeToSleep)+' sec !!!')
        postUpdateCheckFirst(config.customItemNames['reloadFinished'], HELLO)
    return True
