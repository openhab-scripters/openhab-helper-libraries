"""
Eos Lighting Metadata Editor - Utilities
"""

import sys
if sys.version_info[0] < 3: # Python 2.x
    str = basestring
else: # Python 3.x
    pass

import copy, six
from ast import literal_eval
from click import echo, clear
from questionary import select, Choice, Separator, text, confirm
from prompt_toolkit.styles import Style
from pygments import lex
import pygments.lexers.html
HtmlLexer = pygments.lexers.html.HtmlLexer()

from constants import *
from rest_eos_util import *
from rest_utils import validate_item, update_item
from rest_metadata import get_metadata, set_metadata

eos_style = Style([
    ("qmark", "fg:#673ab7 bold"),
    ("question", "bold"),
    ("answer", "fg:#f44336 bold"),
    ("highlighted", "fg:#cc5454"),
    ("selected", "fg:#cc5454"),
    ("text", "fg:#d4d4d4"),
    ("separator", 'fg:#c4c43f'),
    ("pointer", 'fg:#ff9d00 bold'),
    ("itemtype", "fg:#559ad4"),
    ("itemname", "fg:#d4d4d4"),
    ("itemlabel", "fg:#ce9178"),
    ("titletype", "fg:#559ad4 bold"),
    ("titlename", "fg:#d4d4d4 bold"),
    ("titlelabel", "fg:#ce9178 bold"),
    ("instruction", "fg:#d4d4d4 italic"),
    ("disabled", "fg:#858585 italic"),
    ("value", "fg:#9cdcfe"),
    ("valueapplies", "fg:#4ec932"),
    ("valuerequired", "fg:#f0300c bold")
])

col_left_width = 17
col_right_width = 25

