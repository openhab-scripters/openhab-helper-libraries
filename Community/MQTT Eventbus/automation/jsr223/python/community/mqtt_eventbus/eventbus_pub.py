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
from configuration import eb_out_gr, eb_name, eb_cmd_br, eb_up_br

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

    One can use a different broker Thing for updates and for commands. This
    should let you, for example, set the retained flag to true for updates and
    set the retained flag to false for commands.
        - eb_cmd_br: defined in configuration, the broker Thing ID used for
        commands. I recommend the retained flag be set to off for this Thing.
        - eb_up_br: defined in configuration, the broker Thing ID used for
        updates. I recommend the retained flag be set to on for this Thing.
    """
    is_cmd = hasattr(event, 'itemCommand')
    msg = str(event.itemCommand if is_cmd else event.itemState)
    topic = "{}/out/{}/{}".format(eb_name, event.itemName,
                                  "command" if is_cmd else "state")
    broker = eb_cmd_br if is_cmd else eb_up_br
    pub.log.debug("Publishing {} to {} on {}".format(msg, topic, broker))
    actions.get("mqtt", broker).publishMQTT(topic, msg)
