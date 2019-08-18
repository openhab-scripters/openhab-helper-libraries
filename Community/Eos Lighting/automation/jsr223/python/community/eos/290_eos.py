"""
Eos Lighting System
"""

from core.log import log_traceback
from community.eos import log
from community.eos.system import init, uninit
from community.eos.update import update_light, update_scene, update_eos
from community.eos.constants import *


def eos_rule_reinit(event):
    """Eos System Reload Rule"""
    log.debug("{rule} triggered by '{name}'".format(rule=RULE_REINIT_NAME, name=event.itemName))
    uninit()
    init(eos_rule_reinit, eos_rule_scene_command, eos_rule_light_update, eos_rule_level_source_update, eos_rule_motion_source_changed)


def eos_rule_scene_command(event):
    """Eos Scene Received Command Rule"""
    log.debug("{rule} triggered by '{name}' with scene '{scene}'".format(rule=RULE_SCENE_NAME, name=event.itemName, scene=event.itemCommand))
    update_scene(itemRegistry.get(event.itemName))


def eos_rule_light_update(event):
    """Eos Light Received Update Rule"""
    log.debug("{rule} triggered by '{name}' with state '{state}'".format(rule=RULE_LIGHT_NAME, name=event.itemName, state=event.itemState))
    update_light(itemRegistry.get(event.itemName))


def eos_rule_level_source_update(event):
    """Eos Level Source Received Update Rule"""
    log.debug("{rule} triggered by '{name}' with state '{state}'".format(rule=RULE_LEVEL_SOURCE_NAME, name=event.itemName, state=event.itemState))
    update_eos()


def eos_rule_motion_source_changed(event):
    """Eos Motion Source Changed Rule"""
    log.debug("{rule} triggered by '{name}' with state '{state}'".format(rule=RULE_MOTION_SOURCE_NAME, name=event.itemName, state=event.itemState))
    update_eos()


@log_traceback
def scriptLoaded(*args):
    init(eos_rule_reinit, eos_rule_scene_command, eos_rule_light_update, eos_rule_level_source_update, eos_rule_motion_source_changed)

@log_traceback
def scriptUnloaded(*args):
    uninit()
