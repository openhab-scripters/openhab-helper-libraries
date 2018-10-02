# Jython scripting for openHAB 2.x

This is a repository of experimental Jython code that can be used 
with the [Eclipse SmartHome](https://www.eclipse.org/smarthome/) platform and [openHAB 2](http://docs.openhab.org/) Jython scripting. 
Also see the [openHAB 2 scripting documentation](http://docs.openhab.org/configuration/jsr223.html).

_NOTE: To use Jython for defining rules, the Experimental Rule Engine add-on must be installed in openHAB 2._

- [Getting Started](#getting-started)
    - [Applications](#applications)
    - [Jython Scripts and Modules](#jython-scripts-and-modules)
    - [File Locations](#file-locations)
- [Component Scripts](#component-scripts)
- [Example Jython Scripts](#example-scripts)
- [Jython Modules](#jython-modules)
- [Defining Rules](#defining-rules)
    - [Raw ESH Automation API](#raw-esh-automation-api)
    - [Using Jython Extensions](#using-jython-extensions)
        - [Rule Trigger Decorators](#rule-trigger-decorators)
- [But how do I...?](#but-how-do-i)

## Getting Started

<ul>

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
In a Linux apt installation, this would be `/etc/openhab2/automation/jsr223/`. For a Linux manual installation, this would default to `/opt/openhab2/conf/automation/jsr223/`.

Some scripts should be loaded before others because of dependencies between the scripts. 
Scripts that implement OH2 components (like trigger types, item providers, etc.) are one example.
I recommend putting these scripts into a subdirectory called `000_Components`. 
The name prefix will cause the scripts in the directory to be loaded first.
I also recommend naming the component files with a "000_" prefix 
because there are currently bugs in the file loading behavior of OH2.

Example:

```text
/etc/openhab2/automation/jsr223
    /000_Components
        000_StartupTrigger.py
    myotherscript.py
```

Jython modules can be placed anywhere but the Python path must be configured to find them.
There are several ways to do this. 
You can add a `-Dpython.path=mypath1:mypath2` to the JVM command line by modifying the OH2 startup scripts.
You can also modify the `sys.path` list in a Jython script that loads early (like a component script).

I put my Jython modules in `/etc/openhab2/lib/python` (Linux apt installation).
Another option is to checkout the GitHub repo in some location and use a directory soft link (Linux) 
from `/etc/openhab2/lib/python/openhab` to the GitHub workspace `lib\openhab` directory.
</ul>
</ul>

## Component Scripts
<ul>

These scripts are located in the `automation/jsr223/scripts/components` subdirectory. 
They should be copied to the `automation/jsr223/components` directory of your openHAB 2 installation to use them. 
The files have a numeric prefix to cause them to be loaded before regular user scripts.

#### Script: [`000_StartupTrigger.py`](automation/jsr223/components/000_StartupTrigger.py)
<ul>

Defines a rule trigger that triggers immediately when a rule is activated. 
This is similar to the same type of trigger in openHAB 1.x.
</ul>

#### Script: [`000_OsgiEventTrigger.py`](automation/jsr223/components/000_OsgiEventTrigger.py)
<ul>

This rule trigger responds to events on the OSGI EventAdmin event bus.
</ul>

#### Script: [`000_DirectoryTrigger.py`](automation/jsr223/components/000_DirectoryTrigger.py)
<ul>

This trigger can respond to file system changes.
For example, you could watch a directory for new files and then process them.

```python
@rule
class DirectoryWatcherExampleRule(object):
    def getEventTriggers(self):
        return [ DirectoryEventTrigger("/tmp", event_kinds=[ENTRY_CREATE]) ]
    
    def execute(self, module, inputs):
        logging.info("detected new file: %s", inputs['path'])
```
</ul>

#### Script [`000_JythonTransform.py`](automation/jsr223/components/000_JythonTransform.py)
<ul>

This script defines a transformation service (identified by "JYTHON") that will process a value using a Jython script. 
This is similar to the Javascript transformer.
</ul>

#### Scripts: Jython-based Providers
<ul>

These components are used to support Thing handler implementations:
* [`000_JythonThingProvider.py`](automation/jsr223/components/000_JythonThingProvider.py)
* [`000_JythonThingTypeProvider.py`](automation/jsr223/components/000_JythonThingTypeProvider.py)
* [`000_JythonBindingInfoProvider.py`](automation/jsr223/components/000_JythonBindingInfoProvider.py)
* [`000_JythonItemProvider.py`](automation/jsr223/scripts/000_JythonItemProvider.py)

</ul>
</ul>

## Example Scripts
<ul>

These scripts show example usage of various scripting features. 
Some of the examples are intended to provide services to user scripts so they have a numeric prefix to force them to load first 
(but after the general purpose components). In order to use them, these scripts will need to be moved to a subdirectory of `/conf/automation/jsr223/`. 
These scripts utilize the modules located in the `/automation/lib/python/openhab/` subdirectory.

#### Script: [`000_ExampleExtensionProvider.py`](Script%20Examples/100_ExampleExtensionProvider.py)
<ul>

This component implements the openHAB extension provider interfaces and can be used to provide symbols to a script
namespace.
</ul>

#### Script: [`000_LogAction.py`](Script%20Examples/000_LogAction.py)
<ul>

This is a simple rule action that will log a message to the openHAB log file.
</ul>

#### Script: [`100_EchoThing.py`](Script%20Examples/100_EchoThing.py)
<ul>

Experimental Thing binding and handler implemented in Jython. (At the time of this writing, 
it requires a small change to the ESH source code for it to work.) 
This simple Thing will write state updates on its input channel to items states linked to the output channel.
</ul>

#### Script: [`000_JythonConsoleCommand.py`](Script%20Examples/000_JythonConsoleCommand.py)
<ul>

This script defines an command extension to the OSGI console. 
The example command prints some Jython  platform details to the console output.
</ul>

#### Script: [`actors.py`](Script%20Examples/actors.py)
<ul>

Shows an example of using the Pykka actors library. The Pykka library must be in the Java classpath.
</ul>

#### Script: [`esper_example.py`](Script%20Examples/esper_example.py)
<ul>

Shows an example of using the Esper component. The 000_Esper.py component script must be installed.
</ul>

#### Script: [`rule_decorators.py`](Script%20Examples/rule_decorators.py)
<ul>

Provides examples of using the trigger-related rule decorators on functions as an alternative to explicit rule and trigger classes.
</ul>

#### Script: [`testing_example.py`](Script%20Examples/testing_example.py)
<ul>

Examples of unit testing.
</ul>

#### Script: [`dirwatcher_example.py`](Script%20Examples/dirwatcher_example.py)
<ul>

Example of a rule that watches for files created in a specified directory.
</ul>

#### Script: [`rule_registry.py`](Script%20Examples/rule_registry.py)
<ul>

This example shows how to retrieve the RuleRegistry service and use it to query rule instances based on tags,
enable and disable rule instances dynamically, and manually fire rules with specified inputs.
</ul>

#### Script: [`timer_example.py`](Script%20Examples/timer_example.py)
<ul>

Example of a rule that shows how to create and cancel a global timer.
</ul>
</ul>

## Jython Modules
<ul>

One of the benefits of Jython over the openHAB Xtext scripts is that you can use the full power of Python packages 
and modules to structure your code into reusable components. 
The following are some initial experiments in that direction.

There are example scripts in the `/Script Examples` directory.

#### Module: [`openhab.rules`](automation/lib/python/openhab/rules.py)
<ul>

The rules module contains some utility functions and a decorator for converting a Jython class into a `SimpleRule`.
The following example shows how the rule decorator is used:

```python
from openhab.rules import rule, addRule
from openhab.triggers import StartupTrigger

@rule
class ExampleRule(object):
    """This doc comment will become the ESH Rule documentation value for Paper UI"""
    def getEventTriggers(self):
        return [ StartupTrigger() ]

    def execute(self, module, inputs):
        self.log.info("rule executed")

addRule(MyRule())
```

The decorator adds the SimpleRule base class and will call either `getEventTriggers` or `getEventTrigger` (the OH1 function) 
to get the triggers, if either function exists. 
Otherwise you can define a constructor and set `self.triggers` to your list of triggers.

The `addRule` function is similar to the `automationManager.addRule` function except 
that it can be safely used in Jython modules (versus scripts).
Since the `automationManager` is different for every script scope 
the `openhab.rules.addRule` function looks up the automation manager for each call.

The decorator also adds a log object based on the name of the rule (`self.log`, can be overridden in a constructor) and 
wraps the event trigger and `execute` functions in a wrapper that will print nicer stack trace information if an exception 
is thrown.
</ul>

#### Module: [`openhab.triggers`](automation/lib/python/openhab/triggers.py)
<ul>

This module includes trigger subclasses and function decorators to simplify Jython rule definitions.

Trigger classes:

* __ItemStateChangeTrigger__
* __ItemStateUpdateTrigger__
* __ItemCommandStrigger__
* __ItemEventTrigger__ (based on "core.GenericEventTrigger")
* __CronTrigger__
* __StartupTrigger__ - fires when rule is activated (implemented in Jython)
* __DirectoryEventTrigger__ - fires when directory contents change (Jython, see related component for more info).
* __ItemAddedTrigger__ - fires when rule is added to the RuleRegistry (implemented in Jython)
* __ItemRemovedTrigger__ - fires when rule is removed from the RuleRegistry (implemented in Jython)
* __ItemUpdatedTrigger__ - fires when rule is updated in the RuleRegistry (implemented in Jython, not a state update!)
* __ChannelEventTrigger__ - fires when a Channel gets an event e.g. from the Astro Binding

&nbsp;

Trigger function decorators:

* __time_triggered__ - run a function periodically
* __item_triggered__ - run a function based on an item event
* __item_group_triggered__ - run a function based on an item group event
</ul>

#### Module: [`openhab.actions`](automation/lib/python/openhab/actions.py)
<ul>

This module discovers action services registered from OH1 or OH2 bundles or add-ons.
The specific actions that are available will depend on which add-ons are installed.
Each action class is exposed as an attribute of the `openhab.actions` Jython module.
The action methods are static methods on those classes 
(don't try to create instances of the action classes).

```python
from openhab.actions import Astro
from openhab.log import logging
from java.util import Date

log = logging.getLogger("org.eclipse.smarthome.automation")

# Use the Astro action class to get the sunset start time.
log.info("Sunrise: %s", Astro.getAstroSunsetStart(Date(2017, 7, 25), 38.897096, -77.036545).time)
```
</ul>

#### Module: [`openhab.log`](automation/lib/python/openhab/log.py)
<ul>

This module bridges the Python standard `logging` module with ESH logging. Example usage:

```python
from openhab.log import logging

logging.info("Logging example from root logger")
logging.getLogger("myscript").info("Logging example from root logger")  
```
</ul>

#### Module: [`openhab.items`](automation/lib/python/openhab/items.py)
<ul>

This module allows runtime creation and removal of items.

```python
import openhab.items

openhab.items.add("_Test", "String")

# later...
openhab.items.remove("_Test")

```
</ul>

#### Module: [`openhab.testing`](automation/lib/python/openhab/testing.py)
<ul>

One of the challenges of ESH/openHAB rule development is verifying that rules are behaving 
correctly and have broken as the code evolves. T
his module supports running automated tests within a runtime context. 
To run tests directly from scripts:

```python
import unittest # standard Python library
from openhab.testing import run_test

class MyTest(unittest.TestCase):
    def test_something(self):
        "Some test code..."

run_test(MyTest) 
```

The module also defines a rule class, `TestRunner` that will run a testcase 
when an switch item is turned on and store the test results in a string item.
</ul>

#### Module: [`openhab.osgi`](automation/lib/python/openhab/osgi/__init__.py)
<ul>

Provides utility function for retrieving, registering and removing OSGI services.

```python
import openhab.osgi

item_registry = osgi.get_service("org.eclipse.smarthome.core.items.ItemRegistry")
```
</ul>

#### Module: [`openhab.osgi.events`](automation/lib/python/openhab/osgi/events.py)
<ul>

Provides an OSGI EventAdmin event monitor and rule trigger. 
This can trigger off any OSGI event (including ESH events). 
_Rule manager events are filtered to avoid circular loops in the rule execution._

```python
class ExampleRule(SimpleRule):
    def __init__(self):
        self.triggers = [ openhab.osgi.events.OsgiEventTrigger() ]
            
    def execute(self, module, inputs):
        event = inputs['event']
        # do something with event
```
</ul>

#### Module: [`openhab.jsr223`](automation/lib/python/openhab/jsr223.py)
<ul>

One of the challenges of JSR223 scripting with Jython is that Jython modules imported 
into scripts do not have direct access to the JSR223 scope types and objects. 
This module allows imported modules to access that data. Example usage:

```python
# In Jython module, not script...
from openhab.jsr223.scope import events

def update_data(data):
    events.postUpdate("TestString1", str(data))
```
</ul>

#### Module: [`openhab`](automation/lib/python/openhab/__init__.py)
<ul>

This module (really a Python package) patches the default scope `items` object 
so that items can be accessed as if they were attributes (rather than a dictionary).

It can also be used as a module for registering global variables that will outlive script reloads.

```python
import openhab

print items.TestString1
```

Note that this patch will be applied when any module in the `openhab` package is loaded.
</ul>
</ul>

## Defining Rules
<ul>

One of the primary use cases for the JSR223 scripting is to define rules 
for the [Eclipse SmartHome (ESH) rule engine](http://www.eclipse.org/smarthome/documentation/features/rules.html).

The ESH rule engine structures rules as _Modules_ (Triggers, Conditions, Actions). 
Jython rules can use rule Modules that are already present in ESH, and can define new Modules that can be used outside of JSR223 scripting. 
Take care not to confuse ESH Modules with Jython modules.

### Raw ESH Automation API
<ul>

Using the raw ESH API, the simplest rule definition would look something like:

```python
scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleSimple")

class MyRule(SimpleRule):
def __init__(self):
    self.triggers = [
            Trigger("MyTrigger", "core.ItemStateUpdateTrigger", 
                Configuration({ "itemName": "TestString1"}))
    ]
    
def execute(self, module, input):
    events.postUpdate("TestString2", "some data")

automationManager.addRule(MyRule())
```

Note: trigger names must be unique within the scope of a rule instance. 

Post OH 2.4.0 snapshot build 1319, the rule definition would look like:

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

This can be simplified with some extra Jython code, which we'll see later. 
First, let's look at what's happening with the raw functionality.

When a Jython script is loaded it is provided with a _JSR223 scope_ that predefines a number of variables. 
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

To simplify rule creation even further, Jython can be used to wrap the raw ESH API. 
The current experimental wrappers include trigger-related classes so the previous example becomes:

```python
# ... preset calls

from openhab.triggers import ItemStateUpdateTrigger

class MyRule(SimpleRule):
    def __init__(self):
        self.triggers = [ ItemStateUpdateTrigger("TestString1") ]
        
    # rest of rule ...
```

This removes the need to know the internal ESH trigger type strings, 
define trigger names and to know configuration dictionary requirements.

#### Rule Trigger Decorator
<ul>

To make rule creation _even simpler_, `openhab.triggers` defines a function decorator that can be 
used to create a rule with triggers defined similarly to how it is done in the Rules DSL. 

```python
from openhab.triggers import when, rule

@rule("This is the name of a test rule",
    when("Item Test_Switch_1 received command OFF"),
    when("Item Test_Switch_2 received update ON"),
    when("Member of gMotion_Sensors changed to OFF"),
    when("Descendent of gContact_Sensors changed to ON"),
    when("Thing kodi:kodi:familyroom changed"),# Thing statuses cannot currently be used in triggers
    when("Channel astro:sun:local:eclipse#event triggered START"),
    when("System started"),# 'System shuts down' cannot currently be used as a trigger
    when("55 55 5 * * ?")
)
def testFunction(event):
    if items["Test_Switch_3"] == OnOffType.ON:
        events.postUpdate("TestString1", "The test rule has been executed!")
```

Notice there is no explicit preset import and the generated rule is registered automatically with the `HandlerRegistry`. 
Note: 'Descendent of' is similar to 'Member of', but will trigger on any sibling non-group Item (think group_item.allMembers()).

The `items` object is from the default scope and allows access to item state. 
If the function needs to send commands or access other items, it can be done using the `events` scope object. 
When the function is called it is provided the event instance that triggered it.
The specific trigger data depends on the event type.
For example, the `ItemStateChangedEvent` event type has `itemName`, `itemState`, and `oldItemState` attributes.
</ul>
</ul>

## But how do I...?
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
items["My_Item")
```
<ul>

or (uses the `openhab.py` module)...
</ul>

```python
import openhab
items.My_Item
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

#### Iterate through group members:
```python
for lightItem in ir.getItem("Group_of_lights").getMembers():
    # do stuff
```

#### Persistence extensions:
```python
from org.eclipse.smarthome.model.persistence.extensions import PersistenceExtensions
PersistenceExtensions.previousState(ir.getItem("Weather_SolarRadiation"), True).state

import org.joda.time
PersistenceExtensions.changedSince(ir.getItem("Weather_SolarRadiation"), DateTime.now().minusHours(1))
PersistenceExtensions.maximumSince(ir.getItem("Weather_SolarRadiation"), DateTime.now().minusHours(1)).state
```

#### executeCommandLine (similar for using other script Actions):
```python
from org.eclipse.smarthome.model.script.actions.Exec import executeCommandLine
executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 3 --max-time 3 http://some.host.name",5000)
```

#### Logging (the logger can be modified to wherever you want the log to go):
```python
from org.slf4j import Logger, LoggerFactory
log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")
log.debug("JSR223: Test log")
```

#### Convert a value to a state for comparison:
```python
items["String_Item"] == StringType("test string")
items["Switch_Item"] == OnOffType.ON
items["Number_Item"] > DecimalType(5)
items["Contact_Item"] == OpenClosedType.OPEN
items["Some_Item"] != UnDefType.NULL
```
    
#### Convert DecimalType to an integer or float for arithmetic:
```python
int(str(items["Number_Item1"])) + int(str(items["Number_Item2"])) > 5
float(str(items["Number_Item"])) + 5.5555 > 55.555
```

#### Pause a thread:
```python
from time import sleep
sleep(5)# the unit is seconds, so use 0.5 for 500 milliseconds
```

#### Use a timer:

see the [`timer_example.py](#script-timer_examplepy) in the example scripts
