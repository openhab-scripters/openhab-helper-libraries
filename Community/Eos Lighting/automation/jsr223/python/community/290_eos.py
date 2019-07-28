"""
Eos Lighting System
"""

from core.log import log_traceback
from community import eos


def eos_rule_reinit(event):
    """Eos System Reload Rule"""
    eos.log.debug("{rule} triggered by '{name}'".format(rule=eos.RULE_REINIT_NAME, name=event.itemName))
    eos.uninit()
    eos.init(eos_rule_reinit, eos_rule_scene_update, eos_rule_light_update, eos_rule_level_source_update)


def eos_rule_scene_update(event):
    """Eos Scene Received Update Rule"""
    eos.log.debug("{rule} triggered by '{name}' with scene '{scene}'".format(rule=eos.RULE_SCENE_NAME, name=event.itemName, scene=event.itemCommand))

    item = itemRegistry.get(event.itemName)

    for light in eos.get_light_items(eos.get_item_eos_group(item)):
        try: eos.update_light(light)
        except: continue
    for group in eos.get_group_items(eos.get_item_eos_group(item)):
        eos.update_group(group, True)


def eos_rule_light_update(event):
    """Eos Light Received Update Rule"""
    eos.log.debug("{rule} triggered by '{name}' with state '{state}'".format(rule=eos.RULE_LIGHT_NAME, name=event.itemName, state=event.itemState))
    eos.update_light(itemRegistry.get(event.itemName))


def eos_rule_level_source_update(event):
    """Eos Level Source Received Update Rule"""
    eos.log.debug("{rule} triggered by '{name}' with state '{state}'".format(rule=eos.RULE_LEVEL_SOURCE_NAME, name=event.itemName, state=event.itemState))
    eos.update_group(itemRegistry.get(eos.master_group_name))


@log_traceback
def scriptLoaded(*args):
    eos.init(eos_rule_reinit, eos_rule_scene_update, eos_rule_light_update, eos_rule_level_source_update)

@log_traceback
def scriptUnloaded(*args):
    eos.uninit()
