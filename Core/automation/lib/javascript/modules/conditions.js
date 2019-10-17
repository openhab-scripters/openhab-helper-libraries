/**
 * Functions for creating Conditions
 * 
 * Copyright (c) 2019 Contributors to the openHAB Scripters project
 * 
 * @author Helmut Lehmeyer - initial contribution
 */
'use strict';

scriptExtension.importPreset("RuleSupport");

// Get Triggers and Conditions module output
// http://localhost:8080/rest/module-types

// Examles:
// see: org.eclipse.smarthome.automation.sample.extension.java.internal.WelcomeHomeRulesProvider.createLightsRule()

    try {
        exports.ModuleBuilder = Java.type("org.eclipse.smarthome.automation.core.util.ModuleBuilder");
      } catch(e) {
        exports.ModuleBuilder = Java.type("org.openhab.core.automation.util.ModuleBuilder");
      }


// ### stateCondition ###
exports.ItemStateCondition = function(itemName, state, condName){
    return ModuleBuilder.createCondition().withId(getTrName(condName)).withTypeUID("core.ItemStateCondition").withConfiguration( new Configuration({
        "itemName": itemName,
        "operator": "=",
        "state": state
    })).build();
}
exports.stateCondition = exports.ItemStateCondition;

// ### GenericCompareCondition ###
exports.GenericCompareCondition = function(itemName, state, operator, condName){
    return ModuleBuilder.createCondition().withId(getTrName(condName)).withTypeUID("core.GenericCompareCondition").withConfiguration( new Configuration({
        "itemName": itemName,
        "operator": operator,// matches, ==, <, >, =<, =>
        "state": state
    })).build();
}
//compareCondition("itemName", OFF, "==", "condNameOfCompareCondition")
exports.compareCondition = exports.GenericCompareCondition;
