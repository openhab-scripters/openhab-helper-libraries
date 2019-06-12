[[Home]](../README.md)

### Applications

The extensions can be used for general scripting purposes, including defining rules and scripted Actions and Conditions using JavaScript for openHAB Scripted Automation.

### Rules: Raw API

Simplified with some extra JavaScript code found in `/automation/lib/javascript/core/rules.js`:

```JavaScript
'use strict';

var OPENHAB_CONF = Java.type("java.lang.System").getenv("OPENHAB_CONF");
load(OPENHAB_CONF+'/automation/lib/javascript/core/rules.js');

JSRule({
    name: "My JS Rule",
    description: "Line:"+__LINE__,
    triggers: [
        TimerTrigger("0/15 * * * * ?")//Enable/Disable Rule
    ],
    execute: function( module, input){
        print("################ module:", module);
        postUpdate(getItem("testItemSwitch"), ON);
        sendCommand(getItem("testItemSwitch"), OFF);
    }
});
```

`/automation/lib/javascript/core/utils.js` contains more simplifying and helping functions.

`/automation/lib/javascript/core/PersistenceExtensions.js` contains more simplifying PersistenceExtensions functions.

`/automation/lib/javascript/core/triggers.js` contains trigger functions.

`Script Examples/Javascript/ActionExamples.js` contains examples for default actions like PersistenceExtensions, HTTP, Ping, Audio, Voice, ThingAction.

`Script Examples/Javascript/ItemTest.js` contains examples for testing Items and Groups.
