# openHAB 2.x: JSR223 Jython Code

This is a repository of experimental Jython code that can be used with the SmartHome platform and openHAB 2.x (after the pending [PR](https://github.com/eclipse/smarthome/pull/1783) has been merged).

## Applications

The JSR223 scripting extensions can be used for general scripting purposes, including defining rules and associated SmartHome rule "modules" (triggers, conditions, actions). Some possible applications include integration testing of complex rule behaviors or prototyping new OH2/ESH functionality.

The scripting can be used for other purposes like automated integration testing or to access the OSGI framework (using or creating services, for example).

## Defining Rules

One the primary use cases for the JSR223 scripting is to define rules for the [Eclipse SmartHome (ESH) rule engine](http://www.eclipse.org/smarthome/documentation/features/rules.html).

The ESH rule engine structures rules as _modules_ (triggers, conditions, actions). Jython rules can use rule modules that are already present in ESH and can define new modules that can be used outside of JSR223 scripting.

### Rules: Raw ESH API

Using the raw ESH API, the simplest rule definition would look something like:

```python
ScriptExtension.importPreset("RuleSupport")
ScriptExtension.importPreset("RuleSimple")

class MyRule(SimpleRule):
    def __init__(self):
        self.triggers = [
            Trigger("MyTrigger", "core.ItemStateUpdateTrigger", 
                    Configuration({ "itemName": "TestString1"}))
        ]
        
    def execute(self, module, input):
        events.postUpdate("TestString2", "some data")

HandlerRegistry.addRule(MyRule())
```

This can be simplified with some extra Jython code, which we'll see later. First, let's look at what's happening with the raw functionality.

When a Jython script is loaded it is provided with a _JSR223 scope_ that predefines a number of variables. These include the most commonly used core types and values from ESH (e.g., State, Command, OnOffType, etc.). This means you don't need a Jython import statement to load them.

For defining rules, additional symbols must be defined. Rather than using a Jython import (remember, JSR223 support is for other languages too), these additional symbols are imported using:

```python
ScriptExtension.importPreset("RuleSupport")
ScriptExtension.importPreset("RuleSimple")
```

`ScriptExtension` is one of the default scope types. The RuleSimple preset defines the `SimpleRule` base class.  This base class implements a rule with a single custom ESH Action associated with the `execute` function. The list of rule triggers are provided by the triggers attribute of the rule instance.

The trigger in this example is an instance of the `Trigger` class. The constructor arguments define the trigger, the trigger type string and a configuration.

The `events` variable is part of the default scope and supports access to the ESH event bus (posting updates and sending commands). Finally, to register the rule with the ESH rule engine it must be added to the `HandlerRegistry`. This will cause the triggers to be activated and the rule will fire when the TestString1 item is updated.

### Rules: Using Jython extensions

To simplify rule creation even further, Jython can be used to wrap the raw ESH API. The current experimental wrappers include trigger-related classes so the previous example becomes:

```python
# ... preset calls

from openhab.triggers import ItemStateUpdateTrigger

class MyRule(SimpleRule):
    def __init__(self):
        self.triggers = [ ItemStateUpdateTrigger("TestString1") ]
        
    # rest of rule ...
```
This removes the need to know the internal ESH trigger type strings, define trigger names and to know configuration dictionary requirements.

#### Rule Decorators

To make rule creation _even simpler_, `openhab.triggers` defines function decorators. To define a function that will be triggered periodically, the entire script looks like:

```python
from openhab.triggers import time_triggered, EACH_MINUTE

@time_triggered(EACH_MINUTE)
def my_periodic_function():
 	events.postUpdate("TestString1", somefunction())
```
Notice there is no explicit preset import and the generated rule is registered automatically with the `HandlerRegistry`. Another example...

```python
from openhab.triggers import item_triggered

@item_triggered("TestString1", result_item_name="TestString2")
def my_item_function():
	if len(items['TestString1']) > 100:
		return "TOO BIG!"
```
The `item_triggered` decorator creates a rule that will trigger on changes to TestString1. The function result will be posted to TestString2. The `items` object is from the default scope and allows access to item state. If the function needs to send commands or access other items, it can be  done using the `events` scope object. 

## Component Scripts

These scripts are in the `scripts/components` subdirectory. They should be copied to the `automation/jsr223` directory of your openHAB 2 installation to use them.

### Script: `StartupTrigger.py`

Defines a rule trigger that triggers immediately when a rule is activated. This is similar to the same type of trigger in openHAB 1.x.

### Script: `OsgiEventTrigger.py`

This rule trigger responds to events on the OSGI EventAdmin event bus.

### Script: `LogAction.py`

This is a simple rule action that will log a message to the openHAB log file.

### Script `JythonTransform.py`

This script defines a transformation service (identified by "JYTHON") that will process a value using a Jython script. This is similar to the Javascript transformer.

### Script: `JythonConsoleCommand.py`

This script defines an command extension to the OSGI console. The example command prints some Jython  platform details to the console output.

### Scripts: Jython-based Providers

   * `JythonThingProvider.py`
   * `JythonThingTypeProvider.py`
   * `JythonBindingInfoProvider.py`
   * `JythonItemProvider.py`
   
These components are used to support Thing handler implementations.

### Script: `EchoThing.py`

Experimental Thing binding and handler implemented in Jython. (At the time of this writing, it requires a small change to the ESH source code for it to work.) This simple Thing will write state updates on its input channel to items states linked to the output channel.

## Jython Modules

One of the benefits of Jython over the openHAB Xtext scripts is that you can use the full power of Python packages and modules to structure your code into reusable components. The following are some initial experiments in that direction.

There are example scripts in the `scripts/examples` subdirectory.

### Module: `openhab.log`

This module bridges the Python standard `logging` module with ESH logging. Example usage:

```python
from openhab.log import logging

logging.info("Logging example from root logger")
logging.getLogger("myscript").info("Logging example from root logger")  
```

### Module: `openhab.triggers`

This module includes trigger subclasses and function decorators to make simple rule definition very simple.

Trigger classes:

* __ItemStateChangeTrigger__
* __ItemStateUpdateTrigger__
* __ItemCommandStrigger__
* __ItemEventTrigger__ (based on "core.GenericEventTrigger")
* __CronTrigger__
* __StartupTrigger__ - fires when rule is activated (implemented in Jython)

Trigger function decorators:

* __time_triggered__ - run a function periodically
* __item_triggered__ - run a function based on an item event

### Module: `openhab.items`

This module allows runtime creation and removal of items.

```python
import openhab.items

openhab.items.add("_Test", "String")

# later...
openhab.items.remove("_Test")

```

### Module: `openhab.testing`

One of the challenges of ESH/openHAB rule development is verifying that rules are behaving correctly and have broken as the code evolves. This module supports running automated tests within a runtime context. To run tests directly from scripts:

```python
import unittest # standard Python library
from openhab.testing import run_test

class MyTest(unittest.TestCase):
	def test_something(self):
		"Some test code..."

run_test(MyTest) 
```

The module also defines a rule class, `TestRunner` that will run a testcase when an switch item is turned on and store the test results in a string item.

### Module: `openhab.osgi`

Provides utility function for retrieving, registering and removing OSGI services.

```python
import openhab.osgi

item_registry = osgi.get_service("org.eclipse.smarthome.core.items.ItemRegistry")
```

### Module: `openhab.osgi.events`

Provides an OSGI EventAdmin event monitor and rule trigger. This can trigger off any OSGI event (including ESH events). _Rule manager events are filtered to avoid circular loops in the rule execution._

```python
class ExampleRule(SimpleRule):
    def __init__(self):
        self.triggers = [ openhab.osgi.events.OsgiEventTrigger() ]
            
    def execute(self, module, inputs):
        event = inputs['event']
        # do something with event
```

### Module: `openhab.jsr223`

One of the challenges of JSR223 scripting with Jython is that Jython modules imported into scripts do not have direct access to the JSR223 scope types and objects. This module allows imported modules to access that data. Example usage:

```python
# In Jython module, not script...
from openhab.jsr223.scope import events

def update_data(data):
	events.postUpdate("TestString1", str(data))
```

### Module: `openhab`

This module (really a Python package) patches the default scope `items` object so that items can be accessed as if they were attributes (rather than a dictionary).

```python
import openhab

print items.TestString1
```

Note that this patch will be applied when any module in the `openhab` package is loaded.
