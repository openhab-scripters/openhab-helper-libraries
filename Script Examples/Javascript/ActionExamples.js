/**
 * Copyright (c) 2019 by Helmut Lehmeyer.
 * 
 * @author Helmut Lehmeyer 
 */

'use strict';

var OPENHAB_CONF = Java.type("java.lang.System").getenv("OPENHAB_CONF"); // most this is /etc/openhab2
load(OPENHAB_CONF+'/automation/lib/javascript/core/JSRule.js');

var me = "ActionExamples.js";
logInfo("################# "+me+" ##################");


var myRule = JSRule({
	name: me+" Busevents",
	description: "TEST L:"+__LINE__,
	triggers: [ 
		//TimerTrigger("0/55 * * * * ?")
	],
	execute: function( module, input){ 
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");
		logInfo(" SimpleRule::execute "+__LINE__, " input "+ input);
		//logInfo("uuid "+__LINE__, uuid.randomUUID(), "bla", "bla"); 
		logWarn("uuid "+__LINE__, uuid.randomUUID(), "bla", "bla"); 
		logWarn("Rule "+__LINE__, Rule); 
		//logDebug("uuid "+__LINE__, uuid.randomUUID(), "bla", "bla"); 
		//logWarn("uuid "+__LINE__, uuid.randomUUID(), "bla", "bla"); 
		//logTrace("uuid "+__LINE__, uuid.randomUUID(), "bla", "bla"); 
		
		
		var actions = getActions();
		for( var i in actions){
			var ai = actions[i];
			logWarn(" -- service "+i +" = "+ ai);
		}
		
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");
		//logWarn(" -- oh ", oh);
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");
		logWarn(" -- Rule ", Rule);
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");
		
		//postUpdate("testItemSwitch", OFF);
		//postUpdate("testItemSwitch", ON);
		
		//Java 8 
		logWarn(" -#### LocalDateTime.now().withMinute(0) "+__LINE__, LocalDateTime.now().withMinute(0));
		//Java 7
		logWarn(" -#### DateTime.now().withMinute(0) "+__LINE__, DateTime.now().withMinuteOfHour(0));
		
		// Run Timer
		var runme = function(){logWarn(" runme ", "runme");};
		createTimer(now().plusSeconds(2), runme);
		
		//getAction("XMPP").static.sendXMPP("helmutl@lewi-cleantech.net", "automation XMPP :-)");
		//sendXMPP("helmutl@lewi-cleantech.net", "automation XMPP :-)");
		
		//getAction("Mail").static.sendMail("hl@lewi.io", "automation Mail :-)", "It works!");
		//sendMail("hl@lewi.io", "automation Mail :-)", "It works!");
		
		//See: helper.js line 270
		logInfo(" -- input "+ input);
		logInfo(" -- oldState "+ input.oldState);
		logInfo(" -- newState "+ input.newState);
		logInfo(" -- event "+ input.event); //event=testItemSwitch changed from OFF to ON
		logInfo(" -- event "+ getTriggeredData(input).triggerType);

		logWarn(" -- getTriggers ", myRule.getTriggers());
        logWarn(" -- getConditions ", myRule.getConditions());
        logWarn(" -- getActions ", myRule.getActions());
        logWarn(" -- getConfigurationDescriptions ", myRule.getConfigurationDescriptions());
        logWarn(" -- getConfiguration ", myRule.getConfiguration());
        logWarn(" -- getTemplateUID ", myRule.getTemplateUID());
        logWarn(" -- getVisibility ", myRule.getVisibility());

	}
});



/**
 * Busevents
 *
 * see helper.js too.
 *
 * sendCommand(Item, String)
 * sendCommand(Item, Number)
 * sendCommand(String, String)
 * getAcceptedCommandNames(Item)
 * sendCommand(Item, Command)
 * postUpdate(Item, Number)
 * postUpdate(Item, String)
 * postUpdate(String, String)
 * getAcceptedDataTypeNames(Item)
 * postUpdate(Item, State)
 * storeStates(Item...)
 * restoreStates(Map<Item, State>)
 */
JSRule({
	name: me+" Busevents",
	description: "TEST L:"+__LINE__,
	triggers: [ 
		//TimerTrigger("0/15 * * * * ?")
	],
	execute: function( module, input){
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");
		
		var it = getItem("errors_in_logs");
		
		//sendCommand(it, String);
		//sendCommand(it, Number);
		//sendCommand(String, String);
		//sendCommand(it, Command);
		
		//postUpdate(it, Number);
		//postUpdate(it, String);
		//postUpdate(String, String);
		//postUpdate(it, State);
		
		//NOT TESTED YET: storeStates(it);
		//NOT TESTED YET: restoreStates([it, State]);
		//logInfo( me+__LINE__, "meldet "+ it.state +" ");
	}
});


/**
 * Examples to import and use actions that are provided in standard Rule Engine too.
 * PersistenceExtensions
 * HTTP
 * Ping
 * Audio
 * Voice
 * ThingAction
 */

