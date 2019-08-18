"""
Eos Lighting Metadata Editor - Utilities
"""

import sys
if sys.version_info[0] < 3: # Python 2.x
    str = basestring
else: # Python 3.x
    pass

import os, json, copy, collections, six
from ast import literal_eval
from click import echo

from constants import *
from rest_metadata import get_metadata, get_value
from rest_utils import validate_item


__all__ = ["get_conf_value", "validate_item_name", "get_scene_item", "get_light_items",
    "get_group_items", "resolve_type", "get_item_eos_group", "get_other_items",
    "get_global_settings", "get_scene_setting", "get_scene_type"]


def get_conf_value(name, valid_types=None, default=None):
    """Get ``name`` from ``{$OH_CONF}/automation/lib/python/configuration.py``

    Returns ``default`` if not present or not one of types in ``valid_types``
    """
    conf_path = os.path.realpath("{}{sep}..{sep}..{sep}..".format(os.path.dirname(os.path.realpath(__file__)), sep=os.sep))
    sys.path.append(conf_path)
    import configuration
    sys.path.remove(conf_path)

    if hasattr(configuration, name):
        value = getattr(configuration, name)
        if valid_types is None or isinstance(value, valid_types):
            return value
        else:
            return default
    else:
        return default

def validate_item_name(name, prefix, suffix):
    """Verifies that ``name`` starts with ``prefix`` and ends with ``suffix``.
    Returns ``True`` or ``False``"""
    return name[:len(prefix)] == prefix and name[-len(suffix):] == suffix

def get_scene_item(group):
    """Finds the scene item in a group.

    Returns the scene item or ``None`` if it does not find exactly one match.
    """
    items = [item for item in group.get("members", {}) if validate_item_name(item["name"], get_conf_value(CONF_KEY_SCENE_PREFIX, default=""), get_conf_value(CONF_KEY_SCENE_SUFFIX, default=""))]
    if not items:
        return None
    elif len(items) > 1:
        return None
    elif items[0]["type"] not in itemtypesScene:
        return None
    else:
        return items[0]

def get_light_items(group, host):
    """Finds all light items in a group.

    Returns a list of valid Eos lights.
    """
    return [
        item for item in group["members"]
            if item["type"] not in itemtypesGroup
                and item["type"] in itemtypesLight
                and item["name"] != get_scene_item(group)["name"]
                and resolve_type(get_value(item["name"], META_NAME_EOS, host)) is not None
        ] if "members" in group else []

def get_group_items(group):
    """Finds all group items in a group.

    Returns a list of valid Eos groups.
    """
    return [
        item for item in group["members"]
            if item["type"] in itemtypesGroup
                and get_scene_item(group) is not None
        ] if "members" in group else []

def resolve_type(value):
    """Attempts to resolve the type of ``value``.

    It will return ``value`` as the python type if possible, otherwise will
    return value as string.
    """
    value = str(value).strip()
    if str(value).lower() == "true":
        return True
    elif str(value).lower() == "false":
        return False
    elif str(value).lower() == "none":
        return None
    else:
        # attempt to parse
        try:
            return literal_eval(value)
        except ValueError:
            pass
        # parseable
        return value

def get_item_eos_group(item, host):
    """Gets the Eos group from the item's groups.

    Returns the group item or ``None`` if it does not find exactly one match.
    """
    groups = [group for group in item["groupNames"] if get_scene_item(validate_item(group, host))]
    if not groups:
        return None
    elif len(groups) > 1:
        return None
    else:
        return validate_item(groups[0], host)

def get_other_items(group, host):
    """Finds all non Eos items in a group.

    Returns a list of all non Eos items in the group.
    """
    others = {item["name"]:item for item in group["members"]}
    for item in get_light_items(group, host):
        others.pop(item["name"], None)
    for item in get_group_items(group):
        others.pop(item["name"], None)
    for item in [item for item in group["members"] if item["name"] == get_conf_value(CONF_KEY_REINIT_ITEM, str)]:
        others.pop(item["name"], None)
    for item in [others[key] for key in others]:
        if item["type"] not in itemtypesLight and item["type"] != itemtypesGroup:
            others.pop(item["name"], None)
    others.pop(get_scene_item(group)["name"], None)
    return [others[key] for key in others]

def get_global_settings():
    def update(d, u):
        for k, v in six.iteritems(u):
            dv = d.get(k, {})
            if not isinstance(dv, collections.Mapping):
                d[k] = v
            elif isinstance(v, collections.Mapping):
                d[k] = update(dv, v)
            else:
                d[k] = v
        return d
    import constants
    global_settings = copy.deepcopy(constants._global_settings)
    return update(global_settings, get_conf_value(CONF_KEY_GLOBAL_SETTINGS, dict, {}))

