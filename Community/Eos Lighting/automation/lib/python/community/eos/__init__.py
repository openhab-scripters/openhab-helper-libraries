"""
Eos Lighting System
"""

from ast import literal_eval

from core.jsr223.scope import scriptExtension
ruleRegistry = scriptExtension.get("ruleRegistry")
#from core import osgi
#ruleEngine = osgi.get_service("org.openhab.core.automation.RuleManager") or osgi.get_service("org.eclipse.smarthome.automation.RuleManager")
from core.rules import rule
from core.triggers import when
from core.utils import sendCommandCheckFirst, validate_item
from core.log import logging, LOG_PREFIX, log_traceback
from core.metadata import get_value, get_metadata

try: from org.openhab.core.types import UnDefType as ohcUnDefType
except: ohcUnDefType = type(None)
try: from org.eclipse.smarthome.core.types import UnDefType as eshUnDefType
except: eshUnDefType = type(None)
try: from org.openhab.core.items import GroupItem as ohcGroupItem
except: ohcGroupItem = type(None)
try: from org.eclipse.smarthome.core.items import GroupItem as eshGroupItem
except: eshGroupItem = type(None)
try: from org.openhab.core.library.items import StringItem as ohcStringItem
except: ohcStringItem = type(None)
try: from org.eclipse.smarthome.core.library.items import StringItem as eshStringItem
except: eshStringItem = type(None)
try: from org.openhab.core.library.items import ColorItem as ohcColorItem
except: ohcColorItem = type(None)
try: from org.eclipse.smarthome.core.library.items import ColorItem as eshColorItem
except: eshColorItem = type(None)
try: from org.openhab.core.library.items import DimmerItem as ohcDimmerItem
except: ohcDimmerItem = type(None)
try: from org.eclipse.smarthome.core.library.items import DimmerItem as eshDimmerItem
except: eshDimmerItem = type(None)
try: from org.openhab.core.library.items import NumberItem as ohcNumberItem
except: ohcNumberItem = type(None)
try: from org.eclipse.smarthome.core.library.items import NumberItem as eshNumberItem
except: eshNumberItem = type(None)
try: from org.openhab.core.library.items import SwitchItem as ohcSwitchItem
except: ohcSwitchItem = type(None)
try: from org.eclipse.smarthome.core.library.items import SwitchItem as eshSwitchItem
except: eshSwitchItem = type(None)
typesUnDef = (ohcUnDefType, eshUnDefType)
itemtypesLight = (ohcColorItem, eshColorItem, ohcDimmerItem, eshDimmerItem, ohcNumberItem, eshNumberItem, ohcSwitchItem, eshSwitchItem)
itemtypesSwitch = (ohcSwitchItem, eshSwitchItem)
itemtypesDimmer = (ohcColorItem, eshColorItem, ohcDimmerItem, eshDimmerItem, ohcNumberItem, eshNumberItem)
itemtypesColor = (ohcColorItem, eshColorItem)
itemtypesGroup = (ohcGroupItem, eshGroupItem)

__all__ = ["init", "uninit"]

log = logging.getLogger("{prefix}.community.eos".format(prefix=LOG_PREFIX))

master_group_name = ""
scene_item_prefix = ""
scene_item_suffix = ""
group_item_prefix = ""
group_item_suffix = ""
reinit_item_name = ""

RULE_REINIT_NAME = "Eos Reload Rule"
RULE_REINIT_DESC = "This rule allows runtime reloading of the Eos System via a switch item"
RULE_SCENE_NAME = "Eos Scene Rule"
RULE_SCENE_DESC = "This rule is triggered when any Eos Scene item receives an update"
RULE_LIGHT_NAME = "Eos Light Rule"
RULE_LIGHT_DESC = "This rule is triggered when any Eos Light item receives an update"
RULE_LEVEL_SOURCE_NAME = "Eos Level Source Rule"
RULE_LEVEL_SOURCE_DESC = "This rule is triggered when any Level Source registered to an enabled Eos Light item receives an update"

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