/**
 * getActions to see which actions are available
 */
JSRule({
	name: me+" getActions",
	description: "TEST L:"+__LINE__,
	triggers: [ 
		//TimerTrigger("0/15 * * * * ?")
	],
	execute: function( module, input){
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");	
		var a = getActions();
		var aList = getActionList();
		print("getActionList: 	" + JSON.stringify( aList ));
		
		for(var i=0; i<aList.length; i++){
			logInfo("################ "+me+" Line: "+__LINE__+"  #################|"+aList[i]);
			logInfo("################ "+me+" Line: "+__LINE__+"  #################|"+a[aList[i]]);
			if(aList[i] == "XMPP")logInfo("### "+me+" Line: "+__LINE__+"  ###|"+a[aList[i]].getActionClass().static.sendXMPP("helmutl@lewi-cleantech.net","jkkkk")+"|###");
		}
		//
		//var XMP = ScriptServiceUtil.actionServices[6].getActionClass();//.getConstructor().newInstance();
		//logInfo("################ "+me+" Line: "+__LINE__+"  #################|"+XMP.static.sendXMPP("helmutl@lewi-cleantech.net","vvvvvvvvvvv"));
		//logInfo("################ "+me+" Line: "+__LINE__+"  #################|"+getAction("XMPP").static.sendXMPP("helmutl@lewi-cleantech.net","jkkkk")+"|##########");
		
	}
});
 
/**
 * PersistenceExtensions
 * PersistenceExtensions are default imported by helper.js see: 'jslib/PersistenceExtensions.js'
 */
JSRule({
	name: me+" PersistenceExtensions",
	description: "TEST L:"+__LINE__,
	triggers: [ 
		//TimerTrigger("0/15 * * * * ?")
	],
	execute: function( module, input){
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");	
		
		/*
		persist
		historicState
		changedSince
		updatedSince
		maximumSince
		minimumSince
		averageSince
		sumSince
		lastUpdate
		deltaSince
		evolutionRate
		previousState
		*/
		
		//print("PersistenceExtensions TEST: "+persistExt("previousState", "Suntracer_Temp"));
		// ATTENTION this writes to DB!! print("PersistenceExtensions persist: 	"+persist("Suntracer_Temp", 22));
		logInfo("PersistenceExtensions historicState: 	"+historicState("Suntracer_Temp", now().minusDays(3)));
		logInfo("PersistenceExtensions changedSince: 	"+changedSince("Suntracer_Temp", now().minusDays(3)));
		logInfo("PersistenceExtensions updatedSince: 	"+updatedSince("Suntracer_Temp", now().minusDays(3)));
		logInfo("PersistenceExtensions maximumSince: 	"+maximumSince("Suntracer_Temp", now().minusDays(3)));
		logInfo("PersistenceExtensions minimumSince: 	"+minimumSince("Suntracer_Temp", now().minusDays(3)));
		logInfo("PersistenceExtensions averageSince: 	"+averageSince("Suntracer_Temp", now().minusDays(3)));
		logInfo("PersistenceExtensions sumSince: 		"+sumSince("Suntracer_Temp", now().minusDays(3))); 	
		logInfo("PersistenceExtensions lastUpdate: 	"+lastUpdate("Suntracer_Temp")); 
		logInfo("PersistenceExtensions deltaSince: 	"+deltaSince("Suntracer_Temp", now().minusDays(3))); 
		logInfo("PersistenceExtensions evolutionRate: 	"+evolutionRate("Suntracer_Temp", now().minusDays(3)));
		logInfo("PersistenceExtensions previousState: 	"+previousState("Suntracer_Temp"));

	}
});

/**
 * HTTP !! IST DAS NÖTIG? SIEHE ### getActions ### in helper.js
 * sendHttpGetRequest(String url)
 * sendHttpGetRequest(String url, int timeout)
 * sendHttpPutRequest(String url)
 * sendHttpPutRequest(String url, int timeout)
 * sendHttpPutRequest(String url, String contentType, String content)
 * sendHttpPutRequest(String url, String contentType, String content, int timeout)
 * sendHttpPostRequest(String url)
 * sendHttpPostRequest(String url, int timeout)
 * sendHttpPostRequest(String url, String contentType, String content)
 * sendHttpPostRequest(String url, String contentType, String content, int timeout)
 * sendHttpDeleteRequest(String url)
 * sendHttpDeleteRequest(String url, int timeout)
 */
var HTTP = Java.type('org.eclipse.smarthome.model.script.actions.HTTP');
JSRule({
	name: me+" HTTP",
	description: "TEST L:"+__LINE__,
	triggers: [ 
		//TimerTrigger("0/15 * * * * ?")
	],
	execute: function( module, input){
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");	
		print("HTTP sendHttpGetRequest: 	" + HTTP.sendHttpGetRequest("http://www.heise.de"));
	}
});