def get_scene_setting(scene, light_type, key, data, max_depth=10, min_depth=1):
    # Gets a setting value by searching:
    # Scene in Item > Scene in Light Type in Group > Scene in Group >
    # Scene in Light Type in Global > Scene in Global > Item >
    # Light Type in Group > Group > Light Type in Global > Global
    item_data = data["item"]
    group_data = data["group"]
    global_data = data["global"]

    value = None
    if max_depth >= 1 and 1 >= min_depth and 1 in META_KEY_DEPTH_MAP[key] and item_data.get(scene, {}).get(key, None) is not None:
        # source = "Scene in Item"
        value = item_data.get(scene, {}).get(key, None)
    elif max_depth >= 2 and 2 >= min_depth and 2 in META_KEY_DEPTH_MAP[key] and group_data.get(light_type, {}).get(scene, {}).get(key, None) is not None:
        # source = "Scene in Light Type in Group"
        value = group_data.get(light_type, {}).get(scene, {}).get(key, None)
    elif max_depth >= 3 and 3 >= min_depth and 3 in META_KEY_DEPTH_MAP[key] and group_data.get(scene, {}).get(key, None) is not None:
        # source = "Scene in Group"
        value = group_data.get(scene, {}).get(key, None)
    elif max_depth >= 4 and 4 >= min_depth and 4 in META_KEY_DEPTH_MAP[key] and global_data.get(light_type, {}).get(scene, {}).get(key, None) is not None:
        # source = "Scene in Light Type in Global"
        value = global_data.get(light_type, {}).get(scene, {}).get(key, None)
    elif max_depth >= 5 and 5 >= min_depth and 5 in META_KEY_DEPTH_MAP[key] and global_data.get(scene, {}).get(key, None) is not None:
        # source = "Scene in Global"
        value = global_data.get(scene, {}).get(key, None)
    elif max_depth >= 6 and 6 >= min_depth and 6 in META_KEY_DEPTH_MAP[key] and item_data.get(key, None) is not None:
        # source = "Item"
        value = item_data.get(key, None)
    elif max_depth >= 7 and 7 >= min_depth and 7 in META_KEY_DEPTH_MAP[key] and group_data.get(light_type, {}).get(key, None) is not None:
        # source = "Light Type in Group"
        value = group_data.get(light_type, {}).get(key, None)
    elif max_depth >= 8 and 8 >= min_depth and 8 in META_KEY_DEPTH_MAP[key] and group_data.get(key, None) is not None:
        # source = "Group"
        value = group_data.get(key, None)
    elif max_depth >= 9 and 9 >= min_depth and 9 in META_KEY_DEPTH_MAP[key] and global_data.get(light_type, {}).get(key, None) is not None:
        # source = "Light Type in Global"
        value = global_data.get(light_type, {}).get(key, None)
    elif max_depth >= 10 and 10 >= min_depth and 10 in META_KEY_DEPTH_MAP[key] and global_data.get(key, None) is not None:
        # source = "Global"
        value = global_data.get(key, None)
    return resolve_type(value)

def get_scene_type(scene, light_type, data):
    # gets the scene type
    if not light_type: return "unknown"
    def _scan_settings(min_depth, max_depth):
        for depth in range(min_depth, max_depth+1):
            if get_scene_setting(scene, light_type, META_KEY_STATE, data, max_depth=depth) is not None:
                return SCENE_TYPE_FIXED
            elif light_type == LIGHT_TYPE_SWITCH:
                if get_scene_setting(scene, light_type, META_KEY_LEVEL_THRESHOLD, data, max_depth=depth) is not None:
                    return SCENE_TYPE_THRESHOLD
            elif light_type in [LIGHT_TYPE_DIMMER, LIGHT_TYPE_COLOR]:
                if get_scene_setting(scene, light_type, META_KEY_LEVEL_HIGH, data, max_depth=depth) is not None \
                or get_scene_setting(scene, light_type, META_KEY_LEVEL_LOW, data, max_depth=depth) is not None:
                    return SCENE_TYPE_SCALED
                elif max_depth < 5 \
                and (get_scene_setting(scene, light_type, META_KEY_STATE_HIGH, data, max_depth=depth) is not None \
                or get_scene_setting(scene, light_type, META_KEY_STATE_LOW, data, max_depth=depth) is not None):
                    return SCENE_TYPE_SCALED
                elif get_scene_setting(scene, light_type, META_KEY_LEVEL_THRESHOLD, data, max_depth=depth) is not None:
                    return SCENE_TYPE_THRESHOLD
        return None

    return _scan_settings(1, 5) or _scan_settings(6, 10)
