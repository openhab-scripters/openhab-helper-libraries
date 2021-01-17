# pylint: disable=invalid-name
"""
This module provides miscellaneous utility functions that are used across the core packages and modules.
"""
__all__ = [
    "validate_channel_uid",
    "validate_uid",
    "kw",
    "iround",
    "getItemValue",
    "getLastUpdate",
    "sendCommand",
    "postUpdate",
    "post_update_if_different",
    "postUpdateCheckFirst",
    "send_command_if_different",
    "sendCommandCheckFirst"
]

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

try:
    from org.joda.time import DateTime as JodaDateTime
except:
    JodaDateTime = None

from java.time import ZonedDateTime

from core.date import to_java_zoneddatetime, to_joda_datetime
from core.log import getLogger
from core.jsr223.scope import itemRegistry, StringType, NULL, UNDEF, ON, OFF, OPEN, CLOSED, events, things


LOG = getLogger(u"core.utils")


def validate_item(item_or_item_name):
    """
    This function validates whether an Item exists or if an Item name is valid.

    Args:
        item_or_item_name (Item or str): name of the Item

    Returns:
        Item or None: None, if the Item does not exist or the Item name is not
        in a valid format, else validated Item
    """
    item = item_or_item_name
    if isinstance(item, (basestring, unicode, StringType)):
        if itemRegistry.getItems(str(item)) == []:
            LOG.warn(u"'{}' is not in the ItemRegistry".format(str(item)))
            return None
        else:
            item = itemRegistry.getItem(str(item))
    elif not hasattr(item, 'name'):
        LOG.warn(u"'{}' is not a Item or string".format(str(item)))
        return None

    if itemRegistry.getItems(item.name) == []:
        LOG.warn(u"'{}' is not in the ItemRegistry".format(item.name))
        return None

    return item


def validate_channel_uid(channel_uid_or_string):
    """
    This function validates whether a ChannelUID exists or if a ChannelUID is
        valid.

    Args:
        channel_uid_or_string (ChannelUID or str): the ChannelUID

    Returns:
        ChannelUID or None: None, if the ChannelUID does not exist or the
        ChannelUID is not in a valid format, else validated ChannelUID
    """
    channel_uid = channel_uid_or_string
    if isinstance(channel_uid_or_string, basestring):
        channel_uid = ChannelUID(channel_uid_or_string)
    elif not isinstance(channel_uid_or_string, ChannelUID):
        LOG.warn(u"'{}' is not a string or ChannelUID".format(channel_uid_or_string))
        return None
    if things.getChannel(channel_uid) is None:
        LOG.warn(u"'{}' is not a valid Channel".format(channel_uid))
        return None
    return channel_uid


def validate_uid(uid):
    """
    This function validates UIDs.

    Args:
        uid (str or None): the UID to validate or None

    Returns:
        str: a valid UID
    """
    if uid is None:
        uid = uuid.uuid1().hex
    else:
        uid = re.sub(r"[^A-Za-z0-9_-]", "_", uid)
        uid = "{}_{}".format(uid, uuid.uuid1().hex)
    if not re.match("^[A-Za-z0-9]", uid):# in case the first character is still invalid
        uid = "{}_{}".format("jython", uid)
    uid = re.sub(r"__+", "_", uid)
    return uid


def post_update_if_different(item_or_item_name, new_value, sendACommand=False, floatPrecision=None):
    """
    Checks if the current state of the item is different than the desired new
    state. If the target state is the same, no update is posted.

    sendCommand vs postUpdate:
    If you want to tell something to change (turn a light on, change the
    thermostat to a new temperature, start raising the blinds, etc.), then you
    want to send a command to an Item using sendCommand. If your Items' states
    are not being updated by a binding, the autoupdate feature or something
    else external, you will probably want to update the state in a rule using
    ``events.postUpdate``.

    Unfortunately, most decimal fractions cannot be represented exactly as
    binary fractions. A consequence is that, in general, the decimal
    floating-point numbers you enter are only approximated by the binary
    floating-point numbers actually stored in the machine. Therefore,
    comparing the stored value with the new value will most likely always
    result in a difference. You can supply the named argument floatPrecision
    to round the value before comparing.

    Args:
        item_or_item_name (Item or str): name of the Item
        new_value (State or Command): state to update the Item with, or Command
            if using sendACommand (must be of a type supported by the Item)
        sendACommand (Boolean): (optional) ``True`` to send a command instead
            of an update
        floatPrecision (int): (optional) the precision of the Item's state to
            use when comparing values

    Returns:
        bool: ``True``, if the command or update was sent, else ``False``
    """
    compare_value = None
    item = itemRegistry.getItem(item_or_item_name) if isinstance(item_or_item_name, basestring) else item_or_item_name

    if sendACommand:
        compare_value = TypeParser.parseCommand(item.acceptedCommandTypes, str(new_value))
    else:
        compare_value = TypeParser.parseState(item.acceptedDataTypes, str(new_value))

    if compare_value is not None:
        if item.state != compare_value or (isinstance(new_value, float) and floatPrecision is not None and round(item.state.floatValue(), floatPrecision) != new_value):
            if sendACommand:
                events.sendCommand(item, new_value)
                LOG.debug(u"New sendCommand value for '{}' is '{}'".format(item.name, new_value))
            else:
                events.postUpdate(item, new_value)
                LOG.debug(u"New postUpdate value for '{}' is '{}'".format(item.name, new_value))
            return True
        else:
            LOG.debug(u"Not {} {} to '{}' since it is the same as the current state".format("sending command" if sendACommand else "posting update", new_value, item.name))
            return False
    else:
        LOG.warn(u"'{}' is not an accepted {} for '{}'".format(new_value, "command type" if sendACommand else "state", item.name))
        return False


