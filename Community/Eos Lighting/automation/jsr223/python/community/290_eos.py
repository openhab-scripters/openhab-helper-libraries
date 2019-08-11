"""
Eos Lighting System
"""

from core.log import log_traceback
from community.eos import log, update_eos
from community.eos.system import init, uninit
from community.eos.update import update_light, update_scene
from community.eos.constants import RULE_REINIT_NAME, RULE_SCENE_NAME, RULE_LIGHT_NAME, RULE_LEVEL_SOURCE_NAME


def eos_rule_reinit(event):
    """Eos System Reload Rule"""
    log.debug("{rule} triggered by '{name}'".format(rule=RULE_REINIT_NAME, name=event.itemName))
    uninit()
    init(eos_rule_reinit, eos_rule_scene_changed, eos_rule_light_update, eos_rule_level_source_update)


def eos_rule_scene_changed(event):
    """Eos Scene Changed Rule"""
    log.debug("{rule} triggered by '{name}' with scene '{scene}'".format(rule=RULE_SCENE_NAME, name=event.itemName, scene=event.itemState))
    update_scene(itemRegistry.get(event.itemName))


def eos_rule_light_update(event):
    """Eos Light Received Update Rule"""
    log.debug("{rule} triggered by '{name}' with state '{state}'".format(rule=RULE_LIGHT_NAME, name=event.itemName, state=event.itemState))
    update_light(itemRegistry.get(event.itemName))


def eos_rule_level_source_update(event):
    """Eos Level Source Received Update Rule"""
    log.debug("{rule} triggered by '{name}' with state '{state}'".format(rule=RULE_LEVEL_SOURCE_NAME, name=event.itemName, state=event.itemState))
    update_eos()


@log_traceback
def scriptLoaded(*args):
    init(eos_rule_reinit, eos_rule_scene_changed, eos_rule_light_update, eos_rule_level_source_update)

@log_traceback
def scriptUnloaded(*args):
    uninit()
