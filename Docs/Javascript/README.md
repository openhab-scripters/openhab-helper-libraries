# openHAB 2.x: JSR223 JavaScript Code since 2.4

This is a repository of very experimental JavaScript code that can be used with the SmartHome platform and openHAB 2.x.

## Applications

The JSR223 scripting extensions can be used for general scripting purposes, including defining rules with JavaScript Code for openHAB 2 JSR223 Scripting.

## Installation

Copy Files into /etc/openhab2/automation/jsr223

## Defining Rules

OpenHAB 2 JSR223 Scripting Documentation: [JSR223 Scripting and Rule Support](https://www.openhab.org/docs/configuration/jsr223.html#jsr223-scripting).

Further links and information: [openHAB 1 Scripted Rule Support](https://github.com/eclipse/smarthome/wiki/Scripted-Rule-Support).

### Rules: Raw ESH API

Simplified with some extra JavaScript Code, found in `jslib/JSRule.js`:

```JavaScript
'use strict';

var OPENHAB_CONF = Java.type("java.lang.System").getenv("OPENHAB_CONF");
load(OPENHAB_CONF+'/automation/jsr223/jslib/JSRule.js');

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

`jslib/helper.js` contains more simplifying and helping functions.

`jslib/PersistenceExtensions.js` contains more simplifying PersistenceExtensions functions.

`jslib/triggersAndConditions.js` contains trigger functions.

`ActionExamples.js` contains examples for default actions like PersistenceExtensions, HTTP, Ping, Audio, Voice, ThingAction.

`itemTest.js` contains examples for testing Items and Groups.

 

