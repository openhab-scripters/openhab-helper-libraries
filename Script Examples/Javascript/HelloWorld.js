'use strict';

var OPENHAB_CONF = Java.type("java.lang.System").getenv("OPENHAB_CONF");
load(OPENHAB_CONF+'/automation/lib/javascript/core/rules.js');
var me = "HelloWorld.js";

JSRule({
    name: "Javascript Hello World (GenericCronTrigger raw API with JS helper libraries)",
    description: "This is an example Jython cron rule using the raw API",
    triggers: [
        TimerTrigger("0/10 * * * * ?")
    ],
    execute: function( module, inputs){
        logInfo("Hello World!");
    }
});
