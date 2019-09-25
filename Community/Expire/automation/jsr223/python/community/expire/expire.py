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
from org.openhab.core.library.items import StringItem

init_logger = logging.getLogger("{}.Expire Init".format(LOG_PREFIX))
regex = re.compile(r'^((?P<days>[\.\d]+?)d)? *((?P<hours>[\.\d]+?)h)? *((?P<minutes>[\.\d]+?)m)? *((?P<seconds>[\.\d]+?)s)?$')
timers = { }
special = { "UNDEF": UnDefType.UNDEF,
            "NULL":  UnDefType.NULL }

@log_traceback
def parse_time(time_str):
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
        datetime.timedelta: A datetime.timedelta object representing the
        supplied time duration.
    """
    parts = regex.match(time_str)
    assert parts is not None, ("Could not parse any time information from '{}'."
                               "  Examples of valid strings: '8h', '2d8h5m20s',"
                               " '2m4s'".format(time_str))
    time_params = {name: float(param) for name, param in parts.groupdict().items() if param}
    return timedelta(**time_params)

@log_traceback
def get_config(item_name):
    """
    Parses the config string to extract the time duration, type of event, and
    the necessary state. The config string is stored in an "exp" metadata entry.
    The config takes format of exp="<duration>[,][command=|state=][<new state>]"
        - <duration>: a time duration of the format described in parse_time.
        - [,]: if supplying more than just the duration, a comma is required
        here.
        - [command=|state=]: an optional definition of the type of of event to
        send to this Item when it expires. If not supplied it defaults to
        "state=".
        - [<new state>]: an optional state that the Item get's updated (state)
        or commanded (command) to when the time expires. Use '' to represent the
        empty String (differs from Expire1 Binding)

    Examples (taken from the Expire1 Binding docs):
        - expire="1h,command=STOP" (send the STOP command after one hour)
        - expire="5m,state=0"      (update state to 0 after five minutes)
        - expire="3m12s,Hello"     (update state to Hello after three minutes
                                    and 12 seconds)
        - expire="2h"              (update state to UNDEF 2 hours after the last
                                    value)

    Unique to this implementation:
        - expire="5s,state=''"     (update a String Item to the empty String)
    """
    cfg = get_value(item_name, "expire")
    time = cfg
    event = "state"
    state = UNDEF

    # If it contains a ',' there is a state supplied, split and assign the left
    # to time and right to state.
    if ',' in cfg:
        time = cfg.split(',')[0]
        state = cfg.split(',')[1]

        # If it contians a '=' there is an event type supplied, split and assign
        # the left to event and right to state.
        if '=' in state:
            event = state.split('=')[0]
            state = state.split('=')[1]

        # Check for special types.
        if state in special:
            state = special[state]

        # Check for and remove single quotes from state.
        elif state.startswith("'") and state.endswith("'"):
            state = state.replace("'", "")

    td = parse_time(time)

    return { "time":td, "type":event, "state":state }

# TODO listen for Item added/removed events and regenerate the Rule and its
# triggers.

@log_traceback
def trigger_generator():
    """
    Generates triggers for the Expire Rule for all Items that have the expire
    metadata value set.
    """
    def generate_triggers(function):
        for item_name in [i for i in items if get_value(i, "expire")]:
            try:
                get_config(item_name)
            except AssertionError:
                init_logger.log.error("Expire config on {} is not valied: {}"
                                      .format(item_name,
                                              get_value(item_name, "expire")))
            else:
                when("Item {} received update".format(item_name))(function)
        return function
    return generate_triggers

@log_traceback
def expired(item, exp_type, exp_state, log):
    """
    Called when an Item expires. postUpdate or sendCommand to the configured
    state.

    Arguments:
        - item: The Item that expired.
        - cfg: Contians a dict representation of the expire config returned by
        get_config.
        - log: Logger from the expire Rule.
    """
    log.debug("{} expired, {} to {}".format(item.name, exp_type, exp_state))

    # Force the state to a StringType for StringItems to allow us to set the
    # Item to "UNDEF" and "NULL" as opposed to the UnDefTypes.
    if item.type == "String" and isinstance(exp_state, basestring):
        exp_state = StringType(exp_state)

    if exp_type == "state":
        events.postUpdate(item, exp_state)
    else:
        events.sendCommand(item, exp_state)

@rule("Expire",
      description=("Simulates the Expire1 binding, updating or commanding an "
                   "Item after a comnfigured amount of time."),
       tags=["expire"])
@trigger_generator()
def expire(event):
    """
    Called when a member of the configured Group changes. The name of the Group
    is imported from configuration as expire_items_gr.

    If the Item updates to an UnDefType, the change is ignored.
    If the Item updates to the same state configured in the expire config any
    expire timer is cancelled.
    If the Item updates to a different state configured in the expire config a
    new timer is created to go off at the configured time in the future.
    """
    # Ignore changes to an UnDefType.
    if isinstance(event.itemState, UnDefType):
        return

    cfg = get_config(event.itemName)

    # Cancel the timer when the Item enters the cfg state.
    # Use unicode because there is no degree symbol in ASCII so we can handle
    # Number:Temperature Items.
    if unicode(items[event.itemName]) == cfg["state"]:
        if (event.itemName in timers
                and not timers[event.itemName].hasTerminated()):
            timers[event.itemName].cancel()
            del timers[event.itemName]

    # Create an expire timer when the Item differs from the end state.
    else:
        t = (DateTime.now().plusDays(cfg["time"].days)
                           .plusSeconds(cfg["time"].seconds)
                           .plusMillis(int(cfg["time"].microseconds/1000)))
        if event.itemName in timers:
            timers[event.itemName].reschedule(t)
        else:
            timers[event.itemName] = ScriptExecution.createTimer(t,
                                     lambda: expired(ir.getItem(event.itemName),
                                                     cfg["type"],
                                                     cfg["state"],
                                                     expire.log))

@log_traceback
def scriptUnloaded():
    """ Called at script unload, cancel all the latent timers. """
    for key in timers:
        timers[key].cancel()
