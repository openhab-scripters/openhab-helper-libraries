"""
Eos Lighting

Utilities
"""

from community.eos import log, config
from community.eos.constants import *

from core.utils import validate_item
from core.metadata import get_value, get_metadata as core_get_metadata

from ast import literal_eval
import copy

__all__ = [
    "resolve_type", "validate_item_name", "get_scene_item", "get_light_items",
    "get_group_items", "get_item_eos_group", "get_scene_for_item", "get_metadata",
    "get_scene_setting", "get_scene_type"
]


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
        # unparseable, return as str
        return value


def validate_item_name(name, prefix, suffix):
    """Verifies that ``name`` starts with ``prefix`` and ends with ``suffix``.

    Returns ``True`` or ``False``"""
    return name[:len(prefix)] == prefix and name[-len(suffix):] == suffix


def get_scene_item(group):
    """Finds the scene item in a group.

    Returns the scene item or ``None`` if it does not find exactly one match.
    """
    if not group: return None
    items = [item for item in group.members if validate_item_name(item.name, config.scene_item_prefix, config.scene_item_suffix)]
    if not items:
        if config.log_trace: log.debug("Group '{group}' does not contain a scene item".format(group=group.name))
        return None
    elif len(items) > 1:
        itemList = ""
        for item in items: itemList = "{list}'{name}', ".format(list=itemList, name=item.name)
        log.debug("Group '{group}' contains more than one scene item. Each group can only have one scene item, please correct. ({list})".format(
                group=group.name, list=itemList[:-2]))
        return None
    elif not isinstance(items[0], itemtypesScene):
        log.error("Group '{group}' scene item '{name}' is not a StringItem".format(group=group.name, name=items[0].name))
        return None
    else:
        if config.log_trace: log.debug("Got scene item '{name}' for group '{group}'".format(name=items[0].name, group=group.name))
        return items[0]


def get_light_items(group):
    """Finds all light items in a group.

    Returns a list of valid Eos lights.
    """
    return [
        item for item in group.members
            if not isinstance(item, itemtypesGroup)
                and isinstance(item, itemtypesLight)
                and item != get_scene_item(group)
                and resolve_type(get_value(item.name, META_NAME_EOS)) is not None
        ] if hasattr(group, "members") else []


def get_group_items(group, include_no_lights=False):
    """Finds all group items in a group.

    Returns a list of valid Eos groups.
    """
    return [
        item for item in group.members
            if isinstance(item, itemtypesGroup)
                and get_scene_item(group) is not None
                and (len(get_light_items(item)) > 0 or include_no_lights)
        ] if hasattr(group, "members") else []


def get_item_eos_group(item):
    """Gets the Eos group from the item's groups.

    Returns the group item or ``None`` if it does not find exactly one match.
    """
    groups = [group for group in item.groupNames if get_scene_item(validate_item(group))]
    if not groups:
        log.error("No Eos group found for item '{name}'".format(name=item.name))
        return None
    elif len(groups) > 1:
        groupList = ""
        for group in groups: groupList = "{list}'{group}', ".format(list=groupList, group=group)
        log.error("Item '{name}' is a memeber of more than one Eos group: {list}".format(name=item.name, list=groupList[:-2]))
        log.error("Each item can only be a member of one Eos group, please correct.")
        return None
    else:
        if config.log_trace: log.debug("Got Eos group '{group}' for item '{name}'".format(group=groups[0], name=item.name))
        return validate_item(groups[0])


def get_scene_for_item(item):
    """Returns the scene string applicable for ``item``.
    """
    scene_item = get_scene_item(get_item_eos_group(item))
    if scene_item.name == config.master_group_name and str(scene_item.state).lower() == SCENE_PARENT:
        # master group cannot inherit scene from parent, no parent
        # this is caused by invalid site configuration allowing master group scene
        # to be set to parent
        log.error("Master group '{group}' scene item '{name}' is set to 'parent', this is an impossible state. Using '{scene}' scene instead".format(
            group=config.master_group_name, name=scene_item.name, scene=SCENE_MANUAL))
        return SCENE_MANUAL
    elif str(scene_item.state).lower() == SCENE_PARENT:
        # group is set to inherit scene from parent
        return get_scene_for_item(get_item_eos_group(scene_item))
    elif isinstance(scene_item.state, typesUnDef):
        log.warn("Scene item '{name}' is not set, using '{scene}' scene instead.".format(
            name=scene_item.name, scene=SCENE_MANUAL))
        return SCENE_MANUAL
    else:
        return str(scene_item.state).lower()

def get_metadata(item_name, namespace):
    """
    Wrapper for ``get_metadata`` to translate to Python ``dict``.
    """
    def parse_config(config):
        value = copy.deepcopy(config)
        result = {}
        try:
            value = literal_eval(value)
        except: pass
        try:
            for key in value:
                result[str(key)] = parse_config(value[str(key)])
        except:
            if isinstance(value, basestring):
                value = str(value)
        if not value:
            if str(type(value)) == "<type 'java.util.Collections$UnmodifiableMap'>" \
                        or str(type(value)) == "<type 'java.util.LinkedHashMap'>":
                value = {}
        return result or value

    metadata = core_get_metadata(item_name, namespace)
    return {"value": metadata.value, "configuration": parse_config(metadata.configuration)} if metadata else {}