def menu_navigate(root_group_name, host, back_group=None):
    """
    Display the Navigation menu
    """
    menu_message = "Eos Editor > Navigation Menu"
    answer = None
    pointed_at = None
    exit_loop = False
    while not exit_loop:
        echo("Building Menu...")

        root_group = validate_item(root_group_name, host)
        eos_lights = get_light_items(root_group, host)
        eos_groups = get_group_items(root_group)
        other_items = get_other_items(root_group, host)
        item_eos_group = get_item_eos_group(root_group, host)

        menu_choices = []
        menu_choices.append(Separator(line=" "))
        menu_choices.append(Choice(
                title=[
                    ("class:titletype", "Group"),
                    ("class:titlename", " {}".format(root_group["name"])),
                    ("class:titlelabel", "{}".format(" \"{}\"".format(root_group["label"]) if "label" in root_group else ""))
                ],
                disabled=True
            ))
        if item_eos_group:
            menu_choices.append(Choice(     # Item Eos Group
                    title=[
                        ("class:{}".format("disabled"), "{:{width}}".format("Eos Group", width=col_left_width)),
                        ("class:value", "{:{width}}".format(item_eos_group["name"], width=col_right_width))
                    ],
                    value="eos_menu_eos_group",
                    disabled=True
                ))
        menu_choices.append(Separator(line=" "))
        if eos_lights:
            menu_choices.append(Separator(line="    Eos Lights"))
            for item in eos_lights:
                if answer == item["name"]: pointed_at = len(menu_choices)
                menu_choices.append(Choice(
                        title=[
                            ("class:itemtype", "{}".format(item["type"])),
                            ("class:itemname", " {}".format(item["name"])),
                            ("class:itemlabel", "{}".format(" \"{}\"".format(item["label"]) if "label" in item else "")),
                        ],
                        value=item["name"]
                    ))
            menu_choices.append(Separator(line=" "))
        if eos_groups:
            menu_choices.append(Separator(line="    Eos Groups"))
            for item in eos_groups:
                if answer == item["name"]: pointed_at = len(menu_choices)
                menu_choices.append(Choice(
                        title=[
                            ("class:itemtype", "{}".format(item["type"])),
                            ("class:itemname", " {}".format(item["name"])),
                            ("class:itemlabel", "{}".format(" \"{}\"".format(item["label"]) if "label" in item else "")),
                        ],
                        value=item["name"]
                    ))
            menu_choices.append(Separator(line=" "))
        if other_items:
            menu_choices.append(Separator(line="    Non Eos Items"))
            for item in other_items:
                if answer == item["name"]: pointed_at = len(menu_choices)
                menu_choices.append(Choice(
                        title=[
                            ("class:itemtype", "{}".format(item["type"])),
                            ("class:itemname", " {}".format(item["name"])),
                            ("class:itemlabel", "{}".format(" \"{}\"".format(item["label"]) if "label" in item else "")),
                        ],
                        disabled="not implemented yet" if item["type"] == "Group" else False,        # TODO implement group adding
                        value=item["name"]
                    ))
            menu_choices.append(Separator(line=" "))
        menu_choices.append(Separator(line="    Options"))
        if answer == "eos_menu_configure": pointed_at = len(menu_choices)
        menu_choices.append(Choice(title="Configure Group", value="eos_menu_configure"))
        if answer == "eos_menu_add_existing": pointed_at = len(menu_choices)
        menu_choices.append(Choice(title="Add an existing light to this group", value="eos_menu_add_existing", disabled="not implemented yet"))
        if answer == "eos_menu_add_new_light": pointed_at = len(menu_choices)
        menu_choices.append(Choice(title="Add a new light to this group", value="eos_menu_add_new_light", disabled="not implemented yet"))
        if answer == "eos_menu_add_new_group": pointed_at = len(menu_choices)
        menu_choices.append(Choice(title="Add a new Eos group to this group", value="eos_menu_add_new_group", disabled="not implemented yet"))
        menu_choices.append(Separator(line=" "))
        if back_group:
            menu_choices.append(Choice(
                    title=[
                        ("class:text", "Back to '{}'".format(back_group)),
                        ("class:disabled", "  (ctrl+c)")
                    ],
                    value="eos_menu_back"
                ))
        menu_choices.append(Choice(
                title=[
                    ("class:text", "Exit"),
                    ("class:disabled", "  (ctrl+c)" if not back_group else "")
                ],
                value="eos_menu_exit"
            ))

        clear()
        answer = select(message=menu_message, choices=menu_choices, style=eos_style, qmark="", pointed_at=pointed_at).ask()

        if not answer:
            # ctrl+c - back or exit
            answer = "eos_menu_back" if back_group else "eos_menu_exit"

        if answer == "eos_menu_exit":
            # "Exit"
            clear()
            exit(0)
        elif answer == "eos_menu_back":
            # back to previous group
            exit_loop = True
        elif [item for item in eos_lights if item["name"] == answer]:
            # selected a light
            item = validate_item([item for item in eos_lights if item["name"] == answer][0]["name"], host)
            item, data = menu_eos(item, build_data(item, host), host, 6, is_light=True) or (None, None)
            if data:
                if not save_metadata(item, host, data):
                    pass                                    # TODO something went wrong
                if item.get("editable", False):
                    update_item(item, host)
            del item, data
        elif [item for item in eos_groups if item["name"] == answer]:
            # selected an eos group
            menu_navigate([item for item in eos_groups if item["name"] == answer][0], host, back_group=root_group["name"])
        elif [item for item in other_items if item["name"] == answer]:
            # selected a non-eos item
            item = validate_item([item for item in other_items if item["name"] == answer][0]["name"], host)
            item, data = menu_eos(item, build_data(item, host),
                    host, 8 if item["type"] in itemtypesGroup else 6,
                    is_light=True if item["type"] in itemtypesLight else False,
                    is_group=True if item["type"] in itemtypesGroup else False
                ) or (None, None)
            if data:
                if not save_metadata(item, host, data):
                    pass                                    # TODO something went wrong
                if item.get("editable", False):
                    update_item(item, host)
            del item, data
        elif answer == "eos_menu_configure":
            # edit Eos metadata
            item, data = menu_eos(root_group, build_data(root_group, host), host, 8, is_group=True) or (None, None)
            if data:
                if not save_metadata(item, host, data):
                    pass                                    # TODO something went wrong
                if item.get("editable", False):
                    update_item(item, host)
            del item, data
        elif answer == "eos_menu_add_existing":
            # add an existing item not in this group
            # TODO menu_light(menu_search_item(host), host)
            pass
        elif answer == "eos_menu_add_new_light":
            # add a new light to openhab and configure for eos
            # TODO menu_light(menu_add_item(host), host)
            pass
        elif answer == "eos_menu_add_new_group":
            # add a new group to openhab and configure for eos
            # TODO menu_light(menu_add_item(host), host)
            pass

    clear()

