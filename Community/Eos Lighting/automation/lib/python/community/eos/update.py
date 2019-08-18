"""
Eos Lighting

Process Light and Group updates
"""

from community.eos import log, config
from community.eos.util import *
from community.eos.constants import *

from core.log import log_traceback
from core.metadata import get_value
from core.utils import sendCommand, sendCommandCheckFirst, validate_item

__all__ = [ "update_eos", "update_scene", "update_light", "update_group" ]



@log_traceback
def update_eos():
    """
    Public function to update all Eos controlled lights
    """
    update_group(validate_item(config.master_group_name))


@log_traceback
def update_scene(item):
    """
    Updates all lights and subgroups
    """
    for light_item in get_light_items(get_item_eos_group(item)):
        try: update_light(light_item)
        except: continue

    for group_item in get_group_items(get_item_eos_group(item)):
        if str(get_value(group_item.name, META_NAME_EOS)).lower() not in META_STRING_FALSE:
            # set children to "parent" scene unless following is turned off
            if resolve_type(get_metadata(group_item.name, META_NAME_EOS).get("configuration", {}).get(META_KEY_FOLLOW_PARENT, True)):
                log.debug("Setting '{group}' to follow '{name}' scene".format(group=group_item.name, name=item.name))
                sendCommand(get_scene_item(group_item).name, SCENE_PARENT)
            else:
                update_group(group_item, True)


@log_traceback
def update_light(item):
    """
    Sends commands to lights based on scene.

    TODO If light does not have metadata for the scene no command will be sent,
    except for the default scenes ``on`` and ``off``. The default values for
    built-in scenes can be customized in ``configuration.py`` if desired.
    """
    if str(get_value(item.name, META_NAME_EOS)).lower() in META_STRING_FALSE:
        log.debug("Skipping update for light '{name}' as it is disabled".format(name=item.name))
        return
    else:
        log.debug("Processing update for light '{name}'".format(name=item.name))

    scene = get_scene_for_item(item)
    if config.log_trace: log.debug("Got scene '{scene}' for item '{name}'".format(scene=scene, name=item.name))

    if scene != SCENE_MANUAL:
        newState = get_state_for_scene(item, scene)
        if sendCommandCheckFirst(item.name, newState, floatPrecision=3):
            log.debug("Sent command '{command}' to light '{name}'".format(command=newState, name=item.name))
        else:
            log.debug("No command sent to light '{name}'".format(command=newState, name=item.name))
    else:
        log.debug("Scene for item '{name}' is '{scene}', no action taken".format(name=item.name, scene=scene))


@log_traceback
def update_group(target, only_if_scene_parent=False):
    if str(get_value(target.name, META_NAME_EOS)).lower() in META_STRING_FALSE:
        log.debug("Skipping update for group '{name}' as it is disabled".format(name=target.name))
        return
    else:
        log.debug("Processing update for group '{name}'".format(name=target.name))

    if only_if_scene_parent and str(get_scene_item(target).state).lower() != SCENE_PARENT:
        return

    for light_item in get_light_items(target):
        try: update_light(light_item)
        except: continue

    for group_item in get_group_items(target):
        update_group(group_item, only_if_scene_parent)