def send_command_if_different(item_or_item_name, new_value, floatPrecision=None):
    """
    See postUpdateCheckFirst
    """
    return postUpdateCheckFirst(item_or_item_name, new_value, sendACommand=True, floatPrecision=floatPrecision)


# for backwards compatibility
postUpdateCheckFirst = post_update_if_different


# for backwards compatibility
sendCommandCheckFirst = send_command_if_different


def kw(dictionary, value):
    """
    In a given dictionary, get the first key that has a value matching the one provided.

    Args:
        dict (dict): the dictionary to search
        value (str): the value to match to a key

    Returns:
        str or None: string representing the first key with a matching vlaue, or
            None if the value is not found
    """
    LOG.warn("The 'core.utils.kw' function is pending deprecation.")
    for k, v in dictionary.iteritems():
        if v == value:
            return k
    return None


def iround(float_value):
    """
    Round a float to the nearest integer.

    Args:
        x (float): the float to round

    Returns:
        integer: integer value of float
    """
    LOG.warn("The 'core.utils.iround' function is pending deprecation.")
    rounded = round(float_value) - 0.5
    return int(rounded) + (rounded > 0)


def getItemValue(item_or_item_name, default_value):
    """
    Returns the Item's value if the Item exists and is initialized, otherwise
    returns the default value. ``itemRegistry.getItem`` will return an object
    for uninitialized items, but it has less methods. ``itemRegistry.getItem``
    will throw an ItemNotFoundException if the Item is not in the registry.

    Args:
        item_or_item_name (Item or str): name of the Item
        default_value (int, float, ON, OFF, OPEN, CLOSED, str, DateTime): the default
            value

    Returns:
        int, float, ON, OFF, OPEN, CLOSED, str, DateTime, or None: the state if
            the Item converted to the type of default value, or the default
            value if the Item's state is NULL or UNDEF
    """
    LOG.warn("The 'core.utils.getItemValue' function is pending deprecation.")
    item = itemRegistry.getItem(item_or_item_name) if isinstance(item_or_item_name, basestring) else item_or_item_name
    if isinstance(default_value, int):
        return item.state.intValue() if item.state not in [NULL, UNDEF] else default_value
    elif isinstance(default_value, float):
        return item.state.floatValue() if item.state not in [NULL, UNDEF] else default_value
    elif default_value in [ON, OFF, OPEN, CLOSED]:
        return item.state if item.state not in [NULL, UNDEF] else default_value
    elif isinstance(default_value, str):
        return item.state.toFullString() if item.state not in [NULL, UNDEF] else default_value
    elif JodaDateTime and isinstance(default_value, JodaDateTime):
        # We return a org.joda.time.DateTime from a org.eclipse.smarthome.core.library.types.DateTimeType
        return to_joda_datetime(item.state) if item.state not in [NULL, UNDEF] else default_value
    elif isinstance(default_value, ZonedDateTime):
        # We return a java.time.ZonedDateTime
        return to_java_zoneddatetime(item.state) if item.state not in [NULL, UNDEF] else default_value
    else:
        LOG.warn("The type of the passed default value is not handled")
        return None


def getLastUpdate(item_or_item_name):
    """
    Returns the Item's last update datetime as an ``org.joda.time.DateTime``.
    If Joda is missing it will return a ``java.time.ZonedDateTime`` instead.

    Args:
        item_or_item_name (Item or str): name of the Item

    Returns:
        DateTime: Joda DateTime representing the time of the Item's last update
        ZonedDateTime: ZonedDateTime representing the time of the Item's last update
    """
    LOG.warn("The 'core.utils.getLastUpdate' function is pending deprecation.")
    try:
        from core.actions import PersistenceExtensions
        item = itemRegistry.getItem(item_or_item_name) if isinstance(item_or_item_name, basestring) else item_or_item_name
        last_update = PersistenceExtensions.lastUpdate(item)
        if last_update is not None:
            return to_joda_datetime(last_update) if JodaDateTime else to_java_zoneddatetime(last_update)
        LOG.warning(u"No existing lastUpdate data for item: '{}', so returning 1970-01-01T00:00:00Z".format(item.name))
    except:
        # There is an issue using the StartupTrigger and saving scripts over SMB, where changes are detected before the file
        # is completely written. The first read breaks because of a partial file write and the second read succeeds.
        LOG.warning(u"Exception when getting lastUpdate data for item: '{}', so returning 1970-01-01T00:00:00Z".format(item.name))
    return JodaDateTime(0) if JodaDateTime else ZonedDateTime(0)


def sendCommand(item_or_item_name, new_value):
    """
    Sends a command to an item regardless of its current state.

    Args:
        item_or_item_name (Item or str): name of the Item
        new_value (Command): Command to send to the Item
    """
    LOG.warn("The 'core.utils.sendCommand' function is pending deprecation.")
    item = itemRegistry.getItem(item_or_item_name) if isinstance(item_or_item_name, basestring) else item_or_item_name
    events.sendCommand(item, new_value)


def postUpdate(item_or_item_name, new_value):
    """
    Posts an update to an item regardless of its current state.

    Args:
        item_name (Item or str): Item or name of the Item
        new_value (State): State to update the Item with
    """
    LOG.warn("The 'core.utils.postUpdate' function is pending deprecation.")
    item = itemRegistry.getItem(item_or_item_name) if isinstance(item_or_item_name, basestring) else item_or_item_name
    events.postUpdate(item, new_value)
