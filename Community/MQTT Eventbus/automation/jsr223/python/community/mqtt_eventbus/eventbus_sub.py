"""
Author: Rich Koshak

Implements a Rule to subscribe to the MQTT Eventbus topics published to from
another OH instance using the corresponding eventbus_pub.py script. Requires the
MQTT 2.5 or newer binding.

License
=======
Copyright (c) 2019 Contributors to the openHAB Scripters project
"""
from core.rules import rule
from core.triggers import when
from configuration import eb_in_chan

@rule("Eventbus subscribe",
      description="Subscribe to eventbus events and synchronize the Items.",
      tags=["eventbus"])
@when("Channel {} triggered".format(eb_in_chan))
def eb_sub(event):
    """
    Rule triggered by the receipt of a message from another openHAB instance's
    eventbus publisher. The Rule depends on the creation of a Channel on the
    Broker Thing with:
        - MQTT Topic: [device name]/out/# where [device name] is the name of the
        remote openHAB instance as configured in that OH's configuration.py
        eb_name ariable. The # will subscribe to all the topics the given path.
        - Separator character: '#', this will format the event received by the
        Rule as [topic]#[message] where [topic] is of the format
        [device name]/out/[item name]/[state|command] and [message] is the state
        or command that occured on that Item on the remote OH instance. If the
        event was an update the topic will be "state" and if the event was a
        command the topic will be "command".
    The Channel ID is stored in eb_in_chan in configurations.
    """
    topic = event.event.split("#")[0]
    state = event.event.split("#")[1]
    item_name = topic.split("/")[2]
    event_type = topic.split("/")[3]

    if item_name not in items:
        eb_sub.log.debug("Local openHAB does not have Item {}, ignoring."
                         .format(item_name))
    elif event_type == "command":
        events.sendCommand(item_name, state)
    else:
        events.postUpdate(item_name, state)
