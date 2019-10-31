"""
Author: Rich Koshak

Implements a near drop in replacement for the Expire1 binding using Rules.

Requirements:
    - Uninstall the Expire1 binding before use

Limitations:
    - The expire config metadata string must include the default units when
      using with Items that are defined with Units of Measure.

    - Adding new Items or changing Items with an expire metadata config requires
      a reload of this script to regenerate the rule triggers.

Differences from the binding:
    - You can expire a String Item to an empty string: expire="5s,state=''"

    - In the binding, expire="5s,state=UNDEF" will set a StringItem to the
      String "UNDEF". This script will set the String Item to UnDefType.UNDEF.
      To set a String Item to the String "UNDEF", use expire="5s,state='UNDEF'"

License
=======
Copyright (c) contributors to the openHAB Scripters project
"""
from core.rules import rule
from core.triggers import when
from core.metadata import get_value
import re
from datetime import timedelta
from core.actions import ScriptExecution
from org.joda.time import DateTime
from core.log import logging, LOG_PREFIX, log_traceback

regex = re.compile(r'^((?P<days>[\.\d]+?)d)? *((?P<hours>[\.\d]+?)h)? *((?P<minutes>[\.\d]+?)m)? *((?P<seconds>[\.\d]+?)s)?$')
timers = { }
special = { "UNDEF": UnDefType.UNDEF,
            "NULL":  UnDefType.NULL }



def parse_time(time_str, log):
    """
    Parse a time string e.g. (2h13m) into a timedelta object

    https://stackoverflow.com/questions/4628122/how-to-construct-a-timedelta-object-from-a-simple-string

    Arguments:
        - time_str: A string identifying a duration. Use
            - d: days
            - h: hours
            - m: minutes
            - s: seconds
          All options are optional but at least one needs to be supplied. Float
          values are allowed (e.g. "1.5d" is the same as "1d12h"). Spaces
          between each field is allowed. Examples:
              - 1h 30m 45s
              - 1h05s
              - 55h 59m 12s
    Returns:
        A ``datetime.timedelta`` object representing the supplied time duration
        or ``None`` if ``time_str`` cannot be parsed.
    """
    parts = regex.match(time_str)
    if parts is None:
        log.warn("Could not parse any time information from '{}'. Examples "
                  "of valid strings: '8h', '2d8h5m20s', '2m 4s'"
                   .format(time_str))
        return None
    else:
        time_params = {name: float(param) for name, param in parts.groupdict().items() if param}
        return timedelta(**time_params)


def get_config(item_name, log):
    """
    Parses the config string to extract the time duration, type of event, and
    the necessary state. The config string is stored in an "expire" metadata
    entry.The config takes format of
    ``expire="<duration>[,][command=|state=][<new state>]"``
        - <duration>: a time duration of the format described in parse_time.
        - [,]: if supplying more than just the duration, a comma is required
        here.
        - [command=|state=]: an optional definition of the type of of event to
        send to this Item when it expires. If not supplied it defaults to
        "state=".
        - [<new state>]: an optional state that the Item get's updated (state)
        or commanded (command) to when the time expires. Use '' to represent the
        empty String (differs from Expire1 Binding). Use 'UNDEF' or 'NULL' to
        represent the String rather than the state.

    Examples (taken from the Expire1 Binding docs):
        - expire="1h,command=STOP" (send the STOP command after one hour)
        - expire="5m,state=0"      (update state to 0 after five minutes)
        - expire="3m12s,Hello"     (update state to Hello after three minutes
                                    and 12 seconds)
        - expire="2h"              (update state to UNDEF 2 hours after the last
                                    value)

    Unique to this implementation:
        - expire="5s,state=''"      (update a String Item to the empty String)
        - expire="5s,state=UNDEF"   (for String Items, expires to UNDEF, not the
                                     string, "UNDEF")
        - expire="5s,state='UNDEF'" (for String Items, expires to the String
                                     "UNDEF")
    """
    cfg = get_value(item_name, "expire")
    if cfg:
        cfg = cfg.split(",")
    else:
        return None

    time = parse_time(cfg[0], log)
    if not time:
        return None
    event = "state"

    # If config has a state len will be 2
    if len(cfg) > 1:
        state = cfg[1].split("=")

        # If config has an event type it will be 2
        if len(state) > 1:
            event = state[0].strip().lower()
            state = state[1]
        else:
            state = state[0]

        # Check for special types.
        if state in special:
            state = special[state]

        # Remove single quotes from state.
        else:
            state = state.strip("'")

        state = state if state.strip() != "" else UNDEF

        # Force the state to a StringType for StringItems to allow us to set the
        # Item to "UNDEF" and "NULL" as opposed to the UnDefTypes.
        if ir.getItem(item_name).type == "String":
            if isinstance(state, basestring):
                state = StringType(state)
        # Strip whitespace for non String items
        elif isinstance(state, basestring):
            state = state.strip()

    # No state supplied, clear item state
    else:
        state = UNDEF

    if event not in ["state", "command"]:
        log.warn("Unrecognized action '{}' for item '{}'"
                 .format(event, item_name))
        return None

    return { "time": time, "type": event, "state": state }