LIGHT_TYPE_SWITCH = "switch"
LIGHT_TYPE_DIMMER = "dimmer"
LIGHT_TYPE_COLOR = "color"
LIGHT_TYPE_MAP = {"color": LIGHT_TYPE_COLOR, "dimmer": LIGHT_TYPE_DIMMER, "number": LIGHT_TYPE_DIMMER, "switch": LIGHT_TYPE_SWITCH}

SCENE_PARENT = "parent"
SCENE_MANUAL = "manual"
SCENE_ON = "on"
SCENE_OFF = "off"
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


def init(rule_reinit, rule_scene_update, rule_light_update, rule_level_source_update):
    """Initialize Eos.

    This creates a rule with triggers for the scene item in
    ``configuration.eos_master_group`` and any descendants that are a
    ``GroupItem`` and contain a scene item to update members when they receive
    an update.
    """
    levelItemTriggers = {}
    def _gen_triggers_for_group(group, ruleScene, ruleLight):
        log.debug("Scanning group '{group}' for scene and light items".format(group=group.name))
        itemScene = get_scene_item(group)
        if itemScene:
            # add scene trigger
            when("Item {name} received command".format(name=itemScene.name))(ruleScene)
            log.debug("Added scene item trigger for '{name}'".format(name=itemScene.name))
            # add lights triggers
            for light in get_light_items(group):
                if not isinstance(light, itemtypesLight):
                    log.warn("Skipping item '{name}' as it is not a recognized light item type".format(name=light.name))
                elif get_value(light.name, META_NAME_EOS) is None:
                    log.warn("Skipping item '{name}' as it does not have '{meta}' metadata".format(name=light.name, meta=META_NAME_EOS))
                elif get_value(light.name, META_NAME_EOS).lower() in ["false", "disabled"]:
                    log.info("Found light '{name}' in '{group}' but it is disabled".format(name=light.name, group=group.name))
                else:
                    log.debug("Found light '{name}' in '{group}'".format(name=light.name, group=group.name))
                    lightValid = True
                    metadata = dict(get_metadata(light.name, META_NAME_EOS).configuration)
                    itemLevelWhens = {}
                    if META_KEY_LEVEL_SOURCE in metadata:
                        itemLevel = validate_item(metadata[META_KEY_LEVEL_SOURCE])
                        if itemLevel is not None:
                            log.debug("Adding default level source item trigger for '{level}' for light '{name}'".format(level=itemLevel.name, name=light.name))
                            itemLevelWhens[itemLevel.name] = when("Item {name} received update".format(name=itemLevel.name))
                        else:
                            log.error("Light '{name}' was not added, default '{level_source}' item '{level}' does not exist".format(name=light.name, level_source=META_KEY_LEVEL_SOURCE, level=metadata[META_KEY_LEVEL_SOURCE]))
                            continue
                    for key in metadata:
                        if isinstance(metadata[key], dict) and META_KEY_LEVEL_SOURCE in metadata[key]:
                            itemLevel = validate_item(metadata[key][META_KEY_LEVEL_SOURCE])
                            if itemLevel is not None:
                                log.debug("Adding level source item trigger for '{level}' for light '{name}' for scene '{scene}'".format(level=itemLevel.name, name=light.name, scene=key))
                                itemLevelWhens[itemLevel.name] = when("Item {name} received update".format(name=itemLevel.name))
                            else:
                                log.error("Light '{name}' was not added, '{level_source}' item '{level}' for scene '{scene}' does not exist".format(name=light.name, level_source=META_KEY_LEVEL_SOURCE, level=metadata[key][META_KEY_LEVEL_SOURCE], scene=key))
                                lightValid = False
                                break
                    if lightValid:
                        log.debug("Adding light item trigger for '{name}'".format(name=light.name))
                        when("Item {name} received update".format(name=light.name))(ruleLight)
                        levelItemTriggers.update(itemLevelWhens)
            # recurse into groups
            for group in get_group_items(group):
                _gen_triggers_for_group(group, ruleScene, ruleLight)
        else:
            log.warn("No lights or groups in '{group}' will be discovered".format(group=group.name))

    log.info("Eos initializing...")

    global master_group_name
    master_group_name = get_conf_value("eos_master_group", str)
    if not master_group_name:
        log.error("No 'eos_master_group' specified in configuration")
        return

    global scene_item_prefix, scene_item_suffix
    scene_item_prefix = get_conf_value("eos_scene_item_prefix", str, "")
    scene_item_suffix = get_conf_value("eos_scene_item_suffix", str, "")
    if not scene_item_prefix and not scene_item_suffix:
        log.error("Must specify at least one of 'eos_scene_item_prefix' or 'eos_scene_item_suffix' in configuration")
        return

    global group_item_prefix, group_item_suffix
    group_item_prefix = get_conf_value("eos_group_item_prefix", str, "")
    group_item_suffix = get_conf_value("eos_group_item_suffix", str, "")
    if not group_item_prefix and not group_item_suffix:
        log.error("Must specify at least one of 'eos_group_item_prefix' or 'eos_group_item_suffix' in configuration")
        return

    global scene_defaults
    scene_defaults.update(get_conf_value("eos_scene_defaults", dict, {}))

    global reinit_item_name
    reinit_item_name = get_conf_value("eos_reload_item_name")
    if reinit_item_name and validate_item(reinit_item_name) is None:
        log.warn("Eos reload item '{name}' does not exist".format(name=reinit_item_name))
        reinit_item_name = ""

    if not validate_item_name(master_group_name, group_item_prefix, group_item_suffix):
        log.error("Master group item '{group}' does not match the pattern '{prefix}GROUPNAME{suffix}'".format(group=master_group_name, prefix=group_item_prefix, suffix=group_item_suffix))
        return
    master_group_item = validate_item(master_group_name)
    if not master_group_item:
        log.error("Master group item '{group}' does not exist".format(group=master_group_name))
        return
    elif not isinstance(master_group_item, (ohcGroupItem, eshGroupItem)):
        log.error("Master group item '{group}' is not a GroupItem".format(group=master_group_name))
        return

    if not get_scene_item(master_group_item):
        log.error("Could not validate master scene item in '{group}'".format(group=master_group_name))
        return

    for objRule in [objRule for objRule in ruleRegistry.getAll() if objRule.name in [RULE_REINIT_NAME, RULE_SCENE_NAME, RULE_LIGHT_NAME, RULE_LEVEL_SOURCE_NAME]]:
        log.warn("Found existing {rule} with UID '{uid}'".format(rule=objRule.name, uid=objRule.UID))
        ruleRegistry.remove(objRule.UID)
        #try: ruleRegistry.remove(objRule.UID)
        #except:
        #    log.error("Failed to delete {rule} with UID '{uid}', attempting to disable".format(rule=objRule.name, uid=objRule.UID))
        #    ruleEngine.setEnabled(objRule.UID, False)

    # if we are reinit-ing {rule}.triggers will be NoneType
    if hasattr(rule_reinit, "triggers"): delattr(rule_reinit, "triggers")
    if hasattr(rule_scene_update, "triggers"): delattr(rule_scene_update, "triggers")
    if hasattr(rule_light_update, "triggers"): delattr(rule_light_update, "triggers")
    if hasattr(rule_level_source_update, "triggers"): delattr(rule_level_source_update, "triggers")

    # add all scene and light item received update triggers to functions and create rules
    _gen_triggers_for_group(master_group_item, rule_scene_update, rule_light_update)
    if hasattr(rule_light_update, "triggers"): # do not proceed if there are no lights
        log.debug("Creating {rule}".format(rule=RULE_SCENE_NAME))
        rule(RULE_SCENE_NAME, RULE_SCENE_DESC)(rule_scene_update)
        if hasattr(rule_scene_update, "UID"):
            log.debug("{rule} UID is '{uid}'".format(rule=RULE_SCENE_NAME, uid=rule_scene_update.UID))
        else:
            log.error("Failed to create {rule}".format(rule=RULE_SCENE_NAME))
            return

        log.debug("Creating {rule}".format(rule=RULE_LIGHT_NAME))
        rule(RULE_LIGHT_NAME, RULE_LIGHT_DESC)(rule_light_update)
        if hasattr(rule_light_update, "UID"):
            log.debug("{rule} UID is '{uid}'".format(rule=RULE_LIGHT_NAME, uid=rule_light_update.UID))
        else:
            log.error("Failed to create {rule}".format(rule=RULE_LIGHT_NAME))
            return
    else:
        log.error("No lights found")
        return

    # add triggers for each Level Source item and create rule if any exist
    for levelItem in levelItemTriggers: levelItemTriggers[levelItem](rule_level_source_update)
    if hasattr(rule_level_source_update, "triggers"):
        log.debug("Creating {rule}".format(rule=RULE_LEVEL_SOURCE_NAME))
        rule(RULE_LEVEL_SOURCE_NAME, RULE_LEVEL_SOURCE_DESC)(rule_level_source_update)
        if hasattr(rule_level_source_update, "UID"):
            log.debug("{rule} UID is '{uid}'".format(rule=RULE_LEVEL_SOURCE_NAME, uid=rule_level_source_update.UID))
        else:
            log.error("Failed to create {rule}".format(rule=RULE_LEVEL_SOURCE_NAME))
            return

    # add rule to reload Eos if item exists
    if reinit_item_name:
        log.debug("Creating {rule}".format(rule=RULE_REINIT_NAME))
        when("Item {name} received command ON".format(name=reinit_item_name))(rule_reinit)
        rule(RULE_REINIT_NAME, RULE_REINIT_DESC)(rule_reinit)
        if hasattr(rule_reinit, "UID"):
            log.debug("{rule} UID is '{uid}'".format(rule=RULE_REINIT_NAME, uid=rule_reinit.UID))
        else:
            log.error("Failed to create {rule}".format(rule=RULE_REINIT_NAME))
            return

    log.info("Eos initialized")


