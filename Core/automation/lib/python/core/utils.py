"""
Utilities
"""

import random
import time
import re
import uuid

try:
    from org.eclipse.smarthome.core.types import TypeParser
except:
    from org.openhab.core.types import TypeParser

try:
    from org.openhab.core.thing import ChannelUID
except:
    from org.eclipse.smarthome.core.thing import ChannelUID

from core.log import logging, LOG_PREFIX
from core.jsr223 import scope
from core.actions import PersistenceExtensions

from org.joda.time import DateTime
from org.joda.time.format import DateTimeFormat

log = logging.getLogger('{}.core.utils'.format(LOG_PREFIX))

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
    Returns the Item's value if the Item exists and is initialized, otherwise returns the default value.
    itemRegistry.getItem will return an object also for uninitialized items but it has less methods.
    itemRegistry.getItem will throw an exception if the Item is not in the registry.
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

def getLastUpdate(itemName):
    '''
    Returns the Item's last update datetime as a 'org.joda.time.DateTime',
    http://joda-time.sourceforge.net/apidocs/org/joda/time/DateTime.html
    '''
    try:
        item = scope.itemRegistry.getItem(itemName) if isinstance(itemName, basestring) else itemName
        lastUpdate = PersistenceExtensions.lastUpdate(item)
        if lastUpdate is None:
            log.warning("No existing lastUpdate data for item: [{}], so returning 1970-01-01T00:00:00Z".format(item.name))
            return DateTime(0)
        return lastUpdate.toDateTime()
    except:
        # There is an issue using the StartupTrigger and saving scripts over SMB, where changes are detected before the file
        # is completely written. The first read breaks because of a partial file write and the second read succeeds.
        log.warning("Exception when getting lastUpdate data for item: [{}], so returning 1970-01-01T00:00:00Z".format(item.name))
        return DateTime(0)

def sendCommand(itemName, newValue):
    '''
    Sends a command to an item regerdless of it's current state
    The item can be passed as an OH item type or by using the item's name (string)
    '''
    item = scope.itemRegistry.getItem(itemName) if isinstance(itemName, basestring) else itemName
    scope.events.sendCommand(item, newValue)

def postUpdate(itemName, newValue):
    '''
    Posts an update to an item regerdless of it's current state
    The item can be passed as an OH item type or by using the item's name (string)
    '''
    item = scope.itemRegistry.getItem(itemName) if isinstance(itemName, basestring) else itemName
    scope.events.postUpdate(item, newValue)

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

    Unfortunately, most decimal fractions cannot be represented exactly as binary fractions.
    A consequence is that, in general, the decimal floating-point numbers you enter are only
    approximated by the binary floating-point numbers actually stored in the machine.
    Therefore, comparing the stored value with the new value will most likely always result in a difference.
    You can supply the named argument floatPrecision to round the value before comparing.
    '''
    compareValue = None
    item = scope.itemRegistry.getItem(itemName) if isinstance(itemName, basestring) else itemName

    if sendACommand:
        compareValue = TypeParser.parseCommand(item.acceptedCommandTypes, str(newValue))
    else:
        compareValue = TypeParser.parseState(item.acceptedDataTypes, str(newValue))

    if compareValue is not None:
        if item.state != compareValue or (type(newValue) is float and floatPrecision is not None and round(item.state.floatValue(), floatPrecision) != newValue):
            if sendACommand:
                sendCommand(item, newValue)
                log.debug("New sendCommand value for [{}] is [{}]".format(item.name, newValue))
            else:
                postUpdate(item, newValue)
                log.debug("New postUpdate value for [{}] is [{}]".format(item.name, newValue))
            return True
        else:
            return False
    else:
        log.warn("[{}] is not an accepted {} for [{}]".format(newValue, "command type" if sendACommand else "state", item.name))
        return False

def sendCommandCheckFirst(itemName, newValue, floatPrecision=None):
    ''' See postUpdateCheckFirst '''
    return postUpdateCheckFirst(itemName, newValue, sendACommand=True, floatPrecision=floatPrecision)

def validate_item(item_or_item_name):# returns Item or None
    item = item_or_item_name
    if isinstance(item, basestring):
        if scope.itemRegistry.getItems(item) == []:
            log.warn("[{}] is not in the ItemRegistry".format(item))
            return None
        else:
            item = scope.itemRegistry.getItem(item_or_item_name)
    elif not hasattr(item_or_item_name, 'name'):
        log.warn("[{}] is not a string or Item".format(item))
        return None

    if scope.itemRegistry.getItems(item.name) == []:
        log.warn("[{}] is not in the ItemRegistry".format(item.name))
        return None

    return item

def validate_channel_uid(channel_uid_or_string):# returns ChannelUID or None
    channel_uid = channel_uid_or_string
    if isinstance(channel_uid_or_string, basestring):
        channel_uid = ChannelUID(channel_uid_or_string)
    elif not isinstance(channel_uid_or_string, ChannelUID):
        log.warn("[{}] is not a string or ChannelUID".format(channel_uid_or_string))
        return None
    if scope.things.getChannel(channel_uid) is None:
        log.warn("[{}] is not a valid Channel".format(channel_uid))
        return None
    return channel_uid

def validate_uid(uid):# returns a valid UID
    #_valid_chars_re = "^[a-zA-Z][a-zA-Z0-9_]*$"
    valid_characters = re.compile("[^A-Za-z0-9_-]")
    uid = valid_characters.sub("_", uid)
    uid = re.sub(r"__+", "_", uid)
    if not re.match("^[a-zA-Z]", uid):
        uid = "{}_{}".format(uid, uuid.uuid1().hex)
    return uid
