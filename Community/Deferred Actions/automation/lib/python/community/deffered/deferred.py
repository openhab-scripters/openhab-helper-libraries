"""
Author: Rich Koshak

Utility methods to easily schedule a deferred command to be sent to an Item. The
time can either be an absolute time or it can be an amount of time.

License
=======
Copyright (c) contributors to the openHAB Scripters project
"""
import re
from datetime import timedelta
from core.actions import ScriptExecution
from core.jsr223.scope import events
from org.joda.time import DateTime

timers = {}

duration = re.compile(r'^((?P<days>[\.\d]+?)d)? *((?P<hours>[\.\d]+?)h)? *((?P<minutes>[\.\d]+?)m)? *((?P<seconds>[\.\d]+?)s)?$')

def parse_time(time_str):
    """
    Parse a time duration string e.g. (2h13m) into a timedelta object

    https://stackoverflow.com/questions/4628122/how-to-construct-a-timedelta-object-from-a-simple-string

    Arguments:
        - time_str: A string identifying a time duration.
            - d: days
            - h: hours
            - m: minutes
            - s: seconds
        All options are optional but at least one needs to be supplied. Float
        values are allowed (e.g. "1.5d" is the same as "1s12h"). Spaces between
        each field is allowd. Examples:
            - 1h 30m 45s
            - 1h50s
            - 0.5s

    Returns:
        datetime.timedelta: A datetime.timedelta object representing the
        supplied time duration

    Throws:
        AssertionError if the passed in string cannot be parsed
    """
    parts = duration.match(time_str)
    assert parts is not None, ("Could not parse any time information from `{}`."
                               " Examples of valid strings: '8h', '2d8h5m20s',"
                               " '2m4s'".format(time_str))
    time_params = {name: float(param) for name, param in parts.groupdict().items() if param}
    return timedelta(**time_params)

def timer_body(target, command, log):
    """
    Called when the differed action timer expires, sends the command to the
    target Item.

    Arguments:
        - target: Item name to send the command to
        - command: Command to issue to the target Item
        - log: logger passed in from the Rule that is using this.
    """
    log.info("Executing deferred action {} against {}".format(command, target))
    events.sendCommand(target, command)
    del timers[target]

def deferred(target, command, log, dt=None, delay=None):
    """
    Use this function to schedule a command to be sent to an Item at the
    specified time or after the speficied delay. If the passed in time or delay
    ends up in the past, the command is sent immediately.

    Arguments:
        - target: Item name to send the command to
        - command: the command to send the Item
        - log: logger passed in from the Rule
        - dt: a DateTime or ISO 8601 formatted String for when to send the
          command
        - delay: a time duration supporting days, hours, minutes, and seconds
          (e.g. 2d5h23m7.5s)

        One of dt or delay must be passed in or the function will throw an
        AssertionError.

    Throws:
        AssertionError if neither dt nor delay were supplied or delay was
        supplied but it is not in a parsable format.
    """
    trigger_time = None

    assert dt is not None or delay is not None, ("One of dt or delay is "
                                                "required, both are None!")

    # Cancel existing timer
    if target in timers and not timers[target].hasTerminated():
        log.info("There is already a timer set for {}, cancelling and "
                 "rescheduling.".format(target))
        timers[target].cancel()
        del timers[target]


    # Determine when to send the deferred command
    if dt:
        trigger_time = DateTime(dt)
    else:
        td = parse_time(delay)
        trigger_time = (DateTime.now().plusDays(td.days)
                                 .plusSeconds(td.seconds)
                                 .plusMillis(int(td.microseconds/1000)))

    # If trigger_time is in the past, schedule for now
    if trigger_time.isBefore(DateTime.now()):
        trigger_time = DateTime.now()

    # Schedule the timer
    timers[target] = ScriptExecution.createTimer(trigger_time,
                                       lambda: timer_body(target, command, log))

def cancel(target):
    """
    Cancels the timer associated with target if it exists.

    Arguments:
        - target: the Item name whose timer is to be cancelled
    """
    if target in timers and not timers[target].hasTerminated():
        timers[target].cancel()
    del timers[target]

def cancel_all():
    """
    Cancels all timers.
    """
    for key in timers:
        timers[key].cancel()
        del timers[key]
