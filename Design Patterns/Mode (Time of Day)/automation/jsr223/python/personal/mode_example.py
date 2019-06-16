"""
PURPOSE
-------

This example rule will adjust a StringItem named 'Mode' based on the time of
day. If the 'Mode' Item is manually changed to something that is not included
the time_of_day OrderedDict in the ``configuration.py``, such as 'Party', the
Mode will not be updated automatically and will need to be manually changed
back to a 'Mode' included in the OD.

REQUIRES
--------

* a 'Mode' StringItem ``String Mode "Mode [%s]" <house>``
* the time_of_day OrderedDict added to ``configuration.py`` and populated with
times for your modes
"""

from core.rules import rule
from core.triggers import when
from org.joda.time import DateTime, Interval
from configuration import time_of_day

def mode_trigger_generator(time_of_day):
    def generated_triggers(function):
        for mode in list(time_of_day.keys()):
            when("Time cron {} {} {} * * ?".format(time_of_day[mode]['second'], time_of_day[mode]['minute'], time_of_day[mode]['hour']))(function)
        return function
    return generated_triggers

@rule("Cron: Update Mode")
@when("System started")
@mode_trigger_generator(time_of_day)
def update_mode(event):
    last_mode_of_day = time_of_day.items()[-1][0]
    new_mode = last_mode_of_day
    for i, (mode, value) in enumerate(time_of_day.iteritems()):
        if i < len(time_of_day) - 1:
            mode_interval = Interval(
                DateTime.now().withTime(
                    value['hour'],
                    value['minute'],
                    value['second'],
                    0),
                DateTime.now().withTime(
                    time_of_day.items()[i + 1][1]['hour'],
                    time_of_day.items()[i + 1][1]['minute'],
                    time_of_day.items()[i + 1][1]['second'],
                    0))
            if mode_interval.contains(DateTime.now()):
                new_mode = mode
                break
    if items["Mode"] != StringType(new_mode) and (str(items["Mode"]) in time_of_day.keys() + [last_mode_of_day] or isinstance(items["Mode"], UnDefType)):
        update_mode.log.debug("Mode changed from [{}] to [{}]".format(items["Mode"], new_mode))
        events.sendCommand("Mode", new_mode)
    else:
        update_mode.log.debug("Job ran but current Mode [{}] did not need to be changed: [{}]".format(items["Mode"], new_mode))
