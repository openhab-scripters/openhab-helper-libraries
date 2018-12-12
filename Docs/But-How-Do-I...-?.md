[[Home]](README.md)

## But How Do I... ?

#### Single line comment:
```python
# this is a single line comment
```

#### Multiline comment:
```python
'''
this is
a multiline
comment
'''
```

#### Get an item:
```python
itemRegistry.getItem("My_Item")
```
or using the alias to itemRegistry...
```python
ir.getItem("My_Item")
```

#### Get the state of an item:
```python
ir.getItem("My_Item").state
```
<ul>

or...
</ul>

```python
items["My_Item"]
```
<ul>

or (using the `core` package)...
</ul>

```python
items.My_Item
```

#### Get the equivalent of Rules DSL `triggeringItem`:
```python
ir.getItem(event.itemName)
```

#### Get the equivalent of Rules DSL `triggeringItem.name`:
```python
event.itemName
```

#### Get the equivalent of Rules DSL `triggeringItem.state`:
```python
event.itemState
```

#### Get the previous state:
```python
event.oldItemState
```

#### Get the received command:
```python
event.itemCommand
```

#### Send a command to an item ([more options](https://www.openhab.org/docs/configuration/jsr223.html#events-operations)):
```python
events.sendCommand("Test_SwitchItem", "ON")
```

#### Send an update to an item ([more options](https://www.openhab.org/docs/configuration/jsr223.html#events-operations)):
```python
events.postUpdate("Test_SwitchItem", "ON")
```

#### Return from a function if the previous state is NULL:
```
def testFunction(event)
    if event.oldItemState == UnDefType.NULL:
        return
    # do stuff
```

#### Use org.joda.time.DateTime:
```python
from org.joda.time import DateTime
start = DateTime.now()
```

#### [Persistence extensions](https://www.openhab.org/docs/configuration/persistence.html#persistence-extensions-in-scripts-and-rules) (others not listed are similar):
```python
from core.actions import PersistenceExtensions
PersistenceExtensions.previousState(ir.getItem("Weather_SolarRadiation"), True).state

from org.joda.time import DateTime
PersistenceExtensions.changedSince(ir.getItem("Weather_SolarRadiation"), DateTime.now().minusHours(1))
PersistenceExtensions.maximumSince(ir.getItem("Weather_SolarRadiation"), DateTime.now().minusHours(1)).state
```

#### Use other [Core & Cloud Actions](https://www.openhab.org/docs/configuration/actions.html#core-actions):
```python
from org.eclipse.smarthome.model.script.actions.Exec import executeCommandLine
executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 3 --max-time 3 http://some.host.name",5000)

from org.eclipse.smarthome.model.script.actions.HTTP import sendHttpPutRequest
sendHttpPutRequest("someURL.com, "application/json", '{"this": "that"}')

from core.actions import Audio
Audio.playSound("doorbell.mp3")# using the default audiosink
Audi.playSound("my:audio:sink", "doorbell.mp3")# specifying an audiosink
Audio.playStream("http://myAudioServer/myAudioFile.mp3")# using the default audiosink
Audio.playStream("my:audio:sink", "http://myAudioServer/myAudioFile.mp3")# specifying an audiosink

from core.actions import NotificationAction
NotificationAction.sendNotification("someone@someDomain.com","This is the message")
NotificationAction.sendBroadcastNotification("This is the message")
NotificationAction.sendLogNotification("This is the message")

from core.actions import Mail
Mail.sendMail("someone@someDomain.com","This is the message")

from core.actions import Transformation
Transformation.transform("JSONPATH", "$.test", test)

from core.actions import Voice
Voice.say("This will be said")

from core.actions import ThingAction
ThingAction.getThingStatusInfo("zwave:device:c5155aa4:node5")
```