def save_metadata(item, host, data):
    """
    Saves metadata to openHAB
    """
    def purge_empty(d):
        # recursively purge empty dicts and 'None'
        for k in [k for k in d]:
            if isinstance(d[k], dict):
                purge_empty(d[k])
            if d[k] in [{}, None]:
                d.pop(k, None)

    value = str(data.pop("enabled"))

    if item["type"] in itemtypesLight:
        configuration = data["item"]
    else:
        configuration = [data["raw_groups"][i]["data"] for i in range(len(data["raw_groups"])) if data["raw_groups"][i]["name"] == item["name"]][0]

    purge_empty(configuration)

    return set_metadata(
            item["name"], META_NAME_EOS, host,
            configuration=configuration,
            value=value,
            overwrite=True
        )

def build_data(item, host):
    """
    Builds data structure for the eos menu
    """
    def _get_group_data(group):
        """
        Get all group ancestor's data, top level group settings are lowest priority
        """
        data["raw_groups"].append({"name": group["name"], "data": get_metadata(group["name"], META_NAME_EOS, host).get("config", {})})
        if get_item_eos_group(group, host):
            _get_group_data(get_item_eos_group(group, host))

    clear()
    echo("Loading Data...")

    data = {
        "item": {},
        "group": {},
        "raw_groups": [],
        "global": get_global_settings()}

    is_light = item["type"] in itemtypesLight
    is_group = item["type"] in itemtypesGroup

    item_metadata = get_metadata(item["name"], META_NAME_EOS, host)

    if is_light:
        data["item"] = item_metadata.get("config", {})
        data["light_type"] = LIGHT_TYPE_MAP.get(item.get("type", "").lower(), None)
        _get_group_data(get_item_eos_group(item, host))

    if is_group:
        _get_group_data(item)


    # get enabled option
    data["enabled"] = item_metadata.get("value", True)
    if isinstance(data["enabled"], str):
        if data["enabled"].lower() in META_STRING_FALSE:
            data["enabled"] = False
        else:
            data["enabled"] = True

    # make sure follow parent is bool
    if is_group:
        if isinstance(data.get("follow_parent", None), str):
            if data["follow_parent"].lower() in META_STRING_FALSE:
                data["follow_parent"] = False
            else:
                data["follow_parent"] = True

    return data

