"""
:Author: 'Rich Koshak <https://github.com/rkoshak>

Purpose
=======
This rule will perform presence detection with away flapping (i.e. you must be
away for a configured amount of time before being marked as away). It does this
through the use of sensor Items or Groups and proxy Items.

If there is only one sensor Item for a given person, add that Item to the
presence_sensors List (see below). If there is more than one, use a Group to
aggregate the multiple sensors into one Switch.

For each person, there is a proxy Item which represents the actual presence of
that person (or people). This Item is immediately set to ON when a sensor Item
(or Group) changes to ON. But it doesn't change to OFF until the configured
amount of time so if the person returns in that amount of time, the Item remains
ON.

Requires
========
The Rule requires three variables to be created in configuration.py
.. code-block::
    # List of all the sensors, proxies, and timeouts to apply the generic presence
    # rule to.
    # sensor:  A single Switch Item or a Group:Switch that represents the presence
    #          status of the sensors that detect a given person or general
    #          presence.
    #
    # proxy:   The proxy Switch Item that represents the determined presence status
    #          of that person or generally.
    #
    # timeout: The number of minutes to wait after a sensor changes to OFF before
    #          changing the proxy Item to OFF. Changes to ON immediately apply.
                      # Sensor           proxy              Timeout
    presence_config = { "gPresent":     ("vPresent",        2),
                        "gRichPresent": ("vRichPresent",    3),
                        "gJennPresent": ("vJennPresent",    2) }

Examples
========
.. code-block::
    # Example Items:
    // All people
    Group:Switch:OR(ON,OFF) gPresent
    Switch vPresent
    Switch aPresenceOverride (gPresent)
    // Rich
    Group:Switch:OR(ON,OFF) gRichPresent (gPresent)
    Switch vRichPhone (gRichPresent)
    Switch vRichPhone_Manticore_Net (gRichPresent)
    // Jenn
    Group:Switch:OR(ON,OFF) gJennPresent (gPresent)
    Switch vJennPhone (gJennPresent)
    Switch vJennPhone_Manticore_Net (gJennPresent)

Notice how the there are two sensors for each person which aggregate to a
Group. The two person Groups are made members of gPresent. There is an override
Switch to manually set present to ON.
"""
from core.rules import rule
from core.triggers import when
from configuration import presence_config
from core.actions import ScriptExecution
from org.joda.time import DateTime

presence_timers = {}

def trigger_generator(presence_config):
    """
    Called to generate triggers for all of the defined presence sensors imported
    from configuration.

    Arguments:
        - presence_config: A dict whose keys are the names of the sensor Items
        that are managed by this Rule.
    """
    def generated_triggers(function):
        for sensor in list(presence_config):
            when("Item {} changed".format(sensor))(function)
        return function
    return generated_triggers

def away(log, events, proxy_name, flap_time):
    """
    Called when a person has been detected away for more than the flapping time.
    Log out the away state and command the Item to OFF.

    Arguments:
        - log: Logger passed in from the presence Rule.
        - events: Access to the events Object so we can call sendCommand.
        - proxy_name: Name of the proxy Item that we want to set to away.
        - flap_time: Number of minutes we wait before marking the person away.
    """
    log.info("{} has been away for {} minutes, setting to away."
            .format(proxy_name,flap_time))
    events.sendCommand(proxy_name, "OFF")

@rule("Presence",
      description=("Aggregates presence sensor readings and implements "
                   "anti-flapping for away."),
      tags=["presence"])
@trigger_generator(presence_config)
def presence(event):
    """
    Rule that implements presence detection based on the state of sensors. The
    Rule assumes there is a proxy Item associated with each sensor which
    represents the presence for that sensor. There is flapping logic which
    requires the user to be away for some minutes before the proxy will be set
    to OFF.
    """

    # Get the proxy Item associated with the sensor.
    try:
        sensor_name = event.itemName
        proxy_name = presence_config[sensor_name][0]
        flap_time = presence_config[sensor_name][1]

    except ValueError:
        presence.log.error("{} is not in presence_sensors!"
                           .format(event.itemName))
    except IndexError:
        presence.log.error("presence_items does not have the same number of "
                           "elements as presence_sensors, check your "
                           "configuration!")

    else:
        # Item and sensor are the same, cancel the flapping timer if there is
        # one.
        if items[sensor_name] == items[proxy_name]:
            if (proxy_name in presence_timers.keys()
                    and not presence_timers[proxy_name].hasTerminated()):
                presence.log.debug("{} came home, cancelling the flapping "
                                   "timer.".format(proxy_name))
                presence_timers[proxy_name].cancel()
                del presence_timers[proxy_name]
            return

        # Item and sensor are different, set a flapping timer if the sensor went
        # to OFF.
        if event.itemState == OFF:
            presence.log.debug("Setting the flapping timer for {}"
                               .format(proxy_name))
            presence_timers[proxy_name] = ScriptExecution.createTimer(
                DateTime.now().plusMinutes(presence_flap_time),
                lambda: away(presence.log, events, proxy_name, presence_timers))
        elif event.itemState == ON:
            presence.log.debug("{} came home.".format(proxy_name))
            events.sendCommand(proxy_name, "ON")

def scriptUnloaded():
    """
    Cancels all the timers when the script is unloaded to avoid timers hanging
    around.
    """
    if not presence_timers:
        for key in presence_timers.keys():
            if not presence_timers[key].hasTerminated()
                presence_timers.cancel()
