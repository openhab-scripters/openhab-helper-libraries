"""
This script provides a rule that triggers when an area trigger group changes
state and another rule that adjusts the lights after a lux level change.
"""
from thread import start_new_thread

#from org.joda.time import DateTime

import configuration
reload(configuration)
from configuration import AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION

import community.area_triggers_and_actions
reload(community.area_triggers_and_actions)
from community.area_triggers_and_actions import start_action

from core.rules import rule
from core.triggers import when
from core.metadata import get_metadata, get_key_value
from core.actions import PersistenceExtensions

DEFAULT_ACTION_FUNCTION = AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION.get("default_action_function") or "light_action"
MODE_ITEM = AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION.get("mode_item") or "Mode"


@rule("Area triggers", description="This rule will update the light level when the state of an area changes.")
@when("Member of gArea_Trigger changed")
def area_triggers(event):
    """
    This rule triggers when any area trigger group becomes active. If there is
    an action group associated with the trigger group, the action function
    specified in the metadata of each of the group's members will be executed
    using that Item. If the Item does not have an action function in its
    metadata, the default action function will be used from
    ``configuration.AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION["default_action_function"]``.
    If the trigger group has an action function in its metadata, that function
    will also be executed using the trigger group.
    """
    #start_time = DateTime.now().getMillis()
    if items[MODE_ITEM] != StringType("Security"):
        area_triggers.log.debug(u"{}: '{}'".format(event.itemName, event.itemState))
        active = event.itemState in [ON, OPEN]
        action_groups = itemRegistry.getItems(event.itemName.replace("_Trigger", "_Action"))
        if action_groups:
            for action_group in action_groups:# there will be only one
                #area_triggers.log.warn(u"Test: start loop: itemName: '{}', itemState: '{}', time: '{}'".format(event.itemName, event.itemState, DateTime.now().getMillis() - start_time))
                for item in action_group.members:
                    item_metadata = get_metadata(item.name, "area_triggers_and_actions")
                    action_function_names = item_metadata.configuration.keys() if item_metadata else [DEFAULT_ACTION_FUNCTION]
                    for action_function_name in action_function_names:
                        start_new_thread(start_action, (item, active, action_function_name))
                #area_triggers.log.warn(u"Test: end loop: itemName: '{}', itemState: '{}', time: '{}'".format(event.itemName, event.itemState, DateTime.now().getMillis() - start_time))
        else:
            area_triggers.log.debug(u"No action group found for '{}'".format(event.itemName))
        item_metadata = get_metadata(event.itemName, "area_triggers_and_actions")
        trigger_function_names = item_metadata.configuration.keys() if item_metadata else []
        for trigger_function_name in trigger_function_names:
            start_new_thread(start_action, (itemRegistry.getItem(event.itemName), active, trigger_function_name))
    #area_triggers.log.warn(u"Test: {}: '{}': time='{}'".format(event.itemName, event.itemState, DateTime.now().getMillis() - start_time))


# The following rule will update the lights using the default_action_function
def lux_trigger_generator():
    def generated_triggers(function):
        lux_item_names = list(set([get_key_value(item.name, "area_triggers_and_actions", DEFAULT_ACTION_FUNCTION, "lux_item_name") for item in itemRegistry.getAll() if get_key_value(item.name, "area_triggers_and_actions", "light_action", "lux_item_name")]))
        for lux_item_name in lux_item_names:
            when("Item {} changed".format(lux_item_name))(function)
        return function
    return generated_triggers


@rule("Mode or lux change", description="This rule will update the light levels when the Mode or lux changes. This is used with the default light_action function.")
@lux_trigger_generator()
@when("Item {} changed".format(AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION.get("mode_item") or "light_action"))
@when("System started")
def mode_or_lux_change(event):
    """
    This rule iterates through all triggering groups and replays all actions
    for groups that are currently active, using the current mode and lux level.
    """
    #start_time = DateTime.now().getMillis()
    mode_change_or_system_start = (event.itemName == MODE_ITEM) if event is not None else True
    # get a list of active trigger groups (or all of them, if system started)
    for trigger_group in [group for group in itemRegistry.getItem("gArea_Trigger").members]:
        trigger_type = "active" if trigger_group.state in [ON, OPEN] else "inactive"
        action_groups = itemRegistry.getItems(trigger_group.name.replace("_Trigger", "_Action"))
        if action_groups:
            for action_group in action_groups:# there should be only 1 or None
                for item in action_group.members:
                    item_metadata = get_metadata(item.name, "area_triggers_and_actions")
                    action_function_names = item_metadata.configuration.keys() if item_metadata else [DEFAULT_ACTION_FUNCTION]
                    if DEFAULT_ACTION_FUNCTION in action_function_names:
                        light_action_metadata = get_key_value(item.name, "area_triggers_and_actions", DEFAULT_ACTION_FUNCTION)
                        lux_item_name = light_action_metadata.get("lux_item_name", AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION.get(DEFAULT_ACTION_FUNCTION, {}).get("lux_item_name"))
                        if mode_change_or_system_start:
                            start_new_thread(start_action, (item, trigger_group.state in [ON, OPEN], DEFAULT_ACTION_FUNCTION))
                            mode_or_lux_change.log.debug(u"Mode change or System start light adjustment: {}: {}: {}".format(items[MODE_ITEM], action_group.name, item.name))
                        else:
                            if lux_item_name == event.itemName and not isinstance(event.itemState, UnDefType):
                                # the lux Item associated with the action Item has changed state
                                lux_current = event.itemState.intValue()
                                lux_previous = event.oldItemState.intValue()
                            elif lux_item_name is not None and lux_item_name == AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION.get(DEFAULT_ACTION_FUNCTION, {}).get("lux_item_name") and not isinstance(items[lux_item_name], UnDefType):
                                # this action Item is associated to the default lux Item
                                lux_current = items[lux_item_name].intValue()
                                lux_previous = PersistenceExtensions.previousState(itemRegistry.getItem(lux_item_name), True).state.intValue()
                            else:
                                # this action Item is not associated to a lux Item and there is no default lux_item_name configured in AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION
                                break
                            lux_trigger = light_action_metadata.get(trigger_type, {}).get("modes", {}).get(items[MODE_ITEM].toString(), {}).get("lux_trigger", AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION[DEFAULT_ACTION_FUNCTION]["default_levels"][trigger_type]["lux_trigger"])
                            if min(lux_previous, lux_current) < lux_trigger < max(lux_previous, lux_current):
                                start_new_thread(start_action, (item, trigger_group.state in [ON, OPEN], DEFAULT_ACTION_FUNCTION))
                                mode_or_lux_change.log.debug(u"Lux change light adjustment: {}: {}: current: '{}', previous: '{}'".format(action_group.name, item.name, lux_current, lux_previous))
    #mode_or_lux_change.log.warn(u"Test: time: '{}'".format(DateTime.now().getMillis() - start_time))