def menu_eos(item, data, host, depth, light_type=False, is_light=False,
                is_group=False, is_type=False, scene=None, view_only=False):
    """
    Edit a Light, Group, Light Type in a Group, or Scene
    """
    def data_at_depth(depth):
        # return the dict at the specified depth
        def _validate_key(d, k):
            if k not in d:
                d[k] = {}
            return d[k]

        if depth == 1:
            return _validate_key(data["item"], scene)
        elif depth in [2, 3, 4, 5]:
            return _validate_key(data_at_depth(depth+5), scene)
        elif depth == 6:
            return data["item"]
        elif depth in [7, 9]:
            return _validate_key(data_at_depth(depth+1), light_type)
        elif depth == 8:
            return [data["raw_groups"][i]["data"] for i in range(len(data["raw_groups"])) if data["raw_groups"][i]["name"] == item["name"]][0]
        elif depth == 10:
            return data["global"]

    def build_group_data():
        # builds the data dict used in Eos
        del data["group"]
        data["group"] = {}
        for i in range(len(data["raw_groups"])):
            data["group"] = update_dict(data["group"], data["raw_groups"][i]["data"])

    def get_scene_depth_for_type():
        # determine the depth a scene should be at
        if is_light:
            return 1
        elif is_type:
            return 2
        elif is_group:
            return 3

    def value_applies(key):
        # returns true if value will be used to evalute the current scene
        def _get_setting_depth(key):
            for scan_depth in range(depth, 11):
                if get_scene_setting(scene, light_type, key, data, max_depth=scan_depth, min_depth=scan_depth) is not None:
                    break
            return scan_depth

        property_map = {
            SCENE_TYPE_FIXED: [
                META_KEY_STATE
            ],
            SCENE_TYPE_THRESHOLD: [
                META_KEY_LEVEL_SOURCE, META_KEY_LEVEL_THRESHOLD,
                META_KEY_STATE_ABOVE, META_KEY_STATE_BELOW
            ],
            SCENE_TYPE_SCALED: [
                META_KEY_LEVEL_SOURCE, META_KEY_LEVEL_HIGH,
                META_KEY_LEVEL_LOW, META_KEY_STATE_HIGH, META_KEY_STATE_LOW,
                META_KEY_STATE_ABOVE, META_KEY_STATE_BELOW
            ]
        }
        if key in [META_KEY_MOTION_SOURCE, META_KEY_MOTION_ACTIVE, META_KEY_MOTION_STATE, META_KEY_MOTION_SCENE] \
                and get_scene_setting(scene, light_type, META_KEY_MOTION_SOURCE, data, min_depth=depth) is not None:
            if key == META_KEY_MOTION_SCENE:
                if _get_setting_depth(META_KEY_MOTION_SCENE) <= _get_setting_depth(META_KEY_MOTION_STATE):
                    return True
                else:
                    return False
            elif key == META_KEY_MOTION_STATE:
                if _get_setting_depth(META_KEY_MOTION_STATE) < _get_setting_depth(META_KEY_MOTION_SCENE):
                    return True
                else:
                    return False
            else:
                return True
        else:
            return key in property_map.get(scene_type, {}) and light_type and scene

    def get_missing_scene_settings():
        # return a list of keys for required settings missing for this scene
        scene_settings_map = {
            SCENE_TYPE_FIXED: [
                META_KEY_STATE
            ],
            SCENE_TYPE_THRESHOLD: [
                META_KEY_LEVEL_SOURCE, META_KEY_LEVEL_THRESHOLD,
                META_KEY_STATE_ABOVE, META_KEY_STATE_BELOW
            ],
            SCENE_TYPE_SCALED: [
                META_KEY_LEVEL_SOURCE, META_KEY_LEVEL_HIGH,
                META_KEY_LEVEL_LOW, META_KEY_STATE_HIGH, META_KEY_STATE_LOW
            ]
        }
        missing = []
        for key in scene_settings_map.get(scene_type, {}):
            if key not in settings_added:
                missing.append(key)
        if META_KEY_MOTION_SOURCE in settings_added:
            if META_KEY_MOTION_ACTIVE not in settings_added:
                missing.append(META_KEY_MOTION_ACTIVE)
            if META_KEY_MOTION_STATE not in settings_added and META_KEY_MOTION_SCENE not in settings_added:
                missing.append(META_KEY_MOTION_STATE)
                missing.append(META_KEY_MOTION_SCENE)
        return missing

    if not item: return
    if not (is_light or is_group or is_type or scene): return

    if not view_only: # don't waste memory if we won't be editing
        item = copy.deepcopy(item)
        data = copy.deepcopy(data)
    light_type = light_type or data.get("light_type", None)

    menu_message = "Eos Editor > {} {}".format(
            "View" if view_only else "Edit",
            "Light" if is_light else "Group" if is_group else "Light Type" if is_type else "Scene"
        )
    save = False
    answer = None
    pointed_at = None
    exit_loop = False
    while not exit_loop:
        clear()
        echo("Building Menu...")

        item_eos_group = get_item_eos_group(item, host)
        scene_type = get_scene_type(scene, light_type, data) if scene and depth==1 else "unknown"
        build_group_data()

        menu_choices = []
        menu_choices.append(Separator(line=" "))
        menu_choices.append(Choice(     # Title Item
                title=[
                    ("class:titletype", "{}".format(item["type"])),
                    ("class:titlename", " {}".format(item["name"])),
                    ("class:titlelabel", "{}".format(" \"{}\"".format(item["label"]) if "label" in item else ""))
                ],
                disabled=True
            ))
        if item_eos_group:
            if answer == "eos_menu_eos_group": pointed_at = len(menu_choices)
            menu_choices.append(Choice(     # Item Eos Group
                    title=[
                        ("class:{}".format("disabled" if view_only or not item["editable"] else "text"),
                            "{:{width}}".format("Eos Group", width=col_left_width)),
                        ("class:value", "{:{width}}".format(item_eos_group["name"], width=col_right_width))
                    ],
                    value="eos_menu_eos_group",
                    disabled=not item["editable"]
                ))
        if light_type:
            menu_choices.append(Choice(     # Light Type
                    title=[
                        ("class:disabled", "{:{width}}".format("Eos Light Type", width=col_left_width)),
                        ("class:value", "{:{width}}".format(light_type.capitalize(), width=col_right_width))
                    ],
                    value="eos_menu_light_type",
                    disabled=True
                ))
        menu_choices.append(Separator(line=" "))
        if scene:
            if answer == "eos_menu_edit_scene_name": pointed_at = len(menu_choices)
            menu_choices.append(Choice(     # Scene Name
                    title=[
                        ("class:{}".format("disabled" if view_only else "text"),
                            "{:{width}}".format("Scene Name", width=col_left_width)),
                        ("class:value", "{:{width}}".format(scene, width=col_right_width))
                    ],
                    value="eos_menu_edit_scene_name",
                    disabled=view_only
                ))
            menu_choices.append(Choice(     # Scene Type
                    title=[
                        ("class:disabled", "{:{width}}".format("Scene Type", width=col_left_width)),
                        ("class:value", "{:{width}}".format(scene_type.capitalize(), width=col_right_width))
                    ],
                    value="eos_menu_scene_type",
                    disabled=True
                ))
            menu_choices.append(Separator(line=" "))
        if is_light or is_group:
            menu_choices.append(Separator(line="    Options"))
            if answer == "eos_menu_enabled": pointed_at = len(menu_choices)
            menu_choices.append(Choice(     # Item Enabled
                    title=[
                        ("class:text", "{:{width}}".format("Enabled", width=col_left_width)),
                        ("class:value", "{:{width}}".format(str(data["enabled"]), width=col_right_width))
                    ],
                    value="eos_menu_enabled"
                ))
            if is_group:
                if answer == "eos_menu_follow_parent": pointed_at = len(menu_choices)
                menu_choices.append(Choice(     # Group Follow Parent
                        title=[
                            ("class:text", "{:{width}}".format("Follow Parent", width=col_left_width)),
                            ("class:value", "{:{width}}".format(str(data.get("follow_parent", True)), width=col_right_width))
                        ],
                        value="eos_menu_follow_parent"
                    ))
            menu_choices.append(Separator(line=" "))
        if is_group:
            menu_choices.append(Separator(line="    Light Types"))
            for key in LIGHT_TYPE_LIST:
                if answer == "eos_menu_light_type_{}".format(key): pointed_at = len(menu_choices)
                menu_choices.append(Choice(     # Light Types
                        title=[
                            ("class:text", key.capitalize())
                        ],
                        value="eos_menu_light_type_{}".format(key)
                    ))
            menu_choices.append(Separator(line=" "))
        if not scene:
            menu_choices.append(Separator(line="    Scenes"))
            scenes_added = []
            if is_light:
                for key in sorted([key for key in data["item"] if isinstance(data["item"][key], dict)]):
                    scenes_added.append(key)
                    if answer == "eos_menu_scene_{}".format(key): pointed_at = len(menu_choices)
                    menu_choices.append(Choice(     # Item Scenes
                            title=[
                                ("class:text", "{:{width}}".format(key, width=col_left_width)),
                                ("class:value", "{:{width}}".format(str(get_scene_type(key, light_type, data)).capitalize(), width=col_right_width)),
                                ("class:disabled", " item"),
                            ],
                            value="eos_menu_scene_{}".format(key)
                        ))
            for key in sorted([key for key in data["group"].get(light_type, {}) if isinstance(data["group"][light_type][key], dict) and key not in scenes_added]):
                scenes_added.append(key)
                if answer == "eos_menu_scene_{}".format(key): pointed_at = len(menu_choices)
                menu_choices.append(Choice(     # Light Type Scenes in Group
                        title=[
                            ("class:text", "{:{width}}".format(key, width=col_left_width)),
                            ("class:value", "{:{width}}".format(
                                str(get_scene_type(key, light_type, data)).capitalize() if is_light else "", width=col_right_width)),
                            ("class:disabled", " group-type {}".format(get_source_group(None, light_type, key, item["name"], data))),
                        ],
                        value="eos_menu_scene_{}".format(key)
                    ))
            for key in sorted([key for key in data["group"] if isinstance(data["group"][key], dict) and key not in LIGHT_TYPE_LIST and key not in scenes_added]):
                scenes_added.append(key)
                if answer == "eos_menu_scene_{}".format(key): pointed_at = len(menu_choices)
                menu_choices.append(Choice(     # Group Scenes
                        title=[
                            ("class:text", "{:{width}}".format(key, width=col_left_width)),
                            ("class:value", "{:{width}}".format(
                                str(get_scene_type(key, light_type, data)).capitalize() if is_light else "", width=col_right_width)),
                            ("class:disabled", " group {}".format(get_source_group(None, None, key, item["name"], data))),
                        ],
                        value="eos_menu_scene_{}".format(key)
                    ))
            for key in sorted([key for key in data["global"].get(light_type, {}) if isinstance(data["global"][light_type][key], dict) and key not in scenes_added]):
                scenes_added.append(key)
                if answer == "eos_menu_scene_{}".format(key): pointed_at = len(menu_choices)
                menu_choices.append(Choice(     # Light Type Scenes in Global
                        title=[
                            ("class:text", "{:{width}}".format(key, width=col_left_width)),
                            ("class:value", "{:{width}}".format(
                                str(get_scene_type(key, light_type, data)).capitalize() if is_light else "", width=col_right_width)),
                            ("class:disabled", " global-type"),
                        ],
                        value="eos_menu_scene_{}".format(key)
                    ))
            for key in sorted([key for key in data["global"] if isinstance(data["global"][key], dict) and key not in LIGHT_TYPE_LIST and key not in scenes_added]):
                scenes_added.append(key)
                if answer == "eos_menu_scene_{}".format(key): pointed_at = len(menu_choices)
                menu_choices.append(Choice(     # Global Scenes
                        title=[
                            ("class:text", "{:{width}}".format(key, width=col_left_width)),
                            ("class:value", "{:{width}}".format(
                                str(get_scene_type(key, light_type, data)).capitalize() if is_light else "", width=col_right_width)),
                            ("class:disabled", " global"),
                        ],
                        value="eos_menu_scene_{}".format(key)
                    ))
            del scenes_added
            if is_light:
                if answer == "eos_menu_test_scene": pointed_at = len(menu_choices)
                menu_choices.append(Choice(title="Test Scene", value="eos_menu_test_scene"))
            if answer == "eos_menu_add_scene": pointed_at = len(menu_choices)
            menu_choices.append(Choice(title="Add", value="eos_menu_add_scene"))
        menu_choices.append(Separator(line=" "))
        menu_choices.append(Separator(line="    Settings"))
        settings_added = []
        for scan_depth in range(depth, 11):
            for key in META_KEY_LIST:
                if key not in settings_added:
                    value = get_scene_setting(scene, light_type, key, data, max_depth=scan_depth, min_depth=scan_depth)
                    if value is not None:
                        settings_added.append(key)
                        if answer == "eos_menu_setting_{}".format(key): pointed_at = len(menu_choices)
                        menu_choices.append(Choice(     # Settings
                                title=[
                                    ("class:{}".format("disabled" if view_only else "text"),
                                        "{:{width}}".format(key, width=col_left_width)),
                                    ("class:{}".format("valueapplies" if value_applies(key) else "value"),
                                        "{:{width}} ".format("\"{}\"".format(value) if isinstance(value, str) else str(value),
                                        width=col_right_width)),
                                    ("class:disabled", "{} {}".format(DEPTH_NAME_MAP[scan_depth],
                                        get_source_group(key, light_type, scene, item["name"], data) if scan_depth in [2,3,7,8] else "")),
                                ],
                                value="eos_menu_setting_{}".format(key),
                                disabled=view_only
                            ))
        if scene and depth == 1:
            for key in get_missing_scene_settings():
                if answer == "eos_menu_setting_{}".format(key): pointed_at = len(menu_choices)
                menu_choices.append(Choice(     # Missing Settings
                        title=[
                            ("class:{}".format("disabled" if view_only else "text"),
                                "{:{width}}".format(key, width=col_left_width)),
                            ("class:valuerequired", "REQUIRED")
                        ],
                        value="eos_menu_setting_{}".format(key),
                        disabled=view_only
                    ))
        del settings_added
        if not view_only:
            if answer == "eos_menu_add_setting": pointed_at = len(menu_choices)
            menu_choices.append(Choice(title="Add", value="eos_menu_add_setting"))
        menu_choices.append(Separator(line=" "))
        if not view_only:
            menu_choices.append(Choice(title="Save" if (is_light or is_group) else "Apply", value="eos_menu_save"))
        if scene and scene in data_at_depth(depth+5) and not view_only:
            if answer == "eos_menu_remove_scene": pointed_at = len(menu_choices)
            menu_choices.append(Choice(title="Remove scene from {}".format("Light" if depth==1 else "Light Type" if depth==2 else "Group"), value="eos_menu_remove_scene"))
        menu_choices.append(Choice(
                title=[
                    ("class:text", "Done" if view_only else "Cancel"),
                    ("class:disabled", "  (ctrl+c)")
                ],
                value="eos_menu_cancel"
            ))

        clear()
        answer = select(message=menu_message, choices=menu_choices, style=eos_style, qmark="", pointed_at=pointed_at).ask()

        if not answer or answer == "eos_menu_cancel":
            # ctrl+c, or "Cancel"
            exit_loop = True
        elif answer == "eos_menu_eos_group":
            # change item to another group
            new_group = prompt_select_group(item, host)
            if new_group:
                if item_eos_group in item["groupNames"]:
                    item["groupNames"].remove(item_eos_group)
                item["groupNames"].append(new_group)
            del new_group
        elif answer == "eos_menu_edit_scene_name":
            # edit scene name
            new_scene = prompt_text("Enter a new scene name:", default=scene)
            if new_scene and new_scene.lower() != scene:
                data_at_depth(depth+5)[new_scene] = data_at_depth(depth+5).get(scene, {})
                if scene in data_at_depth(depth+5): del data_at_depth(depth+5)[scene]
                scene = new_scene
            del new_scene
        elif answer == "eos_menu_enabled":
            # toggle enabled
            data["enabled"] = not data["enabled"]
        elif answer == "eos_menu_follow_parent":
            # toggle follow parent
            data["follow_parent"] = not data.get("follow_parent", True)
        elif answer[:len("eos_menu_light_type_")] == "eos_menu_light_type_":
            # edit data for light type
            item, data = menu_eos(item, data, host, 7,
                    light_type=answer[len("eos_menu_light_type_"):],
                    is_type=True
                ) or (item, data)
        elif answer[:len("eos_menu_scene_")] == "eos_menu_scene_":
            # edit scene
            item, data = menu_eos(item, data, host,
                    get_scene_depth_for_type(),
                    light_type=light_type,
                    scene=answer[len("eos_menu_scene_"):]
                ) or (item, data)
        elif answer == "eos_menu_test_scene":
            # evaluate a scene to see the options that will be used
            menu_eos(item, data, host, 1, light_type=light_type,
                    scene=prompt_scene_name("Enter the name of a scene to evaluate:"),
                    view_only=True
                )
        elif answer == "eos_menu_add_scene":
            # add a new scene
            new_scene = prompt_scene_name("Enter a name for the new scene:")
            if new_scene:
                item, data = menu_eos(item, data, host, get_scene_depth_for_type(),
                        light_type=light_type, scene=new_scene
                    ) or (item, data)
            del new_scene
        elif answer[:len("eos_menu_setting_")] == "eos_menu_setting_":
            # edit existing setting or add one to item if defined at group or type level
            new_value = prompt_edit_setting(
                    "Enter a new value for {}:".format(answer[len("eos_menu_setting_"):]),
                    answer[len("eos_menu_setting_"):], host,
                    default=get_scene_setting(scene, light_type, answer[len("eos_menu_setting_"):], data, min_depth=depth)
                )
            if new_value is None:
                if answer[len("eos_menu_setting_"):] in data_at_depth(depth):
                    data_at_depth(depth).pop(answer[len("eos_menu_setting_"):], None)
            else:
                data_at_depth(depth)[answer[len("eos_menu_setting_"):]] = new_value
            del new_value
        elif answer == "eos_menu_add_setting":
            # add a new setting to this item
            new_key = prompt_select_setting(depth, keys_to_hide=[key for key in data_at_depth(depth) if key in META_KEY_LIST])
            if new_key in META_KEY_LIST:
                new_value = prompt_edit_setting("Enter a new value for {}:".format(new_key), new_key, host)
                if new_value is not None:
                    data_at_depth(depth)[new_key] = new_value
                    answer = "eos_menu_setting_{}".format(new_key)
                del new_value
            del new_key
        elif answer == "eos_menu_save":
            # save data
            save = True
            exit_loop = True
        elif answer == "eos_menu_remove_scene":
            # remove scene
            save = True
            exit_loop = True
            data_at_depth(depth+5).pop(scene, None)

    clear()
    return (item, data) if save else False