#### Use a timer:
See the [`timer_example.py`](https://github.com/OH-Jython-Scripters/openhab2-jython/blob/master/Script%20Examples/timer_example.py) in the Script Examples for examples of using both Jython and the [`createTimer`](https://www.openhab.org/docs/configuration/actions.html#timers) Action.

#### Use an Addon/Bundle Action (binding must be installed):
[Telegram](https://www.openhab.org/addons/actions/telegram/#telegram-actions)
```python
from core.actions import Telegram
Telegram.sendTelegram("MyBot", "Test")
```

[Mail](https://www.openhab.org/addons/actions/mail/#mail-actions)
```python
from core.actions import Mail
Mail.sendMail("someone@someDomain.com", "This is the subject", "This is the message")
```

#### Logging (the logger can be modified to wherever you want the log to go):
```python
from org.slf4j import Logger, LoggerFactory
log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")
log.debug("Test debug log")
log.info("Test info log")
log.warn("Test warn log")
log.error("Test error log")

or using the log module, which logs to org.eclipse.smarthome.automation.jsr223.jython...

from core.log import logging, LOG_PREFIX
log = logging.getLogger(LOG_PREFIX + ".TEST")
log.debug("This is a test log")
```

#### Convert a value to a state for comparison:
```python
items["String_Item"] == StringType("test string")
items["Switch_Item"] == OnOffType.ON
items["Number_Item"] > DecimalType(5)
items["Contact_Item"] == OpenClosedType.OPEN
items["Some_Item"] != UnDefType.NULL
event.itemState <= DecimalType(event.oldItemState.intValue() + 60)
event.itemState <= DecimalType(event.oldItemState.doubleValue() + 60)
event.itemState <= DecimalType(event.oldItemState.floatValue() + 60)
```
    
#### Convert DecimalType to an integer or float for arithmetic:
```python
int(str(items["Number_Item1"])) + int(str(items["Number_Item2"])) > 5
items["Number_Item1"].intValue() + items["Number_Item2"].intValue() > 5
float(str(items["Number_Item"])) + 5.5555 > 55.555
items["Number_Item"].floatValue() + 5.5555 > 55.555
```

#### Pause a thread:
```python
from time import sleep
sleep(5)# the unit is seconds, so use 0.5 for 500 milliseconds
```

#### Get the members or all members of a Group:
```python
ir.getItem("gTest").members

ir.getItem("gTest").allMembers
```

#### Iterate over members of a Group:
```python
for item in ir.getItem("gTest").members:
    #do stuff
```

#### Filter members of a group (returns a list of Items, not a GroupItem):
```python
listOfMembers = filter(lambda item: item.state == OnOffType.ON, ir.getItem("gTest").members)
```

#### Get the first element of a filtered list of Group members (returns an Item):
```python
filter(lambda item: item.state == OnOffType.ON, ir.getItem("gTest").members)[0]
```

#### Get a list containing the first 5 elements from a filtered list of Group members (returns a list):
```python
filter(lambda item: item.state == OnOffType.OFF, ir.getItem("gTest").members)[0:5]
```

#### Get a sorted list of Group members matching a condition (returns a list of Items):
```python
sortedBatteryLevel = sorted(battery for battery in ir.getItem("gBattery").getMembers() if battery.state < DecimalType(5), key = lambda battery: battery.state)
```

#### Get a list of values mapped from the members of a Group (returns a list):
```python
map(lambda lowBattery: "{}: {}".format(lowBattery.label, str(lowBattery.state) + "%"), ir.getItem("gBattery").members)
```

#### Perform an arithmetic reduction of values from members of a Group (returns a value):
```python
# the state.add(state) is a method of QuantityType
reduce(lambda sum, x: sum.add(x), map(lambda rain: rain.state, ir.getItem("gRainWeeklyForecast").members))
```

#### Example with several functions using Group members:
```python
lowBatteryMessage = "Warning! Low battery alert:\n\n{}".format(",\n".join(map(lambda lowBattery: "{}: {}".format(lowBattery.label,str(lowBattery.state) + "%"), sorted(battery for battery in ir.getItem("gBattery").getMembers() if battery.state < DecimalType(5), key = lambda battery: battery.state))))
```

#### Read/Add/Remove Item metadata:
https://community.openhab.org/t/jsr223-jython-using-item-metadata-in-rules/53868

#### View all names in an obejct's namespace:
```python
from org.slf4j import Logger, LoggerFactory
log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")
log.debug("JSR223: Test dir(object)=[{}]".format(dir(object)))
```

#### Get the UID of a rule by name:
```python
scriptExtension.importPreset("RuleSupport")
ruleUID = filter(lambda rule: rule.name == "This is the name of my rule", rules.getAll())[0].UID
```

#### Enable or disable a rule by UID:
```python
from core import osgi
ruleEngine = osgi.get_service("org.eclipse.smarthome.automation.RuleManager")
ruleEngine.setEnabled(ruleUID, True)# enable rule
ruleEngine.setEnabled(ruleUID, False)# disable rule
```

#### Run a rule by UID:
```python
from core import osgi
ruleEngine = osgi.get_service("org.eclipse.smarthome.automation.RuleManager")
considerConditions = False# consider the rule's Conditions
ruleEngine.runNow(ruleFunction.UID)# without inputs
ruleEngine.runNow(ruleFunction.UID, considerConditions, {'name': 'EXAMPLE'})# with inputs
```