def expired(item, exp_type, exp_state, log):
    """
    Called when an Item expires, postUpdate or sendCommand to the configured
    state.

    Arguments:
        - item: The Item that expired.
        - exp_type: The action type, 'state' or 'command'.
        - exp_state: The state to expire to.
        - log: Logger from the expire rule.
    """
    log.debug("'{}' expired, {} '{}'".format(item.name, exp_type, exp_state))

    if exp_type == "state":
        events.postUpdate(item, exp_state)
    elif exp_type == "command":
        events.sendCommand(item, exp_state)
    else:
        log.warn("Unrecognized action '{}' for item '{}'"
                 .format(exp_type, item.name))


def expire(event):
    """
    Called when an item configured for expire receives an update.

    If the Item updates to an UnDefType, the change is ignored.
    If the Item updates to the same state configured in the expire config any
    expire timer is cancelled.
    If the Item updates to a different state configured in the expire config a
    new timer is created to go off at the configured time in the future.
    """
    item_name = event.itemName

    # Ignore changes to an UnDefType.
    if isinstance(event.itemState, UnDefType):
        if (timers[item_name] is not None
                and not timers[item_name].hasTerminated()):
            timers[item_name].cancel()
        return

    cfg = get_config(item_name, expire.log)
    if not cfg:
        expire.log.warn("Skipping expire processing for '{}'"
                        .format(item_name))
        if (timers[item_name] is not None
                and not timers[item_name].hasTerminated()):
            timers[item_name].cancel()
        return

    # Cancel the timer when the Item enters the cfg state.
    # Use unicode because there is no degree symbol in ASCII so we can handle
    # Number:Temperature Items.
    if unicode(items[item_name]) == cfg["state"]:
        if (timers[item_name] is not None
                and not timers[item_name].hasTerminated()):
            timers[item_name].cancel()
        return

    # Create an expire timer when the Item differs from the end state.
    expire.log.debug("Setting timer for '{}' with delay {}"
                     .format(item_name, cfg["time"]))
    t = (DateTime.now().plusDays(cfg["time"].days)
                        .plusSeconds(cfg["time"].seconds)
                        .plusMillis(int(cfg["time"].microseconds/1000)))
    if (timers[item_name] is not None
            and not timers[item_name].hasTerminated()):
        timers[item_name].reschedule(t)
    else:
        timers[item_name] = ScriptExecution.createTimer(
            t,
            lambda: expired(ir.getItem(item_name),
                            cfg["type"],
                            cfg["state"],
                            expire.log)
        )


def expire_load(event):

    log = logging.getLogger("{}.Expire Load".format(LOG_PREFIX))
    log.debug("Expire loading...")

    # Keep track of items configured this pass
    new_items = []

    # Scan for items with valid expire config
    for item_name in items:
        cfg = get_config(item_name, log)
        if cfg:
            new_items.append(item_name)
            timers[item_name] = timers.get(item_name, None) # don't clobber
            log.debug("Expire configured for '{}' with timeout {} to {} '{}'"
                      .format(item_name, cfg["time"],
                      cfg["type"], cfg["state"]))

    # Remove existing rule
    if hasattr(expire, "UID"):
        rules.remove(expire.UID)
        delattr(expire, "triggers")
        delattr(expire, "UID")

    # Generate triggers
    for item_name in new_items:
        when("Item {} received update".format(item_name))(expire)

    # Create expire rule
    if hasattr(expire, "triggers"):
        rule(
            "Expire",
            description=("Simulates the Expire1 binding, updating or commanding an "
                         "Item after a configured amount of time."),
            tags=["expire"]
        )(expire)
        if hasattr(expire, "UID"):
            log.info("Expire loaded successfully")
        else:
            log.error("Failed to create Expire rule")
    else:
        log.info("Expire found no configured items")

    # Drop items that no longer exist or have expire config
    for item_name in timers:
        if item_name not in new_items:
            if item_name in items:
                log.debug("Removing item '{}' as it no longer has a valid expire config"
                          .format(item_name))
            else:
                log.debug("Removing item '{}' as it no longer exists"
                          .format(item_name))
            if (timers[item_name] is not None
                    and not timers[item_name].hasTerminated()):
                timers[item_name].cancel()
            timers.pop(item_name, None)


@log_traceback
def scriptLoaded(*args):
    """
    Called at script load, sets up the reload rule.
    """
    log = logging.getLogger("{}.Expire Init".format(LOG_PREFIX))

    import configuration
    if hasattr(configuration, "expire_reload_item"):
        item_name = configuration.expire_reload_item
    else:
        item_name = "expire_reload"
        log.debug("No value for 'expire_reload_item' in configuration.py, "
                  "using default item 'expire_reload'")

    if item_name in items:
        when("Item {} received command ON".format(item_name))(expire_load)
        rule(
            "Expire Reload",
            description=("Reloads the Expire script, adding items that did not "
                            "have a valid expire config and removing items that have "
                            "been deleted or no longer have a valid expire config"),
            tags=["expire"]
        )(expire_load)
        if hasattr(expire_load, "UID"):
            log.info("Expire Reload rule created successfully")
        else:
            log.error("Failed to create Expire Reload rule")
    else:
        if hasattr(configuration, "expire_reload_item"):
            log.warn("Unable to create Expire Reload rule, item '{}' does not exist"
                     .format(item_name))
        else:
            log.debug("Unable to create Expire Reload rule, item '{}' does not exist"
                      .format(item_name))

    expire_load(None)


@log_traceback
def scriptUnloaded(*args):
    """
    Called at script unload, cancel all running timers.
    """
    for item_name in timers:
        if (timers[item_name] is not None
                and not timers[item_name].hasTerminated()):
            timers[item_name].cancel()
