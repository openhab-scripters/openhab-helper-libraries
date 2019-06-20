====================
Arming and Disarming
====================

There are a few ways that you can arm and disarm an ideAlarm zone.


Using the openHAB Web GUI
=========================

You can of course use the openHAB web GUI to switch the arming mode.
This is not very convenient though and is probably useful only for testing.


Programatically (e.g. using scripts)
====================================

You can make scrips in any of openHAB's scripting environments.
Below are two JSR223 Jython script examples.
Both of them are based on Jython scripting for openHAB.


A Simple Jython Script Example
------------------------------

.. code-block::

    from core.rules import rule
    from core.triggers import when

    @rule("Bedroom arming", description="This is the bed room arming rule")
    @when("Item Bedroom_Switch changed to ON")
    def bedroom_arming(event):
        bedroom_arming.log.info('Bedroom button pushed')
        events.sendCommand('Toggle_Z1_Armed_Home', 'ON')


A Little Bit More Advanced Jython Example
-----------------------------------------

If you have a physical button device that you want to push 3 times within 10 seconds to toggle the arming mode.
You may want to do like this to make things more obscure, for example if you just use a lighting switch beside the entrance door for arming and disarming.
Security through obscurity in the example below, that physical button Item is named 'Spider_Pig_Button'.
It's also using the getItemValue function from mylib.

.. code-block::

    from core.rules import rule
    from core.triggers import when
    from core.utils import getItemValue

    @rule("Spider Pig rule", description="Keeps track of how many times the Spider Pig Button has been pressed. Counter will be reset by the expire binding.")
    @when("Item Spider_Pig_Button changed to ON")
    def spider_pig(event):
        qty = getItemValue('Count_Spider_Pig', 0)
        spider_pig.log.info('Spider pig was pressed. Qty={}.'.format(qty+1))
        if qty == 2:
            events.sendCommand('Toggle_Z1_Armed_Away', 'ON')
        events.postUpdate('Count_Spider_Pig', str(qty+1))

Here is how the definition of the 2 Items might look like:

.. code-block::

    Number Count_Spider_Pig  {expire="10s,command=0"}
    Switch Spider_Pig_Button "Spider pig button" <switch> {channel="zwave:device:XXXXXXX:nodeNN:sensor_binary1"}


MQTT Alarm Control Panel
========================

(Untested) You can easily integrate an Alarm Control Panel that communicates using MQTT.
For example, the MQTT Alarm Control Panel for Home Assistant project might work well for integration with ideAlarm.


Prerequisites
-------------

You'd need to:

#. Set up a MQTT server.
   Unless you already have one you'd probably want to set up a MQTT message broker such as Mosquitto on the same server as the one that runs openHAB.
#. openHAB MQTT Binding should be installed and configured.
#. Add two openHAB Items like in the example below:

.. code-block::

    String Alarm_CPanel_State   "Alarm CPanel state [%s]" {channel="mqtt:topic:alarmpanel:XXXXXX"}
    String Alarm_CPanel_Command "Alarm CPanel command [%s]" {channel="mqtt:topic:alarmpanel:XXXXX"}

The Alarm Control Panel will send an update to the ``Alarm_CPanel_Command`` Item with a payload to notify ideAlarm to arm or disarm.
The MQTT service will use the ``Alarm_CPanel_State`` Item with the payload to notify the Alarm Control Panel of the current ideAlarm state, which will update the interface accordingly.

When the prerequisites are met, it's time to make a Custom Helper Function in ``custom.py`` that will synchronize your newly created Items ``Alarm_CPanel_State`` and ``Alarm_CPanel_Command`` with an ideAlarm zone.
See `Python/Community/IdeAlarm/Configuration:Event helpers`.
There's a template custom script that we will use as a starter.
Note that this is a Python library script so you'd have to reload the Jython rule binding before any changes that you make to the file takes effect.

Change the function ``onArmingModeChange`` so that it updates the ``Alarm_CPanel_State`` Item when there is a change of arming mode for a zone.
Below is an example:

.. code-block::

    def onArmingModeChange(zone, newArmingMode, oldArmingMode):
        """
        This function will be called when there is a change of arming mode for a zone.
        oldArmingMode is None when initializing.
        """
        if zone.zoneNumber == 1:
            if oldArmingMode is not None:
                pass

            if newArmingMode == ARMINGMODE['DISARMED']:
                events.sendCommand('Alarm_CPanel_State', 'disarmed')
            elif newArmingMode == ARMINGMODE['ARMED_HOME']:
                events.sendCommand('Alarm_CPanel_State', 'armed_home')
            elif newArmingMode == ARMINGMODE['ARMED_AWAY']:
                events.sendCommand('Alarm_CPanel_State', 'armed_away')

            log.debug(u"onArmingModeChange: [{}] ---> [{}]".format(zone.name.decode('utf8'), kw(ARMINGMODE, newArmingMode)))


For syncing the new arming modes that comes from the Alarm Control Panel, we create a regular Jython script.
Below is an example of that:

.. code-block::

    from core.rules import rule
    from core.triggers import when
    from community.idealarm import ideAlarm, ARMINGMODE

    @rule("Sync APC commands", description="MQTT Alarm Control Panel synchronization")
    @when("Item Alarm_CPanel_Command changed")
    def sync_apc_commands(event):
        if event.itemState == 'ARM_HOME' and ideAlarm.getZoneStatus('MY_ZONE_NAME') != ARMINGMODE['ARMED_HOME']:
            ideAlarm.alarmZones[ideAlarm.getZoneIndex('MY_ZONE_NAME')].setArmingMode(ARMINGMODE['ARMED_HOME'])
        elif event.itemState == 'ARM_AWAY' and ideAlarm.getZoneStatus('MY_ZONE_NAME') != ARMINGMODE['ARMED_AWAY']:
            ideAlarm.alarmZones[ideAlarm.getZoneIndex('MY_ZONE_NAME')].setArmingMode(ARMINGMODE['ARMED_AWAY'])
        elif event.itemState == 'DISARM' and ideAlarm.getZoneStatus('MY_ZONE_NAME') != ARMINGMODE['DISARMED']:
            ideAlarm.alarmZones[ideAlarm.getZoneIndex('MY_ZONE_NAME')].setArmingMode(ARMINGMODE['DISARMED'])