def uninit():
    """Uninitialize Eos.

    This will remove the rules created by Eos when it is unloaded.
    """
    log.info("Eos uninitializing...")

    for objRule in [objRule for objRule in ruleRegistry.getAll() if objRule.name in [RULE_REINIT_NAME, RULE_SCENE_NAME, RULE_LIGHT_NAME, RULE_LEVEL_SOURCE_NAME]]:
        log.info("Removing {rule} with UID '{uid}'".format(rule=objRule.name, uid=objRule.UID))
        ruleRegistry.remove(objRule.UID)
        #try: ruleRegistry.remove(objRule.UID)
        #except:
        #    log.error("Failed to delete {rule} with UID '{uid}', attempting to disable".format(rule=objRule.name, uid=objRule.UID))
        #    ruleEngine.setEnabled(objRule.UID, False)

    log.info("Eos uninitialized")


@log_traceback
def update_light(item):
    """Sends commands to lights based on scene.

    If light does not have metadata for the scene no command will be sent,
    except for the default scenes ``on`` and ``off``. The default values for
    built-in scenes can be customized in ``configuration.py`` if desired.
    """
    if get_value(item.name, META_NAME_EOS).lower() in ["false", "disabled"]:
        log.debug("Skipping update for light '{name}' as it is disabled".format(name=item.name))
        return
    else:
        log.debug("Processing update for light '{name}'".format(name=item.name))

    scene = get_scene_for_item(item)
    log.debug("Got scene '{scene}' for item '{name}'".format(scene=scene, name=item.name))

    if scene != SCENE_MANUAL:
        newState = get_state_for_scene(item, scene)
        if sendCommandCheckFirst(item.name, newState, floatPrecision=3):
            log.debug("Sent command '{command}' to light '{name}'".format(command=newState, name=item.name))
        else:
            log.debug("No command sent to light '{name}'".format(command=newState, name=item.name))
    else:
        log.debug("Scene for item '{name}' is '{scene}', no action taken".format(name=item.name, scene=scene))


