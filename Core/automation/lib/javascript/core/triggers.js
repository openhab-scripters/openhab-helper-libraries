/**
 * Functions for creating Triggers
 * 
 * Copyright (c) 2019 Contributors to the openHAB Scripters project
 * 
 * @author Helmut Lehmeyer - initial contribution
 */
'use strict';

scriptExtension.importPreset("RuleSupport");
scriptExtension.importPreset("RuleFactories");

// Get Triggers and Conditions module output
// http://localhost:8080/rest/module-types

// Examles:
// see: org.eclipse.smarthome.automation.sample.extension.java.internal.WelcomeHomeRulesProvider.createLightsRule()

if(ModuleBuilder == undefined)var ModuleBuilder = Java.type("org.eclipse.smarthome.automation.core.util.ModuleBuilder");

//Handlers -> Used Strings for IDs now, so these classes not needed
///if(ChannelEventTriggerHandler   == undefined)var ChannelEventTriggerHandler     = Java.type("org.openhab.core.automation.internal.module.handler.ChannelEventTriggerHandler");
///if(CompareConditionHandler      == undefined)var CompareConditionHandler        = Java.type("org.openhab.core.automation.internal.module.handler.CompareConditionHandler");
/////if(GenericEventConditionHandler == undefined)var GenericEventConditionHandler   = Java.type("org.openhab.core.automation.internal.module.handler.GenericEventConditionHandler");
/////if(GenericEventTriggerHandler   == undefined)var GenericEventTriggerHandler     = Java.type("org.openhab.core.automation.internal.module.handler.GenericEventTriggerHandler");
/////if(ItemCommandActionHandler     == undefined)var ItemCommandActionHandler       = Java.type("org.openhab.core.automation.internal.module.handler.ItemCommandActionHandler");
///if(ItemCommandTriggerHandler    == undefined)var ItemCommandTriggerHandler      = Java.type("org.openhab.core.automation.internal.module.handler.ItemCommandTriggerHandler");
///if(ItemStateConditionHandler    == undefined)var ItemStateConditionHandler      = Java.type("org.openhab.core.automation.internal.module.handler.ItemStateConditionHandler");
///if(ItemStateTriggerHandler      == undefined)var ItemStateTriggerHandler        = Java.type("org.openhab.core.automation.internal.module.handler.ItemStateTriggerHandler");
/////if(RuleEnablementActionHandler  == undefined)var RuleEnablementActionHandler    = Java.type("org.openhab.core.automation.internal.module.handler.RuleEnablementActionHandler");
/////if(RunRuleActionHandler         == undefined)var RunRuleActionHandler           = Java.type("org.openhab.core.automation.internal.module.handler.RunRuleActionHandler");
/////if(DayOfWeekConditionHandler    == undefined)var DayOfWeekConditionHandler      = Java.type("org.openhab.core.automation.internal.module.handler.DayOfWeekConditionHandler");
///if(GenericCronTriggerHandler    == undefined)var GenericCronTriggerHandler      = Java.type("org.openhab.core.automation.internal.module.handler.GenericCronTriggerHandler");
/////if(TimeOfDayTriggerHandler      == undefined)var TimeOfDayTriggerHandler        = Java.type("org.openhab.core.automation.internal.module.handler.TimeOfDayTriggerHandler");

// ### StartupTrigger ### DOES NOT WORK!! TODO?!
/*
//if(Visibility == undefined)var Visibility = Java.type("org.eclipse.smarthome.automation.Visibility");//RuleSimple preset includes this
if(HashSet == undefined)var HashSet = Java.type("java.util.HashSet");
if(TriggerHandler == undefined)var TriggerHandler = Java.type("org.openhab.core.automation.handler.TriggerHandler");
if(Trigger == undefined)var Trigger = Java.type("org.eclipse.smarthome.automation.Trigger");

var _StartupTriggerHandlerFactory = new TriggerHandlerFactory(){
	get: function(trigger){
		logWarn(" -#### #### #### #### #### get trigger "+__LINE__, trigger); 
		//return _StartupTriggerHandlerFactory.handler(trigger);
		return  new TriggerHandler(){
			setRuleEngineCallback: function(rule_engine_callback){
				logWarn(" -#### TriggerHandler setRuleEngineCallback "+__LINE__, " setRuleEngineCallback ");
				rule_engine_callback.triggered(trigger, {});
			}, 
			dispose: function(){
				logWarn(" -#### TriggerHandler dispose "+__LINE__, " dispose ");
			}
		};
	},
	ungetHandler: function( module, ruleUID, handler){ 
		logWarn(" -#### ungetHandler "+__LINE__, module);
		logWarn(" -#### ungetHandler "+__LINE__, ruleUID);
		logWarn(" -#### ungetHandler "+__LINE__, handler);
	},
	dispose: function(){
		logWarn(" -#### dispose "+__LINE__, " dispose ");
	}
};
var STARTUP_MODULE_ID = "jsr223.StartupTrigger";

automationManager.addTriggerType(new TriggerType(
    STARTUP_MODULE_ID, 
	[],
    "the rule is activated", 
    "Triggers when a rule is activated the first time",
    new HashSet(), 
	Visibility.VISIBLE, 
	[]));
	
automationManager.addTriggerHandler(STARTUP_MODULE_ID, _StartupTriggerHandlerFactory);
*/
var StartupTrigger = function(triggerName){
    //DOES NOT WORK - TODO: return new Trigger( getTrName(triggerName), "jsr223.StartupTrigger", new Configuration());
}

