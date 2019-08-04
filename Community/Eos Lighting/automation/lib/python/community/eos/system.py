"""
Eos Lighting

System init and uninit
"""

from community.eos import log, config
from community.eos.util import *
from community.eos.constants import *

from core.jsr223.scope import scriptExtension
ruleRegistry = scriptExtension.get("ruleRegistry")
#from core import osgi
#ruleEngine = osgi.get_service("org.openhab.core.automation.RuleManager") or osgi.get_service("org.eclipse.smarthome.automation.RuleManager")
from core.rules import rule
from core.triggers import when
from core.utils import validate_item
from core.metadata import get_value, get_metadata

__all__ = [ "init", "uninit" ]

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
                if get_value(light.name, META_NAME_EOS).lower() in ["false", "disabled"]:
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
            log.warn("No lights or groups in '{group}' will be discovered because it has no scene item".format(group=group.name))

    log.info("Eos initializing...")

    if not config.master_group_name:
        log.error("No '{name}' specified in configuration".format(name=CONF_KEY_MASTER_GROUP))
        return

    if not config.scene_item_prefix and not config.scene_item_suffix:
        log.error("Must specify at least one of '{prefix}' or '{suffix}' in configuration".format(prefix=CONF_KEY_SCENE_PREFIX, suffix=CONF_KEY_SCENE_SUFFIX))
        return

    master_group_item = validate_item(config.master_group_name)
    if not master_group_item:
        log.error("Master group item '{group}' does not exist".format(group=config.master_group_name))
        return
    elif not isinstance(master_group_item, itemtypesGroup):
        log.error("Master group item '{group}' is not a GroupItem".format(group=config.master_group_name))
        return
    if not get_scene_item(master_group_item):
        log.error("Could not validate master scene item in '{group}'".format(group=config.master_group_name))
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
    if config.reinit_item_name:
        log.debug("Creating {rule}".format(rule=RULE_REINIT_NAME))
        when("Item {name} received command ON".format(name=config.reinit_item_name))(rule_reinit)
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