/**
 * Ping
 * boolean checkVitality(String host, int port, int timeout)
 */
var Ping = Java.type('org.eclipse.smarthome.model.script.actions.Ping');
JSRule({
	name: me+" Ping",
	description: "TEST L:"+__LINE__,
	triggers: [ 
		//TimerTrigger("0/15 * * * * ?")
	],
	execute: function( module, input){
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");	
		print("Ping localhost: 	" + Ping.checkVitality("localhost", 22, 500));
	}
});

/**
 * Exec on bash
 */
JSRule({
	name: me+" Exec",
	description: "TEST L:"+__LINE__,
	triggers: [ 
		//TimerTrigger("0/15 * * * * ?")
	],
	execute: function( module, input){
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");
		var antwort = executeCommandLineAndWaitResponse("bash /data/findErrors.sh", 10000);
		logInfo( me, "meldet "+ antwort +" ");
		antwort = executeCommandLine("bash /data/findErrors.sh");
		logInfo( me, "meldet "+ antwort +" ");
	}
});

/**
 * Audio
 * playSound(String filename)
 * playSound(String sink, String filename)
 * playStream(String url)
 * playStream(String sink, String filename)
 * getMasterVolume()
 * setMasterVolume(float volume)
 * setMasterVolume(PercentType percent)
 * increaseMasterVolume(float volume)
 * decreaseMasterVolume(float volume)
 */
var Audio = Java.type('org.eclipse.smarthome.model.script.actions.Audio');
JSRule({
	name: me+" Audio",
	description: "TEST L:"+__LINE__,
	triggers: [ 
		//TimerTrigger("0/15 * * * * ?")
	],
	execute: function( module, input){
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");		
		print("Ping getMasterVolume: 	" + Audio.getMasterVolume());
	}
});

/**
 * Voice
 * say(Object text)
 * say(Object text, String voice)
 * say(Object text, String voice, String sink)
 * interpret(Object text)
 * interpret(Object text, String voice)
 * interpret(Object text, String voice, String sink)
 */
var Voice = Java.type('org.eclipse.smarthome.model.script.actions.Voice');
JSRule({
	name: me+" Voice",
	description: "TEST L:"+__LINE__,
	triggers: [ 
		//TimerTrigger("0/15 * * * * ?")
	],
	execute: function( module, input){
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");	
		print("Voice say 'Hello Voice': 	" + Voice.say("Hello Voice"));	
	}
});

/**
 * ThingAction
 * ThingStatusInfo getThingStatusInfo(String thingUid)
 */
/* DOES NOT FIND ThingAction anymore
var ThingAction = Java.type('org.eclipse.smarthome.model.script.actions.ThingAction');
JSRule({
	name: me+" ThingAction",
	description: "TEST L:"+__LINE__,
	triggers: [ 
		//TimerTrigger("0/15 * * * * ?")
	],
	execute: function( module, input){
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");		
		print("ThingAction getThingStatusInfo of': 	" + ThingAction.getThingStatusInfo("chromecast:chromecast:6a01c5ef0f0a6b3fd15849eda1379ab8"));	
	}
});*/





JSRule({
	name: "Light_UG_Arbeitsraum Mode",
	description: "",
	triggers: [ 
		//IS WORKING: TimerTrigger("0/15 * * * * ?")
		//IS WORKING: ChangedEventTrigger("testItemSwitch", "ON", "OFF")
		//IS WORKING: UpdatedEventTrigger("testItemSwitch"),
        //IS WORKING: CommandEventTrigger("testItemSwitch")
        CommandEventTrigger("Light_UG_Arbeitsraum") 
	],
	execute: function( module, input){

        logInfo("Light_UG_Arbeitsraum", "Light_UG_Arbeitsraum Switched");
        var receivedCommand = getTriggeredData(input).receivedCommand;
        logInfo("Light_UG_Arbeitsraum", receivedCommand);
        /*
		var Box_Kitchen_Mode = getItem("Box_Kitchen_Mode");

        logInfo("Light_UG_Arbeitsraum", "Light_UG_Arbeitsraum Activated");
        if (receivedCommand == 2) {
            logInfo("Light_UG_Arbeitsraum", "Light_UG_Arbeitsraum 2a " + Box_Kitchen_Mode.state);
            if (Box_Kitchen_Mode.state != 8) {
                sendCommand("Box_Kitchen_Mode", 8)
            }
            logInfo("Light_UG_Arbeitsraum", "Light_UG_Arbeitsraum 2b " + Box_Kitchen_Mode.state);
        }
        else {
            logInfo("Light_UG_Arbeitsraum", "Light_UG_Arbeitsraum 1a " + Box_Kitchen_Mode.state);
            if (Box_Kitchen_Mode.state != 0) {
                sendCommand("Box_Kitchen_Mode", 0)
            }
            logInfo("Light_UG_Arbeitsraum", "Light_UG_Arbeitsraum 1b " + Box_Kitchen_Mode.state);
        }*/

    }
    
});