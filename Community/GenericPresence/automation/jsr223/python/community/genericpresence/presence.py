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
from core.metadata import get_value

presence_timers = {}

def get_name(item_name):
    """
    Arguments:
        item_name: The name of the Item to retrieve the metadata from.
    Returns:
        None the 'name' metadata value of the passed in item_name
    """
    return get_value(item_name, "name") or item_name

def trigger_generator(presence_config):
    """
    Called to generate triggers for all of the defined presence sensors imported
    from configuration.

    Arguments:
        - presence_config: A dict whose keys are the names of the sensor Items
        that are managed by this Rule.
    """
    def generated_triggers(function):
        for sensor in presence_config:
            when("Item {} changed".format(sensor))(function)
        return function
    return generated_triggers

def create_timer(log, events, proxy_name, item_name, flap_time):
    """
    Creates an antiflapping timer.

    Arguments:
        - log: Logger from the Rule that creates the Timer.
        - events: Used to send the command.
        - proxy_name: Name of the proxy Item to set to OFF.
        - item_name: Name of the sensor Item that detects this person.
        - flap_time: Number of minutes to set the timer for.
    """
    presence_timers[proxy_name] = ScriptExecution.createTimer(
        DateTime.now().plusMinutes(flap_time),
        lambda: away(log, events, proxy_name, item_name, flap_time))

def away(log, events, proxy_name, item_name, flap_time):
    """
    Called when a person has been detected away for more than the flapping time.
    Log out the away state and command the Item to OFF.

    Arguments:
        - log: Logger passed in from the presence Rule.
        - events: Access to the events Object so we can call sendCommand.
        - proxy_name: Name of the proxy Item that we want to set to away.
        - item_name: Name of the sensor Item that detects presence.
        - flap_time: Number of minutes we wait before marking the person away.
    """
    if items[proxy_name] == OFF:
        log.warn("Presence away timer expired but {} is already OFF!"
                 .format(proxy_name))
    elif items[item_name] == ON:
        log.warn("Presence away timer expired but {} is ON!".format(item_name))
    else:
        log.info("{} has been away for {} minutes, setting to away."
                .format(get_name(proxy_name),flap_time))
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
        # Sensor changed to ON, cancel any timers if they exist and command the
        # proxy to ON if it isn't already ON.
        if event.itemState == ON:
            if proxy_name in presence_timers:
                if not presence_timers[proxy_name].hasTerminated():
                    presence_timers[proxy_name].cancel()
                del presence_timers[proxy_name]
            if items[proxy_name] != ON:
                presence.log.info("{} came home.".format(get_name(proxy_name)))
                events.sendCommand(proxy_name, "ON")

        # Sensor changed to OFF, create an antiflapping timer.
        elif event.itemState == OFF:
            create_timer(presence.log, events, proxy_name, sensor_name,
                         flap_time)

@rule("Presence Timers Reload",
      description=("Create an necessary timers and update proxies at system "
                   "start"),
      tags=["presence"])
@when("System started")
def presence_started(event):
    """
    Called at system started to update any timers and proxy Items based on
    current and/or restored states of sensors.
    """
    for sensor_name in presence_config:
        proxy_name = presence_config[sensor_name][0]
        flap_time = presence_config[sensor_name][1]

        if items[sensor_name] == ON:
            events.postUpdate(proxy_name, "ON")
        elif items[sensor_name] == OFF and items[proxy_name] != OFF:
            create_timer(presence_started.log, events, proxy_name, sensor_name,
                         flap_time)
        else:
            events.postUpdate(proxy_name, "UNDEF")

def scriptUnloaded():
    """
    Cancels all the timers when the script is unloaded to avoid timers hanging
    around.
    """
    if presence_timers:
        for key in [ k for k in presence_timers.keys()
                     if not presence_timers[k].hasTerminated() ]:
            presence_timers[key].cancel()
