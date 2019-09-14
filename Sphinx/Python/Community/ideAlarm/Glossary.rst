========
Glossary
========

.. glossary::

    Alarm
        Alarm (e.g. alarm system) is a system that gives an audible, visual or other form of alarm signal about a problem or condition.

    Alarm State
        Alarm State is the state of a zone. It can be one of "Normal", "Arming", "Alert", "Error", "Tripped" or "Timed Out".

    Alert
        Alert is an alarm state that typically causes the sirens (if any) to sound.

    Arming
        "Arming" is the action of putting a zone into a an arming mode of "Armed Away" or "Armed Home".
        The delay before the zone enters the new arming mode is called exit delay.

    Arming Mode
        The arming mode state tells the alarm system how react when a sensor in a zone is detecting an open door for example.
        There are three possible arming modes.
        If the arming mode is "Disarmed" nothing will happen.
        However if the arming mode is set to "Armed Away" or "Armed Home" then (depending on the sensor class) the sensor will be considered as tripped and might trigger an alarm state change.

    Armed Away
        "Armed Away" is an arming mode state that is typically used when there is no one at home.

    Armed Home
        "Armed Home" is an arming mode state that is typically used when there is someone at home, possibly sleeping.

    Disarmed
        "Disarmed" is an arming mode state that is typically used to prevent any alerts to occur even if sensors might for example be indicating that a door is open.

    Disarming
        "Disarming" is the action to change an armed zone into a disarmed.

    Entry delay
        The time delay in seconds before an alert occurs after a sensor has been tripped.

    Error
        Error is an alarm state that informs that an error has occurred in the alarm zone.

    Exit delay
        The time delay in seconds between the point of arming and the point when the new arming mode becomes active.
        During the delay, triggering a sensor (opening a door or moving in front of a motion sensor, etc.) will not cause an alert.

    ideAlarm
        ideAlarm is the name of this alarm system. It was formed putting the two words ideal and alarm together.

    Nagging
        IdeAlarm can be set up to harass you constantly to close doors and windows that you have forgotten to lock/close.

    openHAB
        A vendor and technology agnostic open source automation software for your home.
        For more information visit: The [openHAB Home Page](https://www.openhab.org/).

    Sensor
        A sensor is an electronic device whose purpose is to detect events or changes in its environment and send the information to openHAB.

    Sensor class
        Each sensor is associated with one of two sensor classes (SENSOR_CLASS_A or SENSOR_CLASS_B).
        SENSOR_CLASS_A, sensor can be tripped in both arming modes. E.g. "Armed Home" and "Armed Away".
        SENSOR_CLASS_B, sensor can be tripped in arming mode "Armed Away" only.

    Siren
        A siren is a loud noise making device.

    Timed Out
        "Timed Out" is an alarm state that will happen if an entry delay has passed without disarming the zone.

    Trigger
        Trigger or triggering is the... CONTENT NEEDED

    Tripped
        Tripped is a sensor logical state in the context of an arming mode.
        When a sensor is tripped, it will trigger an alarm state change.
        For example, a sensor that has detected an open door.
        For a sensor to be considered as tripped, it must first have detected the change (e.g. a door is open, smoke is detected etc..) and then the tripped condition will be evaluated in the context of the alarms current arming mode and the sensor's sensor class.
        A sensor will never be considered to be tripped if the zone is disarmed.

    Tripping
        Tripping is the action to ... TODO: Is there a confusion between tripping and triggering?

    Zone
        Sensors are connected to ideAlarm grouped together as a Zone (sometimes referred to as alarm zone) for the purpose of better identifying and controlling alarm conditions.
        A zone can be restricted to a specific geographical area like your entire home or a garden shed but you can also put a certain kind of sensors like smoke detectors in a zone.
        Each zone can be individually armed and configured.