def prompt_text(message, pre_lines=[], default=""):
    """
    Prompt for text input
    """
    default = str(default) if default is not None else ""
    clear()
    for line in pre_lines: echo(line)
    return text(message=message, default=default, style=eos_style, qmark="").ask()

def prompt_select_group(item, host):
    """
    Prompt to select an Eos group
    """
    def search_group(target_group, depth=0):
        # recursive Eos group finder
        results = []
        for group in get_group_items(target_group):
            results.append(group)
            results[len(results)-1]["name"] = "{}{name}".format("  " * depth, name=results[len(results)-1]["name"])
            results.extend(search_group(group), depth+1)
        return results

    eos_groups = [validate_item(get_conf_value("eos_master_group"), host)]
    eos_groups.extend(search_group(eos_groups[0]))
    item_group = (get_item_eos_group(item, host) or {}).get("name", None)

    menu_message = "Eos Editor > Select Eos Group"
    pointed_at = None
    menu_choices = []
    menu_choices.append(Separator(line=" "))
    menu_choices.append(Choice(
            title=[
                ("class:titletype", "{}".format(item["type"])),
                ("class:titlename", " {}".format(item["name"])),
                ("class:titlelabel", "{}".format(" \"{}\"".format(item["label"]) if "label" in item else ""))
            ],
            disabled=True
        ))
    menu_choices.append(Separator(line=" "))
    for group in eos_groups:
        if group["name"] == item_group: pointed_at = len(menu_choices)
        menu_choices.append(Choice(
                title=[
                    ("class:itemtype", "{}".format(group["type"])),
                    ("class:itemname", " {}".format(group["name"])),
                    ("class:itemlabel", "{}".format(" \"{}\"".format(group["label"]) if "label" in group else "")),
                ],
                value=group["name"].strip()
            ))

    clear()
    return select(message=menu_message, choices=menu_choices, style=eos_style, qmark="", pointed_at=pointed_at).ask()

