/**
 * Functions for creating rules
 * 
 * Copyright (c) 2019 Contributors to the openHAB Scripters project
 * 
 * @author Helmut Lehmeyer - initial contribution
 */
'use strict';

scriptExtension.importPreset("RuleSupport"); //https://www.openhab.org/docs/configuration/jsr223.html#overview
scriptExtension.importPreset("RuleSimple");
scriptExtension.importPreset("RuleFactories");
scriptExtension.importPreset("default");

var OPENHAB_CONF = Java.type("java.lang.System").getenv("OPENHAB_CONF");
load(OPENHAB_CONF+'/automation/lib/javascript/core/utils.js');
load(OPENHAB_CONF+'/automation/lib/javascript/core/triggers.js');
load(OPENHAB_CONF+'/automation/lib/javascript/core/conditions.js');

//https://docs.oracle.com/javase/8/docs/technotes/guides/scripting/nashorn/api.html
//var StSimpleRule = Java.type("org.openhab.core.automation.module.script.rulesupport.shared.simple.SimpleRule");
//var StSimpleRuleExt = new StSimpleRule();
//var ExtendedSimpleRule = Java.extend(SimpleRule, {
//    setUID: function(i) {
//		//print("Run in separate thread");
//		this.uid = i;
//    }
//});
//var Thread = Java.type("java.lang.Thread");
//var th = new Thread(new MyRun());


//if(RuleBuilder == undefined)var RuleBuilder = Java.type("org.openhab.core.automation.core.util.RuleBuilder");

/*

if(RuleBuilder == undefined)var RuleBuilder = Java.type("org.openhab.core.automation.core.util.RuleBuilder");

In future better do it by org.openhab.core.automation.core.util.RuleBuilder like in 
org.openhab.core.automation.core.dto.RuleDTOMapper Don't know
return RuleBuilder.create(ruleDto.uid)
				.withActions(ActionDTOMapper.mapDto(ruleDto.actions))
                .withConditions(ConditionDTOMapper.mapDto(ruleDto.conditions))
                .withTriggers(TriggerDTOMapper.mapDto(ruleDto.triggers))
                .withConfiguration(new Configuration(ruleDto.configuration))
                .withConfigurationDescriptions(ConfigDescriptionDTOMapper.map(ruleDto.configDescriptions))
				.withTemplateUID(ruleDto.templateUID)
				.withVisibility(ruleDto.visibility)
				.withTags(ruleDto.tags)
				.withName(ruleDto.name)
				.withDescription(ruleDto.description).build();

//  UNTESTED UNTESTED UNTESTED 
//Simplifies spelling for rules.
(function(context) {
	'use strict';
	
	  context.JSRuleNew = function(obj) {
		  //logInfo("################  JSRule Line: "+__LINE__+"  #################");
		  //2. OR second option, to add Rules in rulefile. Is not needed.
		  var triggers = obj.triggers ? obj.triggers : obj.getEventTrigger();
		  return RuleBuilder.create( obj.uid ? obj.uid : uuid.randomUUID()+me.replace(/[^\w]/g, "-"))
		  .withActions( obj.actions ? obj.actions : null)
		  .withConditions( obj.conditions ? obj.conditions : null)
		  .withTriggers( triggers && triggers.length > 0 ? triggers : null)
		  .withConfiguration(new Configuration(ruleDto.configuration))
		  .withConfigurationDescriptions( obj.configurationDescription ? [obj.configurationDescription] : null)
		  .withTemplateUID( obj.templateUID ? obj.templateUID : null)
		  .withVisibility( obj.visibility ? obj.visibility : null)
		  .withTags( obj.tags ? obj.tags : null)
		  .withName( obj.name ? obj.name : null)
		  .withDescription(obj.description ? obj.description : null)
		  .build();
	  };
	
  })(this);
//  UNTESTED UNTESTED UNTESTED 
*/


//Simplifies spelling for rules.
(function (context) {
	'use strict';

	//FROM: https://community.openhab.org/t/port-jsr223-bundle-to-openhab-2/2633/171?u=lewie
	//Search ruleUID = filter(lambda rule: rule.name == "Alert: TV turn off timer alert", rules.getAll())[0].UID
	//ruleEngine.setEnabled(ruleUID, True)# enable rule
	//ruleEngine.setEnabled(ruleUID, False)# disable rule
	context.setEnabled = function (ruid, enable){ //enable rule
		logInfo("################  setEnabled Line: "+__LINE__+"  ################# ruid:" + ruid);
		RuleManager.setEnabled(ruid, enable);
	}

	context.JSRule = function (obj, line) {
		try{
			var ruid = uuid.randomUUID() + "-" + obj.name.replace(/[^\w]/g, "-");
			logInfo("################  JSRule Line: "+__LINE__+"  ################# ruid:" + ruid);
			//var rule = new SimpleRule({ setUID: function(i) { uid = i; } })
			var rule = new SimpleRule(){
				execute: obj.execute //DOES THIS WORK? AND IF YES, WHY? => execute is found in implemented SimpleRuleActionHandler
			};
			var triggers = obj.triggers ? obj.triggers : obj.getEventTrigger();

			rule.setTemplateUID(ruid);

			if (obj.description) {
				rule.setDescription(obj.description);
			}
			if (obj.name) {
				rule.setName(obj.name);
			}

			//1. Register rule here
			if (triggers && triggers.length > 0) {
				rule.setTriggers(triggers);
				automationManager.addRule(rule);
			}

			//rule.setUID( ruid); //I must not set... :-(
			//logInfo("################  JSRule Line: "+__LINE__+"  ################# getUid:" + rule.getUID());
			//logInfo("################  JSRule Line: "+__LINE__+"  ################# templateUID:" + rule.getTemplateUID());
			//2. OR second option, to add Rules in rulefile. Is not needed.
			return rule;
		}catch(err) {
			context.logError("JSRule " + __LINE__ + ". obj: '" + obj + "' Error:" +  err);
		}
		return null;
	},

	//TODO like in org.openhab.core.automation.core.dto.RuleDTOMapper 
	// or org.openhab.core.automation.sample.extension.java.internal.WelcomeHomeRulesProvider
	//Missing SimpleRuleActionHandler!!
	context.JSRuleNew = function (obj, line) {
		logInfo("################  JSRuleNew Line: "+__LINE__+"  #################");
		//2. OR second option, to add Rules in rulefile. Is not needed.
		var rname =  obj.name ? obj.name.replace(/[^\w]/g, "-") : "nameless-generic";
		var ruid = obj.uid ? obj.uid : uuid.randomUUID() + "-" + rname;
		var triggers = obj.triggers ? obj.triggers : obj.getEventTrigger();
		var execX = new SimpleRule(){execute: obj.execute};//Not good!!
		return RuleBuilder.create(ruid)
			.withActions(execX.getActions() ? execX.getActions() : null)
			//.withActions(obj.execute ? [obj.execute] : null) //org.openhab.core.automation.module.script.rulesupport.shared.ScriptedAutomationManager L164
			////.withConditions(obj.conditions ? obj.conditions : [])
			.withTriggers(triggers && triggers.length > 0 ? triggers : null)
			//.withConfiguration(new Configuration(obj.configuration))
			//.withConfigurationDescriptions(obj.configurationDescription ? [obj.configurationDescription] : null)
			//.withTemplateUID(obj.templateUID ? obj.templateUID : ruid)
			.withVisibility(obj.visibility ? obj.visibility : null)
			//.withTags(obj.tags ? obj.tags : null)
			.withName(obj.name ? obj.name : null)
			.withDescription(obj.description ? obj.description : null)
			.build();
	}
	
}) (this);
