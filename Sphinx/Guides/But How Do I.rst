****************
But How Do I...?
****************

Single line comment
-------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            # this is a single line comment

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            // this is a single line comment

    .. group-tab:: Groovy

        .. code-block:: Groovy

            // this is a single line comment

    .. group-tab:: Rules DSL

        .. code-block:: java

            // this is a single line comment


Multiline comment
-----------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            '''
            this is
            a multiline
            comment
            '''

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            /*
            this is
            a multiline
            comment
            */

    .. group-tab:: Groovy

        .. code-block:: Groovy

            /*
            this is
            a multiline
            comment
            */

    .. group-tab:: Rules DSL

        .. code-block:: java

            /*
            this is
            a multiline
            comment
            */


Get an Item
-----------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            itemRegistry.getItem("My_Item")
            # or
            ir.getItem("My_Item")

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            itemRegistry.getItem("My_Item")
            // or
            ir.getItem("My_Item")

    .. group-tab:: Groovy

        .. code-block:: Groovy

            itemRegistry.getItem("My_Item")
            // or
            ir.getItem("My_Item")

    .. group-tab:: Rules DSL

        .. code-block:: java

            My_Item


Get the state of an Item
------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            items["My_Item"]
            # or after importing anything within the ``core`` package
            items.My_Item
            # or
            ir.getItem("My_Item").state

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            items["My_Item"]
            // or
            ir.getItem("My_Item").state

    .. group-tab:: Groovy

        .. code-block:: Groovy

            items["My_Item"]
            // or
            ir.getItem("My_Item").state

    .. group-tab:: Rules DSL

        .. code-block:: java

            My_Item.state


Get the triggering Item
-----------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            ir.getItem(event.itemName)

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            ir.getItem(event.itemName)

    .. group-tab:: Groovy

        .. code-block:: Groovy

            ir.getItem(event.itemName)

    .. group-tab:: Rules DSL

        .. code-block:: java

            triggeringItem


Get the triggering Item's name
------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            event.itemName

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            event.itemName

    .. group-tab:: Groovy

        .. code-block:: Groovy

            event.itemName

    .. group-tab:: Rules DSL

        .. code-block:: java

            triggeringItem.name


Get the triggering Item's state
-------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            event.itemState

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            event.itemState

    .. group-tab:: Groovy

        .. code-block:: Groovy

            event.itemState

    .. group-tab:: Rules DSL

        .. code-block:: java

            triggeringItem.state


Get the triggeringItem's previous state
---------------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            event.oldItemState

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            event.oldItemState

    .. group-tab:: Groovy

        .. code-block:: Groovy

            event.oldItemState

    .. group-tab:: Rules DSL

        .. code-block:: java

            previousState


Get the received command
------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            event.itemCommand

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            event.itemCommand

    .. group-tab:: Groovy

        .. code-block:: Groovy

            event.itemCommand

    .. group-tab:: Rules DSL

        .. code-block:: java

            receivedCommand


Send a command to an Item
-------------------------

`more options <https://www.openhab.org/docs/configuration/jsr223.html#events-operations>`

.. tabs::

    .. group-tab:: Python

        .. code-block::

            events.sendCommand("Test_SwitchItem", "ON")

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            events.sendCommand("Test_SwitchItem", "ON")

    .. group-tab:: Groovy

        .. code-block:: Groovy

            events.sendCommand("Test_SwitchItem", "ON")

    .. group-tab:: Rules DSL

        .. code-block:: java

            Test_SwitchItem.sendCommand(ON)
            // or
            sendCommand("Test_SwitchItem", "ON")


Send an update to an Item
-------------------------

`more options <https://www.openhab.org/docs/configuration/jsr223.html#events-operations>`

.. tabs::

    .. group-tab:: Python

        .. code-block::

            events.postUpdate("Test_SwitchItem", "ON")

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            events.postUpdate("Test_SwitchItem", "ON")

    .. group-tab:: Groovy

        .. code-block:: Groovy

            events.postUpdate("Test_SwitchItem", "ON")

    .. group-tab:: Rules DSL

        .. code-block:: java

            Test_SwitchItem.postUpdate(ON)
            // or
            postUpdate("Test_SwitchItem", "ON")


