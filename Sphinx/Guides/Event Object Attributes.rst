=======================
Event Object Attributes
=======================

When a rule is triggered, the function is provided the event instance that triggered it.
The specific data depends on the event type.
For example, the ``event`` object returned by the `ItemStateChangedEvent <https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateChangedEvent.java>`_ event type has ``itemName``, ``itemState``, and ``oldItemState`` attributes. The ``StartupTrigger`` and ``GenericCronTrigger`` do not provide any ``event`` objects.
Rather than digging through the code to look up the attributes available in a particular ``event`` object, you can add a log entry inside the function and then trigger the rule (:ref:`Guides/But How Do I:View the names of an object's attributes`).

Here is a table of the attributes available in ``event`` objects (or ``inputs['event']``, if using aaw API or extensions), including a comparison to the Rules DSL implicit variables:

+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| Rules DSL Equivalent     | Scripted Automation      | @when Trigger(s)              | Event Object(s)                  | Description                                   |
+==========================+==========================+===============================+==================================+===============================================+
| ``triggeringItem.name``  | ``event.itemName``       | | "received update"           | | `ItemStateEvent`_              | | Name of Item that triggered event (String)  |
|                          |                          | | "changed"                   | | `ItemStateChangedEvent`_       |                                               |
|                          |                          | | "received command"          | | `ItemCommandEvent`_            |                                               |
|                          |                          |                               | | `ItemStatePredictedEvent`_     |                                               |
|                          |                          |                               | | `GroupItemStateChangedEvent`_  |                                               |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| ``triggeringItem.name``  | ``event.memberName``     | | "changed"                   | | `GroupItemStateChangedEvent`_  | | Name of member that caused the state        |
|                          |                          |                               |                                  | | change of a parent Group (String)           |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| ``triggeringItem.state`` | ``event.itemState``      | | "received update"           | | `ItemStateEvent`_              | | State of item that triggered event (State)  |
|                          |                          | | "changed"                   | | `ItemStateChangedEvent`_       |                                               |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| ``previousState``        | ``event.oldItemState``   | | "changed"                   | | `ItemStateChangedEvent`_       | | Previous state of Item or Group that        |
|                          |                          |                               | | `GroupItemStateChangedEvent`_  | | triggered event (State)                     |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| ``receivedCommand``      | ``event.itemCommand``    | | "received command"          | | `ItemCommandEvent`_            | | Command that triggered event (Command)      |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| | N/A                    | ``event.predictedState`` | | **Not currently supported** | | `ItemStatePredictedEvent`_     | | State that the Item triggering the event    |
|                          |                          |                               |                                  | | is predicted to have (State)                |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| | N/A                    | ``event.isConfirmation`` | | **Not currently supported** | | `ItemStatePredictedEvent`_     | | If ``true`` then it basically only confirms |
|                          |                          |                               |                                  | | the previous item state because a received  |
|                          |                          |                               |                                  | | command will not be successfully executed   |
|                          |                          |                               |                                  | | and therefore presumably will not result in |
|                          |                          |                               |                                  | | a state change (e.g. because no handler     |
|                          |                          |                               |                                  | | currently is capable of delivering such an  |
|                          |                          |                               |                                  | | event to its device) (Boolean)              |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| | N/A                    | ``event.newItemState``   | | **Not currently supported** | | `GroupItemStateChangedEvent`_  | | State of Group that triggered event (State) |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| | N/A                    | ``event.item``           | | **Not currently supported** | | `ItemAddedEvent`_              | | Item that triggered event (Item)            |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| | N/A                    | ``event.oldItem``        | | **Not currently supported** | | `ItemUpdatedEvent`_            | | Item DTO prior to the Item being updated    |
|                          |                          |                               |                                  | | (Item)                                      |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| | N/A                    | ``event.channel``        | | "triggered"                 | | `ChannelTriggeredEvent`_       | | Channel associated with Event that          |
|                          |                          |                               |                                  | | triggered event (Channel)                   |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| | N/A                    | ``event.event``          | | "triggered"                 | | `ChannelTriggeredEvent`_       | | Event that triggered event (Event)          |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| | N/A                    | ``event.thing``          | | **Not currently supported** | | `ThingAddedEvent`_             | | Thing that triggered event (Thing)          |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| | N/A                    | ``event.oldThing``       | | **Not currently supported** | | `ThingUpdatedEvent`_           | | Thing DTO prior to the Thing being updated  |
|                          |                          |                               |                                  | | (Thing)                                     |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| | N/A                    | ``event.thingUID``       | | "changed"                   | | `ThingStatusInfoEvent`_        | | ThingUID of Thing that triggered event      |
|                          |                          |                               | | `ThingStatusInfoChangedEvent`_ | | (ThingUID)                                  |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| | N/A                    | ``event.statusInfo``     | | "changed"                   | | `ThingStatusInfoEvent`_        | | ThingStatusInfo of Thing that triggered     |
|                          |                          |                               | | `ThingStatusInfoChangedEvent`_ | | event (ThingStatusInfo)                     |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+
| | N/A                    | ``event.oldStatusInfo``  | | "changed"                   | | `ThingStatusInfoChangedEvent`_ | | Previous ThingStatusInfo of Thing that      |
|                          |                          |                               |                                  | | triggered event (ThingStatusInfo)           |
+--------------------------+--------------------------+-------------------------------+----------------------------------+-----------------------------------------------+

.. _ItemStateEvent: https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateEvent.java
.. _ItemStateChangedEvent: https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateChangedEvent.java
.. _ItemCommandEvent: https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemCommandEvent.java
.. _ItemStatePredictedEvent: https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStatePredictedEvent.java
.. _GroupItemStateChangedEvent: https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/GroupItemStateChangedEvent.java
.. _ItemAddedEvent: https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemAddedEvent.java), [ItemRemovedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemRemovedEvent.java
.. _ItemUpdatedEvent: https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemUpdatedEvent.java
.. _ChannelTriggeredEvent: https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ChannelTriggeredEvent.java
.. _ThingAddedEvent: https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingAddedEvent.java), [ThingRemovedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingRemovedEvent.java
.. _ThingUpdatedEvent: https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingUpdatedEvent.java
.. _ThingStatusInfoEvent: https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingStatusInfoEvent.java
.. _ThingStatusInfoChangedEvent: https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingStatusInfoChangedEvent.java
