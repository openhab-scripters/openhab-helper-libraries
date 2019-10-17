/**
 * Examples of rules that utilize GenericCron Trigger
 * 
 * Copyright (c) 2019 Contributors to the openHAB Scripters project
 * 
 * @author Helmut Lehmeyer - initial contribution
 */
'use strict';

load(Java.type("java.lang.System").getenv("OPENHAB_CONF")+'/automation/lib/javascript/core/init.js');

var rules = require('rules');
var triggers = require('triggers');
var utils = require('utils');

rules.JSRule({
	name: me+" TimerExample",
	description: "TimerExample L:"+__LINE__,
	triggers: [ 
		triggers.TimerTrigger("0/15 * * * * ?")
	],
	execute: function( module, input){ 
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");
		
		logInfo( "createTimer start");
		utils.createTimer(DateTime.now().plusSeconds(2), function(){
			logWarn( "createTimer stopped ");
		});
		
		logInfo( "setTimeout start");
		utils.setTimeout(function(m){
			logWarn( "setTimeout stopped " + m);
		}, 1000, "bla");

	}
});
