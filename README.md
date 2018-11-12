# Jython scripting for openHAB 2.x

This is a repository of experimental Jython code that can be used 
with the [Eclipse SmartHome](https://www.eclipse.org/smarthome/) platform and [openHAB 2](http://openhab.org/) (post OH snapshot build 1318). 
A previous version with reduced functionality but compatible with OH 2.3 has been archived in this [branch](https://github.com/OH-Jython-Scripters/openhab2-jython/tree/original_(%3C%3D2.3)).

- [Getting Started](#getting-started)
    - [Quick Start Guide](#quick-start-guide)
    - [Applications](#applications)
    - [Jython Scripts and Modules](#jython-scripts-and-modules)
    - [File Locations](#file-locations)
- [Jython Modules](#jython-modules)
- [Component Scripts](#component-scripts)
- [Example Jython Scripts](#example-jython-scripts)
- [Defining Rules](#defining-rules)
    - [Raw ESH Automation API](#raw-esh-automation-api)
    - [Using Jython Extensions](#using-jython-extensions)
        - [Rule and Trigger Decorators](#rule-and-trigger-decorators)
    - [Event object attributes](#event-object-attributes)
    - [But how do I...?](#but-how-do-i)

## Getting Started

<ul>

### Quick Start Guide
<ul>

- Since JSR223 is still under development, it is best to use a current testing or snapshot release of openHAB. 
More importantly, there are breaking changes in the API, so at least OH snapshot 1319 or milestone M3 are required to use these modules.
- Install the [Experimental Rule Engine](https://www.openhab.org/docs/configuration/rules-ng.html) add-on.
- Review the [JSR223 Jython documentation](https://www.openhab.org/docs/configuration/jsr223-jython.html).
- Turn on debugging for org.eclipse.smarthome.automation (`log:set DEBUG org.eclipse.smarthome.automation` in Karaf). Leave this on for setup and testing, but you may want to set to WARN when everything is setup.
- Download the contents of this repository and copy the `automation` directory into `/etc/openhab2/` (package repository OH install, like openHABian) or `/opt/openhab2/conf` (default manual OH install).
- Add/modify your EXTRA_JAVA_OPTS. These examples assume that you will be using the standalone Jython 2.7.0 jar. 

    **Using a `/etc/default/openhab2` file with a package repository OH installation (includes openHABian):**
    ```
    EXTRA_JAVA_OPTS="-Xbootclasspath/a:/etc/openhab2/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/etc/openhab2/automation/jython -Dpython.path=/etc/openhab2/automation/lib/python"
    ```
    **Using the `start.sh` script with a manual OH installation:**
    ```
    export EXTRA_JAVA_OPTS="-Xbootclasspath/a:/opt/openhab2/conf/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/opt/openhab2/conf/automation/jython -Dpython.path=/opt/openhab2/conf/automation/lib/python"
    ```
- Download the [standalone Jython 2.7.0 jar](http://www.jython.org/downloads.html) and copy it to the path specified above. A full install of Jython can also be used, but the paths above will need to be modified.
- Restart OH and watch the logs for errors.
- Copy the [`hello_world.py`](/Script%20Examples/hello_world.py) example script to `/automation/jsr223/` to test if everything is working. This script will make a log entry every 10s.
- Review the general [openHAB2 JSR223 scripting documentation](http://docs.openhab.org/configuration/jsr223.html).
- Review the rest of this documentation.
- Create rules using [rule and trigger decorators](#rule-and-trigger-decorators).
- Ask questions on the [openHAB forum](https://community.openhab.org/tags/jsr223) and tag posts with `jsr223`. Report issues [here](https://github.com/OH-Jython-Scripters/openhab2-jython/issues).

Some directions specifically for Docker are available at [Docker.md](Docker.md)

</ul>

### Applications
<ul>

The [JSR223 scripting extensions](https://www.jcp.org/en/jsr/detail?id=223) can be used for general scripting purposes, 
including defining rules and associated SmartHome rule "modules" (triggers, conditions, actions). 
Some possible applications include integration testing of complex rule behaviors or prototyping new OH2/ESH functionality.

(_JSR223_ refers to a Java specification request for adding scripting to the Java platform. 
That term will not be used in Java versions 9 and above. 
The previous JSR223 functionality will be provided by the Java `javax.script` package in the standard runtime libraries.)

The scripting can be used for other purposes like automated integration testing 
or to access the OSGI framework (using or creating services, for example).
</ul>

### Jython Scripts and Modules
<ul>

It's important to understand the distinction between Jython _scripts_ and Jython _modules_. 
In this repo, scripts are in the `scripts` directory and modules are in the `lib` directory.

A Jython script is loaded by the `javax.script` script engine manager (JSR223) integrated into openHAB 2. 
Each time the file is loaded, OH2 creates a execution context for that script.
When the file is modified, OH2 will destroy the old script context and create a new one.
This means any variables defined in the script will be lost when the script is reloaded.

A Jython module is loaded by Jython itself through the standard Python `import` directive and uses `sys.path`.
The normal Python module loading behavior applies.
This means the module is loaded once and is not reloaded when the module source code changes.
</ul>

### File Locations
<ul>

Scripts should be put into the `/automation/jsr223/` subdirectory hierarchy of your OH2 configuration directory.
In a Linux package repository installation, like openHABian, this would be `/etc/openhab2/automation/jsr223/`. For a Linux manual installation, this would default to `/opt/openhab2/conf/automation/jsr223/`.

Some scripts should be loaded before others because of dependencies between the scripts. 
Scripts that implement OH2 components (like trigger types, item providers, etc.) are one example.
It is recommended to put these scripts into a subdirectory called `000_Components`. 
The name prefix will cause the scripts in the directory to be loaded first.
It is also recommended to name the component files with a `000_` prefix, 
because there are currently bugs in the file loading behavior of OH2 (ref? likely resolved).

Example:

```text
|_ etc
    |_ openhab2
        |_ automation
            |_ jsr223
                |_ 000_Components
                    |_ 000_StartupTrigger.py
                |_ my_rule_script.py
```

Jython modules can be placed anywhere, but the Python path must be configured to find them.
There are several ways to do this. 
You can add a `-Dpython.path=mypath1:mypath2` to the JVM command line by modifying the OH2 startup scripts.
You can also modify the `sys.path` list in a Jython script that loads early (like a component script).

Another option is to checkout the GitHub repo in some location and use a directory soft link (Linux) 
from `/etc/openhab2/automation/lib/python/openhab` to the GitHub workspace `automation/lib/python/openhab` directory.
</ul>
</ul>

## [Jython Modules](/automation/lib/python/openhab/README.md)
<ul>

One of the benefits of Jython over the openHAB Xtext scripts is that you can use the full power of Python packages 
and modules to structure your code into reusable components. 
The following are some initial experiments in that direction.
In order to use them, these modules will need to be copied to a subdirectory of `/automation/lib/python/`.

#### Modifying Modules
<ul>

Changes to a module will not take effect until all other modules and scripts that have imported it have been reloaded. 
Restarting OH will remedy this, but another option is to use the reload() function:

```
import myModule
reload(myModule)
import myModule
```
If using imports like `from openhab.triggers import when`, or if the module is in a package, you will need to use:
```
import sys
from openhab.triggers import when
reload(sys.modules['openhab.triggers'])
from openhab.triggers import when
```
... or import the whole module to reload it...
```
from openhab.triggers import when
import openhab.triggers
reload(openhab.triggers)
from openhab.triggers import when
```
</ul>

#### Custom Modules
<ul>

Custom modules and packages can also be added into `/automation/lib/python/`. Modules do not have the same scope as scripts, but this can be remedied by importing `scope` from the `jsr223` module. This will allow for things like accessing the itemRegistry:
```
from openhab.jsr223 import scope
scope.itemRegistry.getItem("MyItem")
```

</ul>
</ul>

## [Component Scripts](/automation/jsr223/000_components/README.md)
<ul>

These scripts are located in the `/automation/jsr223/000_components` subdirectory. 
They should be copied to the same directory structure inside your openHAB 2 installation to use them. 
The files have a numeric prefix to cause them to be loaded before regular user scripts.

</ul>

## [Example Jython Scripts](/Script%20Examples/README.md)
<ul>

These scripts show example usage of various scripting features. 
Some of the examples are intended to provide services to user scripts so they have a numeric prefix to force them to load first 
(but after the general purpose components). In order to use them, these scripts can be copied to a subdirectory of `/automation/jsr223/` to test them.
These scripts will import certain modules, so they will also need to be instaled.

</ul>

## Defining Rules
<ul>

One of the primary use cases for JSR223 scripting in OH is to define rules for the [Eclipse SmartHome (ESH) rule engine](http://www.eclipse.org/smarthome/documentation/features/rules.html) using the [Java/Automation API](http://www.eclipse.org/smarthome/documentation/features/rules.html#java-api).
The ESH rule engine structures rules as _Modules_ (Triggers, Conditions, Actions). 
Jython rules can use rule Modules that are already present in ESH, and can define new Modules that can be used outside of JSR223 scripting. Take care not to confuse ESH Modules with Jython modules. 
In decreasing order of complexity, rules can be created using the [raw Automation API](#raw-esh-automation-api), [extensions](#using-jython-extensions), and [rule and trigger decorators](#rule-and-trigger-decorators). 
The detais for all of these methods are included here for reference, but the section on [decorators](#rule-and-trigger-decorators) should be all that is needed for creating your rules.

Take care in your choice of object names used in your rules, so as not to use one that is already included in the [default scope](https://www.openhab.org/docs/configuration/jsr223.html#default-variables-no-preset-loading-required). 
For example, the `items` object is from the default scope, and allows access to [each Item's state](#get-the-state-of-an-item). 
Another important object from the default scope is the `events` object, which can be used to [send a command](#send-a-command-to-an-item) or [change the state](#send-an-update-to-an-item) of an Item.

### Raw ESH Automation API
<ul>

The simplest raw API rule definition would look something like this:

```python
scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleSimple")

class MyRule(SimpleRule):
    def __init__(self):
        self.triggers = [
            TriggerBuilder.create()
                    .withId("MyTrigger")
                    .withTypeUID("core.ItemStateUpdateTrigger")
                    .withConfiguration(
                        Configuration({
                            "itemName": "TestString1"
                        })).build()
        ]
        
    def execute(self, module, input):
        events.postUpdate("TestString2", "some data")

automationManager.addRule(MyRule())
```
Note: trigger names must be unique within the scope of a rule instance, and can only contain alphanumeric characters, hythens, and underscores (no spaces).

This can be simplified with some extra Jython code, which we'll see later. 
First, let's look at what's happening with the raw functionality.

When a Jython script is loaded it is provided with a _JSR223 scope_ that [predefines a number of variables](https://www.openhab.org/docs/configuration/jsr223.html#default-variables-no-preset-loading-required). 
These include the most commonly used core types and values from ESH (e.g., State, Command, OnOffType, etc.). 
This means you don't need a Jython import statement to load them.

For defining rules, additional symbols must be defined. 
Rather than using a Jython import (remember, JSR223 support is for other languages too), 
these additional symbols are imported using:

```python
scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleSimple")
```

The `scriptExtension` instance is provided as one of the default scope variables. 
The RuleSimple preset defines the `SimpleRule` base class.  
This base class implements a rule with a single custom ESH Action associated with the `execute` function. 
The list of rule triggers are provided by the triggers attribute of the rule instance.

The trigger in this example is an instance of the `Trigger` class. 
The constructor arguments define the trigger, the trigger type string and a configuration.

The `events` variable is part of the default scope and supports access to the ESH event bus (posting updates and sending commands). 
Finally, to register the rule with the ESH rule engine it must be added to the `ruleRegistry`. 
This will cause the triggers to be activated and the rule will fire when the TestString1 item is updated.
</ul>

### Using Jython extensions
<ul>

To simplify rule creation even further, Jython can be used to wrap the raw Automation API. 
The current experimental wrappers include trigger-related classes, so the previous example becomes:

```python
scriptExtension.importPreset("RuleSimple")
scriptExtension.importPreset("RuleSupport")

from openhab.triggers import ItemStateUpdateTrigger

class exampleExtensionRule(SimpleRule):
    def __init__(self):
        self.triggers = [ ItemStateChangeTrigger("TestString1").trigger ]

    def execute(self, module, input):
        events.postUpdate("TestString2", "some data")

automationManager.addRule(exampleExtensionRule())
```

This removes the need to know the internal ESH trigger type strings, 
define trigger names and to know configuration dictionary requirements.

#### Rule and Trigger Decorators
<ul>

To make rule creation _even simpler_, `openhab.rules` defines a decorator that can be 
used to create a rule, which can be fed triggers from a decorator in `openhab.triggers`. These triggers can be defined similarly to how it is done in the Rules DSL. 

```python
from openhab.rules import rule
from openhab.triggers import when

@rule("This is the name of a test rule")
@when("Item Test_Switch_1 received command OFF")
@when("Item Test_Switch_2 received update ON")
@when("Item gMotion_Sensors changed to ON")
@when("Member of gMotion_Sensors changed to OFF")
@when("Descendent of gContact_Sensors changed to ON")
@when("Thing kodi:kodi:familyroom changed")# ThingStatusInfo (from <status> to <status>) cannot currently be used in triggers
@when("Channel astro:sun:local:eclipse#event triggered START")
@when("System started")# 'System shuts down' cannot currently be used as a trigger, and 'System started' needs to be updated to work with Automation API updates
@when("Time cron 55 55 5 * * ?")
def testFunction(event):
    if items["Test_Switch_1"] == OnOffType.ON:
        events.postUpdate("Test_String_1", "The test rule has been executed!")
```

Notice there is no explicit preset import, and the generated rule is registered automatically with the `HandlerRegistry`. 
Note: 'Descendent of' is similar to 'Member of', but will create a trigger for each sibling non-group Item (think group_item.allMembers()).

</ul>
</ul>

### Event object attributes
<ul>

When a rule is triggered, the function is provided the event instance that triggered it.
The specific data depends on the event type.
For example, the [`ItemStateChangedEvent`](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateChangedEvent.java) event type has `itemName`, `itemState`, and `oldItemState` attributes. Rather than digging through the code to look up the attributes available in a particular `event` object, you can add a log entry inside the function, and then trigger the rule:
```
log.info("JSR223: dir(event)=[{}]".format(dir(event)))
```

Here is a table of the attributes available in `event` objects (or `inputs.get('event')` if using Raw ESH or extensions), including a comparison to the Rules DSL implicit variables:

| Rules DSL | JSR223 | @when Trigger(s) | Raw ESH Event(s) | Description
| --- | --- | --- | --- | --- |
triggeringItem.name | event.itemName | "received update", "changed", "received&nbsp;command" | [ItemStateEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateEvent.java), [ItemStateChangedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateChangedEvent.java), [ItemCommandEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemCommandEvent.java), [ItemStatePredictedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStatePredictedEvent.java), [GroupItemStateChangedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/GroupItemStateChangedEvent.java) | Name of Item that triggered event (String)
triggeringItem.name | event.memberName | "changed" | [GroupItemStateChangedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/GroupItemStateChangedEvent.java) | Name of member that caused the state change of a parent Group (String)
triggeringItem.state | event.itemState | "received update", "changed" | [ItemStateEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateEvent.java), [ItemStateChangedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateChangedEvent.java) | State of item that triggered event (State)
previousState | event.oldItemState | "changed" | [ItemStateChangedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateChangedEvent.java), [GroupItemStateChangedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/GroupItemStateChangedEvent.java) | Previous state of Item or Group that triggered event (State)
receivedCommand | event.itemCommand | "received&nbsp;command" | [ItemCommandEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemCommandEvent.java) | Command that triggered event (Command)
N/A | event.predictedState | *Not&nbsp;currently&nbsp;supported* | [ItemStatePredictedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStatePredictedEvent.java) | State that the Item triggering the event is predicted to have (State)
N/A | event.isConfirmation | *Not&nbsp;currently&nbsp;supported* | [ItemStatePredictedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStatePredictedEvent.java) | If&nbsp;`true`,&nbsp;then&nbsp;it&nbsp;basically&nbsp;only&nbsp;confirms&nbsp;the&nbsp;previous&nbsp;item&nbsp;state&nbsp;because&nbsp;a&nbsp;received&nbsp;command&nbsp;will&nbsp;not&nbsp;be&nbsp;successfully&nbsp;executed&nbsp;and&nbsp;therefore&nbsp;presumably&nbsp;will&nbsp;not&nbsp;result&nbsp;in&nbsp;a&nbsp;state&nbsp;change&nbsp;(e.g.&nbsp;because&nbsp;no&nbsp;handler&nbsp;currently&nbsp;is&nbsp;capable&nbsp;of&nbsp;delivering&nbsp;such&nbsp;an&nbsp;event&nbsp;to&nbsp;its&nbsp;device)&nbsp;(Boolean)
N/A | event.newItemState | *Not&nbsp;currently&nbsp;supported* | [GroupItemStateChangedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/GroupItemStateChangedEvent.java) | State of Group that triggered event (State)
N/A | event.item | *Not&nbsp;currently&nbsp;supported* | [ItemAddedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemAddedEvent.java), [ItemRemovedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemRemovedEvent.java) | Item that triggered event (Item)
N/A | event.oldItem | *Not&nbsp;currently&nbsp;supported* | [ItemUpdatedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemUpdatedEvent.java) | Item DTO prior to the Item being updated (Item)
N/A | event.channel | "triggered" | [ChannelTriggeredEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ChannelTriggeredEvent.java) | Channel associated with Event that triggered event (Channel)
N/A | event.event | "triggered" | [ChannelTriggeredEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ChannelTriggeredEvent.java) | Event that triggered event (Event)
N/A | event.thing | *Not&nbsp;currently&nbsp;supported* | [ThingAddedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingAddedEvent.java), [ThingRemovedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingRemovedEvent.java) | Thing that triggered event (Thing)
N/A | event.oldThing | *Not&nbsp;currently&nbsp;supported* | [ThingUpdatedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingUpdatedEvent.java) | Thing DTO prior to the Thing being updated (Thing)
N/A | event.thingUID | "changed" | [ThingStatusInfoEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingStatusInfoEvent.java), [ThingStatusInfoChangedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingStatusInfoChangedEvent.java) | ThingUID of Thing that triggered event (ThingUID)
N/A | event.statusInfo | "changed" | [ThingStatusInfoEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingStatusInfoEvent.java), [ThingStatusInfoChangedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingStatusInfoChangedEvent.java) | ThingStatusInfo of Thing that triggered event (ThingStatusInfo)
N/A | event.oldStatusInfo | "changed" | [ThingStatusInfoChangedEvent](https://github.com/eclipse/smarthome/blob/master/bundles/core/org.eclipse.smarthome.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingStatusInfoChangedEvent.java) | Previous ThingStatusInfo of Thing that triggered event (ThingStatusInfo)

</ul>

### But how do I...?
<ul>

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

or (uses the `openhab.py` module)...
</ul>

```python
import openhab
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

#### Send a command to an item:
```python
events.sendCommand("Test_SwitchItem", "ON")
```

#### Send an update to an item:
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

#### Persistence extensions:
```python
from org.eclipse.smarthome.model.persistence.extensions import PersistenceExtensions
PersistenceExtensions.previousState(ir.getItem("Weather_SolarRadiation"), True).state

from org.joda.time import DateTime
PersistenceExtensions.changedSince(ir.getItem("Weather_SolarRadiation"), DateTime.now().minusHours(1))
PersistenceExtensions.maximumSince(ir.getItem("Weather_SolarRadiation"), DateTime.now().minusHours(1)).doubleValue()
```

#### Use [Core & Cloud Actions](https://www.openhab.org/docs/configuration/actions.html#core-actions):
```python
from org.eclipse.smarthome.model.script.actions.Exec import executeCommandLine
executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 3 --max-time 3 http://some.host.name",5000)

from org.eclipse.smarthome.model.script.actions.Audio import playSound
playSound("doorbell.mp3")# using the default audiosink
playSound("my:audio:sink", "doorbell.mp3")# specifying an audiosink

from org.eclipse.smarthome.model.script.actions.Audio import playStream
playStream("http://myAudioServer/myAudioFile.mp3")# using the default audiosink
playStream("my:audio:sink", "http://myAudioServer/myAudioFile.mp3")# specifying an audiosink

from org.eclipse.smarthome.model.script.actions.HTTP import sendHttpPutRequest
sendHttpPutRequest("someURL.com, "application/json", '{"this": "that"}')

from org.openhab.io.openhabcloud import NotificationAction
NotificationAction.sendNotification("someone@someDomain.com","This is the message")
```

#### Use a timer:
See the [`timer_example.py`](https://github.com/OH-Jython-Scripters/openhab2-jython/blob/master/Script%20Examples/timer_example.py) in the Script Examples for examples of using both Jython and the [`createTimer`](https://www.openhab.org/docs/configuration/actions.html#timers) Action.

#### Use an Addon/Bundle Action (binding must be installed):
[Telegram](https://www.openhab.org/addons/actions/telegram/#telegram-actions)
```python
from openhab.actions import Telegram
Telegram.sendTelegram("MyBot", "Test")
```

[Mail](https://www.openhab.org/addons/actions/mail/#mail-actions)
```python
from openhab.actions import Mail
Mail.sendMail("someone@someDomain.com", "This is the subject", "This is the message")
```

#### Logging (the logger can be modified to wherever you want the log to go):
```python
from org.slf4j import Logger, LoggerFactory
log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")
log.debug("JSR223: Test debug log")
log.info("JSR223: Test info log")
log.warn("JSR223: Test warn log")
log.error("JSR223: Test error log")
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

#### View all names in namespace:
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
from openhab import osgi
ruleEngine = osgi.get_service("org.eclipse.smarthome.automation.RuleManager")
ruleEngine.setEnabled(ruleUID, True)# enable rule
ruleEngine.setEnabled(ruleUID, False)# disable rule
```

</ul>
</ul>
