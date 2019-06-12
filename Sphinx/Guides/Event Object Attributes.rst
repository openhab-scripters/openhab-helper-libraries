=======================
Event Object Attributes
=======================

When a rule is triggered, the function is provided the event instance that triggered it.
The specific data depends on the event type.
For example, the `ItemStateChangedEvent <https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateChangedEvent.java>`_ event type has ``itemName``, ``itemState``, and ``oldItemState`` attributes. The ``StartupTrigger`` and ``GenericCronTrigger`` do not provide any ``event`` objects.
Rather than digging through the code to look up the attributes available in a particular ``event`` object, you can add a log entry inside the function and then trigger the rule:

.. tabs::

    .. group-tab:: Python

        .. code-block::

            @rule("Log event")
            @when("Item Test_Switch_1 received update")
            def my_rule_function(event):
                my_rule_function.info("dir(event)=[{}]".format(dir(event)))

    .. group-tab:: JavaScript

        Not documented

    .. group-tab:: Groovy

        .. code-block:: Groovy

            import org.openhab.core.automation.Action
            import org.openhab.core.automation.module.script.rulesupport.shared.simple.SimpleRule
            import org.eclipse.smarthome.config.core.Configuration

            import org.slf4j.LoggerFactory

            scriptExtension.importPreset("RuleSupport")
            scriptExtension.importPreset("RuleSimple")

            def log = LoggerFactory.getLogger('jsr223.groovy.Log event')

            def testRule1 = new SimpleRule() {
                Object execute(Action module, Map<String, ?> inputs) {
                    inputs['event'].properties.each{log.warn("event: " + it)}
                }
            }
            testRule1.setName("Log event");
            testRule1.setTriggers([
                TriggerBuilder.create()
                    .withId("anItemTrigger")
                    .withTypeUID("core.ItemStateUpdateTrigger")
                    .withConfiguration(new Configuration([itemName: "Virtual_Switch_1"]))
                    .build()
                ])

            automationManager.addRule(testRule1); 

Here is a table of the attributes available in ``event`` objects (or ``inputs['event']``, if using aaw API or extensions), including a comparison to the Rules DSL implicit variables:

| Rules DSL | JSR223 | @when Trigger(s) | Event Object(s) | Description
| --- | --- | --- | --- | --- |
triggeringItem.name | event.itemName | "received update", "changed", "received&nbsp;command" | [ItemStateEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateEvent.java), [ItemStateChangedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateChangedEvent.java), [ItemCommandEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemCommandEvent.java), [ItemStatePredictedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStatePredictedEvent.java), [GroupItemStateChangedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/GroupItemStateChangedEvent.java) | Name of Item that triggered event (String)
triggeringItem.name | event.memberName | "changed" | [GroupItemStateChangedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/GroupItemStateChangedEvent.java) | Name of member that caused the state change of a parent Group (String)
triggeringItem.state | event.itemState | "received update", "changed" | [ItemStateEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateEvent.java), [ItemStateChangedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateChangedEvent.java) | State of item that triggered event (State)
previousState | event.oldItemState | "changed" | [ItemStateChangedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStateChangedEvent.java), [GroupItemStateChangedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/GroupItemStateChangedEvent.java) | Previous state of Item or Group that triggered event (State)
receivedCommand | event.itemCommand | "received&nbsp;command" | [ItemCommandEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemCommandEvent.java) | Command that triggered event (Command)
N/A | event.predictedState | *Not&nbsp;currently&nbsp;supported* | [ItemStatePredictedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStatePredictedEvent.java) | State that the Item triggering the event is predicted to have (State)
N/A | event.isConfirmation | *Not&nbsp;currently&nbsp;supported* | [ItemStatePredictedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemStatePredictedEvent.java) | If&nbsp;`true`,&nbsp;then&nbsp;it&nbsp;basically&nbsp;only&nbsp;confirms&nbsp;the&nbsp;previous&nbsp;item&nbsp;state&nbsp;because&nbsp;a&nbsp;received&nbsp;command&nbsp;will&nbsp;not&nbsp;be&nbsp;successfully&nbsp;executed&nbsp;and&nbsp;therefore&nbsp;presumably&nbsp;will&nbsp;not&nbsp;result&nbsp;in&nbsp;a&nbsp;state&nbsp;change&nbsp;(e.g.&nbsp;because&nbsp;no&nbsp;handler&nbsp;currently&nbsp;is&nbsp;capable&nbsp;of&nbsp;delivering&nbsp;such&nbsp;an&nbsp;event&nbsp;to&nbsp;its&nbsp;device)&nbsp;(Boolean)
N/A | event.newItemState | *Not&nbsp;currently&nbsp;supported* | [GroupItemStateChangedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/GroupItemStateChangedEvent.java) | State of Group that triggered event (State)
N/A | event.item | *Not&nbsp;currently&nbsp;supported* | [ItemAddedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemAddedEvent.java), [ItemRemovedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemRemovedEvent.java) | Item that triggered event (Item)
N/A | event.oldItem | *Not&nbsp;currently&nbsp;supported* | [ItemUpdatedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core/src/main/java/org/eclipse/smarthome/core/items/events/ItemUpdatedEvent.java) | Item DTO prior to the Item being updated (Item)
N/A | event.channel | "triggered" | [ChannelTriggeredEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ChannelTriggeredEvent.java) | Channel associated with Event that triggered event (Channel)
N/A | event.event | "triggered" | [ChannelTriggeredEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ChannelTriggeredEvent.java) | Event that triggered event (Event)
N/A | event.thing | *Not&nbsp;currently&nbsp;supported* | [ThingAddedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingAddedEvent.java), [ThingRemovedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingRemovedEvent.java) | Thing that triggered event (Thing)
N/A | event.oldThing | *Not&nbsp;currently&nbsp;supported* | [ThingUpdatedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingUpdatedEvent.java) | Thing DTO prior to the Thing being updated (Thing)
N/A | event.thingUID | "changed" | [ThingStatusInfoEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingStatusInfoEvent.java), [ThingStatusInfoChangedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingStatusInfoChangedEvent.java) | ThingUID of Thing that triggered event (ThingUID)
N/A | event.statusInfo | "changed" | [ThingStatusInfoEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingStatusInfoEvent.java), [ThingStatusInfoChangedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingStatusInfoChangedEvent.java) | ThingStatusInfo of Thing that triggered event (ThingStatusInfo)
N/A | event.oldStatusInfo | "changed" | [ThingStatusInfoChangedEvent](https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.thing/src/main/java/org/eclipse/smarthome/core/thing/events/ThingStatusInfoChangedEvent.java) | Previous ThingStatusInfo of Thing that triggered event (ThingStatusInfo)
