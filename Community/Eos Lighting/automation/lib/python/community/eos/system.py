"""
Eos Lighting

System init and uninit
"""

from community.eos import log, config
from community.eos.update import update_eos
from community.eos.util import *
from community.eos.constants import *

from core.jsr223.scope import scriptExtension
ruleRegistry = scriptExtension.get("ruleRegistry")
#from core import osgi
#ruleEngine = osgi.get_service("org.openhab.core.automation.RuleManager") or osgi.get_service("org.eclipse.smarthome.automation.RuleManager")
from core.rules import rule
from core.triggers import when
from core.utils import validate_item
from core.metadata import get_value
from core.log import log_traceback

__all__ = [ "init", "uninit" ]

@log_traceback
def init(rule_reinit, rule_scene_changed, rule_light_update, rule_level_source_update):
    """Initialize Eos.

    This creates a rule with triggers for the scene item in
    ``configuration.eos_master_group`` and any descendants that are a
    ``GroupItem`` and contain a scene item to update members when they receive
    an update.
    """
    def _gen_triggers_for_level_sources(config):
        all_items_valid = True
        for key in config:
            if isinstance(config[key], dict):
                all_items_valid = all_items_valid and _gen_triggers_for_level_sources(config[key])
            elif key == META_KEY_LEVEL_SOURCE:
                itemLevel = validate_item(config[key])
                if itemLevel is not None:
                    if itemLevel.name not in levelItemTriggers:
                        log.debug("Adding '{level_source}' item trigger for '{level}'".format(level=itemLevel.name, level_source=META_KEY_LEVEL_SOURCE))
                        levelItemTriggers[itemLevel.name] = when("Item {name} received update".format(name=itemLevel.name))
                else:
                    log.error("Failed to add '{level_source}' item trigger for '{level}', item does not exist".format(level=itemLevel.name, level_source=META_KEY_LEVEL_SOURCE))
                    all_items_valid = False
        return all_items_valid

    def _gen_triggers_for_group(group, ruleScene, ruleLight):
        if str(get_value(group.name, META_NAME_EOS)).lower() in META_STRING_FALSE:
            log.info("Found group '{group}' but it is disabled".format(name=group.name))
        else:
            log.debug("Scanning group '{group}' for scene and light items".format(group=group.name))
            itemScene = get_scene_item(group)
            if itemScene:
                if not _gen_triggers_for_level_sources(get_metadata(group.name, META_NAME_EOS).get("configuration", {})):
                    log.warn("Some '{level_source}' items for group '{group}' do not exist".format(
                            level_source=META_KEY_LEVEL_SOURCE, group=group.name))
                # add scene trigger
                when("Item {name} changed".format(name=itemScene.name))(ruleScene)
                log.debug("Added scene item trigger for '{name}'".format(name=itemScene.name))
                # add lights triggers
                for light in get_light_items(group):
                    if str(get_value(light.name, META_NAME_EOS)).lower() in META_STRING_FALSE:
                        log.info("Found light '{name}' in '{group}' but it is disabled".format(name=light.name, group=group.name))
                    else:
                        log.debug("Found light '{name}' in '{group}'".format(name=light.name, group=group.name))
                        if not _gen_triggers_for_level_sources(get_metadata(light.name, META_NAME_EOS).get("configuration", {})):
                            log.warn("Some '{level_source}' items for light '{name}' do not exist".format(
                                    level_source=META_KEY_LEVEL_SOURCE, name=light.name))
                        log.debug("Adding light item trigger for '{name}'".format(name=light.name))
                        when("Item {name} received update".format(name=light.name))(ruleLight)
                # recurse into groups
                for group in get_group_items(group, include_no_lights=True):
                    _gen_triggers_for_group(group, ruleScene, ruleLight)
            else:
                log.warn("No lights or groups in '{group}' will be discovered because it has no scene item".format(group=group.name))

    log.info("Eos initializing...")

    if not config.master_group_name:
        log.error("No '{name}' specified in configuration".format(name=CONF_KEY_MASTER_GROUP))
        log.error("Eos failed to initialize")
        return

    if not config.scene_item_prefix and not config.scene_item_suffix:
        log.error("Must specify at least one of '{prefix}' or '{suffix}' in configuration".format(prefix=CONF_KEY_SCENE_PREFIX, suffix=CONF_KEY_SCENE_SUFFIX))
        log.error("Eos failed to initialize")
        return

    master_group_item = validate_item(config.master_group_name)
    if not master_group_item:
        log.error("Master group item '{group}' does not exist".format(group=config.master_group_name))
        log.error("Eos failed to initialize")
        return
    elif not isinstance(master_group_item, itemtypesGroup):
        log.error("Master group item '{group}' is not a GroupItem".format(group=config.master_group_name))
        log.error("Eos failed to initialize")
        return
    if not get_scene_item(master_group_item):
        log.error("Could not validate master scene item in '{group}'".format(group=config.master_group_name))
        log.error("Eos failed to initialize")
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
    if hasattr(rule_scene_changed, "triggers"): delattr(rule_scene_changed, "triggers")
    if hasattr(rule_light_update, "triggers"): delattr(rule_light_update, "triggers")
    if hasattr(rule_level_source_update, "triggers"): delattr(rule_level_source_update, "triggers")

    # add rule to reload Eos if item exists
    if config.reinit_item_name:
        log.debug("Creating {rule}".format(rule=RULE_REINIT_NAME))
        when("Item {name} received command ON".format(name=config.reinit_item_name))(rule_reinit)
        rule(RULE_REINIT_NAME, RULE_REINIT_DESC)(rule_reinit)
        if hasattr(rule_reinit, "UID"):
            log.debug("{rule} UID is '{uid}'".format(rule=RULE_REINIT_NAME, uid=rule_reinit.UID))
        else:
            log.error("Failed to create {rule}".format(rule=RULE_REINIT_NAME))

    # generate triggers for all scene, light, and level source items
    levelItemTriggers = {}
    _gen_triggers_for_level_sources(config.global_settings)
    _gen_triggers_for_group(master_group_item, rule_scene_changed, rule_light_update)

    if hasattr(rule_light_update, "triggers"): # do not proceed if there are no lights
        # create scene changed update
        log.debug("Creating {rule}".format(rule=RULE_SCENE_NAME))
        rule(RULE_SCENE_NAME, RULE_SCENE_DESC)(rule_scene_changed)
        if hasattr(rule_scene_changed, "UID"):
            log.debug("{rule} UID is '{uid}'".format(rule=RULE_SCENE_NAME, uid=rule_scene_changed.UID))
        else:
            log.error("Failed to create {rule}".format(rule=RULE_SCENE_NAME))
            log.error("Eos failed to initialize")
            return

        # create light received update rule
        log.debug("Creating {rule}".format(rule=RULE_LIGHT_NAME))
        rule(RULE_LIGHT_NAME, RULE_LIGHT_DESC)(rule_light_update)
        if hasattr(rule_light_update, "UID"):
            log.debug("{rule} UID is '{uid}'".format(rule=RULE_LIGHT_NAME, uid=rule_light_update.UID))
        else:
            log.error("Failed to create {rule}".format(rule=RULE_LIGHT_NAME))
            log.error("Eos failed to initialize")
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
    else:
        log.warn("No lights found")
        return

    log.info("Eos initialized")
    update_eos()


@log_traceback
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
