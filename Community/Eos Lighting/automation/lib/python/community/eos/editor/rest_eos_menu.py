"""
Eos Lighting Metadata Editor - Utilities
"""

import sys
if sys.version_info[0] < 3: # Python 2.x
    str = basestring
else: # Python 3.x
    pass

import copy
from ast import literal_eval
from click import echo, clear
from questionary import select, Choice, Separator, text, confirm
from prompt_toolkit.styles import Style
from pygments import lex
import pygments.lexers.html
HtmlLexer = pygments.lexers.html.HtmlLexer()

import rest_editor_eos as eos
from rest_eos_util import get_light_items, get_group_items, get_item_eos_group, \
    get_other_items, get_conf_value
from rest_utils import validate_item, update_item
from rest_metadata import get_metadata, set_metadata

eos_style = Style([
    ("qmark", "fg:#673ab7 bold"),     # token in front of the question
    ("question", "bold"),             # question text
    ("answer", "fg:#f44336 bold"),    # submitted answer text behind the question
    #("pointer", "fg:#673ab7 bold"),   # pointer used in select and checkbox prompts
    ("highlighted", "fg:#cc5454"),    # highlighted choice in select and checkbox prompts
    ("selected", "fg:#cc5454"),       # style for a selected item of a checkbox
    #("separator", "fg:#cc5454"),      # separator in lists
    #("instruction", ""),              # user instructions for select, rawselect, checkbox
    ("text", "fg:#d4d4d4"),
    ("separator", 'fg:#c4c43f'),
    #("qmark", '#5F819D'),
    #("selected", 'fg:#ff0000'),  # default
    ("pointer", 'fg:#ff9d00 bold'),  # AWS orange
    #("instruction", 'italic'),  # default
    #("answer", '#FF9D00 bold'),  # AWS orange
    #("question", 'bold'),
    ("itemtype", "fg:#559ad4"),
    ("itemname", "fg:#d4d4d4"),
    ("itemlabel", "fg:#ce9178"),
    ("titletype", "fg:#559ad4 bold"),
    ("titlename", "fg:#d4d4d4 bold"),
    ("titlelabel", "fg:#ce9178 bold"),
    ("instruction", "fg:#d4d4d4 italic"),
    ("disabled", "fg:#858585 italic"),
    ("value", "fg:#9cdcfe")
])

col_left_width = 17

def group(root_group, host, exit_label="Exit"):
    """
    Display a Group menu
    """
    parent_group = root_group
    answer = None
    pointed_at = None
    exit_loop = False
    while not exit_loop:
        menu_message = "Eos Editor > Group Menu"
        menu_choices = []
        menu_choices.append(Separator(line=" "))
        menu_choices.append(Choice(
                title=[
                    ("class:titletype", "Group"),
                    ("class:titlename", " {}".format(parent_group["name"])),
                    ("class:titlelabel", "{}".format(" \"{}\"".format(parent_group["label"]) if "label" in parent_group else ""))
                ],
                disabled=True
            ))
        menu_choices.append(Separator(line=" "))
        lights = get_light_items(parent_group, host)
        if lights:
            menu_choices.append(Separator(line="    Eos Lights"))
            for item in lights:
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
        groups = get_group_items(parent_group)
        if groups:
            menu_choices.append(Separator(line="    Eos Groups"))
            for item in groups:
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
        others = get_other_items(parent_group, host)
        if others:
            menu_choices.append(Separator(line="    Non Eos Items"))
            for item in others:
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
        if lights or groups or others:
            menu_choices.append(Separator(line="    Options"))
        if answer == "eos_menu_add_existing": pointed_at = len(menu_choices)
        menu_choices.append(Choice(title="Add an existing light to this group", value="eos_menu_add_existing", disabled="not implemented yet"))
        if answer == "eos_menu_add_new_light": pointed_at = len(menu_choices)
        menu_choices.append(Choice(title="Add a new light to this group", value="eos_menu_add_new_light", disabled="not implemented yet"))
        if answer == "eos_menu_add_new_group": pointed_at = len(menu_choices)
        menu_choices.append(Choice(title="Add a new Eos group to this group", value="eos_menu_add_new_group", disabled="not implemented yet"))
        menu_choices.append(Separator(line=" "))
        menu_choices.append(Choice(title=exit_label, value="eos_menu_exit"))

        clear()
        answer = select(message=menu_message, choices=menu_choices, style=eos_style, qmark="", pointed_at=pointed_at).ask()

        if not answer or answer == "eos_menu_exit":
            # escape, ctrl+c, or "back"
            exit_loop = True
        elif [item for item in lights if item["name"] == answer]:
            # selected a light
            light([item for item in lights if item["name"] == answer][0], host)
        elif [item for item in groups if item["name"] == answer]:
            # selected an eos group
            group([item for item in groups if item["name"] == answer][0], host, exit_label="Back")
        elif [item for item in others if item["name"] == answer]:
            # selected a non-eos item
            light([item for item in others if item["name"] == answer][0], host)
        elif answer == "eos_menu_add_existing":
            # add an existing item not in this group
            light(search(host), host)
        elif answer == "eos_menu_add_new_light":
            # add a new light to openhab and configure for eos
            light(add(host), host)
        elif answer == "eos_menu_add_new_group":
            # add a new group to openhab and configure for eos
            pass
            #light(add(host), host)

    clear()

def light(target, host):
    """
    Edit an Item
    """
    def select_group():
        """
        Prompt to select an Eos group
        """
        def search_group(target_group):
            # recursive Eos group finder
            results = []
            for group in get_group_items(target_group):
                results.append(group)
                results.extend(search_group(group))
            return results

        eos_groups = [validate_item(get_conf_value("eos_master_group"), host)]
        eos_groups.extend(search_group(eos_groups[0]))
        item_group = get_item_eos_group(item, host).get("name", None)
        pointed_at = None

        menu_message = "Eos Editor > Select Group"
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
                    value=group["name"]
                ))

        clear()
        answer = select(message=menu_message, choices=menu_choices, style=eos_style, qmark="", pointed_at=pointed_at).ask()

        if answer:
            if item_group: item["groupNames"].remove(item_group)
            item["groupNames"].append(answer)

    def edit_label():
        """
        Prompt for new item label
        """
        clear()
        item["label"] = text(
                message="Enter a new label for '{}'".format(item["name"]),
                default=item.get("label", ""),
                qmark=""
            ).ask()


    if target is None: return
    item = validate_item(target["name"], host)
    menu_message = "Eos Editor > Edit Item"
    answer = None
    pointed_at = None
    exit_loop = False
    while not exit_loop:
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
        if "label" in item and item["editable"]:
            if answer == "eos_menu_edit_label": pointed_at = len(menu_choices)
            menu_choices.append(Choice(
                    title=[
                        ("class:text", "{:{width}}".format("Label", width=col_left_width)),
                        ("class:value", item["label"])
                    ],
                    value="eos_menu_edit_label"
                ))
        if item["editable"] and answer == "eos_menu_group": pointed_at = len(menu_choices)
        menu_choices.append(Choice(
                title=[
                    ("class:{}".format("text" if item["editable"] else "disabled"), "{:{width}}".format("Eos Group", width=col_left_width)),
                    ("class:value", get_item_eos_group(item, host)["name"])
                ],
                value="eos_menu_group",
                disabled=False if item["editable"] else "item not editable"
            ))
        if answer == "eos_menu_settings": pointed_at = len(menu_choices)
        menu_choices.append(Choice(
                title="Eos Settings",
                value="eos_menu_settings"
            ))
        menu_choices.append(Separator(line=" "))
        menu_choices.append(Choice(
                title="Save",
                value="eos_menu_save"
            ))
        menu_choices.append(Choice(
                title="Cancel",
                value="eos_menu_cancel"
            ))

        clear()
        answer = select(message=menu_message, choices=menu_choices, style=eos_style, qmark="", pointed_at=pointed_at).ask()

        if answer == "eos_menu_edit_label":
            # edit item label
            edit_label()
        elif answer == "eos_menu_group":
            # change item to another group
            select_group()
        elif answer == "eos_menu_settings":
            # edit Eos metadata
            metadata(item, host)
        elif answer == "eos_menu_save":
            # save item and return
            exit_loop = True
            if item.get("metadata", {}).get(eos.META_NAME_EOS, False):
                if not set_metadata(
                        item["name"], eos.META_NAME_EOS, host,
                        configuration=item["metadata"][eos.META_NAME_EOS].get("config", {}),
                        value=str(item["metadata"][eos.META_NAME_EOS].get("value", False)),
                        overwrite=True
                    ): exit(1)
                item.pop("metadata", None)
            if item.get("editable", False):
                update_item(item, host)
        elif not answer or answer == "eos_menu_cancel":
            # return without save
            exit_loop = True

