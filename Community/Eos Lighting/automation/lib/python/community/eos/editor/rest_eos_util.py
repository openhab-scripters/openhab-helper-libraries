"""
Eos Lighting Metadata Editor - Utilities
"""

import sys
if sys.version_info[0] < 3: # Python 2.x
    str = basestring
else: # Python 3.x
    pass

import os, json
from ast import literal_eval
from click import echo

from rest_metadata import get_metadata, get_value
from rest_utils import validate_item
import rest_editor_eos as eos

itemtypesScene = ["String"]
itemtypesLight = ["Color", "Dimmer", "Number", "Switch"]
itemtypesSwitch = ["Switch"]
itemtypesDimmer = ["Color", "Dimmer", "Number"]
itemtypesColor = ["Color"]
itemtypesGroup = ["Group"]

__all__ = ["get_conf_value", "validate_item_name", "get_scene_item", "get_light_items",
    "get_group_items", "resolve_type", "get_item_eos_group", "get_scene_type"]


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
    if name[:len(prefix)] == prefix and name[-len(suffix):] == suffix:
        return True
    else:
        return False

def get_scene_item(group):
    """Finds the scene item in a group.

    Returns the scene item or ``None`` if it does not find exactly one match.
    """
    if group is None: return None
    items = [item for item in group["members"] if validate_item_name(item["name"], get_conf_value(eos.CONF_KEY_SCENE_PREFIX, default=""), get_conf_value(eos.CONF_KEY_SCENE_SUFFIX, default=""))]
    if not items:
        return None
    elif len(items) > 1:
        return None
    elif items[0]["type"] not in itemtypesScene:
        return None
    else:
        return items[0]

def get_light_items(group, openhab_host):
    """Finds all light items in a group.

    Returns a list of valid Eos lights.
    """
    return [
        item for item in group["members"]
            if item["type"] not in itemtypesGroup
                and item["type"] in itemtypesLight
                and item["name"] != get_scene_item(group)["name"]
                and resolve_type(get_value(item["name"], eos.META_NAME_EOS, openhab_host)) is not None
        ] if "members" in group else []

def get_group_items(group):
    """Finds all group items in a group.

    Returns a list of valid Eos groups.
    """
    return [
        item for item in group["members"]
            if item["type"] in itemtypesGroup
                and validate_item_name(item["name"], get_conf_value(eos.CONF_KEY_GROUP_PREFIX, default=""), get_conf_value(eos.CONF_KEY_GROUP_SUFFIX, default=""))
                and get_scene_item(group) is not None
        ] if "members" in group else []
                # removed because we want any groups that might have lights we can configure
                #and len(get_light_items(item)) > 0

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

def get_item_eos_group(item, openhab_host):
    """Gets the Eos group from the item's groups.

    Returns the group item or ``None`` if it does not find exactly one match.
    """
    groups = [group for group in item["groupNames"] if get_scene_item(validate_item(group, openhab_host))]
    if not groups:
        return None
    elif len(groups) > 1:
        return None
    else:
        return validate_item(groups[0], openhab_host)

def get_other_items(group, openhab_host):
    """Finds all non Eos items in a group.

    Returns a list of all non Eos items in the group.
    """
    others = [item for item in group["members"]]
    for item in get_light_items(group, openhab_host):
        others.remove(item)
    for item in get_group_items(group):
        others.remove(item)
    try:
        others.remove(get_scene_item(group))
    except:
        pass
    return others

def get_scene_type(item, scene):
    """
    Determine the scene type of ``scene`` for ``item``

    Returns the name of scene type
    """
    return "SCENE TYPE"
