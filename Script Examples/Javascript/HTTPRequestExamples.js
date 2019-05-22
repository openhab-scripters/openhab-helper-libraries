/**
 * Copyright (c) 2019 Contributors to the openHAB Scripters project
 * 
 * @author Helmut Lehmeyer 
 */

'use strict';

load(Java.type("java.lang.System").getenv("OPENHAB_CONF")+'/automation/lib/javascript/core/JSRule.js');

var me = "HTTPRequestExamples.js";
logInfo("################# "+me+" ##################");

JSRule({
	name: me+" NativeHTTPRequestExamples",
	description: "Native HTTPRequestExamples L:"+__LINE__,
	triggers: [ 
		//TimerTrigger("0/15 * * * * ?")
	],
	execute: function( module, input){ 
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");

		var url = "http://demo.openhab.org:8080/rest/";
		var timeout = 5000;

		// Native Java
		var HttpUtilNativ = Java.type("org.eclipse.smarthome.io.net.http.HttpUtil");
		var results = HttpUtilNativ.executeUrl("GET", url, timeout);
		logInfo("results GET: ", results);
		results = HttpUtilNativ.executeUrl("PUT", url, timeout);
		logInfo("results PUT: ", results);
		results = HttpUtilNativ.executeUrl("POST", url, timeout);
		logInfo("results POST: ", results);
	}
});

JSRule({
	name: me+" XMLHttpRequestJavaScript",
	description: "XMLHttpRequest Native JavaScript L:"+__LINE__,
	triggers: [ 
		//TimerTrigger("0/15 * * * * ?")
	],
	execute: function( module, input){ 
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");

		var url = "http://demo.openhab.org:8080/rest/";
		var timeout = 5000;

		// Native JavaScript
		// global JavaScript functions such as setTimeout, setInterval or XMLHttpRequest do not exist in Nashorn.
		// https://blog.codecentric.de/en/2014/06/project-nashorn-javascript-jvm-polyglott/

	}
});

JSRule({
	name: me+" HTTPRequestExamples",
	description: "HTTPRequestExamples L:"+__LINE__,
	triggers: [ 
		//TimerTrigger("0/15 * * * * ?")
	],
	execute: function( module, input){ 
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");

		var url = "http://demo.openhab.org:8080/rest/";
		var timeout = 5000;

		// Library
		var results = sendHttpGetRequest(url, timeout);
		logInfo("results sendHttpGetRequest: ", results);
		results = sendHttpPutRequest(url, timeout);
		logInfo("results sendHttpPutRequest: ", results);
		results = sendHttpPostRequest(url, timeout);
		logInfo("results sendHttpPostRequest: ", results);
		results = sendHttpDeleteRequest(url, timeout);
		logInfo("results sendHttpDeleteRequest: ", results);
		
		//  Library executeUrlWithContent( httpMethod, url, httpHeaders, content, contentType, timeout)
		var header  = "application/x-www-form-urlencoded; charset=UTF-8";
		var results = executeUrlWithContent("POST", url, null, "", header, timeout);
		logInfo("results executeUrlWithContent: ", results);

	}
});