def search(host):
    """
    Search for an existing Item
    """
    return None

def add(host):
    """
    Add a new Item
    """
    return None

def metadata(item, host):
    """
    Edit an Item's Eos metadata
    """
    menu_message = "Eos Editor > Eos Settings"
    metadata = copy.deepcopy(item.get("metadata", {}).get(eos.META_NAME_EOS, None)) or get_metadata(item["name"], eos.META_NAME_EOS, host)
    enabled = metadata.get("value", False)
    if isinstance(enabled, str): enabled = False if enabled.lower() in ["false", "disabled"] else True
    config = metadata.get("config", {})
    answer = None
    pointed_at = None
    exit_loop = False
    while not exit_loop:
        defaults = {key:value for key, value in config.items() if not isinstance(value, dict)}
        scenes = {key:value for key, value in config.items() if isinstance(value, dict)}

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
        if answer == "eos_menu_enabled": pointed_at = len(menu_choices)
        menu_choices.append(Choice(
                title=[
                    ("class:text", "{:{width}}".format("Enabled", width=col_left_width)),
                    ("class:value", str(enabled))
                ],
                value="eos_menu_enabled"
            ))
        menu_choices.append(Separator(line=" "))
        menu_choices.append(Separator(line="    Item Defaults"))
        if defaults:
            for key in defaults:
                if answer == key: pointed_at = len(menu_choices)
                menu_choices.append(Choice(
                        title=[
                            ("class:text", "{:{width}}".format(key, width=col_left_width)),
                            ("class:value", "{}".format("\"{}\"".format(defaults[key]) if isinstance(defaults[key], str) else defaults[key]))
                        ],
                        value=key
                    ))
        else:
            menu_choices.append(Choice(title="(no defaults)", disabled=True))
        if answer == "eos_menu_add_default": pointed_at = len(menu_choices)
        menu_choices.append(Choice(
                title="Add",
                value="eos_menu_add_default"
            ))
        menu_choices.append(Separator(line=" "))
        menu_choices.append(Separator(line="    Scenes"))
        if scenes:
            for key in scenes:
                if answer == key: pointed_at = len(menu_choices)
                menu_choices.append(Choice(
                        title=[
                            ("class:text", "{:{width}}".format(key, width=col_left_width)),
                            ("class:value", "{}".format(get_scene_type(item, key, host)).capitalize())
                        ],
                        value=key
                    ))
        else:
            menu_choices.append(Choice(title="(no scenes defined)", disabled=True))
        for key in [eos.SCENE_ON, eos.SCENE_OFF]:
            if key in scenes: continue # skip if item already has scene defined
            if answer == key: pointed_at = len(menu_choices)
            menu_choices.append(Choice(
                    title=[
                        ("class:text", "{}".format(key)),
                        ("class:disabled", "{:{width}}".format(" (built-in)", width=col_left_width-len(key))),
                        ("class:value", "{}".format(get_scene_type(item, key, host)).capitalize())
                    ],
                    value=key
                ))
        if answer == "eos_menu_add_scene": pointed_at = len(menu_choices)
        menu_choices.append(Choice(
                title="Add",
                value="eos_menu_add_scene"
            ))
        menu_choices.append(Separator(line=" "))
        menu_choices.append(Choice(
                title="Save",
                value="eos_menu_save"
            ))
        menu_choices.append(Choice(
                title="Cancel",
                value="eos_menu_cancel"
            ))

        clear()
        answer = select(message=menu_message, choices=menu_choices, style=eos_style, qmark="", pointed_at=pointed_at).ask()

        if answer == "eos_menu_enabled":
            # toggle enabled
            enabled = not enabled
        elif answer in defaults:
            # edit existing default
            edit_key("Set item default '{}' for {}:".format(answer, item["name"]), config, answer, host)
        elif answer == "eos_menu_add_default":
            # add a new default to this item
            new_key = select_key(keys_to_hide=defaults.keys())
            edit_key("Set item default '{}' for {}:".format(new_key, item["name"]), config, new_key, host)
            del new_key
        elif answer in scenes or answer in [eos.SCENE_ON, eos.SCENE_OFF]:
            # edit existing scene
            scene(item, answer, config, host)
        elif answer == "eos_menu_add_scene":
            # add a new scene
            scene(item, None, config, host)
        elif answer == "eos_menu_save":
            # save item and return
            exit_loop = True
            if "metadata" not in item: item["metadata"] = {}
            item["metadata"][eos.META_NAME_EOS] = {
                "value": enabled,
                "config": config
            }
        elif not answer or answer == "eos_menu_cancel":
            # return without save
            exit_loop = True

