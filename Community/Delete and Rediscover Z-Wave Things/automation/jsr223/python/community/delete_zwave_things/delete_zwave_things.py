"""
Purpose
-------

openHAB does not currently support automatically updating a Thing's definition
after it has been updated in a binding. In order to update it, the existing
Thing must be deleted and rediscovered. This rule will delete all managed
Z-Wave Things and rediscover them. Any existing configuration (name, location,
etc.) for the Z-Wave Things is not restored.


Requires
--------

* openHAB installed on Linux (executeCommandLine is used to launch
  ``/usr/bin/curl`` in a ``/bin/sh`` shell
* The Z-Wave binding
* A ``Delete_Zwave_Things`` Item (the script will create this for you, if it
  does not exist)


Known Issues
------------

* Manual Thing configurations (e.q., location, name, etc.) are not retained
  and restored.


Change Log
==========

05/29/20: Pylint updates
"""
from time import sleep

from core.rules import rule
from core.triggers import when
from core.actions import Exec
from core.items import add_item
from core.metadata import set_value

if not itemRegistry.getItems("Delete_Zwave_Things"):
    add_item("Delete_Zwave_Things", item_type="Switch", label="Delete Z-Wave Things", category="Error", tags=["Switchable"])

set_value("Delete_Zwave_Things", "autoupdate", "false")


@rule("Misc: Delete and rediscover Z-Wave Things")
@when("Item Delete_Zwave_Things received command")
def delete_rediscover_zwave_things(event):
    delete_rediscover_zwave_things.log.debug("Delete Z-Wave Things: Start")
    status = {
        "DeletionSuccess"       : 0,
        "DeletionFailure"       : 0,
        "DiscoveryFailure"      : 0,
        "ThingsAdded"           : 0,
        "ThingsNotAdded"        : 0}
    thing_uid_list = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 10 -m 10 -X GET --header \"Accept: application/json\" \"http://localhost:8080/rest/things\" | /usr/bin/jq '.[].UID | select(contains(\"zwave:device\"))'", 10000).split("\n")# get List of Things and filter out everything but Zwave device Thing UIDs
    delete_rediscover_zwave_things.log.debug("Delete Z-Wave Things: thing_uid_list: {}, len(thing_uid_list): {}".format(thing_uid_list, len(thing_uid_list)))
    if "" not in thing_uid_list:
        delete_rediscover_zwave_things.log.debug("Delete Z-Wave Things: {} Things found".format(len(thing_uid_list)))
        for thing in thing_uid_list:# delete Zwave Things
            deletion_response = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -o /dev/null -s -w \"%{{http_code}}\" --connect-timeout 10 -m 10 -X DELETE --header \"Accept: application/json\" \"http://localhost:8080/rest/things/{}?force=false\"".format(thing), 10000)# delete Thing
            if deletion_response in ["200", "202"]:
                status["DeletionSuccess"] += 1
            else:
                status["DeletionFailure"] += 1
            delete_rediscover_zwave_things.log.debug("Delete Z-Wave Things: Thing deletion: <<<<< deletion_response: {}, Thing: {}".format(deletion_response, thing))
    thing_uid_list = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 10 -m 10 -X GET --header \"Accept: application/json\" \"http://localhost:8080/rest/things\" | /usr/bin/jq '.[].UID | select(contains(\"zwave:device\"))'", 10000).split("\n")# get List of Things and filter out everything but Zwave device Thing UIDs (if deletion was successful, this should be empty)
    if len(thing_uid_list) == 1 and "" in thing_uid_list:
        delete_rediscover_zwave_things.log.debug("Delete Z-Wave Things: All Zwave Things were deleted, so starting Zwave Discovery")
        discovery_response = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -o /dev/null -s -w \"%{http_code}\" --connect-timeout 10 -m 10 -X POST --header \"Content-Type: application/json\" --header \"Accept: text/plain\" \"http://localhost:8080/rest/discovery/bindings/zwave/scan\"", 10000)# start discovery
        delete_rediscover_zwave_things.log.debug("Delete Z-Wave Things: Started discovery: >>>>> discovery_response: {}".format(discovery_response))
        if discovery_response != "200":
            status["DeletionFailure"] += 1
        sleep(10)
        inbox_list = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 10 -m 10 -X GET --header \"Accept: application/json\" \"http://localhost:8080/rest/inbox\" | /usr/bin/jq -r '.[] | {thingUID:(.thingUID | select(contains(\"zwave:device\"))), label:.label} | .[]'", 10000).split("\n")# get List of Thing UIDs and labels from Inbox
        delete_rediscover_zwave_things.log.debug("Delete Z-Wave Things: len(inbox_list): {}".format(len(inbox_list)/2))
        for index in range(0, len(inbox_list) + 2, 2):
            approval_response = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -o /dev/null -s -w \"%{{http_code}}\" --connect-timeout 10 -m 10 -X POST --header \"Content-Type: text/plain\" --header \"Accept: application/json\" -d \"{}\" \"http://localhost:8080/rest/inbox/{}/approve\"".format(inbox_list[index + 1], inbox_list[index]), 10000)# approve Thing in Inbox
            delete_rediscover_zwave_things.log.debug("Delete Z-Wave Things: Inbox approval: approval_response: {}, Thing: {}, label: {}".format(approval_response, inbox_list[index], inbox_list[index + 1]))
            if approval_response == "200":
                status["ThingsAdded"] += 1
            else:
                status["ThingsNotAdded"] += 1
    else:
        delete_rediscover_zwave_things.log.debug("Delete Z-Wave Things: {} Z-Wave Things were not deleted, so did not start Z-Wave Discovery. thing_uid_list: {}".format(len(thing_uid_list), thing_uid_list))
    delete_rediscover_zwave_things.log.debug("Delete Z-Wave Things: End: {}".format(status))
