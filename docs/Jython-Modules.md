[[Home]](README.md)

## Jython Modules

One of the benefits of Jython over the openHAB Xtext scripts is that you can use the full power of Python packages 
and modules to structure your code into reusable components. 
The following are some initial experiments in that direction.
In order to use them, these modules will need to be copied to a subdirectory of `/automation/lib/python/`.

#### Modifying Modules

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

#### Custom Modules

Custom modules and packages can also be added into `/automation/lib/python/`. Modules do not have the same scope as scripts, but this can be remedied by importing `scope` from the `jsr223` module. This will allow for things like accessing the itemRegistry:
```
from openhab.jsr223 import scope
scope.itemRegistry.getItem("MyItem")
```

When using the settings from the [Quick Start Guide](https://github.com/OH-Jython-Scripters/openhab2-jython/blob/master/README.md#quick-start-guide), these modules need to be copied to a subdirectory of `/automation/lib/python/`.

#### Module: [`openhab.triggers`](../automation/lib/python/openhab/triggers.py)
<ul>

This module includes trigger subclasses and function decorators to simplify Jython rule definitions.

Trigger classes fr wrapping Automation API (see [Using Jython extensions](Defining-Rules.md#using-jython-extensions)):

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

Trigger function decorator (see openhab.rules module for the [rule decorator](#module-openhabrules) that is used in conjunction with the trigger decorator:

* __@when("Item Test_Switch_1 received command OFF")__
* __@when("Item Test_Switch_2 received update ON")__
* __@when("Member of gMotion_Sensors changed to OFF")__
* __@when("Descendent of gContact_Sensors changed to ON")__
* __@when("Thing kodi:kodi:familyroom changed")__# Thing statuses cannot currently be used in triggers
* __@when("Channel astro:sun:local:eclipse#event triggered START")__
* __@when("System started")__# 'System shuts down' cannot currently be used as a trigger, and 'System started' needs to be updated to work with Automation API updates
* __@when("55 55 5 * * ?")__

</ul>

#### Module: [`openhab.rules`](../automation/lib/python/openhab/rules.py)
<ul>

The rules module contains some utility functions and a decorator that can 1) convert a Jython class into a `SimpleRule`, 2) decorate the trigger decorator (@when) to create a `SimpleRule`.
The following example shows how the rule decorator is used to decorate a class:

```python
from openhab.rules import rule
from openhab.triggers import StartupTrigger

@rule("My example rule")
class ExampleRule(object):
    """This doc comment will become the ESH Rule documentation value for Paper UI"""
    def getEventTriggers(self):
        return [ StartupTrigger().trigger ]

    def execute(self, module, inputs):
        self.log.info("rule executed")
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

The following example shows how the rule decorator is used to decorate the trigger decorator:

```python
from openhab.rules import rule
from openhab.triggers import when

@rule("My example rule")
@when("Time cron 0/10 * * * * ?")
def exampleDecoratedCronRule(event):
    # do stuff
```

</ul>

#### Module: [`openhab.actions`](../automation/lib/python/openhab/actions.py)
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

#### Module: [`openhab.log`](../automation/lib/python/openhab/log.py)
<ul>

This module bridges the Python standard `logging` module with ESH logging. Example usage:

```python
from openhab.log import logging

logging.info("Logging example from root logger")
logging.getLogger("myscript").info("Logging example from root logger")  
```
</ul>

#### Module: [`openhab.items`](../automation/lib/python/openhab/items.py)
<ul>

This module allows runtime creation and removal of items.

```python
import openhab.items

openhab.items.add("_Test", "String")

# later...
openhab.items.remove("_Test")

```
</ul>

#### Module: [`openhab.testing`](../automation/lib/python/openhab/testing.py)
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

#### Module: [`openhab.osgi`](../automation/lib/python/openhab/osgi/__init__.py)
<ul>

Provides utility function for retrieving, registering and removing OSGI services.

```python
import openhab.osgi

item_registry = osgi.get_service("org.eclipse.smarthome.core.items.ItemRegistry")
```
</ul>

#### Module: [`openhab.osgi.events`](../automation/lib/python/openhab/osgi/events.py)
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

#### Module: [`openhab.jsr223`](../automation/lib/python/openhab/jsr223.py)
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

#### Module: [`openhab`](../automation/lib/python/openhab/__init__.py)
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