"""
Eos Lighting

Config value loader
"""

from community.eos import log
from community.eos.constants import *

import sys

_master_group_name = ""
_scene_item_prefix = ""
_scene_item_suffix = ""
_reinit_item_name = ""
_scene_defaults = {
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

__all__ = [  ]


def _get_conf_value(name, valid_types=None, default=None):
    """Gets ``name`` from configuration.

    Returns ``default`` if not present or not one of types in ``valid_types``
    """
    # importing here so we can reload each time and catch any updates the user may have made
    import configuration
    reload(configuration)

    if hasattr(configuration, name):
        value = getattr(configuration, name)
        if valid_types is None or isinstance(value, valid_types):
            log.debug("Got '{name}': '{value}' from configuration".format(name=name, value=value))
            return value
        else:
            log.error("'{name}' is type '{type}', must be one of '{valid_types}'".format(
                name=name, type=type(value), valid_types=valid_types))
            return default
    else:
        log.debug("No '{name}' specified in configuration".format(name=name))
        return default

def load():
    #global _master_group_name, _scene_item_prefix, _scene_item_suffix, _reinit_item_name
    this.master_group_name = _get_conf_value(CONF_KEY_MASTER_GROUP, str, "")
    this.scene_item_prefix = _get_conf_value(CONF_KEY_SCENE_PREFIX, str, "")
    this.scene_item_suffix = _get_conf_value(CONF_KEY_SCENE_SUFFIX, str, "")
    this.reinit_item_name = _get_conf_value(CONF_KEY_REINIT_ITEM, str, "")
    this.scene_defaults = _scene_defaults.copy()
    this.scene_defaults.update(_get_conf_value(CONF_KEY_SCENE_DEFAULTS, dict, {}))

"""
def master_group_name():
    return _get_conf_value(CONF_KEY_MASTER_GROUP, str, "")

def scene_item_prefix():
    return _get_conf_value(CONF_KEY_SCENE_PREFIX, str, "")

def scene_item_suffix():
    return _get_conf_value(CONF_KEY_SCENE_SUFFIX, str, "")

def reinit_item_name():
    value = _get_conf_value(CONF_KEY_REINIT_ITEM, str, "")
    if validate_item(value):
        return value
    else:
        log.warn("Eos reload item '{name}' does not exist".format(name=value))
        return ""

def scene_defaults():
    value = _scene_defaults.copy
    value.update(_get_conf_value(CONF_KEY_SCENE_DEFAULTS, dict, {}))
    return value
"""

this = sys.modules[__name__]
load()
