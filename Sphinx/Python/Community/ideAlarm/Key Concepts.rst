============
Key Concepts
============

Reliability
===========

A dedicated home security system might provide higher reliability than what you achive by a DIY system.
It depends how you set things up.
With that said, in case don't already own a dedicated home security system but you still want to take advantage of the capabilities of your home automation system together with all its sensors you might want to use it to set up your own DIY home alarm system.
Please make sure that you've read and understood the disclaimer.


Helps You to Maintain Safety Also When Unarmed
==============================================

ideAlarm has an optional feature that you can use to alert you about doors, windows etc that you have forgotten to close.
We call this feature nagging.


Alarm Zones
===========

Your ideAlarm system will have one or more [zones].
Zones might be areas located at different places.
You might also want to use place certain kind of detectors in a separate zone (like water leak detectors) and always keep that zone armed.
If an alert occurs the system informs you which zone is alerting and what sensor has been triggered.


Highly Customizable
===================

ideAlarm has a number of predefined events that will trigger your custom event helpers.
These will not be overwritten when upgrading.
That way you can choose whatever shall happen on those events.


Alarm Zone State
================

Each Alarm Zone has an openHAB Item that holds one of the following states: 'Normal', 'Arming', 'Alert', 'Error', 'Tripped' or 'Timed out'.


Alarm Zone Arming Mode
======================

Each Alarm Zone has an openHAB Item that holds one of the following arming modes: 'Disarmed', 'Armed Home', or 'Armed Away'.


A Sensor Can Be Enabled or Disabled
===================================

For your convenience you can easily enable or disable a sensor in the configuration file.
If you wish you can also declare a function for a specific sensor in the configuration file that allows the sensor to be automatically enabled for example only when it's dark or depending on the state of other openHAB Items.
If you have implemented presence detection in your system, you could for example disable a specific sensor when you are at home.