def get_state_for_scene(item, scene):
    """
    Returns state for scene for item.
    """
    def constrain(value, min, max):
        return max if value > max else min if value < min else value

    # get Eos Light Type
    light_type = LIGHT_TYPE_MAP.get(item.type.lower(), None)
    if light_type is None:
        log.error("Couldn't get light type for '{name}'".format(name=item.name))
        return str(item.state)
    else:
        if config.log_trace: log.debug("Got light type '{type}' for '{name}'".format(type=light_type, name=item.name))

    state = None
    data = {}
    data["item"] = get_metadata(item.name, META_NAME_EOS).get("configuration", {})
    if config.log_trace: log.debug("Got Item data for '{name}': {data}".format(name=item.name, data=data["item"]))
    data["group"] = get_metadata(get_item_eos_group(item).name, META_NAME_EOS).get("configuration", {})
    if config.log_trace: log.debug("Got Group data for '{name}': {data}".format(name=get_item_eos_group(item).name, data=data["group"]))
    if config.log_trace: log.debug("Got Global data: {data}".format(name=light_type, data=config.global_settings))

    # check for Motion settings
    motion_source = validate_item(get_scene_setting(item, scene, META_KEY_MOTION_SOURCE, data=data))
    if motion_source:
        motion_active = get_scene_setting(item, scene, META_KEY_MOTION_ACTIVE, data=data)
        motion_state = get_scene_setting(item, scene, META_KEY_MOTION_STATE, data=data)
        motion_scene = get_scene_setting(item, scene, META_KEY_MOTION_SCENE, data=data)
        if motion_active is not None and (motion_state is not None or motion_scene):
            log.debug("Checking Motion trigger for '{name}' for scene '{scene}'".format(name=item.name, scene=scene))
            if str(motion_source.state) == str(motion_active):
                log.debug("Motion trigger is active for '{name}' for scene '{scene}'".format(name=item.name, scene=scene))
                if motion_state is not None:
                    log.debug("Motion trigger applying fixed state '{motion}' for '{name}' for scene '{scene}'".format(
                            motion=motion_state, name=item.name, scene=scene))
                    state = motion_state
                elif motion_scene:
                    log.debug("Motion trigger applying scene '{motion}' for '{name}' for scene '{scene}'".format(
                            motion=motion_scene, name=item.name, scene=scene))
                    scene = motion_scene
            else:
                log.debug("Motion trigger is not active for '{name}' for scene '{scene}'".format(name=item.name, scene=scene))
        elif motion_active is None:
            log.warn("Motion triggers require '{key}' setting, nothing found for '{name}' for scene '{scene}'".format(
                    key=META_KEY_MOTION_ACTIVE, name=item.name, scene=scene))
        elif motion_state is None or not motion_scene:
            log.warn("Motion triggers require '{key_state}' or {key_scene} setting, nothing found for '{name}' for scene '{scene}'".format(
                    key_state=META_KEY_MOTION_STATE, key_scene=META_KEY_MOTION_SCENE, name=item.name, scene=scene))

    # get Scene Type
    scene_type = get_scene_type(item, scene, light_type, data=data)
    if scene_type is None:
        log.error("Couldn't get scene type for '{name}'".format(name=item.name))
        return str(item.state)
    else:
        if config.log_trace: log.debug("Got scene type '{type}' for '{name}'".format(type=scene_type, name=item.name))

    # Fixed State type
    if scene_type == SCENE_TYPE_FIXED and state is None:
        state = get_scene_setting(item, scene, META_KEY_STATE, data=data)
        if state is None:
            log.error("Fixed State type scenes require '{key}' setting, nothing found for '{name}' for scene '{scene}'".format(
                key=META_KEY_STATE, name=item.name, scene=scene))
            return str(item.state)

    # Threshold type
    elif scene_type == SCENE_TYPE_THRESHOLD and state is None:
        if not get_scene_setting(item, scene, META_KEY_LEVEL_SOURCE, data=data):
            log.error("Threshold type scenes require '{key}' setting, nothing found for '{name}' for scene '{scene}'".format(
                key=META_KEY_LEVEL_SOURCE, name=item.name, scene=scene))
            return str(item.state)
        level_value = resolve_type(validate_item(get_scene_setting(item, scene, META_KEY_LEVEL_SOURCE, data=data)).state)
        if isinstance(level_value, str) and level_value.lower() in ["null", "undef"]:
            log.warn("Level item '{key}' for scene '{scene}' for item '{name}' has no value".format(
                key=get_scene_setting(item, scene, META_KEY_LEVEL_SOURCE, data=data), scene=scene, name=item.name))
            return str(item.state)

        level_threshold = get_scene_setting(item, scene, META_KEY_LEVEL_THRESHOLD, data=data)
        if level_threshold is None:
            log.error("Threshold type scenes require '{key}' setting, nothing found for '{name}' for scene '{scene}'".format(
                key=META_KEY_LEVEL_THRESHOLD, name=item.name, scene=scene))
            return str(item.state)

        state_above = get_scene_setting(item, scene, META_KEY_STATE_ABOVE, data=data)
        if state_above is None:
            log.error("Threshold type scenes require '{key}' setting, nothing found for '{name}' for scene '{scene}'".format(
                key=META_KEY_STATE_ABOVE, name=item.name, scene=scene))
            return str(item.state)

        state_below = get_scene_setting(item, scene, META_KEY_STATE_BELOW, data=data)
        if state_below is None:
            log.error("Threshold type scenes require '{key}' setting, nothing found for '{name}' for scene '{scene}'".format(
                key=META_KEY_STATE_BELOW, name=item.name, scene=scene))
            return str(item.state)

        state = state_above if level_value > level_threshold else state_below

    # Scaling type
    elif scene_type == SCENE_TYPE_SCALED and light_type in [LIGHT_TYPE_DIMMER, LIGHT_TYPE_COLOR] and state is None:
        if not get_scene_setting(item, scene, META_KEY_LEVEL_SOURCE, data=data):
            log.error("Scaling type scenes require '{key}' setting, nothing found for '{name}' for scene '{scene}'".format(
                key=META_KEY_LEVEL_SOURCE, name=item.name, scene=scene))
            return str(item.state)
        level_value = resolve_type(validate_item(get_scene_setting(item, scene, META_KEY_LEVEL_SOURCE, data=data)).state)
        if isinstance(level_value, str) and level_value.lower() in ["null", "undef"]:
            log.warn("Level item '{key}' for scene '{scene}' for item '{name}' has no value".format(
                key=get_scene_setting(item, scene, META_KEY_LEVEL_SOURCE, data=data), scene=scene, name=item.name))
            return str(item.state)
        level_value = float(level_value)

        level_high = get_scene_setting(item, scene, META_KEY_LEVEL_HIGH, data=data)
        if level_high is None:
            log.error("Scaling type scenes require '{key}' setting, nothing found for '{name}' for scene '{scene}'".format(
                key=META_KEY_LEVEL_HIGH, name=item.name, scene=scene))
            return str(item.state)
        level_high = float(level_high)

        level_low = get_scene_setting(item, scene, META_KEY_LEVEL_LOW, data=data)
        if level_low is None:
            level_low = 0.0
            log.debug("No value for key '{key}' for scene '{scene}' for item '{name}', using default '{value}'".format(
                key=META_KEY_LEVEL_LOW, scene=scene, name=item.name, value=level_low))
        level_low = float(level_low)

        state_high = get_scene_setting(item, scene, META_KEY_STATE_HIGH, data=data)
        if state_high is None:
            log.error("Scaling type scenes require '{key}' setting, nothing found for '{name}' for scene '{scene}'".format(
                key=META_KEY_STATE_HIGH, name=item.name, scene=scene))
            return str(item.state)

        state_low = get_scene_setting(item, scene, META_KEY_STATE_LOW, data=data)
        if state_low is None:
            log.error("Scaling type scenes require '{key}' setting, nothing found for '{name}' for scene '{scene}'".format(
                key=META_KEY_STATE_LOW, name=item.name, scene=scene))
            return str(item.state)

        state_above = get_scene_setting(item, scene, META_KEY_STATE_ABOVE, data=data) or state_high
        state_below = get_scene_setting(item, scene, META_KEY_STATE_BELOW, data=data) or state_low

        if level_value > level_high:
            state = state_above
        elif level_value < level_low:
            state = state_below
        else:
            scaling_factor = (level_value - level_low) / (level_high - level_low)
            def scale(low, high): return int(round(low + (high - low) * scaling_factor))
            if isinstance(state_high, (int, float)): # Dimmer value
                state = scale(state_low, state_high)
            elif isinstance(state_high, list): # HSV list
                state = [scale(float(state_low[0]), float(state_high[0]))]
                state.append(scale(float(state_low[1]), float(state_high[1])))
                state.append(scale(float(state_low[2]), float(state_high[2])))

    elif state is None:
        log.error("Invalid scene configuration for '{name}' scene '{scene}'".format(name=item.name, scene=scene))
        return str(item.state)

    if light_type == LIGHT_TYPE_SWITCH and isinstance(state, (str)) and state.upper() in ["ON", "OFF"]:
        state = state.upper()
    elif light_type == LIGHT_TYPE_DIMMER and isinstance(state, (int, float)):
        state = str(constrain(int(round(state)), 0, 1000000))
    elif light_type == LIGHT_TYPE_COLOR and isinstance(state, (int, float, list)):
        if isinstance(state, (int, float)):
            oldState = str("0,0,0" if isinstance(item.state, typesUnDef) else item.state).split(",")
            state = ",".join([str(oldState[0]), str(oldState[1]), str(constrain(int(round(state)), 0, 100))])
        else:
            if state[0] > 359: state[0] -= 359
            elif state[0] < 0: state[0] += 359
            state[1] = constrain(state[1], 0, 100)
            state[2] = constrain(state[2], 0, 100)
            if state[2] == 0:
                # needed because some devices will return '0,0,0' if V=0
                state = "0,0,0"
            else:
                state = ",".join([str(i) for i in state])
    else:
        log.warn("New state '{state}' for '{name}' scene '{scene}' is not valid for item type '{type}'".format(
            state=state, name=item.name, scene=scene, type=item.type))
        return str(item.state)

    log.debug("Determined {type} state '{state}' for '{name}' scene '{scene}'".format(
            type=scene_type, state=state, name=item.name, scene=scene))
    return state
