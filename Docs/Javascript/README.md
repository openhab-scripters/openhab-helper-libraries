# openHAB 2.x: JSR223 JavaScript Code since 2.4

This is a repository of very experimental JavaScript code that can be used with the SmartHome platform and openHAB 2.x.

## Applications

The JSR223 scripting extensions can be used for general scripting purposes, including defining rules with JavaScript Code for openHAB 2 JSR223 Scripting.

## Installation

Download the contents of this repository and, using the openHAB account, copy the _contents_ of the `/Core/` directory into `/etc/openhab2/` (package repository OH install, like openHABian) or `/opt/openhab2/conf/` (default manual OH install). 
This will create a directory structure as described in [File Locations](../Python/Getting-Started.md#file-locations), and will include all of the Core files, including a startup delay script that ensures OH is started completely before loading other scripts.
If you are not also setting up Javascript and Groovy, remove the directories for them under `/automation/jsr223/` and `/automation/lib/`.

## Defining Rules

OpenHAB 2 JSR223 Scripting Documentation: [JSR223 Scripting and Rule Support](https://www.openhab.org/docs/configuration/jsr223.html#jsr223-scripting).

Further links and information: [openHAB 1 Scripted Rule Support](https://github.com/eclipse/smarthome/wiki/Scripted-Rule-Support).

### Rules: Raw ESH API

Simplified with some extra JavaScript Code, found in `jslib/JSRule.js`:

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
