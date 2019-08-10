"""
Eos Lighting

Config value loader
"""

from community.eos import log
from community.eos.constants import *
from community.eos import constants

import sys, copy, collections

_master_group_name = ""
_scene_item_prefix = ""
_scene_item_suffix = ""
_reinit_item_name = ""

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
    this.master_group_name = _get_conf_value(CONF_KEY_MASTER_GROUP, str, "")
    this.scene_item_prefix = _get_conf_value(CONF_KEY_SCENE_PREFIX, str, "")
    this.scene_item_suffix = _get_conf_value(CONF_KEY_SCENE_SUFFIX, str, "")
    this.reinit_item_name = _get_conf_value(CONF_KEY_REINIT_ITEM, str, "")
    this.log_trace = _get_conf_value(CONF_KEY_LOG_TRACE, None, False)

    # recursively update global settings with dict from config
    def update(d, u):
        for k, v in u.iteritems():
            dv = d.get(k, {})
            if not isinstance(dv, collections.Mapping):
                d[k] = v
            elif isinstance(v, collections.Mapping):
                d[k] = update(dv, v)
            else:
                d[k] = v
        return d
    global_settings = copy.deepcopy(constants._global_settings)
    this.global_settings = update(global_settings, _get_conf_value(CONF_KEY_GLOBAL_SETTINGS, dict, {}))


this = sys.modules[__name__]
load()
