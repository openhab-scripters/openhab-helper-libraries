/**
 * Utility functions and variables
 * 
 * Copyright (c) 2019 Contributors to the openHAB Scripters project
 * 
 * @author Helmut Lehmeyer - initial contribution
 */
'use strict';

	var OPENHAB_CONF 			= Java.type("java.lang.System").getenv("OPENHAB_CONF");
	var automationPath 			= OPENHAB_CONF+'/automation/';
	var mainPath 				= automationPath + 'lib/javascript/core/';
	//https://wiki.shibboleth.net/confluence/display/IDP30/ScriptedAttributeDefinition
	var logger 					= Java.type("org.slf4j.LoggerFactory").getLogger("jsr223.javascript");
	
	try {
		var RuleBuilder = Java.type("org.openhab.core.automation.util.RuleBuilder");
	} catch(e) {
		var RuleBuilder = Java.type("org.eclipse.smarthome.automation.core.util.RuleBuilder");
	}
	
	try {
		var RuleManager = Java.type("org.openhab.core.automation.RuleManager");
	} catch(e) {
		var RuleManager = Java.type("org.eclipse.smarthome.automation.RuleManager");
	}

	var uuid 					= Java.type("java.util.UUID");
	var ScriptExecution 		= Java.type("org.eclipse.smarthome.model.script.actions.ScriptExecution");
	var ScriptServiceUtil 		= Java.type("org.eclipse.smarthome.model.script.ScriptServiceUtil");
	var ExecUtil 				= Java.type("org.eclipse.smarthome.io.net.exec.ExecUtil");
	var HttpUtil 				= Java.type("org.eclipse.smarthome.io.net.http.HttpUtil");


	//Other
	var Modifier 				= Java.type("java.lang.reflect.Modifier");
	var InputStream				= Java.type("java.io.InputStream");
	var IOUtils					= Java.type("org.apache.commons.io.IOUtils");
	

    //Types
    /* included in "default" preset
	var UnDefType 				= Java.type("org.eclipse.smarthome.core.types.UnDefType");
	var StringListType 			= Java.type("org.eclipse.smarthome.core.library.types.StringListType");	
	var RawType 				= Java.type("org.eclipse.smarthome.core.library.types.RawType");
	var RewindFastforwardType 	= Java.type("org.eclipse.smarthome.core.library.types.RewindFastforwardType");
	var PlayPauseType 			= Java.type("org.eclipse.smarthome.core.library.types.PlayPauseType");
	var NextPreviousType 		= Java.type("org.eclipse.smarthome.core.library.types.NextPreviousType");
    */
    	
	//Time JAVA 7 joda
	var DateTime 				= Java.type("org.joda.time.DateTime");
	//Time JAVA 8
	var LocalDate 				= Java.type("java.time.LocalDate");
	var LocalDateTime 			= Java.type("java.time.LocalDateTime");
	var FormatStyle 			= Java.type("java.time.format.FormatStyle");
	var DateTimeFormatter 		= Java.type("java.time.format.DateTimeFormatter");//https://www.programcreek.com/java-api-examples/?class=java.time.format.DateTimeFormatter&method=ofLocalizedDateTime
	var LocalTime 				= Java.type("java.time.LocalTime");
	var Month 					= Java.type("java.time.Month");
	var ZoneOffset 				= Java.type("java.time.ZoneOffset");
	var ZoneId 					= Java.type("java.time.ZoneId");
	var OffsetDateTime 			= Java.type("java.time.OffsetDateTime");

	var Timer = Java.type('java.util.Timer');
	
	//var QuartzScheduler = Java.type("org.quartz.core.QuartzScheduler");
	
	load( mainPath + '/PersistenceExtensions.js');
	
