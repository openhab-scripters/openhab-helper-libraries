****************
But How Do I...?
****************

Items
=====

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

        .. code-block:: Xtend

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

        .. code-block:: Xtend

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

        .. code-block:: Xtend

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

        .. code-block:: Xtend

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

        .. code-block:: Xtend

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

        .. code-block:: Xtend

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

        .. code-block:: Xtend

            receivedCommand


Send a command to an Item
-------------------------

`More details <https://www.openhab.org/docs/configuration/jsr223.html#events-operations>`_

.. tabs::

    .. group-tab:: Python

        .. code-block::

            events.sendCommand("Test_SwitchItem", "ON")
            # or
            events.sendCommand(ir.getItem("Test_SwitchItem"), ON)

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            events.sendCommand("Test_SwitchItem", "ON")
            // or
            events.sendCommand(ir.getItem("Test_SwitchItem"), ON)

    .. group-tab:: Groovy

        .. code-block:: Groovy

            events.sendCommand("Test_SwitchItem", "ON")
            // or
            events.sendCommand(ir.getItem("Test_SwitchItem"), ON)

    .. group-tab:: Rules DSL

        .. code-block:: Xtend

            Test_SwitchItem.sendCommand(ON)
            // or
            sendCommand("Test_SwitchItem", "ON")


Send an update to an Item
-------------------------

`More details <https://www.openhab.org/docs/configuration/jsr223.html#events-operations>`_

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

        .. code-block:: Xtend

            Test_SwitchItem.postUpdate(ON)
            // or
            postUpdate("Test_SwitchItem", "ON")


Stop a rule if the triggering Item's state is NULL or UNDEF
-----------------------------------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            if isinstance(items[event.itemName], UnDefType):
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

        .. code-block:: Xtend

            if (triggeringItem.state == NULL || triggeringItem.state == UNDEF) {
                return
            } else {
                // do stuff
            }


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

        .. code-block:: Xtend

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

        .. code-block:: Xtend

            TODO

Convert a state to a formatted string
-------------------------------------

Follow the formatting syntax from: https://docs.oracle.com/javase/7/docs/api/java/util/Formatter.html#syntax

.. tabs::

    .. group-tab:: Python

        .. code-block::

            str = items["DateTime_Item"].format("%1$tR")    
            str = items["Number_Item"].format("%.2f")

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: Xtend

            TODO


Groups
======


Get the members or all members of a Group
-----------------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            # just direct members, which could include groups
            ir.getItem("gTest").members

            # iteratively, all child Items and the child Items of all child groups
            ir.getItem("gTest").allMembers

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            // just direct members, which could include groups
            ir.getItem("gTest").members

            // iteratively, all child Items and the child Items of all child groups
            ir.getItem("gTest").allMembers

    .. group-tab:: Groovy

        .. code-block:: Groovy

            // just direct members, which could include groups
            ir.getItem("gTest").members

            // iteratively, all child Items and the child Items of all child groups
            ir.getItem("gTest").allMembers

    .. group-tab:: Rules DSL

        .. code-block:: Xtend

            // just direct members, which could include groups
            gTest.members

            // iteratively, all child Items and the child Items of all child groups
            gTest.allMembers


Intersection of two groups
--------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            list_of_items = [item.name for item in itemRegistry.getItem("gDS_FamilyRoom").members if "gMotion_Sensor" in item.groupNames]

            # or
            list_of_items = [item for item in itemRegistry.getItem("gDS_FamilyRoom").members if item in itemRegistry.getItem("gMotion_Sensor").members]

            # or
            list_of_items = [item.name for item in itemRegistry.getItem("gMotion_Sensor").members if item in itemRegistry.getItem("gDownstairs").allMembers]

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: Xtend

            TODO


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

        .. code-block:: Xtend

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

            # or using a list comprehension

            listOfMembers = [item for item in ir.getItem("gTest").members if item.state == ON]

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        Returns a GrouptItem

        .. code-block:: Xtend

            val listOfMembers = gTest.members.filter(GenericItem item | item.state == ON)


Get the first Item in a filtered list of Group members
------------------------------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            my_item = filter(lambda item: item.state == ON, ir.getItem("gTest").members)[0]

            # or using a list comprehension

            my_item = [item for item in ir.getItem("gTest").members if item.state == ON][0]

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: Xtend

            val myItem = gTest.members.findFirst(item.state == ON)