Stop a rule if the triggering Item's state is NULL or UNDEF
-----------------------------------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            if isinstance(items[event.itemName].class, UnDefType):
                return
            # do stuff

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            if (items[event.itemName].class == UnDefType.class) {
                return
            } else {
                // do stuff
            }

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            if (triggeringItem.state == NULL || triggeringItem.state == UNDEF) {
                return
            } else {
                // do stuff
            }


Use org.joda.time.DateTime
--------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            from org.joda.time import DateTime
            start = DateTime.now()

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            var DateTime = Java.type("org.joda.time.DateTime");
            start = DateTime.now()

    .. group-tab:: Groovy

        .. code-block:: Groovy

            import org.joda.time.DateTime
            start = DateTime.now()

    .. group-tab:: Rules DSL

        .. code-block:: java

            now


Use a timer
-----------

.. tabs::

    .. group-tab:: Python

        See the `timer_example.py <https://github.com/openhab-scripters/openhab-helper-libraries/blob/master/Script%20Examples/Python/timer_example.py>`_ in the Script Examples for examples of using both Python `threading.Timer <https://docs.python.org/2/library/threading.html#timer-objects>`_ and the openHAB `createTimer Action <https://www.openhab.org/docs/configuration/actions.html#timers>`_.

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            TODO


Convert a value to a state for comparison
-----------------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            items["String_Item"] == StringType("test string")
            items["Number_Item"] > DecimalType(5)
            items["Temperature_Item"] > QuantityType(u"55 °F")
            event.itemState <= DecimalType(event.oldItemState.intValue() + 60)
            event.itemState <= DecimalType(event.oldItemState.doubleValue() + 60)
            event.itemState <= DecimalType(event.oldItemState.floatValue() + 60)

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            TODO


Convert DecimalType to an integer or float for arithmetic
---------------------------------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            int(str(items["Number_Item1"])) + int(str(items["Number_Item2"])) > 5
            items["Number_Item1"].intValue() + items["Number_Item2"].intValue() > 5
            float(str(items["Number_Item"])) + 5.5555 > 55.555
            items["Number_Item"].floatValue() + 5.5555 > 55.555

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            TODO


Pause a thread
--------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            from time import sleep
            sleep(5)# the unit is seconds, so use 0.5 for 500 milliseconds

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            Thread::sleep(5000)// the unit is milliseconds


Get the members or all members of a Group
-----------------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            ir.getItem("gTest").members

            ir.getItem("gTest").allMembers

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            ir.getItem("gTest").members

            ir.getItem("gTest").allMembers

    .. group-tab:: Groovy

        .. code-block:: Groovy

            ir.getItem("gTest").members

            ir.getItem("gTest").allMembers

    .. group-tab:: Rules DSL

        .. code-block:: java

            gTest.members

            gTest.allMembers


Iterate over members of a Group
-------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            for item in ir.getItem("gTest").members:
                # do stuff

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            gTest.members.forEach[item |
                // do stuff
            ]


Filter members of a group
-------------------------

.. tabs::

    .. group-tab:: Python

        Returns a list of Items, not a GroupItem

        .. code-block::

            listOfMembers = filter(lambda item: item.state == ON, ir.getItem("gTest").members)

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        Returns a GrouptItem

        .. code-block:: java

            val listOfMembers = gTest.members.filter(GenericItem item | item.state == ON)


Get the first Item in a filtered list of Group members
------------------------------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            my_item = filter(lambda item: item.state == ON, ir.getItem("gTest").members)[0]

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            val myItem = gTest.members.findFirst(item.state == ON)


Get first 5 Items from a filtered list of Group members
-------------------------------------------------------