def prompt_scene_name(message, instructions=[], default=""):
    """
    Prompt for a scene name
    """
    err_msg = None
    while True:
        answer = prompt_text(message, pre_lines=[err_msg]+instructions, default=default)
        if answer:
            if answer.lower() in ["parent", "manual", "enabled", "follow_parent", "light_type", "true", "false", "none"]+META_KEY_LIST:
                err_msg = ("class:pointer", "Reserved keywords cannot be used for scene names!")
                default = answer
            else:
                return answer
        else:
            return None

def prompt_select_setting(depth, keys_to_hide=[]):
    """
    Prompt to select a setting to add
    """
    menu_message = "Eos Editor > Select Setting"
    menu_choices = []
    menu_choices.append(Separator(line=" "))
    menu_choices.append(Choice(
            title=[("class:text", "Select setting to add:")],
            value="eos_menu_message",
            disabled=True
        ))
    menu_choices.append(Separator(line=" "))
    for key in META_KEY_LIST:
        if key not in keys_to_hide and depth in META_KEY_DEPTH_MAP[key]:
            menu_choices.append(str(key))
    menu_choices.append(Separator(line=" "))
    menu_choices.append(Choice(title="Cancel", value="eos_menu_cancel"))

    clear()
    return select(message=menu_message, choices=menu_choices, style=eos_style, qmark="").ask()