def update_group(group, only_if_scene_parent=False):
    if only_if_scene_parent and str(get_scene_item(group).state).lower() != SCENE_PARENT:
        return
    for light in get_light_items(group):
        try: update_light(light)
        except: continue
    for groupItem in get_group_items(group):
        update_group(groupItem, only_if_scene_parent)


def get_conf_value(name, valid_types=None, default=None):
    """Gets ``name`` from configuration.

    Returns ``default`` if not present or not one of types in ``valid_types``
    """
    # importing here so we can reload each time and catch any updates the user may have made
    import configuration
    reload(configuration)

    if hasattr(configuration, name):
        value = getattr(configuration, name)
        if valid_types is None or isinstance(value, valid_types):
            log.debug("Got '{name}':'{value}' from configuration".format(name=name, value=value))
            return value
        else:
            log.error("'{name}' is type '{type}', must be one of '{valid_types}'".format(
                name=name, type=type(value), valid_types=valid_types))
            return default
    else:
        log.debug("No '{name}' specified in configuration".format(name=name))
        return default


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
    items = [item for item in group.members if validate_item_name(item.name, scene_item_prefix, scene_item_suffix)]
    if not items:
        log.error("Group '{group}' does not contain a scene item".format(group=group.name))
        return None
    elif len(items) > 1:
        itemList = ""
        for item in items: itemList = "{list}'{name}', ".format(list=itemList, name=item.name)
        log.error("Group '{group}' contains more than one scene item: {list}".format(group=group.name, list=itemList[:-2]))
        log.error("Each group can only have one scene item, please correct.")
        return None
    elif not isinstance(items[0], (ohcStringItem, eshStringItem)):
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
                and item != get_scene_item(group)
                and resolve_type(get_value(item.name, META_NAME_EOS)) is not None
        ] if hasattr(group, "members") else []


