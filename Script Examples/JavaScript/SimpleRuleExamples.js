/**
 * Examples of rules
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

logInfo("################# SimpleRuleExamples.js ##################", TimerTrigger);

//### Example 1: Default spelling, not simplified
var xRule = new rules.SimpleRule(){
	execute: function( module, input){
		logInfo(" ################  xRule Line: "+__LINE__+"  #################");
		logInfo(" xRule::execute "+__LINE__, " input "+ input, " module "+ module, " uuid "+ utils.uuid.randomUUID());
		
		for( var i in input){
			var ai = input[i];
			logInfo(" -- input "+i +" = "+ ai);
		}
		
	}
};
xRule.setTriggers([
		triggers.TimerTrigger("0/15 * * * * ?")
]);
//Enable/Disable Rule:
utils.automationManager.addRule(xRule); 
//logInfo(" -- getUID "+xRule.getUID());
//logInfo(" -- getUID "+automationManager.addRule(xRule).getUID());


//### Example 2: More backward compatible spelling
rules.JSRule({
	getEventTrigger: function(){
		return [ 
			new triggers.TimerTrigger("0/5 * * * * ?")//Enable/Disable Rule
		]
	},
	execute: function( module, input){
		logInfo(" ################  yRule Line: "+__LINE__+"  #################");
		logInfo(" yRule::execute "+__LINE__, " input "+ input, " module "+ module);
	}
});


//### Example 3: Simplest spelling
rules.JSRule({
	triggers: [
		triggers.TimerTrigger("0/5 * * * * ?")//Enable/Disable Rule
	],
	execute: function( module, input){
		logInfo(" ################  zRule Line: "+__LINE__+"  #################");
	}
});

//### Example 4: Most simple spelling live.
rules.JSRule({
	name: "Example 4",
	description: "Most simple spelling live",
	triggers: [ //Enable/Disable Rule
		//NOT Working: ShutDown()
		//NOT Working: StartupTrigger()
		//stateCondition("testItemSwitch", "ON", "cond1") //Error: Can not create new object with constructor org.eclipse.smarthome.automation.Condition with the passed arguments; they do not match any of its method signatures.
		//IS WORKING: TimerTrigger("0/15 * * * * ?")
		//IS WORKING: new TimerTrigger("0/15 * * * * ?")
		//TimerTrigger("0/15 * * * * ?")
		//StartupTrigger()
		//IS WORKING: ChangedEventTrigger("testItemSwitch", "ON", "OFF")
		//IS WORKING: UpdatedEventTrigger("testItemSwitch"),
		//IS WORKING: CommandEventTrigger("testItemSwitch")
	],
	execute: function( module, input){
		logInfo(" ################  zRule Line: "+__LINE__+"  #################");
		logInfo(" zRule::execute "+__LINE__, " input "+ input, " module "+ module);
		logInfo("uuid "+__LINE__, uuid.randomUUID()); 
		
		//Logging
		logInfo("log "+__LINE__, "logInfo"); 
		logWarn("log "+__LINE__, "logWarn"); 
		logDebug("log "+__LINE__, "logDebug"); 
		logTrace("log "+__LINE__, "logTrace"); 
		
		var act = getActions();
		for( var i in act){
			var ai = act[i];
			logInfo(" -- service "+i +" = "+ ai);
		}
		
		var testItemSwitch = updateIfUninitialized('testItemSwitch', OFF); 
		logInfo("testItemSwitch "+__LINE__, "testItemSwitch.state = " + testItemSwitch.state);
		
		utils.sendCommand("testItemSwitch", ON);
		utils.postUpdate("testItemSwitch", OFF);
		
		//Java 8 
		logInfo(" -#### LocalDateTime.now().withMinute(0) "+__LINE__, LocalDateTime.now().withMinute(0));
		//Java 7
		logInfo(" -#### DateTime.now().withMinute(0) "+__LINE__, DateTime.now().withMinuteOfHour(0));
		
		// Run Timer
		var runme = function(){logInfo(" runme ", "Timer has been executed at "+DateTime.now());};
		utils.createTimer(now().plusSeconds(5), runme);
		
		//Action Examples
		//getAction("XMPP").static.sendXMPP("any@jabber.com", "automation XMPP :-)");
		//getAction("Mail").static.sendMail("any@mail.com", "automation Mail :-)", "It works!");
		
		//using helper.js:
		//sendXMPP("any@jabber.com", "automation XMPP :-)");
		//sendMail("any@mail.com", "automation Mail :-)", "It works!");
		

		logInfo(" -- getTriggers ", xRule.getTriggers());
        logInfo(" -- getConditions ", xRule.getConditions());
        logInfo(" -- getActions ", xRule.getActions());
        logInfo(" -- getConfigurationDescriptions ", xRule.getConfigurationDescriptions());
        logInfo(" -- getConfiguration ", xRule.getConfiguration());
        logInfo(" -- getTemplateUID ", xRule.getTemplateUID());
        logInfo(" -- getVisibility ", xRule.getVisibility());
	}
});
