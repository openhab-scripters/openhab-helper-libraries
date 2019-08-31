"""
PURPOSE
-------

This script will create a rule that will adjust a StringItem named 'Mode'
based on the time of day. If the 'Mode' Item is manually changed to a state
that is not a key found in configuration.mode_dict, such as 'Party', the Mode
will not be updated automatically and will need to be manually changed back.
The Modes can be configured with Times and/or Channels. If both are used, the
first one that occurs will trigger the Mode. If a Time, the Mode will be set
after saving the file. If not, the Mode will need to be manuallly set the
first time, or just wait for the first trigger.

REQUIRES
--------

* a 'Mode' Item (the script will create it for you, if it does not exist)
* the mode_dict OrderedDict added to ``configuration.py`` and populated with
  times for your modes
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
            if mode_dict[mode].get("Second") is not None and mode_dict[mode].get("Minute") is not None and mode_dict[mode].get("Hour") is not None:
                when("Time cron {} {} {} * * ?".format(mode_dict[mode]["Second"], mode_dict[mode]["Minute"], mode_dict[mode]["Hour"]))(function)
            if mode_dict[mode].get("Channel") is not None and mode_dict[mode].get("Event") is not None:
                when("Channel {} triggered {}".format(mode_dict[mode]["Channel"], mode_dict[mode]["Event"]))(function)
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
            if not event and mode_dict[mode].get("Hour") is not None and Interval(
                    DateTime.now().withTime(
                        value["Hour"],
                        value["Minute"],
                        value["Second"],
                        0
                    ),
                    DateTime.now().withTime(
                        mode_dict.items()[i + 1][1]["Hour"],
                        mode_dict.items()[i + 1][1]["Minute"],
                        mode_dict.items()[i + 1][1]["Second"],
                        0
                    )
                ).contains(DateTime.now()):
                    new_mode = mode
                    break
            elif hasattr(event, "channel") and mode_dict[mode].get("Channel") is not None and event.channel == ChannelUID(mode_dict[mode].get("Channel")) and event.event == mode_dict[mode].get("Event"):
                new_mode = mode
                break

    if items["Mode"] != StringType(new_mode) and (str(items["Mode"]) in mode_dict.keys() + [last_mode_of_day] or isinstance(items["Mode"], UnDefType)):
        update_mode.log.debug("Mode changed from [{}] to [{}]".format(items["Mode"], new_mode))
        events.sendCommand("Mode", new_mode)
    else:
        update_mode.log.debug("Job ran but current Mode [{}] did not need to be changed: [{}]".format(items["Mode"], new_mode))
