======================
ideAlarm Event Helpers
======================

Naming
======

When you installed ideAlarm you placed two example files in ``$OPENHAB_CONF/automation/lib/python/personal/idealarm`` named ``custom_template_verbose.py.example`` and ``custom_template.py.example``.
Have a good look at them and choose the one that best suit your needs.
Then rename that file to ``custom.py``.
This is now your personal Custom Helper Functions library.


Custom Helper Functions for Various Alarm Events
================================================

Every installation is unique and has it's own needs.
Therefore, ideAlarm has a number of alarm events that will trigger your ``custom.py`` script functions (if you choose to define them).
That way you can choose whatever shall happen at those events.
You define those functions in the event helpers file (``custom.py``).
The helper functions provides useful ideAlarm objects that makes your custom scripting easy.


The Different Events
====================

.. code-block::

    onArmingModeChange(zone, newArmingMode, oldArmingMode)

This function will be called when there is a change of arming mode for a zone.

Function arguments:

zone: The zone object.
newArmingMode: The current arming mode.
oldArmingMode: The previous arming mode.

.. code-block::

    onZoneStatusChange(zone, newZoneStatus, oldZoneStatus, errorMessage=None)

This function will be called when there is a change of zone status.
``oldZoneStatus`` is None when initializing.

Function arguments:

- zone: The zone object.
- newZoneStatus: The current zone status.
- oldZoneStatus: The previous zone status.
- errorMessage: Holds an error message (string) when an error has occurred, typically when trying to arm a zone with tripped sensors.

.. code-block::

    onArmingWithOpenSensors(zone, armingMode)

There might be open sensors when trying to arm, so this function gets called.
That doesn't necessarily need to be an error condition.
However, if the zone has been configured not to allow opened sensors during arming, the function ``onZoneStatusChange`` will be called with status ERROR.

Function arguments:

- zone: The zone object.
- armingMode: The current arming mode.

.. code-block::

    onNagTimer(zone, nagSensors)

If you have set up "nagging", this function will be called to remind you to close them.

Function arguments:

- zone: The zone object.
- nagSensors: A Python list with all sensor objects that have been active (OPEN, ON) for too long.
