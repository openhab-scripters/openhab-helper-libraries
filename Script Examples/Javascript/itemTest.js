/**
 * Copyright (c) 2019 by Helmut Lehmeyer.
 * 
 * @author Helmut Lehmeyer 
 */

'use strict';
var OPENHAB_CONF = Java.type("java.lang.System").getenv("OPENHAB_CONF"); // most this is /etc/openhab2
load(OPENHAB_CONF+'/automation/lib/javascript/core/JSRule.js');

var me = "itemTest.js";
logInfo("################# "+me+" ##################");

//var count=0;

JSRule({
	name: me+" L"+__LINE__,
	description: "Set Items"+__LINE__,
	triggers: [ 
		TimerTrigger("0/5 * * * * ?")//, //alle 15 sec
		//TimerTrigger("0/15 * * * * ?"), //alle 15 sec
		//TimerTrigger("0 0/5 * * * ?"), //alle 5 Minuten
		//TimerTrigger("53 0 8 * * ?") //8:00:53
	],
	execute: function( module, input){
		logInfo("################ "+me+" Line: "+__LINE__+"  #################");
		//logInfo("################ postUpdate:",postUpdate);
		//logInfo("################ sendCommand:",sendCommand);
		//logInfo("################ events.sendCommand:",events.sendCommand);
        //logInfo("################ events.storeStates:",events.storeStates);
        
        //https://community.openhab.org/t/curl-and-executecommandline/27184
        //var image = executeCommandLineAndWaitResponse("bash "+ automationPath + "getImage.sh https://loremflickr.com/320/240&"+count++, 5000);
        //var currentPath = executeCommandLineAndWaitResponse("bash " + automationPath + "getFolder.sh", 1000);
		//logInfo("################ currentPath:"+currentPath);
		//logInfo("################ OFF:",OFF);
		//logInfo("################ PREVIOUS,PAUSE,PLAY,NEXT:",PREVIOUS,PAUSE,PLAY,NEXT);
		//logInfo("################ UP,DOWN,STOP:",UP,DOWN,STOP);
		//logInfo("################ OpenClosedType:",OpenClosedType);
		//logInfo("################ OPEN,CLOSE:",OPEN,CLOSED);
		//logInfo("################ HSBType:",HSBType);
		//logInfo("################ PercentType:",PercentType);
		//logInfo("################ StringListType:",StringListType);
		//logInfo("################ CallType:",CallType);// old oh1 style does not work anymore
		//logInfo("################ Color_Item:",updateIfUninitialized("Color_Item"));

        //https://community.openhab.org/t/type-conversions/32684

        //## Call //ONLY postUpdate?!
        //var sl = new StringListType("017922398##0919162558");
        var sl = new StringListType("017922398,0919162558");
        postUpdate("Call_Item", ["017922399","0919162559"] );
        postUpdate("Call_Item", "017922398,0919162558" );
        postUpdate("Call_Item", sl );

        //################
        //## Color
        var h = new DecimalType(11.0);
		var s = new PercentType(77);
        var v = new PercentType(99);
        var hsv = new HSBType(h,s,v);
		sendCommand("Color_Item", hsv);
		sendCommand("Color_Item", new PercentType(getRandom100()));
		sendCommand("Color_Item", OFF);
		sendCommand("Color_Item", new HSBType(getRandom100() + "," + getRandom100() + "," + getRandom100()));//as String
		sendCommand("Color_Item", new PercentType(getRandom100()+""));//as String
        sendCommand("Color_Item","ON");//as String
        //Example for conversion to 8-bit representation
        var Color_Item = getItem("Color_Item");
        var hsvs = new HSBType( Color_Item.state );
        logInfo("################ Color_Item.state:", Color_Item.state);
        var red   = Math.round(hsvs.red * 2.55);
        var green = Math.round(hsvs.green * 2.55);
        var blue  = Math.round(hsvs.blue * 2.55);
        logInfo("################  red, green, blue:", red + "," + green + "," + blue);
    
        //################
        //## Contact
     	postUpdate("Contact_Item", getRandom2str([OPEN,CLOSED]));

         //################
        //## DateTime 
        //Format: '2018-09-11T11:21:17.029+0200'
        postUpdate("DateTime_Item", isoDateTimeString());

        //################
        //## Dimmer
        postUpdate("Dimmer_Item", getRandom100());

        //################
        //## Group
        //postUpdate("Group_item", "");

        //################
        //## Image
        //postUpdate("Image_item", "");

        //################
        //## Location
        postUpdate("Location_Item", new PointType("52.5200066,13.4049540"));

        //################
        //## Number
        postUpdate("Number_Item", getRandom100());

        //################
        //## Player
        sendCommand("Player_Item", getRandom4str([PREVIOUS,PAUSE,PLAY,NEXT]));

        //################
        //## Rollershutter
        sendCommand("Rollershutter_Item", getRandom4str([UP,DOWN,STOP,getRandom100()]));

        //################
        //## String
        postUpdate("String_Item", getRandom2str(["str1","str2"]));

        //################
        //## Switch
        postUpdate("Switch_Item", getRandom2str([ON,OFF]));	
	}
});

var getRandom254 = function(){
    return Math.floor(Math.random() * 255);
}
var getRandom100 = function(){
    return Math.floor(Math.random() * 100);
}

var getRandom2str = function(str){
    return Math.random() > 0.5 ? str[0] : str[1];
}
var getRandom4str = function(str){
    return Math.random() > 0.5 ? getRandom2str([str[0], str[1]]) : getRandom2str([str[2], str[3]]);
}