def get_group_items(group):
    """Finds all group items in a group.

    Returns a list of valid Eos groups.
    """
    return [
        item for item in group.members
            if isinstance(item, (ohcGroupItem, eshGroupItem))
                and validate_item_name(item.name, group_item_prefix, group_item_suffix)
                and len(get_light_items(item)) > 0
        ] if hasattr(group, "members") else []


def get_item_eos_group(item):
    """Gets the Eos group from the item's groups.

    Returns the group item or ``None`` if it does not find exactly one match.
    """
    groups = [group for group in item.groupNames if validate_item_name(group, group_item_prefix, group_item_suffix)]
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
    if sceneItem.name == master_group_name and str(sceneItem.state) == SCENE_PARENT:
        # master group cannot inherit scene from parent, no parent
        # this is caused by invalid site configuration allowing master group scene
        # to be set to parent
        log.error("Master group '{group}' scene item '{name}' is set to 'parent', this is an impossible state. Using state '{off}' instead".format(
            group=master_group_name, name=sceneItem.name, off=SCENE_OFF))
        return SCENE_OFF
    elif str(sceneItem.state) == SCENE_PARENT:
        # group is set to inherit scene from parent
        return get_scene_for_item(get_item_eos_group(sceneItem))
    else:
        return str(sceneItem.state)


