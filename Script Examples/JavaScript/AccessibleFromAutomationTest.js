/**
 * Tests for checking the availability of objects provided by the built in scriptExtensions
 * 
 * Copyright (c) 2019 Contributors to the openHAB Scripters project
 * 
 * @author Helmut Lehmeyer - initial contribution
 */
'use strict';

var OPENHAB_CONF = Java.type("java.lang.System").getenv("OPENHAB_CONF"); // repository installation: /etc/openhab2, manual installation: /opt/openhab2/conf
load(OPENHAB_CONF+'/automation/lib/javascript/core/utils.js');
load(OPENHAB_CONF+'/automation/lib/javascript/core/triggers.js');
load(OPENHAB_CONF+'/automation/lib/javascript/core/conditions.js');

logInfo("################# AccessibleFromAutomationTest.js ##################");

var rSup = scriptExtension.importPreset("RuleSupport");
var rSim = scriptExtension.importPreset("RuleSimple");
var rFac = scriptExtension.importPreset("RuleFactories");
var rDef = scriptExtension.importPreset("default");
var rMed = scriptExtension.importPreset("media");

logWarn(" -- scriptExtension.presets "+__LINE__, scriptExtension.presets); 

logInfo(" reachable"+__LINE__, "###############################################");
logInfo(" reachable"+__LINE__, "SimpleRule", SimpleRule);
//logInfo(" reachable"+__LINE__, "SimpleActionHandler", SimpleActionHandler);
//logInfo(" reachable"+__LINE__, "SimpleConditionHandler", SimpleConditionHandler);
logInfo(" reachable"+__LINE__, "ActionHandlerFactory", ActionHandlerFactory);
logInfo(" reachable"+__LINE__, "ConditionHandlerFactory", ConditionHandlerFactory);
logInfo(" reachable"+__LINE__, "TriggerHandlerFactory", TriggerHandlerFactory);
logInfo(" reachable"+__LINE__, "Configuration", Configuration);
logInfo(" reachable"+__LINE__, "Action", Action);
logInfo(" reachable"+__LINE__, "Condition", Condition);
logInfo(" reachable"+__LINE__, "Trigger", Trigger);
logInfo(" reachable"+__LINE__, "Rule", Rule);
logInfo(" reachable"+__LINE__, "ModuleType", ModuleType);
logInfo(" reachable"+__LINE__, "ActionType", ActionType);
logInfo(" reachable"+__LINE__, "TriggerType", TriggerType);
logInfo(" reachable"+__LINE__, "ConfigDescriptionParameter", ConfigDescriptionParameter);
//logInfo(" reachable"+__LINE__, "RuleSupport", RuleSupport);
//logInfo(" reachable"+__LINE__, "RuleSimple", RuleSimple);
//logInfo(" reachable"+__LINE__, "RuleFactories", RuleFactories);
//RuleSupportScriptExtension -> presets.put("RuleSupport", Arrays.asList("Configuration", "Action", "Condition", "Trigger", "Rule", "ModuleType", "ActionType"));
logInfo(" types"+__LINE__, "Configuration", Configuration);
logInfo(" types"+__LINE__, "Action", Action);
logInfo(" types"+__LINE__, "Condition", Condition);
logInfo(" types"+__LINE__, "Trigger", Trigger);
logInfo(" types"+__LINE__, "Rule", Rule);
logInfo(" types"+__LINE__, "ModuleType", ModuleType);
logInfo(" types"+__LINE__, "ActionType", ActionType);
//RuleSupportScriptExtension -> presets.put("RuleSimple", Arrays.asList("ScriptedRule", "SimpleRule"));
//logInfo(" types"+__LINE__, "ScriptedRule", ScriptedRule);
logInfo(" types"+__LINE__, "SimpleRule", SimpleRule);
//RuleSupportScriptExtension -> presets.put("RuleFactories", Arrays.asList("ActionHandlerFactory", "ConditionHandlerFactory", "TriggerHandlerFactory", "TriggerType", "ConfigDescriptionParameter"));
logInfo(" types"+__LINE__, "ActionHandlerFactory", ActionHandlerFactory);
logInfo(" types"+__LINE__, "ConditionHandlerFactory", ConditionHandlerFactory);
logInfo(" types"+__LINE__, "TriggerHandlerFactory", TriggerHandlerFactory);
logInfo(" types"+__LINE__, "TriggerType", TriggerType);
logInfo(" types"+__LINE__, "ConfigDescriptionParameter", ConfigDescriptionParameter);

//        types.add("AutomationManager");
//        types.add("RuleRegistry");
//        types.add("rules");

logInfo(" types"+__LINE__, "automationManager", automationManager);
logInfo(" types"+__LINE__, "ruleRegistry", ruleRegistry);
logInfo(" types"+__LINE__, "rules", rules);


logInfo(" activate "+__LINE__, "###############################################");
logInfo(" activate "+__LINE__, "State", State);
logInfo(" activate "+__LINE__, "Command", Command);
//logInfo(" activate "+__LINE__, "DateTime", DateTime);
logInfo(" activate "+__LINE__, "LocalTime", LocalTime);
logInfo(" activate "+__LINE__, "URLEncoder", URLEncoder);
logInfo(" activate "+__LINE__, "FileUtils", FileUtils);
logInfo(" activate "+__LINE__, "FilenameUtils", FilenameUtils);
logInfo(" activate "+__LINE__, "File", File);
logInfo(" activate "+__LINE__, "IncreaseDecreaseType", IncreaseDecreaseType);
logInfo(" activate "+__LINE__, "DECREASE", DECREASE);
logInfo(" activate "+__LINE__, "INCREASE", INCREASE);
logInfo(" activate "+__LINE__, "OnOffType", OnOffType);
logInfo(" activate "+__LINE__, "ON", ON);
logInfo(" activate "+__LINE__, "OFF", OFF);
logInfo(" activate "+__LINE__, "OpenClosedType", OpenClosedType);
logInfo(" activate "+__LINE__, "CLOSED", CLOSED);
logInfo(" activate "+__LINE__, "OPEN", OPEN);
logInfo(" activate "+__LINE__, "StopMoveType", StopMoveType);
logInfo(" activate "+__LINE__, "MOVE", MOVE);
logInfo(" activate "+__LINE__, "STOP", STOP);
logInfo(" activate "+__LINE__, "UpDownType", UpDownType);
logInfo(" activate "+__LINE__, "DOWN", DOWN);
logInfo(" activate "+__LINE__, "UP", UP);
logInfo(" activate "+__LINE__, "DateTimeType", DateTimeType);
logInfo(" activate "+__LINE__, "DecimalType", DecimalType);
logInfo(" activate "+__LINE__, "HSBType", HSBType);
logInfo(" activate "+__LINE__, "PercentType", PercentType);
logInfo(" activate "+__LINE__, "PointType", PointType);
logInfo(" activate "+__LINE__, "StringType", StringType);
// services
logInfo(" services "+__LINE__, "items", items);
logInfo(" services "+__LINE__, "ir", ir);
logInfo(" services "+__LINE__, "itemRegistry", itemRegistry);
logInfo(" services "+__LINE__, "things", things);
logInfo(" services "+__LINE__, "events", events);
logInfo(" services "+__LINE__, "rules", rules);
logInfo(" services "+__LINE__, "###############################################");
