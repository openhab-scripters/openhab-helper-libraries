"""
Author: Rich Koshak

Implements a Rule to publish ONLINE to a status topic to indicate when this
instance of OH comes online.

License
=======
Copyright (c) 2019 contributors to the openHAB Scripters project
"""
from core.rules import rule
from core.triggers import when
from configuration import eb_name, eb_up_br

@rule("Eventbus Online",
      description="Publsih that this instance of OH is now online",
      tags=["eventbus"])
@when("System started")
def online(event):
    """
    At OH system start, publish "ONLINE" to eb_name/status to indicate that OH
    has come back online. eb_name is defined in configuration and contains the
    unique name for this OH instance. The Broker Thing ID stored in eb_up_br is
    used. I recommend setting the retained flag to true for this Thing.

    I also recommend that the LWT configured on the eb_up_br Thing be the same
    topic used here. This will allow any client to instantly know whether this
    OH is online whether or not that client happened to be itself online when
    this OH went offline or came back online.
    """
    online.log.debug("Reported eventbus as online")
    actions.get("mqtt", eb_up_br).publishMQTT("{}/status".format(eb_name),
                                                                 "ONLINE")