def get_state_for_scene(item, scene):
    """Returns state for scene from ``item`` metadata.

    If ``item`` does not have a definition for ``scene`` and ``scene`` is ``on``
    or ``off`` it will look for look for a default state in configuration, if
    one is not found the built-in default state will be used.

    See full documentation for scene definitions here.
    """
    def constrain(value, min, max): return max if value > max else min if value < min else value

    def resolve_value(key):
        value = None
        if key in sceneData:
            value = sceneData[key]
        elif lightType in scene_defaults:
            if scene in scene_defaults[lightType] and key in scene_defaults[lightType][scene]:
                value = scene_defaults[lightType][scene][key]
            elif key in scene_defaults[lightType]:
                value = scene_defaults[lightType][key]
        if value is not None:
            log.debug("Got value '{value}' for key '{key}' for scene '{scene}' for item '{name}'".format(
                value=str(value), key=key, scene=scene, name=item.name))
            return resolve_type(value)
        else:
            return None

    metadata = get_metadata(item.name, META_NAME_EOS).configuration
    log.debug("Got metadata dict for '{name}': {metadata}".format(name=item.name, metadata=metadata))

    lightType = LIGHT_TYPE_MAP[item.type.lower()]
    log.debug("Got light type '{type}' for '{name}'".format(type=lightType, name=item.name))

    if scene in metadata:
        sceneData = resolve_type(metadata[scene])
        log.debug("Got scene data for '{name}' scene '{scene}': {data}".format(name=item.name, scene=scene, data=sceneData))
    elif scene in scene_defaults[lightType]:
        sceneData = scene_defaults[lightType][scene]
        log.debug("Falling back to default scene data for '{name}' scene '{scene}': {data}".format(name=item.name, scene=scene, data=sceneData))
    elif META_KEY_STATE in scene_defaults[lightType] or META_KEY_LEVEL_THRESHOLD in scene_defaults[lightType] or META_KEY_LEVEL_HIGH in scene_defaults[lightType]:
        sceneData = scene_defaults[lightType]
        log.debug("Falling back to default type data for '{name}' type '{type}': {data}".format(name=item.name, type=lightType, data=sceneData))
    else:
        log.warn("Light '{name}' has no definition for scene '{scene}' and there is no default to fall back to".format(name=item.name, scene=scene))
        return str(item.state)

    # Fixed State type
    if META_KEY_STATE in sceneData:
        log.debug("Selected 'Fixed State' type for scene '{scene}' for light '{name}'".format(scene=scene, name=item.name))

        state = sceneData[META_KEY_STATE]
        log.debug("Got fixed state '{state}' for '{name}' scene '{scene}'".format(state=state, name=item.name, scene=scene))

    # Threshold type
    elif META_KEY_LEVEL_THRESHOLD in sceneData or META_KEY_STATE_ABOVE in sceneData or META_KEY_STATE_BELOW in sceneData:
        log.debug("Selected 'Threshold' type for scene '{scene}' for light '{name}'".format(scene=scene, name=item.name))

        if not META_KEY_LEVEL_SOURCE in metadata:
            log.error("Threshold type scene requires '{level_source}' entry in '{eos}' namespace, nothing found for '{name}'".format(
                level_source=META_KEY_LEVEL_SOURCE, eos=META_NAME_EOS, name=item.name))
            return str(item.state)
        levelValue = resolve_type(validate_item(metadata[META_KEY_LEVEL_SOURCE]).state)
        log.debug("Got value '{value}' for level for scene '{scene}' for item '{name}'".format(value=levelValue, scene=scene, name=item.name))

        levelThreshold = resolve_value(META_KEY_LEVEL_THRESHOLD)
        if levelThreshold is None:
            log.warn("Light '{name}' has no '{key}' for scene '{scene}' and there is no default to fall back to".format(name=item.name, key=META_KEY_LEVEL_THRESHOLD, scene=scene))
            return str(item.state)

        stateAbove = resolve_value(META_KEY_STATE_ABOVE)
        if stateAbove is None:
            log.warn("Light '{name}' has no '{key}' for scene '{scene}' and there is no default to fall back to".format(name=item.name, key=META_KEY_STATE_ABOVE, scene=scene))
            return str(item.state)

        stateBelow = resolve_value(META_KEY_STATE_BELOW)
        if stateBelow is None:
            log.warn("Light '{name}' has no '{key}' for scene '{scene}' and there is no default to fall back to".format(name=item.name, key=META_KEY_STATE_BELOW, scene=scene))
            return str(item.state)

        state = stateAbove if levelValue > levelThreshold else stateBelow
        log.debug("Calculated threshold state '{state}' for '{name}' scene '{scene}'".format(state=state, name=item.name, scene=scene))

    # Scaling type
    elif lightType in [LIGHT_TYPE_DIMMER, LIGHT_TYPE_COLOR] and ( META_KEY_LEVEL_HIGH in sceneData or META_KEY_LEVEL_LOW in sceneData or META_KEY_STATE_HIGH in sceneData or META_KEY_STATE_LOW in sceneData ):
        log.debug("Selected 'Scaling' type for scene '{scene}' for light '{name}'".format(scene=scene, name=item.name))

        if not META_KEY_LEVEL_SOURCE in metadata:
            log.error("Scaling type scenes require a '{level_source}' entry in '{eos}' namespace, nothing found for '{name}'".format(
                level_source=META_KEY_LEVEL_SOURCE, eos=META_NAME_EOS, name=item.name))
            return str(item.state)
        levelValue = float(resolve_type(validate_item(metadata[META_KEY_LEVEL_SOURCE]).state))
        log.debug("Got value '{value}' for level for scene '{scene}' for item '{name}'".format(value=levelValue, scene=scene, name=item.name))

        levelHigh = resolve_value(META_KEY_LEVEL_HIGH)
        if levelHigh is None:
            log.warn("Light '{name}' has no '{key}' for scene '{scene}' and there is no default to fall back to".format(name=item.name, key=META_KEY_LEVEL_HIGH, scene=scene))
            return str(item.state)
        levelHigh = float(levelHigh)

        levelLow = resolve_value(META_KEY_LEVEL_LOW)
        if levelLow is None:
            levelLow = 0.0
            log.debug("No value for key '{key}' for scene '{scene}' for item '{name}', using default '{value}'".format(
                key=META_KEY_LEVEL_LOW, scene=scene, name=item.name, value=levelLow))
        levelLow = float(levelLow)

        stateHigh = resolve_value(META_KEY_STATE_HIGH)
        if stateHigh is None:
            log.warn("Light '{name}' has no '{key}' for scene '{scene}' and there is no default to fall back to".format(name=item.name, key=META_KEY_STATE_HIGH, scene=scene))
            return str(item.state)

        stateLow = resolve_value(META_KEY_STATE_LOW)
        if stateLow is None:
            log.warn("Light '{name}' has no '{key}' for scene '{scene}' and there is no default to fall back to".format(name=item.name, key=META_KEY_STATE_LOW, scene=scene))
            return str(item.state)

        if META_KEY_STATE_ABOVE in sceneData:
            stateAbove = resolve_type(sceneData[META_KEY_STATE_ABOVE])
        else:
            stateAbove = stateHigh
        log.debug("Got value '{value}' for key '{key}' for scene '{scene}' for item '{name}'".format(value=stateAbove, key=META_KEY_STATE_ABOVE, scene=scene, name=item.name))

        if META_KEY_STATE_BELOW in sceneData:
            stateBelow = resolve_type(sceneData[META_KEY_STATE_BELOW])
        else:
            stateBelow = stateLow
        log.debug("Got value '{value}' for key '{key}' for scene '{scene}' for item '{name}'".format(value=stateBelow, key=META_KEY_STATE_BELOW, scene=scene, name=item.name))

        if levelValue > levelHigh:
            state = stateAbove
        elif levelValue <= levelLow:
            state = stateBelow
        else:
            scalingFactor = (levelValue - levelLow) / (levelHigh - levelLow)
            def scale(low, high): return int(round(low + (high - low) * scalingFactor))
            if isinstance(stateHigh, (int, float)): # Dimmer value
                state = scale(stateLow, stateHigh)
            elif isinstance(stateHigh, list): # HSV list
                state = [scale(float(stateLow[0]), float(stateHigh[0]))]
                state.append(scale(float(stateLow[1]), float(stateHigh[1])))
                state.append(scale(float(stateLow[2]), float(stateHigh[2])))

        log.debug("Calculated scaled state '{state}' for '{name}' scene '{scene}'".format(state=state, name=item.name, scene=scene))
    else:
        log.error("Invalid scene configuration for '{name}' scene '{scene}'".format(name=item.name, scene=scene))
        return str(item.state)

    if lightType == LIGHT_TYPE_SWITCH and isinstance(state, (str)) and state.upper() in ["ON", "OFF"]:
        state = state.upper()
    elif lightType == LIGHT_TYPE_DIMMER and isinstance(state, (int, float)):
        state = str(constrain(int(round(state)), 0, 100))
    elif lightType == LIGHT_TYPE_COLOR and isinstance(state, (int, float, list)):
        if isinstance(state, (int, float)):
            oldState = str("0,0,0" if isinstance(item.state, typesUnDef) else item.state).split(",")
            state = ",".join([str(oldState[0]), str(oldState[1]), str(constrain(int(round(state)), 0, 100))])
        else:
            if state[0] > 359: state[0] -= 359
            elif state[0] < 0: state[0] += 359
            constrain(state[1], 0, 100)
            constrain(state[2], 0, 100)
            state = ",".join([str(i) for i in state])
    else:
        log.warn("New state '{state}' for '{name}' scene '{scene}' is not valid for item type '{type}'".format(
            state=state, name=item.name, scene=scene, type=item.type))
        return str(item.state)

    log.debug("New state '{state}' for '{name}' scene '{scene}'".format(state=state, name=item.name, scene=scene))
    return state