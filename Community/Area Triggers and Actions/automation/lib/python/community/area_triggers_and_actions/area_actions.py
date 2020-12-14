"""
The ``area_actions`` module contains the ``light_action``  and
``toggle_action`` functions that should be useable by everyone without
customization. Custom actions should not be put into this file, as they could
be overwritten during an upgrade. Instead, place them in the
``personal.area_triggers_and_actions.area_actions`` module.
"""
__all__ = ['light_action', 'toggle_action']

#from org.joda.time import DateTime

from core.jsr223.scope import events, items, PercentType, DecimalType, HSBType, ON, OFF, OnOffType
from core.metadata import get_key_value
from core.log import logging, LOG_PREFIX, log_traceback

import configuration
reload(configuration)
from configuration import AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION

MODE_ITEM = AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION.get("mode_item") or "Mode"
DISABLE_AUTOMATION_BRIGHTNESS = AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION.get("disable_automation_brightness") or 100
LOG = logging.getLogger(u"{}.community.area_triggers_and_actions.area_actions".format(LOG_PREFIX))


@log_traceback
def light_action(item, active):
    """
    This function performs an action on a light Item.

    When called, this function pulls in the metadata for the supplied Item or
    uses the default values specified in
    ``configuration.AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION"["default_levels"]``, if the
    metadata does not exist. This metadata is then compared to the current lux
    level to determine if a light should be turned OFF or set to the specified
    level. This function should work for everyone without modification.

    Args:
        Item item: The Item to perform the action on
        boolean active: Area activity (True for active and False for inactive)
    """
    #start_time = DateTime.now().getMillis()
    item_metadata = get_key_value(item.name, "area_triggers_and_actions", "light_action")
    lux_item_name = item_metadata.get("lux_item_name", AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION["light_action"].get("lux_item_name"))
    trigger_type = "active" if active else "inactive"
    lux_trigger = item_metadata.get(trigger_type, {}).get("modes", {}).get(items[MODE_ITEM].toString(), {}).get("lux_trigger", AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION["light_action"]["default_levels"][trigger_type]["lux_trigger"])
    lux_type = "low_lux" if lux_trigger == 0 or lux_item_name is None or items[lux_item_name].intValue() < lux_trigger else "high_lux"
    levels = item_metadata.get(trigger_type, {}).get("modes", {}).get(items[MODE_ITEM].toString(), {}).get(lux_type, {})
    brightness = PercentType(str(levels.get("brightness", AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION["light_action"]["default_levels"][trigger_type][lux_type]["brightness"])))
    #LOG.warn(u"light_action: trigger_type: {}, item.name: {}, item.state: {}, lux: {}, lux_trigger: {}, lux_type: {}, brightness: {}, lux_item_name: {}".format(trigger_type, item.name, item.state, items[AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION["light_action"]["lux_item_name"]], lux_trigger, lux_type, brightness, lux_item_name))
    if item.type in ["Dimmer", "Rollershutter"] or (item.type == "Group" and item.baseItem.type == "Dimmer"):
        if item.state != brightness:
            if item.state <= PercentType(DISABLE_AUTOMATION_BRIGHTNESS):
                events.sendCommand(item, brightness)
                LOG.info(u"{} {}: {}".format("<<<<<<<<<<<<<<<<<<<<<" if brightness == DecimalType(0) else ">>>>>>>", item.name, brightness))
            else:
                LOG.info(u"'{}': dimmer is currently set > {}, so not adjusting".format(DISABLE_AUTOMATION_BRIGHTNESS, item.name))
        else:
            LOG.debug(u"'{}': dimmer is already set to '{}', so not sending command".format(item.name, brightness))
    elif item.type == "Color" or (item.type == "Group" and item.baseItem.type == "Color"):
        hue = DecimalType(str(levels.get("hue", AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION["light_action"]["default_levels"][trigger_type][lux_type]["hue"])))
        saturation = PercentType(str(levels.get("saturation", AREA_TRIGGERS_AND_ACTIONS_CONFIGURATION["light_action"]["default_levels"][trigger_type][lux_type]["saturation"])))
        if item.state != HSBType(hue, saturation, brightness):
            if item.state.brightness < PercentType(DISABLE_AUTOMATION_BRIGHTNESS):
                events.sendCommand(item, HSBType(hue, saturation, brightness))
                LOG.info(u"{} {}: '{}'".format("<<<<<<<<<<<<<<<<<<<<<" if brightness == DecimalType(0) else ">>>>>>>", item.name, HSBType(hue, saturation, brightness)))
            else:
                LOG.info(u"'{}': brightness is currently set > {}, so not adjusting".format(DISABLE_AUTOMATION_BRIGHTNESS, item.name))
        else:
            LOG.debug(u"'{}': color is already set to [{}, {}, {}], so not sending command".format(item.name, hue, saturation, brightness))
    elif item.type == "Switch" or (item.type == "Group" and item.baseItem.type == "Switch"):
        new_state = brightness.as(OnOffType)
        if item.state != new_state:
            events.sendCommand(item, new_state)
            LOG.info(u"{} {}: {}".format("<<<<<<<<<<<<<<<<<<<<<" if new_state == OFF else ">>>>>>>", item.name, new_state))
        else:
            LOG.debug(u"'{}': switch is already '{}', so not sending command".format(item.name, new_state))


@log_traceback
def toggle_action(item, active):
    """
    This function sends the OFF command to the Item.

    Args:
        Item item: The Item to perform the action on
        boolean active: Area activity (True for active and False for inactive)
    """
    events.sendCommand(item, ON if item.state.as(OnOffType) == OFF else OFF)
