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
"""
from time import sleep

from core.rules import rule
from core.triggers import when
from core.actions import Exec
from core.items import add_item
from core.metadata import set_value

if not itemRegistry.getItems("Delete_Zwave_Things"):
    add_item("Delete_Zwave_Things", item_type="Switch", label="Delete Z-Wave Things [%s]", category="Error", tags=["Switchable"])

set_value("Delete_Zwave_Things", "autoupdate", "false")

@rule("Misc: Delete and rediscover Z-Wave Things")
@when("Item Delete_Zwave_Things received command")
def deleteRediscoverZwaveThings(event):
    deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: Start")
    statusMap = {
        "DeletionSuccess"       : 0,
        "DeletionFailure"       : 0,
        "DiscoveryFailure"      : 0,
        "ThingsAdded"           : 0,
        "ThingsNotAdded"        : 0}
    thingUIDList = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 10 -m 10 -X GET --header \"Accept: application/json\" \"http://localhost:8080/rest/things\" | /usr/bin/jq '.[].UID | select(contains(\"zwave:device\"))'",10000).split("\n")# get List of Things and filter out everything but Zwave device Thing UIDs
    deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: thingUIDList=[{}], len(thingUIDList)=[{}]".format(thingUIDList,len(thingUIDList)))
    if "" not in thingUIDList:
        deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: {} Things found".format(len(thingUIDList)))
        for thing in thingUIDList:# delete Zwave Things
            deletionResponse = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -o /dev/null -s -w \"%{{http_code}}\" --connect-timeout 10 -m 10 -X DELETE --header \"Accept: application/json\" \"http://localhost:8080/rest/things/{}?force=false\"".format(thing),10000)# delete Thing
            if deletionResponse in ["200", "202"]:
                statusMap["DeletionSuccess"] += 1
            else:
                statusMap["DeletionFailure"] += 1
            deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: Thing deletion: <<<<< deletionResponse=[{}], Thing=[{}]".format(deletionResponse,thing))
    thingUIDList = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 10 -m 10 -X GET --header \"Accept: application/json\" \"http://localhost:8080/rest/things\" | /usr/bin/jq '.[].UID | select(contains(\"zwave:device\"))'",10000).split("\n")# get List of Things and filter out everything but Zwave device Thing UIDs (if deletion was successful, this should be empty)
    if len(thingUIDList) == 1 and "" in thingUIDList:
        deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: All Zwave Things were deleted, so starting Zwave Discovery")
        discoveryResponse = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -o /dev/null -s -w \"%{http_code}\" --connect-timeout 10 -m 10 -X POST --header \"Content-Type: application/json\" --header \"Accept: text/plain\" \"http://localhost:8080/rest/discovery/bindings/zwave/scan\"",10000)# start discovery
        deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: Started discovery: >>>>> discoveryResponse=[{}]".format(discoveryResponse))
        if discoveryResponse != "200":
            statusMap["DeletionFailure"] += 1
        sleep(10)
        inboxList = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 10 -m 10 -X GET --header \"Accept: application/json\" \"http://localhost:8080/rest/inbox\" | /usr/bin/jq -r '.[] | {thingUID:(.thingUID | select(contains(\"zwave:device\"))), label:.label} | .[]'",10000).split("\n")# get List of Thing UIDs and labels from Inbox
        deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: len(inboxList)=[{}], [{}]".format(len(inboxList)/2))
        for index in range(0,len(inboxList) + 2,2):
            approvalResponse = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -o /dev/null -s -w \"%{{http_code}}\" --connect-timeout 10 -m 10 -X POST --header \"Content-Type: text/plain\" --header \"Accept: application/json\" -d \"{}\" \"http://localhost:8080/rest/inbox/{}/approve\"".format(inboxList[index + 1],inboxList[index]),10000)# approve Thing in Inbox
            deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: Inbox approval: approvalResponse=[{}], Thing=[{}], label=[{}]".format(approvalResponse,inboxList[index],inboxList[index + 1]))
            if approvalResponse == "200":
                statusMap["ThingsAdded"] += 1
            else:
                statusMap["ThingsNotAdded"] += 1
    else:
        deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: {} Z-Wave Things were not deleted, so did not start Z-Wave Discovery. thingUIDList=[{}]".format(len(thingUIDList),thingUIDList))
    deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: End: {}".format(statusMap))