def select_key(keys_to_hide=[], point_at=None):
    """
    Prompt to select a metadata key to add
    """
    menu_message = "Eos Editor > Select Setting"
    pointed_at = None
    menu_choices = []
    menu_choices.append(Separator(line=" "))
    for key in eos.META_KEY_LIST:
        if key not in keys_to_hide:
            if key == point_at: pointed_at = len(menu_choices)
            menu_choices.append(str(key))

    clear()
    return select(message=menu_message, choices=menu_choices, style=eos_style, qmark="", pointed_at=pointed_at).ask()

def edit_key(message, scene, key, host, instructions=None):
    """
    Prompt for new item label
    """
    if key is None: return
    valid = False
    err_msg = None
    while not valid:
        clear()
        if err_msg: echo(err_msg)
        if instructions: echo(instructions)
        echo("Leave blank to remove this setting")
        answer = text(
                message=message,
                default=str(scene.get(key, "")),
                qmark=""
            ).ask()

        if not answer or answer is None:
            answer = None
            valid = True
        elif key in [eos.META_KEY_LEVEL_SOURCE, eos.META_KEY_MOTION_SOURCE]:
            valid = True if validate_item(answer, host) else False
            if not valid: err_msg = "Value of {key} must be an item that exists!".format(key=key)
        elif key in [eos.META_KEY_LEVEL_HIGH, eos.META_KEY_LEVEL_LOW, eos.META_KEY_LEVEL_THRESHOLD]:
            try:
                valid = True if isinstance(literal_eval(str(answer)), (int, float)) else False
                answer = literal_eval(str(answer))
            except:
                pass
            if not valid: err_msg = "Value of {key} must be a number!".format(key=key)
        elif len(str(answer).split(",")) == 3:
            # list for color state
            try:
                answer = [literal_eval(part.strip()) for part in str(answer).split(",")]
            except:
                answer = [part.strip() for part in str(answer).split(",")]
        else:
            valid = True
        # keys that still need validation:
            # META_KEY_STATE = "state"
            # META_KEY_STATE_ABOVE = "state_above"
            # META_KEY_STATE_BELOW = "state_below"
            # META_KEY_STATE_HIGH = "state_high"
            # META_KEY_STATE_LOW = "state_low"
            # META_KEY_MOTION_ACTIVE = "motion_active"
            # META_KEY_MOTION_STATE = "motion_state"

    if answer is None:
        scene.pop(key, None)
    else:
        scene[key] = answer