.. tabs::

    .. group-tab:: Python

        Returns a list of Items

        .. code-block::

            my_items = filter(lambda item: item.state == OFF, ir.getItem("gTest").members)[0:5]

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            TODO



Get a sorted list of Group members matching a condition
-------------------------------------------------------

.. tabs::

    .. group-tab:: Python

        Returns a list of Items

        .. code-block::

            sorted_battery_level = sorted(battery for battery in ir.getItem("gBattery").getMembers() if battery.state < DecimalType(5), key = lambda battery: battery.state)

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            TODO




Get a list of values mapped from the members of a Group
-------------------------------------------------------

.. tabs::

    .. group-tab:: Python

        Returns a list of strings

        .. code-block::

            battery_levels = map(lambda lowBattery: "{}: {}".format(lowBattery.label, str(lowBattery.state) + "%"), ir.getItem("gBattery").members)

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            TODO



Perform an arithmetic reduction of values from members of a Group
-----------------------------------------------------------------

.. tabs::

    .. group-tab:: Python

        Returns a value

        .. code-block::

            # the state.add(state) is a method of QuantityType
            weekly_rainfall = reduce(lambda sum, x: sum.add(x), map(lambda rain: rain.state, ir.getItem("gRainWeeklyForecast").members))

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            TODO



Example with several functions using Group members
--------------------------------------------------

.. tabs::

    .. group-tab:: Python

        Returns a string

        .. code-block::

            lowBatteryMessage = "Warning! Low battery alert:\n\n{}".format(",\n".join(map(lambda lowBattery: "{}: {}".format(lowBattery.label,str(lowBattery.state) + "%"), sorted(battery for battery in ir.getItem("gBattery").getMembers() if battery.state < DecimalType(5), key = lambda battery: battery.state))))

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            TODO


Read/Add/Remove Item metadata
-----------------------------

.. tabs::

    .. group-tab:: Python

            https://community.openhab.org/t/jsr223-jython-using-item-metadata-in-rules/53868

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            Metadata can be added and removed, but not read


View the names of an object's attributes
----------------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            # replace `object` with the object you'd like to introspect
            log.debug("dir(object)=[{}]".format(dir(object)))

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            Not possible



View all symbols in a context
-----------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            log.debug("dir()=[{}]".format(dir()))

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            Not possible

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            Not possible


Get the UID of a rule by name
-----------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            scriptExtension.importPreset("RuleSupport")
            ruleUID = filter(lambda rule: rule.name == "This is the name of my rule", rules.getAll())[0].UID

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            Not possible


Enable or disable a rule by UID
-------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            from core import osgi
            ruleEngine = osgi.get_service("org.eclipse.smarthome.automation.RuleManager")
            ruleEngine.setEnabled(ruleUID, True)# enable rule
            ruleEngine.setEnabled(ruleUID, False)# disable rule

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            Not possible


Run a rule by UID
-----------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            from core import osgi
            rule_engine = osgi.get_service("org.eclipse.smarthome.automation.RuleManager")
            ruleEngine.runNow(ruleFunction.UID)
            consider_conditions = True# consider the rule's Conditions
            ruleEngine.runNow(ruleFunction.UID, considerConditions, {'name': 'EXAMPLE'})

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            Not possible


Enable/disable a Thing
----------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            from core.log import logging, LOG_PREFIX
            log = logging.getLogger(LOG_PREFIX + ".TEST")
            from org.eclipse.smarthome.core.thing import ThingUID
            from core import osgi

            thing_manager = osgi.get_service("org.eclipse.smarthome.core.thing.ThingManager")
            kodi_thing = things.get(ThingUID("kodi:kodi:familyroom"))
            thing_manager.setEnabled(ThingUID("kodi:kodi:familyroom"), False)# disable Thing
            log.debug("Disabled: isEnabled [{}], statusInfo [{}]".format(kodi_thing.isEnabled(), kodi_thing.statusInfo))
            thing_manager.setEnabled(ThingUID("kodi:kodi:familyroom"), True)# enable Thing
            log.debug("Enabled: isEnabled [{}], statusInfo [{}]".format(kodi_thing.isEnabled(), kodi_thing.statusInfo))

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            TODO


