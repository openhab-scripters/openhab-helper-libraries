"""
This script provides a rule that triggers when an area trigger group changes
state and another rule that adjusts the lights after a lux level change.
"""
from threading import Timer

from core.rules import rule
from core.triggers import when
from core.metadata import get_metadata, get_key_value, get_value
from core.items import add_item

import configuration
reload(configuration)
from configuration import area_triggers_and_actions_dict

import community.area_triggers_and_actions
reload(community.area_triggers_and_actions)
from community.area_triggers_and_actions import start_action

#from org.joda.time import DateTime

@rule("Area triggers")
@when("Member of gArea_Trigger changed")
def area_triggers(event):
    """
    This rule triggers when any area trigger group becomes active. If there is
    an action group associated with the trigger group, the action function
    specified in the metadata of each of the group's members will be executed
    using that Item. If the Item does not have an action function in its
    metadata, the default action function will be used from
    ``configuration.area_triggers_and_actions_dict["default_action_function"]``.
    If the trigger group has an action function in its metadata, that function
    will also be executed using the trigger group.
    """
    #start_time = DateTime.now().getMillis()
    if items["Mode"] != StringType("Security"):
        area_triggers.log.debug("{}: [{}]".format(event.itemName, event.itemState))
        active = event.itemState in [ON, OPEN]
        action_groups = itemRegistry.getItems(event.itemName.replace("_Trigger", "_Action"))
        if action_groups:
            action_group = action_groups[0]
            #area_triggers.log.warn("Test: start loop: {}: [{}]: time=[{}]".format(event.itemName, event.itemState, DateTime.now().getMillis() - start_time))
            for item in action_group.members:
                action_function_names = get_key_value(item.name, "area_triggers_and_actions", "actions").keys()
                if not action_function_names:
                    action_function_names.append(area_triggers_and_actions_dict.get("default_action_function"))
                for action_function_name in action_function_names:
                    start_action(item, active, action_function_name)
            #area_triggers.log.warn("Test: end loop: {}: [{}]: time=[{}]".format(event.itemName, event.itemState, DateTime.now().getMillis() - start_time))
        else:
            area_triggers.log.debug("No action group found for [{}]".format(event.itemName))
        trigger_function_names = get_key_value(event.itemName, "area_triggers_and_actions", "actions").keys()
        for trigger_function_name in trigger_function_names:
            start_action(itemRegistry.getItem(event.itemName), active, trigger_function_name)
    #area_triggers.log.warn("Test: {}: [{}]: time=[{}]".format(event.itemName, event.itemState, DateTime.now().getMillis() - start_time))

if area_triggers_and_actions_dict.get("lux_item_name") and itemRegistry.getItems(area_triggers_and_actions_dict["lux_item_name"]):
    @rule("Mode or lux change")
    @when("Item {} changed".format(area_triggers_and_actions_dict["lux_item_name"]))
    @when("Item Mode changed")
    @when("System started")
    def mode_or_lux_change(event):
        """
        This rule iterates through all triggering groups and replays all actions
        for groups that are currently active, using the current mode and lux level.
        """
        #start_time = DateTime.now().getMillis()
        mode_change_or_system_start = (event.itemName == "Mode") if event is not None else True
        if not mode_change_or_system_start:
            lux_current = event.itemState
            lux_previous = event.oldItemState
        spanned = False
        # get a list of active trigger groups (or all of them, if system started)
        for trigger_group in [group for group in itemRegistry.getItem("gArea_Trigger").members if (group.state in [ON, OPEN] if event is not None else True)]:
            action_groups = itemRegistry.getItems(trigger_group.name.replace("_Trigger", "_Action"))
            action_group = action_groups[0] if action_groups else None
            if action_group:
                for item in action_group.members:
                    low_lux_trigger = get_key_value(item.name, "area_triggers_and_actions", "modes", str(items["Mode"]), "low_lux_trigger") or area_triggers_and_actions_dict["default_levels"]["low_lux_trigger"]
                    low_lux_trigger_buffer = get_low_lux_trigger_buffer(item.name)
                    up_breach = down_breach = False
                    if not mode_change_or_system_start and lux_current is not NULL:
                        up_breach = (lux_previous == NULL or lux_previous.intValue() < low_lux_trigger + low_lux_trigger_buffer) and low_lux_trigger + low_lux_trigger_buffer  <= lux_current.intValue()
                        down_breach = (lux_previous == NULL or lux_previous.intValue() > low_lux_trigger - low_lux_trigger_buffer) and  low_lux_trigger - low_lux_trigger_buffer >= lux_current.intValue()
                    # replay actions for all lights on mode change and system start, or only the lights affected on a lux change
                    if mode_change_or_system_start or up_breach or down_breach:
                        action_function_names = get_key_value(item.name, "area_triggers_and_actions", "actions").keys()
                        if not action_function_names or "light_action" in action_function_names:
                            start_action(item, True if event is not None else trigger_group.state in [ON, OPEN], "light_action")
                            if mode_change_or_system_start:
                                mode_or_lux_change.log.info("Mode adjust: [{}]: {}: {}".format(items["Mode"], action_group.name, item.name))
                            else:
                                spanned = True
                                mode_or_lux_change.log.info("Lux adjust: {}: {}: current=[{}], previous=[{}]".format(action_group.name, item.name, lux_current, lux_previous))
        if not mode_change_or_system_start and not spanned:
            mode_or_lux_change.log.debug("No lights were adjusted: current=[{}], previous=[{}]".format(lux_current, lux_previous))
        #mode_or_lux_change.log.warn("Test: time=[{}]".format(DateTime.now().getMillis() - start_time))

def get_low_lux_trigger_buffer(item_name):
    try:
        return get_key_value(item_name, "area_triggers_and_actions", "modes", str(items["Mode"]), "low_lux_trigger_buffer") or area_triggers_and_actions_dict["default_levels"]["low_lux_trigger_buffer"]
    except KeyError:
        return 0 # without any configuration we default to no buffer
