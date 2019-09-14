===
API
===

About the API
=============

For basic usage you can interact with ideAlarm (e.g. arming and disarming) using the openHAB GUI or by scripts using the openHAB Items that you have created for each alarm zone.
You can also make scripts trigger on the change of of the openHAB Items that you've created for each zone.
ideAlarm aims to make it easier for you to develop scripts by exposing definitions from a the ideAlarm module.
Those definitions can be imported into your ordinary jython scripts allowing you to interact with ideAlarm using the functions described on this page.


Preparations
============

Before you can use the ideAlarm definitions in your scripts, you need to import the ideAlarm module by inserting a single line of code like in the following example.

.. code-block::

    from community.idealarm import ideAlarm, ARMINGMODE, ZONESTATUS

Just insert the code at the beginning of your Jython script together with your other imports.
The above example will give you access to the ideAlarm object and to the ``ARMINGMODE`` and ``ZONESTATUS`` "constants" (python dictionaries).

.. code-block::

    ZONESTATUS = {'NORMAL': 0, 'ALERT': 1, 'ERROR': 2, 'TRIPPED': 3, 'ARMING': 4}
    ARMINGMODE = {'DISARMED': 0, 'ARMED_HOME': 1, 'ARMED_AWAY': 2}


The ideAlarm Object
===================

The ideAlarm object is the top level parent object of ideAlarm.
It provides functions to query and manipulate your ideAlarm system.

* ideAlarm.isArmed(zone='1')
    * Returns True if the zone given is armed.
    * **Parameters**
        * zone: (integer or string) The zone's name or ordinal number.
          Defaults to the zone first defined in the configuration file.
    * **Return value**
        * (boolean)
    * **Usage example**
        * ``if ideAlarm.isArmed('My Home'):``

* ideAlarm.isDisArmed(zone='1')
    * Returns True if the zone given is disarmed.
    * **Parameters**
        * zone: (integer or string) The zone's name or ordinal number.
          Defaults to the zone first defined in the configuration file.
    * **Return value**
        * (boolean)
    * **Usage example**
        * ``if ideAlarm.isDisArmed('My Home'):``

* ideAlarm.getZoneStatus(zone='1')
    * Returns the given zone's status.
    * **Parameters**
        * zone: (integer or string) The zone's name or ordinal number.
          Defaults to the zone first defined in the configuration file.
    * **Return value**
        * (integer) The return value refers to the ``ZONESTATUS`` constant.
    * **Usage example**
        * ``if ideAlarm.getZoneStatus('My Home') in [ZONESTATUS['ALERT'], ZONESTATUS['TRIPPED']]:``

* ideAlarm.getAlertingZonesCount()
    * Returns the total count of alarm zones which has the status ``ZONESTATUS['ALERT']``.
    * **Return value**
        * (integer)
    * **Usage example**
        * ``numAlertingZones = ideAlarm.getAlertingZonesCount()``