def prompt_edit_setting(message, key, host, instructions=[], default=""):
    """
    Prompt for new setting value
    """
    if key is None: return default
    leave_blank = ["Leave blank to remove this setting"]
    valid = False
    err_msg = None
    while not valid:
        clear()

        answer = prompt_text(message, pre_lines=[err_msg]+instructions+leave_blank, default=default)

        if answer is None or answer == "":
            answer = None
            valid = True
        elif key in [META_KEY_LEVEL_SOURCE, META_KEY_MOTION_SOURCE]:
            valid = True if validate_item(answer, host) else False
            if not valid: err_msg = "Value of {key} must be an item that exists!".format(key=key)
        elif key in [META_KEY_LEVEL_HIGH, META_KEY_LEVEL_LOW, META_KEY_LEVEL_THRESHOLD]:
            answer = resolve_type(answer)
            valid = True if isinstance(answer, (int, float)) else False
            if not valid: err_msg = "Value of {key} must be a number!".format(key=key)
        elif len(str(answer).split(",")) == 3:
            # list for color state
            hsb = [resolve_type(part.strip()) for part in str(answer).split(",") if isinstance(resolve_type(part.strip()), (int, float))]
            valid = True if len(hsb)==3 else False
            if not valid: err_msg = "HSB states must be 3 numbers"
        else:
            valid = True
        # TODO keys that still need validation:
            # META_KEY_STATE = "state"
            # META_KEY_STATE_ABOVE = "state_above"
            # META_KEY_STATE_BELOW = "state_below"
            # META_KEY_STATE_HIGH = "state_high"
            # META_KEY_STATE_LOW = "state_low"
            # META_KEY_MOTION_ACTIVE = "motion_active"
            # META_KEY_MOTION_STATE = "motion_state"
            # META_KEY_MOTION_SCENE = "motion_scene"

        if not valid: default = answer

    return answer
