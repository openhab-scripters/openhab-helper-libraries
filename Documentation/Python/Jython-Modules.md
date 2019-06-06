[[Jython Home]](README.md)

## Modules

One of the benefits of Jython over the openHAB rule DSL scripts is that you can use the full power of Python packages and modules to structure your code into reusable components. 
When using the instructions in the [Quick Start Guide](/Docs/README.md#quick-start-guide), these modules will be located in `/automation/lib/python/`.
They can be located anywhere, but the Python path must be configured to find them.
There are several ways to do this: 
1) Append the path to the `python.path` used in the EXTRA_JAVA_OPTS, separated woth a colon in Linux and a semicolon in Windows, e.g. `-Dpython.path=mypath1:mypath2`. 
2) Modify the `sys.path` list in a Jython script that loads early (like a component script).
3) Add a symlink in `/automation/lib/python/personal/`, which is already in the Python path, to the module or a package that contains it.

#### Modifying Modules

Changes to a module will not take effect until all other modules and scripts that have imported it have been reloaded. 
Restarting OH will remedy this, but another option is to use the reload() function:

```
import myModule
reload(myModule)
import myModule
```
If using imports like `from core.triggers import when`, or if the module is in a package, you will need to use:
```
import sys
from core.triggers import when
reload(sys.modules['core.triggers'])
from core.triggers import when
```
... or import the whole module to reload it...
```
from core.triggers import when
import core.triggers
reload(core.triggers)
from core.triggers import when
```

#### Custom Modules

Custom modules and packages should be placed in `/automation/lib/python/personal/`. 
Modules do not have the same scope as scripts, but this can be remedied by importing `scope` from the `jsr223` module. 
This will allow for things like accessing the itemRegistry:
```
from core.jsr223 import scope
scope.itemRegistry.getItem("MyItem")
```

#### Module: [`core.triggers`](../Core/automation/lib/python/core/triggers.py)
<ul>

This module includes trigger subclasses and function decorators to simplify Jython rule definitions.

