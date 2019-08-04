"""
Eos Lighting

Utilities
"""

from community.eos import log, config
from community.eos.constants import *

from core.utils import validate_item
from core.metadata import get_value

from ast import literal_eval

__all__ = [
    "resolve_type", "validate_item_name", "get_scene_item", "get_light_items",
    "get_group_items", "get_item_eos_group", "get_scene_for_item"
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
        # parseable
        return value


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
    items = [item for item in group.members if validate_item_name(item.name, config.scene_item_prefix, config.scene_item_suffix)]
    if not items:
        log.error("Group '{group}' does not contain a scene item".format(group=group.name))
        return None
    elif len(items) > 1:
        itemList = ""
        for item in items: itemList = "{list}'{name}', ".format(list=itemList, name=item.name)
        log.error("Group '{group}' contains more than one scene item: {list}".format(group=group.name, list=itemList[:-2]))
        log.error("Each group can only have one scene item, please correct.")
        return None
    elif not isinstance(items[0], itemtypesScene):
        log.error("Group '{group}' scene item '{name}' is not a StringItem".format(group=group.name, name=items[0].name))
        return None
    else:
        log.debug("Got scene item '{name}' for group '{group}'".format(name=items[0].name, group=group.name))
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


def get_group_items(group):
    """Finds all group items in a group.

    Returns a list of valid Eos groups.
    """
    return [
        item for item in group.members
            if isinstance(item, itemtypesGroup)
                and get_item_eos_group(item)
                and get_scene_item(group) is not None
                and len(get_light_items(item)) > 0
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
        return validate_item(groups[0])


def get_scene_for_item(item):
    """Returns the scene string applicable for ``item``.
    """
    sceneItem = get_scene_item(get_item_eos_group(item))
    if sceneItem.name == config.master_group_name and str(sceneItem.state) == SCENE_PARENT:
        # master group cannot inherit scene from parent, no parent
        # this is caused by invalid site configuration allowing master group scene
        # to be set to parent
        log.error("Master group '{group}' scene item '{name}' is set to 'parent', this is an impossible state. Using state '{off}' instead".format(
            group=config.master_group_name, name=sceneItem.name, off=SCENE_OFF))
        return SCENE_OFF
    elif str(sceneItem.state) == SCENE_PARENT:
        # group is set to inherit scene from parent
        return get_scene_for_item(get_item_eos_group(sceneItem))
    else:
        return str(sceneItem.state).lower()
