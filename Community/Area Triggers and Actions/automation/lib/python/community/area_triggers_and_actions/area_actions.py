"""
The ``area_actions`` module contains the ``light_action``  and
``toggle_action`` functions that should be useable by everyone without
customization. Custom actions should not be put into this file, as they could
be overwritten during an upgrade. Instead, place them in the
``personal.area_triggers_and_actions.area_actions`` module.
"""
__all__ = ['light_action', 'toggle_action']

from core.jsr223.scope import events, ir, items, PercentType, DecimalType, HSBType, ON, OFF, NULL
from core.metadata import get_key_value
from core.log import logging, LOG_PREFIX
from org.eclipse.smarthome.core.items import ItemNotFoundException

import configuration
reload(configuration)
from configuration import area_triggers_and_actions_dict

#from org.joda.time import DateTime

log = logging.getLogger("{}.community.area_triggers_and_actions.area_actions".format(LOG_PREFIX))

def light_action(item, active):
    """
    This function performs an action on a light Item.

    When called, this function pulls in the metadata for the supplied Item or
    uses the default values specified in
    ``configuration.area_triggers_and_actions_dict"["default_levels"]``, if the
    metadata does not exist. This metadata is then compared to the current lux
    level to determine if a light should be turned OFF or set to the specified
    level. This function should work for everyone without modification.

    Args:
        Item item: The Item to perform the action on
        boolean active: Area activity (True for active and False for inactive)
    """
    #start_time = DateTime.now().getMillis()
    item_metadata = get_key_value(item.name, "area_triggers_and_actions", "modes", str(items["Mode"]))
    low_lux_trigger = item_metadata.get("low_lux_trigger", area_triggers_and_actions_dict["default_levels"]["low_lux_trigger"])

    brightness_override_by_state = get_key_value(item.name, "area_triggers_and_actions", "brightness_override_by_state")
    if brightness_override_by_state == {}:
        brightness_override_by_state = True # turn on brightness_override_by_state by default if not configured

    brightness = PercentType(str(item_metadata.get("brightness", area_triggers_and_actions_dict["default_levels"]["brightness"])))
    hue = DecimalType(item_metadata.get("hue", area_triggers_and_actions_dict["default_levels"]["hue"]))
    saturation = PercentType(str(item_metadata.get("saturation", area_triggers_and_actions_dict["default_levels"]["saturation"])))

    lux_item_name = area_triggers_and_actions_dict.get("lux_item_name")
    if lux_item_name is not None and items[lux_item_name] == NULL:
        log.debug("Lux item {} is reporting NULL".format(lux_item_name))
    # item from inactive area or above lux threshold will be turned off
    if not active or (lux_item_name is not None and items[lux_item_name] != NULL and items[lux_item_name].intValue() > low_lux_trigger):
        brightness = PercentType(0)
        hue = DecimalType(0)
        saturation = PercentType(0)

    # apply brightness override if available
    brightness_override_item_name = get_key_value(item.name, "area_triggers_and_actions", "brightness_override_item_name")
    if brightness_override_item_name != {}:
        try:
            brightness_override_item = ir.getItem(brightness_override_item_name)
            if brightness_override_item.state is not NULL and 0 <= brightness_override_item.state.floatValue() <= 100:
                brightness = brightness_override_item.state
        except ItemNotFoundException:
            log.warn("Configured brightness override item {} doesn't exist".format(brightness_override_item_name))
        
    #log.warn("light_action: item.name [{}], active [{}], brightness [{}], lux [{}], low_lux_trigger [{}]".format(item.name, active, brightness, items[area_triggers_and_actions_dict["lux_item_name"]], low_lux_trigger))
    #apply newly determined brightness
    if item.type == "Dimmer" or (item.type == "Group" and item.baseItem.type == "Dimmer"):
        new_state = brightness
        brightness_override_by_state = brightness_override_by_state and item.state != NULL and item.state >= PercentType(99)
    elif item.type == "Color" or (item.type == "Group" and item.baseType == "Color"):
        new_state = HSBType(hue, saturation, brightness)
        brightness_override_by_state = brightness_override_by_state and item.state != NULL and item.state.brightness >= PercentType(99)
    elif item.type == "Switch" or (item.type == "Group" and item.baseItem.type == "Switch"):
        new_state = OFF if brightness == PercentType(0) else ON
        brightness_override_by_state = False # switches can't support override by state since they only have 2 states
    
    if item.state != new_state:
        if not brightness_override_by_state:
            events.sendCommand(item, new_state)
            log.info("{} {}: {}".format("<<<<<<<" if brightness == PercentType(0) else ">>>>>>>", item.name, new_state))
        else:
            log.info("[{}]: item was manually set > 98, so not adjusting".format(item.name))
    else:
        log.debug("[{}]: item is already set to [{}], so not sending command".format(item.name, brightness))

    #log.warn("Test: light_action: {}: [{}]: time=[{}]".format(item.name, "ON" if active else "OFF", DateTime.now().getMillis() - start_time))

def toggle_action(item, active):
    """
    This function sends the OFF command to the Item.

    Args:
        Item item: The Item to perform the action on
        boolean active: Area activity (True for active and False for inactive)
    """
    events.sendCommand(item, ON if item.state == OFF else OFF)