def scene(item, scene, metadata, host):
    """
    Menu to edit scene settings for an item
    """
    def edit_name():
        """
        Prompt for new scene name
        """
        err_msg = ""
        while True:
            clear()
            if err_msg: echo(err_msg)
            new_name = text(
                    message="Enter a name for this scene:",
                    default=scene or "",
                    qmark=""
                ).ask()
            if not new_name or new_name is None:
                # exit if no name provided for new scene prompt
                return scene
            elif new_name in eos.META_KEY_LIST:
                err_msg = "Scene cannot have the same name as any settings!"
            elif new_name in metadata and new_name != scene:
                err_msg = "Scene '{}' already exists!".format(new_name)
            else:
                return new_name.lower()

    menu_message = "Eos Editor > {} Scene".format("Edit" if scene else "Add")

    if scene is None: scene = edit_name()
    if scene is None: return

    scene_config = copy.deepcopy(metadata.get(scene, {}))
    dummy_metadata = copy.deepcopy(metadata)
    dummy_metadata[scene] = scene_config
    answer = None
    pointed_at = None
    exit_loop = False
    while not exit_loop:
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
        if answer == "eos_menu_edit_name": pointed_at = len(menu_choices)
        menu_choices.append(Choice(
                title=[
                    ("class:{}".format("disabled" if scene in [eos.SCENE_ON, eos.SCENE_OFF] else "text"), "{:{width}}".format("Scene Name", width=col_left_width)),
                    ("class:value", scene)
                ],
                disabled="built-in" if scene in [eos.SCENE_ON, eos.SCENE_OFF] else False,
                value="eos_menu_edit_name"
            ))
        menu_choices.append(Choice(
                title=[
                    ("class:disabled", "{:{width}}".format("Scene Type", width=col_left_width)),
                    ("class:value", str(get_scene_type(item, scene, host)).capitalize())
                ],
                disabled=True,
                value="eos_menu_scene_type"
            ))
        menu_choices.append(Separator(line=" "))
        for key in [key for key in eos.META_KEY_LIST if get_scene_setting(item, scene, key, host, metadata=dummy_metadata, depth=1) is not None]:
            if answer == key:  pointed_at = len(menu_choices)
            menu_choices.append(Choice(
                    title=[
                        ("class:text", "{:{width}}".format(key, width=col_left_width)),
                        ("class:value", str(get_scene_setting(item, scene, key, host, metadata=dummy_metadata, depth=1)))
                    ],
                    value=key
                ))
        menu_choices.append(Choice(
                title="Add Scene Setting",
                value="eos_menu_add"
            ))
        menu_choices.append(Separator(line=" "))
        for key in [key for key in eos.META_KEY_LIST if get_scene_setting(item, scene, key, host, metadata=dummy_metadata, depth=1) is None and get_scene_setting(item, scene, key, host, metadata=dummy_metadata, depth=2) is not None]:
            menu_choices.append(Choice(
                    title=[
                        ("class:disabled", "{:{width}}".format(key, width=col_left_width)),
                        ("class:value", str(get_scene_setting(item, scene, key, host, metadata=dummy_metadata, depth=2)))
                    ],
                    value="defaults_{}".format(key),
                    disabled="item default"
                ))
        for key in [key for key in eos.META_KEY_LIST if get_scene_setting(item, scene, key, host, metadata=dummy_metadata, depth=2) is None and get_scene_setting(item, scene, key, host, metadata=dummy_metadata, depth=3) is not None]:
            menu_choices.append(Choice(
                    title=[
                        ("class:disabled", "{:{width}}".format(key, width=col_left_width)),
                        ("class:value", str(get_scene_setting(item, scene, key, host, metadata=dummy_metadata, depth=3)))
                    ],
                    value="defaults_{}".format(key),
                    disabled="scene default"
                ))
        for key in [key for key in eos.META_KEY_LIST if get_scene_setting(item, scene, key, host, metadata=dummy_metadata, depth=3) is None and get_scene_setting(item, scene, key, host, metadata=dummy_metadata, depth=4) is not None]:
            menu_choices.append(Choice(
                    title=[
                        ("class:disabled", "{:{width}}".format(key, width=col_left_width)),
                        ("class:value", str(get_scene_setting(item, scene, key, host, metadata=dummy_metadata, depth=4)))
                    ],
                    value="defaults_{}".format(key),
                    disabled="{type} default".format(type=str(eos.LIGHT_TYPE_MAP.get(item.get("type", "").lower(), None)))
                ))
        menu_choices.append(Separator(line=" "))
        menu_choices.append(Choice(
                title="Save",
                value="eos_menu_save"
            ))
        if metadata.get(scene, False):
            if answer == "eos_menu_remove":  pointed_at = len(menu_choices)
            menu_choices.append(Choice(
                    title="Remove Scene",
                    value="eos_menu_remove"
                ))
        menu_choices.append(Choice(
                title="Cancel",
                value="eos_menu_cancel"
            ))

        clear()
        echo(metadata)
        answer = select(message=menu_message, choices=menu_choices, style=eos_style, qmark="", pointed_at=pointed_at).ask()

        if answer == "eos_menu_edit_name":
            # edit scene name
            scene = edit_name()
        elif answer in scene_config:
            # edit existing setting
            edit_key("Set item default '{}' for {}:".format(answer, item["name"]), scene_config, answer, host)
        elif answer == "eos_menu_add":
            # add a new setting
            new_key = select_key(keys_to_hide=scene_config.keys())
            edit_key("Set item default '{}' for {}:".format(new_key, item["name"]), scene_config, new_key, host)
            del new_key
        elif answer == "eos_menu_save":
            # save scene and return
            exit_loop = True
            if scene_config: metadata[scene] = scene_config
        elif answer == "eos_menu_remove":
            # remove scene and return
            if confirm("Are you sure you want to remove '{}' scene? This can be undone by cancelling item changes.".format(scene), style=eos_style, qmark="").ask():
                exit_loop = True
                metadata.pop(scene, None)
        elif not answer or answer == "eos_menu_cancel":
            # return without save
            exit_loop = True

