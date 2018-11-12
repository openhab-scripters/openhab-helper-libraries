[[Home]](README.md)

## Defining Rules

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
define trigger names, and to know configuration dictionary requirements.

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
@when("Descendent of gContact_Sensors changed to ON")# Similar to 'Member of', but will create a trigger for each non-group sibling Item (think group_item.allMembers())
@when("Thing kodi:kodi:familyroom changed")# ThingStatusInfo (from <status> to <status>) cannot currently be used in triggers
@when("Channel astro:sun:local:eclipse#event triggered START")
@when("System started")# 'System shuts down' cannot currently be used as a trigger, and 'System started' needs to be updated to work with Automation API updates
@when("Time cron 55 55 5 * * ?")
def testFunction(event):
    if items["Test_Switch_1"] == OnOffType.ON:
        events.postUpdate("Test_String_1", "The test rule has been executed!")
```

Notice there is no explicit preset import, and the generated rule is registered automatically with the `HandlerRegistry`. 

</ul>