// ### ChannelEventTriggerHandler ###
// Works like: ChannelEventTrigger('astro:sun:local:rise#event', 'START')
var ChannelEventTrigger = function(channel, event, triggerName) {
    return ModuleBuilder.createTrigger().withId(getTrName(triggerName)).withTypeUID("core.ChannelEventTrigger").withConfiguration( new Configuration({
        "channelUID": channel,
        "event": event
    })).build();
}

// ### ChangedEventTrigger ###
var ItemStateChangeTrigger = function(itemName, oldState, newState, triggerName){
    return ModuleBuilder.createTrigger().withId(getTrName(triggerName)).withTypeUID("core.ItemStateChangeTrigger").withConfiguration( new Configuration({
        "itemName": itemName,
        "state": newState,
        "oldState": oldState
    })).build();
}
var ChangedEventTrigger = ItemStateChangeTrigger; 


// ### UpdatedEventTrigger ###
var ItemStateUpdateTrigger = function(itemName, state, triggerName){
    return ModuleBuilder.createTrigger().withId(getTrName(triggerName)).withTypeUID("core.ItemStateUpdateTrigger").withConfiguration( new Configuration({
        "itemName": itemName,
        "state": state
    })).build();
}
var UpdatedEventTrigger = ItemStateUpdateTrigger; 


// ### CommandEventTrigger ###
var ItemCommandTrigger = function(itemName, command, triggerName){
	//logWarn("#### ItemCommandTrigger "+__LINE__, triggerName);
    return ModuleBuilder.createTrigger().withId(getTrName(triggerName)).withTypeUID("core.ItemCommandTrigger").withConfiguration( new Configuration({
        "itemName": itemName,
        "command": command
    })).build();
}
var CommandEventTrigger = ItemCommandTrigger; 

// ### TimerTrigger ###
//!!!!!!!! timer.GenericCronTrigger !!!!!!!!!!!!!
var GenericCronTrigger = function(expression, triggerName){
	//logWarn("#### GenericCronTrigger "+__LINE__, expression, getTrName(triggerName), Trigger);  // see: org.eclipse.smarthome.automation.sample.extension.java.internal.WelcomeHomeRulesProvider.createLightsRule()
    return ModuleBuilder.createTrigger().withId(getTrName(triggerName)).withTypeUID("timer.GenericCronTrigger").withConfiguration( new Configuration({
        "cronExpression": expression
    })).build();
}
var TimerTrigger = GenericCronTrigger; 


// ### stateCondition ###
var ItemStateCondition = function(itemName, state, condName){
    return ModuleBuilder.createCondition().withId(getTrName(condName)).withTypeUID("core.ItemStateCondition").withConfiguration( new Configuration({
        "itemName": itemName,
        "operator": "=",
        "state": state
    })).build();
}
var stateCondition = ItemStateCondition; 

// ### GenericCompareCondition ###
var GenericCompareCondition = function(itemName, state, operator, condName){
    return ModuleBuilder.createCondition().withId(getTrName(condName)).withTypeUID("core.GenericCompareCondition").withConfiguration( new Configuration({
        "itemName": itemName,
        "operator": operator,// matches, ==, <, >, =<, =>
        "state": state
    })).build();
}
//compareCondition("itemName", OFF, "==", "condNameOfCompareCondition")
var compareCondition = GenericCompareCondition; 



var getTrName = function(trn){
	return trn == undefined || trn == null || trn == "" ? uuid.randomUUID() + "-" + me.replace(/[^\w]/g, "-") : trn;
	//return trn == undefined || trn == null || trn == "" ? uuid.randomUUID() : trn;
}
