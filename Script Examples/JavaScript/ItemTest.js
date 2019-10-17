/**
 * Test rules testing Item functionality
 * 
 * Copyright (c) 2019 Contributors to the openHAB Scripters project
 * 
 * @author Helmut Lehmeyer - initial contribution
 */

/*
REQUIRES:
Call    Call_Item
Color    Color_Item
Contact    Contact_Item
DateTime    DateTime_Item
Dimmer    Dimmer_Item
Location    Location_Item
Number    Number_Item
Player    Player_Item
Rollershutter    Rollershutter_Item
String    String_Item
Switch    Switch_Item
*/
'use strict';

load(Java.type("java.lang.System").getenv("OPENHAB_CONF")+'/automation/lib/javascript/core/init.js');

var rules = require('rules');
var triggers = require('triggers');
var utils = require('utils');

rules.JSRule({
	name: me+" L"+__LINE__,
	description: "Set Items"+__LINE__,
	triggers: [ 
		triggers.TimerTrigger("0/5 * * * * ?")//, //alle 5 sec
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
        utils.postUpdate("Call_Item", ["017922399","0919162559"] );
        utils.postUpdate("Call_Item", "017922398,0919162558" );
        utils.postUpdate("Call_Item", sl );

        //################
        //## Color
        var h = new DecimalType(11.0);
		var s = new PercentType(77);
        var v = new PercentType(99);
        var hsv = new HSBType(h,s,v);
		utils.sendCommand("Color_Item", hsv);
		utils.sendCommand("Color_Item", new PercentType(getRandom100()));
		utils.sendCommand("Color_Item", OFF);
		utils.sendCommand("Color_Item", new HSBType(getRandom360() + "," + getRandom100() + "," + getRandom100()));//as String
		utils.sendCommand("Color_Item", new PercentType(getRandom100()+""));//as String
        utils.sendCommand("Color_Item","ON");//as String
        //Example for conversion to 8-bit representation
        var Color_Item = utils.getItem("Color_Item");
        var hsvs = new HSBType( Color_Item.state );
        logInfo("################ Color_Item.state:", Color_Item.state);
        var red   = Math.round(hsvs.red * 2.55);
        var green = Math.round(hsvs.green * 2.55);
        var blue  = Math.round(hsvs.blue * 2.55);
        logInfo("################  red, green, blue:", red + "," + green + "," + blue);
    
        //################
        //## Contact
        utils.postUpdate("Contact_Item", getRandom2str([OPEN,CLOSED]));

         //################
        //## DateTime 
        //Format: '2018-09-11T11:21:17.029+0200'
        utils.postUpdate("DateTime_Item", isoDateTimeString());

        //################
        //## Dimmer
        utils.postUpdate("Dimmer_Item", getRandom100());

        //################
        //## Group
        //postUpdate("Group_item", "");

        //################
        //## Image
        //postUpdate("Image_item", "");

        //################
        //## Location
        utils.postUpdate("Location_Item", new PointType("52.5200066,13.4049540"));

        //################
        //## Number
        utils.postUpdate("Number_Item", getRandom100());

        //################
        //## Player
        utils.sendCommand("Player_Item", getRandom4str([PREVIOUS,PAUSE,PLAY,NEXT]));

        //################
        //## Rollershutter
        utils.sendCommand("Rollershutter_Item", getRandom4str([UP,DOWN,STOP,getRandom100()]));

        //################
        //## String
        utils.postUpdate("String_Item", getRandom2str(["str1","str2"]));

        //################
        //## Switch
        utils.postUpdate("Switch_Item", getRandom2str([ON,OFF]));	
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