def get_scene_setting(item, scene, key, host, metadata=None, depth=4):
    # gets a setting value by searching:
    # item-scene > item-default > type-scene-default > type-default
    config = metadata or get_metadata(item["name"], eos.META_NAME_EOS, host).get("config", {})
    scene_defaults = copy.deepcopy(eos.scene_defaults)
    scene_defaults.update(get_conf_value("scene_defaults", valid_types=dict, default={}))
    light_type = eos.LIGHT_TYPE_MAP.get(item.get("type", "").lower(), None)
    if depth > 0 and key in config.get(scene, {}):
        return config.get(scene, {}).get(key, None)
    elif depth > 1 and key in config:
        return config.get(key, None)
    elif depth > 2 and key in scene_defaults.get(light_type, {}).get(scene, {}):
        return scene_defaults.get(light_type, {}).get(scene, {}).get(key, None)
    elif depth > 3 and key in scene_defaults.get(light_type, {}):
        return scene_defaults.get(light_type, {}).get(key, None)
    else:
        return None

def get_scene_type(item, scene, host, metadata=None):
    # gets the scene type
    for depth in range(1, 5):
        if get_scene_setting(item, scene, eos.META_KEY_STATE, host, metadata=metadata, depth=depth):
            return eos.SCENE_TYPE_FIXED
        elif get_scene_setting(item, scene, eos.META_KEY_LEVEL_HIGH, host, metadata=metadata, depth=depth) \
          or get_scene_setting(item, scene, eos.META_KEY_LEVEL_LOW, host, metadata=metadata, depth=depth) \
          or get_scene_setting(item, scene, eos.META_KEY_STATE_HIGH, host, metadata=metadata, depth=depth) \
          or get_scene_setting(item, scene, eos.META_KEY_STATE_LOW, host, metadata=metadata, depth=depth):
            return eos.SCENE_TYPE_SCALED
        elif get_scene_setting(item, scene, eos.META_KEY_LEVEL_THRESHOLD, host, metadata=metadata, depth=depth):
            return eos.SCENE_TYPE_THRESHOLD
    return None
