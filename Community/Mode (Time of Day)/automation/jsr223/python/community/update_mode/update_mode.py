"""
Purpose
-------

This is an example script that can be modified to suit your implementation. It
will create a rule that will adjust a StringItem named ``Mode`` based on the
time of day. Your modes are configured in ``configuration.mode_dict``. Each
``Mode`` can be configured with Times and/or Channels. If both are used, the
first one that occurs will trigger the ``Mode``. If just a Time is used, the
``Mode`` will be set after saving the script or an openHAB restart. If a
Channel is used, you will need to wait for the next trigger or manually update
the``Mode``. If the ``Mode`` Item is manually changed to a state that is not a
key found in the ``configuration.mode_dict``, such as ``Party``, the
``Mode`` will not be updated automatically and will need to be manually changed
back to a mode in the dict for the automation to take pver again.


Requires
--------

* A ``Mode`` Item (the script will create it for you, if it does not exist)
* The ``mode_dict`` OrderedDict added to ``configuration.py`` and populated
  with times for your modes
"""
from core.rules import rule
from core.triggers import when
import configuration
reload(configuration)
from configuration import mode_dict
from core.items import add_item

try:
    from org.openhab.core.thing import ChannelUID
except:
    from org.eclipse.smarthome.core.thing import ChannelUID

from org.joda.time import DateTime, Interval

if not itemRegistry.getItems("Mode"):
    add_item("Mode", item_type="String", label="Mode [%s]", category="House")

def mode_trigger_generator(mode_dict):
    def generated_triggers(function):
        for mode in list(mode_dict.keys()):
            if mode_dict[mode].get("second") is not None and mode_dict[mode].get("minute") is not None and mode_dict[mode].get("hour") is not None:
                when("Time cron {} {} {} * * ?".format(mode_dict[mode]["second"], mode_dict[mode]["minute"], mode_dict[mode]["hour"]))(function)
            if mode_dict[mode].get("channel") is not None and mode_dict[mode].get("event") is not None:
                when("Channel {} triggered {}".format(mode_dict[mode]["channel"], mode_dict[mode]["event"]))(function)
        return function
    return generated_triggers

@rule("Update Mode")
@when("System started")
@mode_trigger_generator(mode_dict)
def update_mode(event):
    last_mode_of_day = mode_dict.items()[-1][0]
    new_mode = last_mode_of_day
    for i, (mode, value) in enumerate(mode_dict.iteritems()):
        if mode != last_mode_of_day:
            if not event and mode_dict[mode].get("hour") is not None and Interval(
                    DateTime.now().withTime(
                        value["hour"],
                        value["minute"],
                        value["second"],
                        0
                    ),
                    DateTime.now().withTime(
                        mode_dict.items()[i + 1][1]["hour"],
                        mode_dict.items()[i + 1][1]["minute"],
                        mode_dict.items()[i + 1][1]["second"],
                        0
                    )
                ).contains(DateTime.now()):
                    new_mode = mode
                    break
            elif hasattr(event, "channel") and mode_dict[mode].get("channel") is not None and event.channel == ChannelUID(mode_dict[mode].get("channel")) and event.event == mode_dict[mode].get("event"):
                new_mode = mode
                break

    if items["Mode"] != StringType(new_mode) and (str(items["Mode"]) in mode_dict.keys() or isinstance(items["Mode"], UnDefType)):
        update_mode.log.debug("Mode changed from [{}] to [{}]".format(items["Mode"], new_mode))
        events.sendCommand("Mode", new_mode)
    else:
        update_mode.log.debug("Job ran but current Mode [{}] did not need to be changed: [{}]".format(items["Mode"], new_mode))
