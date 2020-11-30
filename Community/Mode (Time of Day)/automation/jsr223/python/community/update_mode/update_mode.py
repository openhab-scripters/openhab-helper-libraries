"""
Purpose
-------

This is an example script that can be modified to suit your implementation. It
will create a rule that will adjust a StringItem named ``Mode`` based on the
time of day. Your modes are configured in ``configuration.MODE_CONFIGURATION``. Each
``Mode`` can be configured with Times and/or Channels. If both are used, the
first one that occurs will trigger the ``Mode``.

If just a Time is used, the ``Mode`` will be set after saving the script or an
openHAB restart. If a Channel is used, you will need to wait for the next
trigger or manually update the ``Mode`` Item to the curent mode. If the
``Mode`` Item is manually changed to a state that is not a key found in the
``configuration.MODE_CONFIGURATION``, such as ``Party``, the ``Mode`` will not
be updated automatically and will need to be manually changed back to a mode in
the dict for the automation to take over again.


Requires
--------

* A ``Mode`` Item (the script will create it for you, if it does not exist)
* The ``MODE_CONFIGURATION`` OrderedDict added to ``configuration.py`` and populated
  with times for your modes
"""
from datetime import datetime

from org.joda.time import DateTime, Interval

from core.rules import rule
from core.triggers import when
from core.items import add_item
import configuration
reload(configuration)
from configuration import MODE_CONFIGURATION

try:
    from org.openhab.core.thing import ChannelUID
except:
    from org.eclipse.smarthome.core.thing import ChannelUID

if not itemRegistry.getItems("Mode"):
    add_item("Mode", item_type="String", label="Mode [%s]", category="House")


def mode_trigger_generator(mode_dict):
    def generated_triggers(function):
        for day_of_week in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            for mode in list(mode_dict[day_of_week].keys()):
                if mode_dict[day_of_week][mode].get("second") is not None and mode_dict[day_of_week][mode].get("minute") is not None and mode_dict[day_of_week][mode].get("hour") is not None:
                    when("Time cron {} {} {} ? * {}".format(mode_dict[day_of_week][mode]["second"], mode_dict[day_of_week][mode]["minute"], mode_dict[day_of_week][mode]["hour"], day_of_week[:3]))(function)
                if mode_dict[day_of_week][mode].get("channel") is not None and mode_dict[day_of_week][mode].get("event") is not None:
                    when("Channel {} triggered {}".format(mode_dict[day_of_week][mode]["channel"], mode_dict[day_of_week][mode]["event"]))(function)
        return function
    return generated_triggers


@rule("Update Mode")
@when("System started")
@mode_trigger_generator(MODE_CONFIGURATION)
def update_mode(event):
    day_of_week = datetime.today().strftime('%A')
    last_mode_of_day = MODE_CONFIGURATION[day_of_week].items()[-1][0]
    new_mode = last_mode_of_day
    for i, (mode, value) in enumerate(MODE_CONFIGURATION[day_of_week].iteritems()):
        if mode != last_mode_of_day:
            if event is None and MODE_CONFIGURATION[day_of_week][mode].get("hour") is not None and Interval(
                DateTime.now().withTime(
                    value["hour"],
                    value["minute"],
                    value["second"],
                    0
                ),
                DateTime.now().withTime(
                    MODE_CONFIGURATION[day_of_week].items()[i + 1][1].get("hour", value["hour"]),
                    MODE_CONFIGURATION[day_of_week].items()[i + 1][1].get("minute", value["minute"] + 1),
                    MODE_CONFIGURATION[day_of_week].items()[i + 1][1].get("second", value["second"]),
                    0
                )
            ).contains(DateTime.now()):
                new_mode = mode
                break
            elif hasattr(event, "channel") and MODE_CONFIGURATION[day_of_week][mode].get("channel") is not None and event.channel == ChannelUID(MODE_CONFIGURATION[day_of_week][mode].get("channel")) and event.event == MODE_CONFIGURATION[day_of_week][mode].get("event"):
                new_mode = mode
                break

    if items["Mode"] != StringType(new_mode) and (str(items["Mode"]) in MODE_CONFIGURATION[day_of_week].keys() or isinstance(items["Mode"], UnDefType)):
        update_mode.log.debug(u"Mode changed from '{}' to '{}'".format(items["Mode"], new_mode))
        events.sendCommand("Mode", new_mode)
    else:
        update_mode.log.debug(u"Job ran but current Mode '{}' did not need to be changed: '{}'".format(items["Mode"], new_mode))
