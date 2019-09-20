"""
Author: Rich Koshak

Implements a Rule to implement the publishing side of an MQTT Eventbus
using the MQTT 2.5 or newer binding.

License
=======
Copyright (c) 2019 Contributors to the openHAB Scripters project
"""
from core.rules import rule
from core.triggers import when
from configuration import eb_out_gr, eb_name, eb_br

@rule("Publish Item events",
      description=("Publishes commands and update events for all members of {} "
                   "to the configured topic".format(eb_out_gr)),
      tags=["eventbus"])
@when("Member of {} received command".format(eb_out_gr))
@when("Member of {} received update".format(eb_out_gr))
def pub(event):
    """
    Called when a member of the Group defined by eb_out_gr in configuration.py
    receives a command or an update. When the Rule triggers it publishes the
    state or command to the MQTT topic
    [eb_name]/out/[item name]/[state|command] where:
        - eb_name: defined in configurations, the name of this OH instance
        - item name: the name of the Item that triggerd the Rule
        - state: when the Rule was triggered by an update
        - command: when the Rule was triggered by a command.
    For example, if the Item Foo received a command and eb_name is "appartment"
    the topic would be "appartment/out/Foo/command".

    The Broker Thing used to publish the messages is stored in eb_br. Commands
    are published with the retained flag set to False. Updates are published
    with the retained flag set to True.
    """
    is_cmd = hasattr(event, 'itemCommand')
    msg = str(event.itemCommand if is_cmd else event.itemState)
    topic = "{}/out/{}/{}".format(eb_name, event.itemName,
                                  "command" if is_cmd else "state")
    retained = False if is_cmd else True
    pub.log.debug("Publishing {} to {} on {}".format(msg, topic, eb_br))
    actions.get("mqtt", broker).publishMQTT(topic, msg, retained)