Trigger classes for wrapping Automation API (see [Using Jython extensions](Defining-Rules.md#using-jython-extensions)):

* __ItemStateChangeTrigger__
* __ItemStateUpdateTrigger__
* __ItemCommandTrigger__
* __ItemEventTrigger__ (based on "core.GenericEventTrigger")
* __CronTrigger__
* __StartupTrigger__ - fires when rule is activated (implemented in Jython)
* __DirectoryEventTrigger__ - fires when directory contents change (Jython, see related component for more info)
* __ItemAddedTrigger__ - fires when rule is added to the RuleRegistry (implemented in Jython)
* __ItemRemovedTrigger__ - fires when rule is removed from the RuleRegistry (implemented in Jython)
* __ItemUpdatedTrigger__ - fires when rule is updated in the RuleRegistry (implemented in Jython, not a state update!)
* __ChannelEventTrigger__ - fires when a Channel gets an event e.g. from the Astro Binding

&nbsp;

Trigger function decorator (see the `core.rules` module for the [rule decorator](#module-corerules) that is used in conjunction with the trigger decorator):

* __@when("Item Test_Switch_1 received command OFF")__
* __@when("Item Test_Switch_2 received update ON")__
* __@when("Member of gMotion_Sensors changed to OFF")__
* __@when("Descendent of gContact_Sensors changed to ON")__
* __@when("Thing kodi:kodi:familyroom changed")__# Thing statuses cannot currently be used in triggers
* __@when("Channel astro:sun:local:eclipse#event triggered START")__
* __@when("System started")__# 'System started' requires S1566 or newer, and 'System shuts down' is not available
* __@when("55 55 5 * * ?")__

&nbsp;

As a workaround for 'System started', add the rule function directly to the script. Here is an example that can be used with the function from the [`hello_world.py`](/Script%20Examples/Python/hello_world.py) example script...
```python
helloWorldCronDecorators(None)
```
</ul>

#### Module: [`core.rules`](../../Core/automation/lib/python/core/rules.py)
<ul>

The rules module contains some utility functions and a decorator that can 1) convert a Jython class into a `SimpleRule`, 2) decorate the trigger decorator (@when) to create a `SimpleRule`.
The following example shows how the rule decorator is used to decorate a class:

```python
from core.rules import rule
from core.triggers import StartupTrigger

@rule("My example rule")
class ExampleRule(object):
    """This doc comment will become the ESH Rule documentation value for Paper UI"""
    #def __init__(self):
    #    self.triggers = [ StartupTrigger().trigger ]
    
    def getEventTriggers(self):
        return [ StartupTrigger().trigger ]

    def execute(self, module, inputs):
        self.log.info("rule executed")
```
The `rule` decorator adds the SimpleRule base class and will call `getEventTriggers` to get the triggers, or you can define a constructor and set `self.triggers` to your list of triggers (commented out in the example). 
The `addRule` function is similar to the `automationManager.addRule` function, except that it can be safely used in modules (versus scripts).
Since the `automationManager` is different for every script scope, the `core.rules.addRule` function looks up the automation manager for each call. 
The decorator adds a log object based on the name of the decorated class or function, but `self.log` can be overridden in a constructor. 
It also wraps the event trigger and `execute` functions in a wrapper that will print nicer stack trace information, if an exception is thrown. 

The following example shows how the rule decorator is used to decorate the trigger decorator:

```python
from core.rules import rule
from core.triggers import when

@rule("My example rule")
@when("Time cron 0/10 * * * * ?")
def exampleDecoratedCronRule(event):
    exampleDecoratedCronRule.log("Log from example rule")
```

</ul>

#### Module: [`core.actions`](../../Core/automation/lib/python/core/actions.py)
<ul>

This module discovers action services registered from OH1 or OH2 bundles or add-ons.
The specific actions that are available will depend on which add-ons are installed.
Each action class is exposed as an attribute of the `core.actions` module.
The action methods are static methods on those classes (don't try to create instances of the action classes).

```python
from core.actions import Astro
from core.log import logging, LOG_PREFIX
from java.util import Date

log = logging.getLogger(LOG_PREFIX + ".astro_test")

# Use the Astro action class to get the sunset start time.
log.info("Sunrise: {}".format(Astro.getAstroSunsetStart(Date(2017, 7, 25), 38.897096, -77.036545).time))
```
</ul>

#### Module: [`core.log`](../../Core/automation/lib/python/core/log.py)
<ul>

This module bridges the [Python standard `logging` module](https://docs.python.org/2/library/logging.html) with OH logging. 
The `configuration` module also provides a `LOG_PREFIX` variable, which is used throughout the core modules and scripts including the `log` module. 
LOG_PREFIX can be modified based on personal preference, which will change the default logger. 
Example usage:

```python
from core.log import logging, LOG_PREFIX

logging.critical("Logging example from root logger [TRACE]")
logging.debug("Logging example from root logger [DEBUG]")
logging.info("Logging example from root logger [INFO]")
logging.warning("Logging example from root logger [WARN]")
logging.error("Logging example from root logger [ERROR]")

logging.getLogger(LOG_PREFIX + ".test_logging_script").info("Logging example from logger, using text appended to LOG_PREFIX")

log = logging.getLogger(LOG_PREFIX + ".test_logging_script")
log.info("Logging example from logger, using text appended to LOG_PREFIX")
```

</ul>

#### Module: [`core.items`](../../Core/automation/lib/python/core/items.py)
<ul>

This module allows runtime creation and removal of items.
It will also remove any links from an Item before it is removed.
Requires the JythonItemProvder and JythonItemChannelLinkProvider component scripts.

```python
import core.items

core.items.add_item("Test_String", item_type="String", label="Test String")

# later...
core.items.remove_item("Test_String")

```
</ul>

#### Module: [`core.links`](../../Core/automation/lib/python/core/links.py)
<ul>

This module allows runtime creation and removal of links.
Requires the JythonItemChannelLinkProvider component script.
Take a look at the [Community OWM script](../../Community/OpenWeatherMap/automation/jsr223/python/community/openweathermap/owm_daily_forecast.py) for an example usage.

```python
import core.links

core.links.add_link("Kodi_Control", channel_uid="kodi:kodi:familyroom:control")

# later...
core.link.remove_link("Kodi_Control")

```
</ul>

#### Module: [`core.date`](../../Core/automation/lib/python/core/date.py)
<ul>

This module includes functions for converting between various datetime types used in openHAB and Jython, several functions for determining durations, and a function to format datetimes. 
The preferred datetime type is `ZonedDateTime` from `java.time` as `org.joda.DateTime` is depreciated beyond Java 8. The usage of `ZonedDateTime` is similar to the Joda Time `DateTime` type. 
The Java doc for it can be found [here](https://docs.oracle.com/javase/8/docs/api/java/time/ZonedDateTime.html).

All of the functions in this module accept any mix of the following datetime types:
`java.time.ZonedDateTime`, `java.time.LocalDateTime`, `java.util.Calendar`, `java.util.Date`, `org.joda.DateTime`, `datetime.datetime` (Python), `org.eclipse.smarthome.core.library.types.DateTimeType`, and `org.openhab.core.library.types.DateTimeType`.

The conversion functions provided are:

* __to_java_zoneddatetime(datetime)__  - returns a `java.time.ZonedDateTime` value
* __to_java_calendar(datetime)__ - returns a `java.util.Calendar` value
* __to_joda_datetime(datetime)__ - returns a `org.joda.DateTime` value
* __to_python_datetime(datetime)__ - returns Python's built-in `datetime.datetime` value

&nbsp;

The following functions can be used to determine the duration between two datetimes and will return an `int`. They will return a negative value if the first datetime is after the second:

* __seconds_between(datetime_from, datetime_to)__ will return the number of whole seconds between the two times
* __minutes_between(datetime_from, datetime_to)__ will return the number of whole minutes
* __hours_between(datetime_from, datetime_to)__ will return the number of whole hours
* __days_between(datetime_from, datetime_to, calendar_days=False)__ will return the number of whole days (24 hour intervals by default) or calendar days (if that argument is set to True)

&nbsp;

There is also a function to format a datetime as a string. This is useful for setting `DateTimeItem` values. It is not neccesary to supply a format string, the default is identical to the format used in openHAB.
&nbsp;
For information on format codes to use in the `format_string`, see the documentation for [`java.time.format.DateTimeFormatter`](https://docs.oracle.com/javase/8/docs/api/java/time/format/DateTimeFormatter.html).

* __format_date(datetime[, format_string])__

&nbsp;

</ul>

#### Module: [`core.testing`](../../Core/automation/lib/python/core/testing.py)
<ul>

One of the challenges of ESH/openHAB rule development is verifying that rules are behaving correctly and haven't broken as the code evolves. 
This module supports running automated tests within a runtime context. 
To run tests directly from scripts:

```python
import unittest # standard Python library
from core.testing import run_test

class MyTest(unittest.TestCase):
    def test_something(self):
        "Some test code..."

run_test(MyTest) 
```

The module also defines a rule class, `TestRunner` that will run a testcase 
when an switch item is turned on and store the test results in a string item.
</ul>

#### Module: [`core.osgi`](../../Core/automation/lib/python/core/osgi/__init__.py)
<ul>

Provides utility function for retrieving, registering and removing OSGI services.

```python
import core.osgi

item_registry = osgi.get_service("org.eclipse.smarthome.core.items.ItemRegistry")
```
</ul>

#### Module: [`core.osgi.events`](../../Core/automation/lib/python/core/osgi/events.py)
<ul>

Provides an OSGI EventAdmin event monitor and rule trigger. 
This can trigger off any OSGI event (including ESH events). 
_Rule manager events are filtered to avoid circular loops in the rule execution._

```python
class ExampleRule(SimpleRule):
    def __init__(self):
        self.triggers = [ core.osgi.events.OsgiEventTrigger() ]
            
    def execute(self, module, inputs):
        event = inputs['event']
        # do something with event
```
</ul>

#### Module: [`core.jsr223`](../../Core/automation/lib/python/core/jsr223.py)
<ul>

One of the challenges of scripted automation with Jython is that modules imported into scripts do not have direct access to the JSR223 scope types and objects. 
This module allows imported modules to access that data. 
Example usage:

```python
# In Jython module, not script...
from core.jsr223.scope import events

def update_data(data):
    events.postUpdate("TestString1", str(data))
```
</ul>

#### Module: [`core`](../../Core/automation/lib/python/core/__init__.py)
<ul>

This module (really a Python package) patches the default scope `items` object so that items can be accessed as if they were attributes (rather than a dictionary).
It can also be used as a module for registering global variables that will outlive script reloads.

```python
import core

print items.TestString1
```

Note that this patch will be applied when any module in the `core` package is loaded.
</ul>
