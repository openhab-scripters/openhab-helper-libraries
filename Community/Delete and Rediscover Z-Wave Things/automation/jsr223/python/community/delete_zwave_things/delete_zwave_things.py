'''
PURPOSE
-------

OH does not currently support automatically updating a Things definition, when
a binding is updated. This rule will delete all managed Z-Wave Things and then
rediscover them.

REQUIRES
--------

* OH installed on Linux
* The Z-Wave binding
* A Delete_Zwave_Things Item

KNOWN ISSUES
------------

* Manual configurations (e.q., location, name, etc.) will not be replaced after the deletion.

'''

from time import sleep

from org.eclipse.smarthome.model.script.actions.Exec import executeCommandLine

from core.rules import rule
from core.triggers import when

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
    thingUIDList = executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 10 -m 10 -X GET --header \"Accept: application/json\" \"http://localhost:8080/rest/things\" | /usr/bin/jq '.[].UID | select(contains(\"zwave:device\"))'",10000).split("\n")# get List of Things and filter out everything but Zwave device Thing UIDs
    deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: thingUIDList=[{}], len(thingUIDList)=[{}]".format(thingUIDList,len(thingUIDList)))
    if "" not in thingUIDList:
        deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: {} Things found".format(len(thingUIDList)))
        for thing in thingUIDList:# delete Zwave Things
            deletionResponse = executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -o /dev/null -s -w \"%{{http_code}}\" --connect-timeout 10 -m 10 -X DELETE --header \"Accept: application/json\" \"http://localhost:8080/rest/things/{}?force=false\"".format(thing),10000)# delete Thing
            if deletionResponse in ["200", "202"]:
                statusMap["DeletionSuccess"] += 1
            else:
                statusMap["DeletionFailure"] += 1
            deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: Thing deletion: <<<<< deletionResponse=[{}], Thing=[{}]".format(deletionResponse,thing))
    thingUIDList = executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 10 -m 10 -X GET --header \"Accept: application/json\" \"http://localhost:8080/rest/things\" | /usr/bin/jq '.[].UID | select(contains(\"zwave:device\"))'",10000).split("\n")# get List of Things and filter out everything but Zwave device Thing UIDs (if deletion was successful, this should be empty)
    if len(thingUIDList) == 1 and "" in thingUIDList:
        deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: All Zwave Things were deleted, so starting Zwave Discovery")
        discoveryResponse = executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -o /dev/null -s -w \"%{http_code}\" --connect-timeout 10 -m 10 -X POST --header \"Content-Type: application/json\" --header \"Accept: text/plain\" \"http://localhost:8080/rest/discovery/bindings/zwave/scan\"",10000)# start discovery
        deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: Started discovery: >>>>> discoveryResponse=[{}]".format(discoveryResponse))
        if discoveryResponse != "200":
            statusMap["DeletionFailure"] += 1
        sleep(10)
        inboxList = executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 10 -m 10 -X GET --header \"Accept: application/json\" \"http://localhost:8080/rest/inbox\" | /usr/bin/jq -r '.[] | {thingUID:(.thingUID | select(contains(\"zwave:device\"))), label:.label} | .[]'",10000).split("\n")# get List of Thing UIDs and labels from Inbox
        deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: len(inboxList)=[{}], [{}]".format(len(inboxList)/2))
        for index in range(0,len(inboxList) + 2,2):
            approvalResponse = executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -o /dev/null -s -w \"%{{http_code}}\" --connect-timeout 10 -m 10 -X POST --header \"Content-Type: text/plain\" --header \"Accept: application/json\" -d \"{}\" \"http://localhost:8080/rest/inbox/{}/approve\"".format(inboxList[index + 1],inboxList[index]),10000)# approve Thing in Inbox
            deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: Inbox approval: approvalResponse=[{}], Thing=[{}], label=[{}]".format(approvalResponse,inboxList[index],inboxList[index + 1]))
            if approvalResponse == "200":
                statusMap["ThingsAdded"] += 1
            else:
                statusMap["ThingsNotAdded"] += 1
    else:
        deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: {} Z-Wave Things were not deleted, so did not start Z-Wave Discovery. thingUIDList=[{}]".format(len(thingUIDList),thingUIDList))
    deleteRediscoverZwaveThings.log.debug("Delete Z-Wave Things: End: {}".format(statusMap))