(function(context) {
  'use strict';	
	context.automationPath 	= automationPath;
	context.mainPath 		= mainPath;

    /* included in "default" preset
	//Todo missing:
	context.UnDefType 	= UnDefType;
	context.OPEN 		= OpenClosedType.OPEN;
	context.CLOSED		= OpenClosedType.CLOSED;
	context.REWIND 		= RewindFastforwardType.REWIND;
	context.FASTFORWARD	= RewindFastforwardType.FASTFORWARD;
	context.PLAY 		= PlayPauseType.PLAY;
	context.PAUSE		= PlayPauseType.PAUSE;
	context.NEXT		= NextPreviousType.NEXT;
    context.PREVIOUS	= NextPreviousType.PREVIOUS;
    */
    
	context.uuid = uuid;
	
	context.logInfo = function(type , value) {
		logger.info(args(arguments));
	};
	context.logWarn = function(type , value) {
		logger.warn(args(arguments));
	};
	context.logDebug = function(type , value) {
		logger.debug(args(arguments));
	};
	context.logError = function(type , value) {
		logger.error(args(arguments));
	};
	context.logTrace = function(type , value) {
		logger.trace(args(arguments));
	};
	
	
	context.console  = {};
	context.console.info = context.logInfo;
	context.console.warn = context.logWarn;
	context.console.debug = context.logDebug;
	context.console.error = context.logError;
	
	context.console.log = function(value) {
		logger.info("console.log", value);
	};
	
	context.isUndefined = function(item) {
		return isUndefinedState(item.state);
	};
	context.isUndefinedStr = function(itemStr) {
		return itemRegistry.getItem(itemStr) ? isUndefinedState(itemRegistry.getItem(itemStr).state) : true;
	};
	
	context.isUndefinedState = function(itemState) {
		if(itemState.toString() == "Uninitialized" || itemState.toString() == "Undefined")return true;
		return false;
	};
	
	context.getItem = function(it) {
		try {
			//print("################## "+itemRegistry.getItem(it));
			return (typeof it === 'string' || it instanceof String) ? itemRegistry.getItem(it) : it;
		}catch(err) {
			context.logError("getItem "+__LINE__, err);
		} 
		return null;
	};
	context.getItem.sendCommand = context.sendCommand;
	context.isUninitialized = function(it) {
		try {
			var item = context.getItem(it);
			if(item == null || item.state instanceof UnDefType || item.state.toString() == "Undefined" || item.state.toString() == "Uninitialized" )return true;
		}catch(err) {
			context.logError("isUninitialized "+__LINE__, err);
			return true;
		} 
		return false;
	};
	
	//returns item if exists, if got a value and this is not set, it will be updated
	context.updateIfUninitialized = function(it, val, getFromDB) {	
		try {
			var item = context.getItem(it);
			/*
			context.logInfo("|-|-updateIfUninitialized "+__LINE__, item +" -> "+val);	//val -> undefined
			context.logInfo("|-|-updateIfUninitialized "+__LINE__, isUninitialized(it));	//true
			context.logInfo("|-|-updateIfUninitialized "+__LINE__, val == undefined);    //true
			context.logInfo("|-|-updateIfUninitialized "+__LINE__, val == "undefined");  //false
			context.logInfo("|-|-updateIfUninitialized "+__LINE__, val === null);        //false
			context.logInfo("|-|-updateIfUninitialized "+__LINE__, val == null);         //true
			if(val){context.logInfo("|-|-updateIfUninitialized "+__LINE__, "val is defined!!!!")};
			if(item){context.logInfo("|-|-updateIfUninitialized "+__LINE__, "item is defined!!!!")}; //item is defined!!!!
			
			if(item && item.state instanceof UnDefType){
				if(item.type == 
			}
			*/
			if(item == undefined || item == null){
				context.error("updateIfUninitialized item not found "+__LINE__ + " item=" + item);
				return item;
			}
			if(getFromDB && isUninitialized(it)){
				var it_histval = historicState(it, now());
				if(it_histval != undefined){
					postUpdate( it, it_histval);
					context.logInfo("updateIfUninitialized use DB history "+__LINE__ + " it_histval=" + it_histval);
					return item;
				}
			}
			if( isUninitialized(it) && val != undefined){
				postUpdate( it, val);
				context.logInfo("updateIfUninitialized use gotten val "+__LINE__ + " val=" + val);
				return item;
			}
			return item;
		}catch(err) {
			context.logError("updateIfUninitialized "+__LINE__, err);
			return null;
		} 
		return null;
	};

	context.sendMail = function(mail, subject, message) {
		getAction("Mail").static.sendMail(mail, subject, message);
	};
	context.sendXMPP = function(mail, message) {
		getAction("XMPP").static.sendXMPP(mail, message);
	};
	context.transform = function(type, script, value) {
		//var myList = transform("JS", "wunderground.js", wundergr);//returns String
		//https://www.openhab.org/docs/configuration/transformations.html#usage
		context.logInfo("|-|-transform "+__LINE__, "type:" + type, "script:" + script, "content:" + value.substring(0, 40));
		var t = getAction("Transformation").static.transform;
		context.logInfo("|-|-transform "+__LINE__, "transform:" + t);

		getAction("Transformation").static.transform(type, script, value);
	};
	
	context.postUpdate = function(item, value) {
		try {
			events.postUpdate(item, value);
		}catch(err) {
			context.logError("utils.js postUpdate " + __LINE__ + ". Item: '" + item + "' with value: '" + value + "' ' Error:" +  err);
		}
	};
	
	context.sendCommand = function(item, value) {
		try {
			events.sendCommand(item, value);
		}catch(err) {
			context.logError("utils.js sendCommand " + __LINE__ + ". Item: '" + item + "' with value: '" + value + "' ' Error:" +  err);
		}
	};

	context.sendCommandLater = function(item, value, millis) {
		var zfunc = function(args){ 
			sendCommand(""+args[0], args[1]);
		};
		setTimeout( zfunc, millis || 1000, [item, value]);
	};
	
	//NOT TESTED YET: storeStates(Item...);
	context.storeStates = function(item) {
		events.storeStates((typeof item === 'string' || item instanceof String) ? itemRegistry.getItem(item) : item);
	};
	//NOT TESTED YET: restoreStates(Map<Item, State>);
	context.restoreStates = function(mapArray) {
		events.restoreStates(mapArray);
	};

	context.createTimer = function(time, runnable) {
		try{
			return ScriptExecution.createTimer(time, runnable);
		}catch(err) {
			context.logError("utils.js createTimer " + __LINE__ + " Error:" +  err);
		}
	};

	//https://blog.codecentric.de/en/2014/06/project-nashorn-javascript-jvm-polyglott/
	context.timerObject = {
		timerCount: 0,
		evLoops:[]
	};
	context.setTimeout = function(fn, millis, arg) {
		try{ 
			if( isFunction(fn) ){ //use
				var t = context.timerObject;
				if(t.timerCount > 999) t.timerCount = 0;
				var tCountLocal = t.timerCount + 1;
				t.timerCount = tCountLocal;
				t.evLoops[t.timerCount] = new Timer('jsEventLoop'+t.timerCount, false);
				t.evLoops[t.timerCount].schedule(function() {
					fn(arg);
					try{ 
						//cancel and purge itself
						if(t.evLoops[tCountLocal]){
							t.evLoops[tCountLocal].cancel();
							t.evLoops[tCountLocal].purge();
						}
					}catch(err) {
						context.logError("utils.js setTimeout " + __LINE__ + " Error:" +  err);
					}
				}, millis);
				return t.evLoops[t.timerCount];
			}else{
				context.logWarn("utils.js setTimeout " + __LINE__ + "Please use like: setTimeout(function, milliseconds, arguments)");
			}
		}catch(err) {
			context.logError("utils.js setTimeout " + __LINE__ + " Error:" +  err);
		}
	};

	//round(ungerundeter Wert, Stellen nach dem Komma); round(6,66666, 2); -> 6,67
	context.round = function( x, p) { return(Math.round(Math.pow(10, p)*x)/Math.pow(10, p));};
	
	//Joda for Java 7 and openHAB2 !!!!!!NICHT AUF LocalDateTime UMSCHALTEN!!!!!!
	//https://github.com/JodaOrg/joda-time/issues/81
	context.now = function() { return DateTime.now();};
	//Java8: 
	//context.now 				= function() { return LocalDateTime.now(); };
	context.zoneOffset 			= function() { return OffsetDateTime.now().getOffset(); }; // +02:00
	context.isoDateTimeString 	= function() { return context.now() + (""+context.zoneOffset()).split(":").join(""); }; // '2018-09-11T12:39:40.004+0200'
	context.dateString 			= function(kind) { 
		//https://www.programcreek.com/java-api-examples/?class=java.time.format.DateTimeFormatter&method=ofLocalizedDateTime
		//return DateTimeFormatter.ofLocalizedDateTime(FormatStyle.SHORT, FormatStyle.SHORT).ISO_LOCAL_DATE_TIME;
		//var n = LocalDateTime.now();
        //System.out.println("Before : " + n);
        //// DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        //var formatter = DateTimeFormatter.ofPattern("dd.MM.yyyy HH:mm:ss");
        //var formatDateTime = n.format(formatter);
		//System.out.println("After : " + formatDateTime);
		if(kind == "short")return LocalDateTime.now().format(DateTimeFormatter.ofPattern("dd.MM.yy HH:mm:ss"));
		return LocalDateTime.now().format(DateTimeFormatter.ofPattern("dd.MM.yyyy HH:mm:ss"));
	};
	
	context.getObjectProperties = function(obj) {
		for (var key in obj) {
			if (obj.hasOwnProperty(key)) {
				context.logInfo("", key+" = "+obj[""+key]);
			}
		}
	};
	
	//### getTriggeredData ###
	context.getTriggeredData = function(input) {
		
		//https://stackoverflow.com/questions/679915/how-do-i-test-for-an-empty-javascript-object
		//context.logInfo(typeof input);
		//context.logInfo(typeof input === "function");
		//context.logInfo(typeof input === "boolean");
		//context.logInfo(typeof input === "string");
		//context.logInfo(typeof input === "number");
		//context.logInfo(typeof input === "symbol");
		//context.logInfo(typeof input === "undefined");
		//context.logInfo(typeof input === "object");
		//context.logInfo("isEmpty: JSON.stringify(obj)="+JSON.stringify(input));
		//context.logInfo("isEmpty: JSON.stringify(obj)="+JSON.parse(input));
		//context.logInfo(isEmpty(input));
		
		context.logInfo("input", input);
		var ev = input.get("event")+"";
		context.logInfo("event",ev.split("'").join("").split("Item ").join("").split(" "));
		var evArr = [];
		if(context.strIncludes(ev, "triggered")){
			var atmp = ev.split(" triggered "); //astro:sun:local:astroDawn#event triggered START
			evArr = [atmp[0], "triggered", atmp[1]];
		}else{
			evArr = ev.split("'").join("").split("Item ").join("").split(" "); //Item 'benqth681_switch' received command ON
		}
		
		var d = {
			//size: 		input.size(),
			oldState:	input.get("oldState")+"",
			newState:	input.get("newState")+"",
			receivedCommand:	null,
			receivedState:		null,
			receivedTrigger:	null,
			itemName:	evArr[0]
		};
		
		switch (evArr[1]) {
			case "received":
				d.eventType = "command";
				d.triggerType = "ItemCommandTrigger";
				d.receivedCommand = input.get("command")+"";
				break;
			case "updated":
				d.eventType = "update";
				d.triggerType = "ItemStateUpdateTrigger";
				d.receivedState = input.get("state")+"";
				break;
			case "changed":
				d.eventType = "change";
				d.triggerType = "ItemStateChangeTrigger";
				break;
			case "triggered":
				d.eventType = "triggered";
				d.triggerType = "ChannelEventTrigger";
				d.receivedTrigger =	evArr[2];
				break;
			default:
				if(input.size() == 0){
					d.eventType = "time";
					d.triggerType = "GenericCronTrigger";
					d.triggerTypeOld = "TimerTrigger";
				}else{
					d.eventType = "";
					d.triggerType = "";
				}
		}		
		return d;
	};	
		
	//### getActions ###
	context.getActions = function() {
		if(actions == null){
			actions = {};
			var services = ScriptServiceUtil.getActionServices();
			if (services != null) {
				for (var actionService in services) {
					var cn = services[actionService].getActionClassName();
					var className = cn.substring(cn.lastIndexOf(".") + 1);
					actions[className] = services[actionService];
					actionList[actionService] = className;
				}
			}
		}
		logInfo("actions = " + actions);
		logInfo("actionList = " + actionList);
		return actions;
	};
	context.getActionList = function(str) {
		if(actions == null){
			actions = getActions();
		}
		return actionList;
	};
	context.getAction = function(str) {
		if(actions == null){
			actions = getActions();
		}
		return actions[str].getActionClass();
	};
	
	//### ExecUtil ###
	context.executeCommandLine = function(commandLine) {
		if(commandLine == null || commandLine == "" ){
			return null;
		}
		return ExecUtil.executeCommandLine(commandLine);
	};
	context.executeCommandLineAndWaitResponse = function(commandLine, timeout) {
		if(commandLine == null || commandLine == "" ){
			return null;
		}
		return ExecUtil.executeCommandLineAndWaitResponse(commandLine, timeout);
	};



	/**
	 * SIEHE ### getActions ### in utils.js
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

	context.HttpUtil = HttpUtil;
	//sendHttpGetRequest(String url): Sends an GET-HTTP request and returns the result as a String
	context.sendHttpGetRequest = function(url, timeout) {
		//logInfo("arguments = " + arguments, arguments.length);
		return context.executeUrl("GET", url, timeout);
	};
	//sendHttpPutRequest(String url, Sting contentType, String content): Sends a PUT-HTTP request with the given content and returns the result as a String
	//sendHttpPutRequest(String url): Sends a PUT-HTTP request and returns the result as a String
	context.sendHttpPutRequest = function(url, timeout) {
		return context.executeUrl("PUT", url, timeout);
	};
    //sendHttpPostRequest(String url, String contentType, String content): Sends a POST-HTTP request with the given content and returns the result as a String
	//sendHttpPostRequest(String url): Sends a POST-HTTP request and returns the result as a String
	context.sendHttpPostRequest = function(url, timeout) {
		return context.executeUrl("POST", url, timeout);
	};
    //sendHttpDeleteRequest(String url): Sends a DELETE-HTTP request and returns the result as a String
	context.sendHttpDeleteRequest = function(url, timeout) {
		return context.executeUrl("DELETE", url, timeout);
	};
	context.executeUrl = function(httpMethod, url, timeout) {
		if(url == undefined || url == null || url == "" ){ return null; }
		if(timeout == undefined ){ timeout = 5000; }
		return HttpUtil.executeUrl(httpMethod, url, timeout);
	};
	//like getAction("Lewi").static.sendHttpPostRequest(posturl, header, "", timeout); 
	// NOW    => executeUrlPostWithContent(posturl, "", header, timeout);
	// BETTER =>     executeUrlWithContent("POST", posturl, null, "", header, timeout);
	//context.executeUrlPostWithContent = function(url, content, contentType, timeout) {
	//	return context.executeUrlWithContent("POST", url, null, content, contentType, timeout); 
	//};
	//executeUrl(String httpMethod, String url, Properties httpHeaders, InputStream content, String contentType, int timeout) 
	context.executeUrlWithContent = function(httpMethod, url, httpHeaders, content, contentType, timeout) {
		logInfo("httpMethod = " + httpMethod);
		logInfo("url = " + url);
		logInfo("httpHeaders = " + httpHeaders);
		logInfo("content = " + content);
		logInfo("contentType = " + contentType);
		logInfo("timeout = " + timeout);
		if(httpMethod == undefined || httpMethod == null){ httpMethod = "POST"; }
		if(url == undefined || url == null || url == "" ){ return null; }
		if(httpHeaders == undefined ){ httpHeaders = null; }
		if(content == undefined || content == null ){ content = ""; }
		if(contentType == undefined || contentType == null ){ contentType = ""; }
		if(timeout == undefined || timeout == null ){ timeout = 5000; }
		return HttpUtil.executeUrl(httpMethod, url, httpHeaders, IOUtils.toInputStream(content), contentType, timeout); 
	};
	
	/** STRING FUNCTIONS **/
	context.endTrim = function(x) {
		return x.replace(/\s*$/,'');
	}
	context.endTrim = function(x) {
		return x.replace(/^\s+/g, '');
	}
	context.endAndStartTrim = function(x) {
		return x.replace(/^\s+|\s+$/gm,'');
	}
	context.allTrim = function(x) {
		return x.replace(/^\s+|\s+$/gm,'');
	}
	context.strIncludes = function(str, x) {
		return str.indexOf(x) != -1 ? true : false;
	}

	/** JAVA COLLECTION TO ARRAY **/
	context.javaCollectionToArray = function( jCollection){
		try{ 
			var jsArray = [];
			jCollection.forEach(function(key) {
				jsArray.push(key);
			});
			return jsArray;
		}catch(err) {
			context.logError("utils.js javaCollectionToArray " + __LINE__ + " Error:" +  err);
		}
		return null;
		
	}
	context.includes = function( obj, val ){
		try{ 
			for (var key in obj) {
				if(val != undefined && val == key+"")return true;
			};
		}catch(err) {
			context.logError("utils.js includes " + __LINE__ + " Error:" +  err);
			return false;
		}
		return false;
	}

	//### Locals vars/functions
	var actions = null;
	var actionList = [];

	var args = function(a) {
		var um = a.length > 1 ? "\n" : "";
		var s1 = "";
		for(var i in a){
			if(i == 0){
				s1 = "|" + a[i] +"| ";
			}else{
				s1 += um + i + ":'" + a[i] +"' ";
			}
		}
		return s1 + um;
	};
	
	// Is Object empty?
	var isEmpty = function(obj) {
		for(var prop in obj) {
			if(obj.hasOwnProperty(prop)){
				context.logInfo("isEmpty: prop="+prop);
				return false;
			}
		}
		context.logInfo("isEmpty: JSON.stringify(obj)="+JSON.stringify(obj));
		context.logInfo("isEmpty: JSON.stringify({})="+JSON.stringify({}));
		return JSON.stringify(obj) === JSON.stringify({});
	}

	var isFunction = function(v) {
		if (v instanceof Function) { 
			return true;
		}
		return false
	};
	
	
})(this);
