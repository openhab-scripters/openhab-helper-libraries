'use strict';

load(Java.type("java.lang.System").getenv("OPENHAB_CONF")+'/automation/lib/javascript/core/init.js');

var rules = require('rules');
var triggers = require('triggers');

rules.JSRule({
    name: "Javascript Hello World (GenericCronTrigger raw API with JS helper libraries)",
    description: "This is an example Jython cron rule using the raw API",
    triggers: [
        triggers.TimerTrigger("0/10 * * * * ?")
    ],
    execute: function( module, inputs){
        logInfo("Hello World!");
    }
});
