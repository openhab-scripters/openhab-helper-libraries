"""
Eos Lighting Metadata Editor
"""

import sys
if sys.version_info[0] < 3: # Python 2.x
    str = basestring
else: # Python 3.x
    pass

import json
import requests as http
import click
from click import echo, clear

import rest_eos_menu as menu
import rest_eos_util as util
from rest_utils import validate_hostname, validate_item
from rest_metadata import get_value

CONF_KEY_MASTER_GROUP = "eos_master_group"
CONF_KEY_SCENE_PREFIX = "eos_scene_item_prefix"
CONF_KEY_SCENE_SUFFIX = "eos_scene_item_suffix"
CONF_KEY_GROUP_PREFIX = "eos_group_item_prefix"
CONF_KEY_GROUP_SUFFIX = "eos_group_item_suffix"
CONF_KEY_SCENE_DEFAULTS = "eos_scene_defaults"
CONF_KEY_REINIT_ITEM = "eos_reload_item_name"

META_NAME_EOS = "eos"
META_KEY_LEVEL_SOURCE = "level_source"
META_KEY_LEVEL_THRESHOLD = "level_threshold"
META_KEY_LEVEL_HIGH = "level_high"
META_KEY_LEVEL_LOW = "level_low"
META_KEY_STATE = "state"
META_KEY_STATE_ABOVE = "state_above"
META_KEY_STATE_BELOW = "state_below"
META_KEY_STATE_HIGH = "state_high"
META_KEY_STATE_LOW = "state_low"
META_KEY_MOTION_SOURCE = "motion_source"
META_KEY_MOTION_ACTIVE = "motion_active"
META_KEY_MOTION_STATE = "motion_state"
META_KEY_LIST = [META_KEY_LEVEL_SOURCE, META_KEY_LEVEL_THRESHOLD, META_KEY_LEVEL_HIGH, META_KEY_LEVEL_LOW,
    META_KEY_STATE, META_KEY_STATE_ABOVE, META_KEY_STATE_BELOW, META_KEY_STATE_HIGH, META_KEY_STATE_LOW,
    META_KEY_MOTION_SOURCE, META_KEY_MOTION_ACTIVE, META_KEY_MOTION_STATE]

LIGHT_TYPE_SWITCH = "switch"
LIGHT_TYPE_DIMMER = "dimmer"
LIGHT_TYPE_COLOR = "color"
LIGHT_TYPE_MAP = {"color": LIGHT_TYPE_COLOR, "dimmer": LIGHT_TYPE_DIMMER, "number": LIGHT_TYPE_DIMMER, "switch": LIGHT_TYPE_SWITCH}

SCENE_TYPE_FIXED = "fixed"
SCENE_TYPE_THRESHOLD = "threshold"
SCENE_TYPE_SCALED = "scaled"
SCENE_PARENT = "parent"
SCENE_MANUAL = "manual"
SCENE_ON = "on"
SCENE_OFF = "off"

master_group_name = ""
reinit_item_name = ""
scene_defaults = {
    LIGHT_TYPE_SWITCH: {
        SCENE_ON: { META_KEY_STATE: "ON" },
        SCENE_OFF: { META_KEY_STATE: "OFF" },
        META_KEY_STATE: "OFF",
        META_KEY_STATE_ABOVE: "OFF",
        META_KEY_STATE_BELOW: "ON"
    },
    LIGHT_TYPE_DIMMER: {
        SCENE_ON: { META_KEY_STATE: 100 },
        SCENE_OFF: { META_KEY_STATE: 0 },
        META_KEY_STATE: 0,
        META_KEY_STATE_HIGH: 0,
        META_KEY_STATE_LOW: 100,
        META_KEY_STATE_ABOVE: 0,
        META_KEY_STATE_BELOW: 100
    },
    LIGHT_TYPE_COLOR: {
        SCENE_ON: { META_KEY_STATE: 100 },
        SCENE_OFF: { META_KEY_STATE: 0 },
        META_KEY_STATE: 0,
        META_KEY_STATE_HIGH: 0,
        META_KEY_STATE_LOW: 100,
        META_KEY_STATE_ABOVE: 0,
        META_KEY_STATE_BELOW: 100
    }
}


def load_config(openhab_host):
    """Load Eos settings from ``{$OH_CONF}/automation/lib/python/configuration.py``
    """
    global master_group_name
    master_group_name = util.get_conf_value(CONF_KEY_MASTER_GROUP, str)
    if not master_group_name:
        echo("ERROR: No '{name}' specified in configuration".format(name=CONF_KEY_MASTER_GROUP), err=True)
        exit(1)

    if not util.get_conf_value(CONF_KEY_SCENE_PREFIX, str, "") and not util.get_conf_value(CONF_KEY_SCENE_SUFFIX, str, ""):
        echo("ERROR: Must specify at least one of '{prefix}' or '{suffix}' in configuration".format(prefix=CONF_KEY_SCENE_PREFIX, suffix=CONF_KEY_SCENE_SUFFIX), err=True)
        exit(1)

    global reinit_item_name
    reinit_item_name = util.get_conf_value(CONF_KEY_REINIT_ITEM)
    if reinit_item_name and validate_item(reinit_item_name, openhab_host) is None:
        echo("WARNING: Eos reload item '{name}' does not exist".format(name=reinit_item_name), err=True)
        reinit_item_name = ""

    master_group_item = validate_item(master_group_name, openhab_host)
    if not master_group_item:
        echo("ERROR: Master group item '{group}' does not exist".format(group=master_group_name))
        exit(1)
    elif master_group_item["type"] not in util.itemtypesGroup:
        echo("ERROR: Master group item '{group}' is not a GroupItem".format(group=master_group_name))
        exit(1)


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("-s", "--openhab-host", "opt_openhab_host")
def eos_editor(ctx, opt_openhab_host):
    """
    Eos Item Metadata Editor

    If called with no command it will start in interactive mode.
    """
    if ctx.invoked_subcommand is None: live()

@eos_editor.command()
@click.option("-s", "--openhab-host", "opt_openhab_host", prompt="Enter your openHAB server address", default="localhost:8080", callback=validate_hostname, help="openHAB server address")
def live(opt_openhab_host):
    """Interactive editing of all lights in Eos"""
    load_config(opt_openhab_host)
    menu.group(validate_item(master_group_name, opt_openhab_host), opt_openhab_host)

@eos_editor.command()
@click.option("-s", "--openhab-host", "opt_openhab_host", prompt="Enter your openHAB server address", default="localhost:8080", callback=validate_hostname, help="openHAB server address")
@click.argument("arg_item_name")
def edit(opt_openhab_host, arg_item_name):
    """Edit a single light"""
    load_config(opt_openhab_host)
    menu.light(validate_item(arg_item_name, opt_openhab_host), opt_openhab_host)
    clear()


if __name__ == "__main__": eos_editor()