`Persistence extensions <https://www.openhab.org/docs/configuration/persistence.html#persistence-extensions-in-scripts-and-rules>`_
-----------------------------------------------------------------------------------------------------------------------------------

Others not listed are similar

.. tabs::

    .. group-tab:: Python

        .. code-block::

            from core.actions import PersistenceExtensions
            PersistenceExtensions.previousState(ir.getItem("Weather_SolarRadiation"), True).state

            from org.joda.time import DateTime
            PersistenceExtensions.changedSince(ir.getItem("Weather_SolarRadiation"), DateTime.now().minusHours(1))
            PersistenceExtensions.maximumSince(ir.getItem("Weather_SolarRadiation"), DateTime.now().minusHours(1)).state

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            TODO


Use other `Core & Cloud Actions <https://www.openhab.org/docs/configuration/actions.html#core-actions>`_
--------------------------------------------------------------------------------------------------------

In order to avoid namespace conflicts with the ``actions`` object provided in the default scope, don't do ``import core.actions``.

For ScriptExecution, see :ref:`Guides/But How Do I:Use a timer`.
For LogAction, see :doc:`Logging`.

.. tabs::

    .. group-tab:: Python

        .. code-block::

            from core.actions import Exec
            Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 3 --max-time 3 http://some.host.name",5000)

            from core.actions import HTTP
            HTTP.sendHttpPutRequest("someURL.com, "application/json", '{"this": "that"}')

            from core.actions import Ping
            if Ping.checkVitality("10.5.5.5", 0, 5000):
                log.info("Server is online")
            else:
                log.info("Server is offline")

            from core.actions import Audio
            Audio.playSound("doorbell.mp3")# using the default audiosink
            Audio.playSound("my:audio:sink", "doorbell.mp3")# specifying an audiosink
            Audio.playStream("http://myAudioServer/myAudioFile.mp3")# using the default audiosink
            Audio.playStream("my:audio:sink", "http://myAudioServer/myAudioFile.mp3")# specifying an audiosink

            from core.actions import NotificationAction
            NotificationAction.sendNotification("someone@someDomain.com","This is the message")
            NotificationAction.sendBroadcastNotification("This is the message")
            NotificationAction.sendLogNotification("This is the message")

            from core.actions import Transformation
            Transformation.transform("JSONPATH", "$.test", test)

            from core.actions import Voice
            Voice.say("This will be said")

            from core.actions import Things
            Things.getThingStatusInfo("zwave:device:c5155aa4:node5")

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            TODO



Use an Addon/Bundle Action
--------------------------

 The binding or Action must be installed.

.. tabs::

    .. group-tab:: Python

        `Telegram <https://www.openhab.org/addons/actions/telegram/#telegram-actions>`_
        
        .. code-block::

            from core.actions import Telegram
            Telegram.sendTelegram("MyBot", "Test")

        `Mail <https://www.openhab.org/addons/actions/mail/#mail-actions>`_

        .. code-block::

            from core.actions import Mail
            Mail.sendMail("someone@someDomain.com", "This is the subject", "This is the message")

        `Astro <https://www.openhab.org/addons/actions/astro/#astro-actions>`_

        .. code-block::

            from core.actions import Astro
            from core.log import logging, LOG_PREFIX
            from java.util import Date

            log = logging.getLogger(LOG_PREFIX + ".astro_test")

            # Use the Astro action class to get the sunset start time.
            log.info("Sunrise: {}".format(Astro.getAstroSunsetStart(Date(2017, 7, 25), 38.897096, -77.036545).time))

        `MQTT2 <https://www.openhab.org/addons/bindings/mqtt/>`_

        .. code-block::

            # no import needed
            actions.get("mqtt", "mqtt:systemBroker:embedded-mqtt-broker").publishMQTT("test/system/started", "true");

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            TODO