def get_scene_setting(item, scene, key, data=None, depth=10):
    """
    Gets a setting value by searching:
    Scene in Item > Item > Scene in Light Type in Group > Light Type in Group >
    Light Type in Group > Group > Scene in Light Type in Global > Scene in Global >
    Light Type in Global > Global
    """
    light_type = LIGHT_TYPE_MAP.get(item.type.lower(), None)
    item_data = data["item"] if data else get_metadata(item.name, META_NAME_EOS).get("configuration", {})
    if config.log_trace: log.debug("Got Item data for '{name}': {data}".format(name=item.name, data=item_data))
    group_data = data["group"] if data else get_metadata(get_item_eos_group(item).name, META_NAME_EOS).get("configuration", {})
    if config.log_trace: log.debug("Got Group data for '{name}': {data}".format(name=get_item_eos_group(item).name, data=group_data))
    global_data = config.global_settings
    if config.log_trace: log.debug("Got Global data: {data}".format(name=light_type, data=global_data))
    value = None
    if depth >= 1 and 1 in META_KEY_DEPTH_MAP[key] and item_data.get(scene, {}).get(key, None) is not None:
        source = "Scene in Item"
        value = item_data.get(scene, {}).get(key, None)
    elif depth >= 2 and 2 in META_KEY_DEPTH_MAP[key] and item_data.get(key, None) is not None:
        source = "Item"
        value = item_data.get(key, None)
    elif depth >= 3 and 3 in META_KEY_DEPTH_MAP[key] and group_data.get(light_type, {}).get(scene, {}).get(key, None) is not None:
        source = "Scene in Light Type in Group"
        value = group_data.get(light_type, {}).get(scene, {}).get(key, None)
    elif depth >= 4 and 4 in META_KEY_DEPTH_MAP[key] and group_data.get(scene, {}).get(key, None) is not None:
        source = "Scene in Group"
        value = group_data.get(scene, {}).get(key, None)
    elif depth >= 5 and 5 in META_KEY_DEPTH_MAP[key] and group_data.get(light_type, {}).get(key, None) is not None:
        source = "Light Type in Group"
        value = group_data.get(light_type, {}).get(key, None)
    elif depth >= 6 and 6 in META_KEY_DEPTH_MAP[key] and group_data.get(key, None) is not None:
        source = "Group"
        value = group_data.get(key, None)
    elif depth >= 7 and 7 in META_KEY_DEPTH_MAP[key] and global_data.get(light_type, {}).get(scene, {}).get(key, None) is not None:
        source = "Scene in Light Type in Global"
        value = global_data.get(light_type, {}).get(scene, {}).get(key, None)
    elif depth >= 8 and 8 in META_KEY_DEPTH_MAP[key] and global_data.get(scene, {}).get(key, None) is not None:
        source = "Scene in Global"
        value = global_data.get(scene, {}).get(key, None)
    elif depth >= 9 and 9 in META_KEY_DEPTH_MAP[key] and global_data.get(light_type, {}).get(key, None) is not None:
        source = "Light Type in Global"
        value = global_data.get(light_type, {}).get(key, None)
    elif depth >= 10 and 10 in META_KEY_DEPTH_MAP[key] and global_data.get(key, None) is not None:
        source = "Global"
        value = global_data.get(key, None)
    else:
        if config.log_trace: log.debug("No value found for key '{key}' for scene '{scene}' for item '{name}' at depth {depth}".format(
                key=key, scene=scene, name=item.name, depth=depth))
        return None
    if config.log_trace: log.debug("Got setting '{key}' for scene '{scene}' for item '{name}' from {source}: {value}".format(
            key=key, scene=scene, name=item.name, source=source, value=value))
    return value

def get_scene_type(item, scene, light_type, data=None):
    # gets the scene type
    for depth in range(1, 11):
        if light_type == LIGHT_TYPE_SWITCH:
            if get_scene_setting(item, scene, META_KEY_STATE, data=data, depth=depth) is not None:
                return SCENE_TYPE_FIXED
            elif get_scene_setting(item, scene, META_KEY_LEVEL_THRESHOLD, data=data, depth=depth) is not None:
                return SCENE_TYPE_THRESHOLD
        elif light_type == LIGHT_TYPE_DIMMER:
            if get_scene_setting(item, scene, META_KEY_STATE, data=data, depth=depth) is not None:
                return SCENE_TYPE_FIXED
            elif get_scene_setting(item, scene, META_KEY_LEVEL_HIGH, data=data, depth=depth) is not None \
            or get_scene_setting(item, scene, META_KEY_LEVEL_LOW, data=data, depth=depth) is not None \
            or get_scene_setting(item, scene, META_KEY_STATE_HIGH, data=data, depth=depth) is not None \
            or get_scene_setting(item, scene, META_KEY_STATE_LOW, data=data, depth=depth) is not None:
                return SCENE_TYPE_SCALED
            elif get_scene_setting(item, scene, META_KEY_LEVEL_THRESHOLD, data=data, depth=depth) is not None:
                return SCENE_TYPE_THRESHOLD
        elif light_type == LIGHT_TYPE_COLOR:
            if get_scene_setting(item, scene, META_KEY_STATE, data=data, depth=depth) is not None:
                return SCENE_TYPE_FIXED
            elif get_scene_setting(item, scene, META_KEY_LEVEL_HIGH, data=data, depth=depth) is not None \
            or get_scene_setting(item, scene, META_KEY_LEVEL_LOW, data=data, depth=depth) is not None \
            or get_scene_setting(item, scene, META_KEY_STATE_HIGH, data=data, depth=depth) is not None \
            or get_scene_setting(item, scene, META_KEY_STATE_LOW, data=data, depth=depth) is not None:
                return SCENE_TYPE_SCALED
            elif get_scene_setting(item, scene, META_KEY_LEVEL_THRESHOLD, data=data, depth=depth) is not None:
                return SCENE_TYPE_THRESHOLD
    return None