Get first 5 Items from a filtered list of Group members
-------------------------------------------------------

.. tabs::

    .. group-tab:: Python

        Returns a list of Items

        .. code-block::

            my_items = filter(lambda item: item.state == OFF, ir.getItem("gTest").members)[0:5]

            # or using a list comprehension

            my_items = [item for item in ir.getItem("gTest").members if item.state == ON][0:5]

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: Xtend

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

        .. code-block:: Xtend

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

        .. code-block:: Xtend

            TODO


Perform an arithmetic reduction of values from members of a Group
-----------------------------------------------------------------

.. tabs::

    .. group-tab:: Python

        Returns a value

        .. code-block::

            # to use the add() method, the states must be of type QuantityType (`Units of Measure <https://www.openhab.org/docs/concepts/units-of-measurement.html>`_)
            weekly_rainfall = reduce(lambda sum, x: sum.add(x), map(lambda rain: rain.state, ir.getItem("gRainWeeklyForecast").members))

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: Xtend

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

        .. code-block:: Xtend

            TODO


Miscellaneous
=============


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

        .. code-block:: Xtend

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

        .. code-block:: Xtend

            /*
            this is
            a multiline
            comment
            */


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

            // replace `object` with the object you'd like to introspect
            object.properties.each{log.warn("object: " + it)}

    .. group-tab:: Rules DSL

        .. code-block:: Xtend

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

        .. code-block:: Xtend

            Not possible


Get the UID of a rule by name
-----------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            ruleUID = filter(lambda rule: rule.name == "This is the name of my rule", rules.getAll())[0].UID

            # or using a list comprehension

            ruleUID = [rule for rule in rules.getAll() if rule.name == "This is the name of my rule"][0].UID

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: Xtend

            Not possible


Enable or disable a rule by UID
-------------------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            from core import osgi
            ruleEngine = osgi.get_service("org.openhab.core.automation.RuleManager") or osgi.get_service("org.eclipse.smarthome.automation.RuleManager")
            ruleEngine.setEnabled(ruleUID, True)# enable rule
            ruleEngine.setEnabled(ruleUID, False)# disable rule

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: Xtend

            Not possible


Run a rule by UID
-----------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            from core import osgi
            ruleEngine = osgi.get_service("org.openhab.core.automation.RuleManager") or osgi.get_service("org.eclipse.smarthome.automation.RuleManager")
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

        .. code-block:: Xtend

            Not possible


Get Thing Status
----------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            from org.eclipse.smarthome.core.thing import ThingUID

            thing_status = things.get(ThingUID('kodi:kodi:familyroom')).status

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            var ThingUID = Java.type("org.eclipse.smarthome.core.thing.ThingUID");

            var thingStatus = things.get(new ThingUID('kodi:kodi:familyroom')).status;

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: Xtend

            var thingStatus = getThingStatusInfo('kodi:kodi:familyroom').status


Enable/disable a Thing
----------------------

.. tabs::

    .. group-tab:: Python

        .. code-block::

            from core.log import logging, LOG_PREFIX
            log = logging.getLogger("{}.TEST".format(LOG_PREFIX))
            from core import osgi
            try:
                from org.openhab.core.thing import Thing UID
            except:
                from org.eclipse.smarthome.core.thing import ThingUID

            thing_manager = osgi.get_service("org.openhab.core.thing.ThingManager") or osgi.get_service("org.eclipse.smarthome.core.thing.ThingManager")
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

        .. code-block:: Xtend

            TODO


Read/Add/Remove Item metadata
-----------------------------

.. tabs::

    .. group-tab:: Python

            See the examples in the module... :doc:`../Python/Core/Packages and Modules/metadata`

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            Metadata can be added and removed, but not read


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

        .. code-block:: Xtend

            now


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

        .. code-block:: Xtend

            Thread::sleep(5000)// the unit is milliseconds


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

        .. code-block:: Xtend

            TODO

Use Logging
-----------

See :ref:`Guides/Logging:Logging`.


Use Actions
-----------

See :ref:`Guides/Actions:Actions`.
