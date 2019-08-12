
CONF_KEY_MASTER_GROUP = "eos_master_group"
CONF_KEY_SCENE_PREFIX = "eos_scene_item_prefix"
CONF_KEY_SCENE_SUFFIX = "eos_scene_item_suffix"
CONF_KEY_GLOBAL_SETTINGS = "eos_global_settings"
CONF_KEY_REINIT_ITEM = "eos_reload_item_name"
CONF_KEY_LOG_TRACE = "eos_log_trace"

META_NAME_EOS = "eos"
META_STRING_FALSE = ["false", "disabled", "off", "no"]
META_KEY_FOLLOW_PARENT = "follow_parent"
META_KEY_LEVEL_SOURCE = "level_source"
META_KEY_LEVEL_THRESHOLD = "level_threshold"
META_KEY_LEVEL_HIGH = "level_high"
META_KEY_LEVEL_LOW = "level_low"
META_KEY_STATE = "state"
META_KEY_STATE_ABOVE = "state_above"
META_KEY_STATE_BELOW = "state_below"
META_KEY_STATE_HIGH = "state_high"
META_KEY_STATE_LOW = "state_low"
META_KEY_MOTION_SOURCE = "motion_source"
META_KEY_MOTION_ACTIVE = "motion_active"
META_KEY_MOTION_STATE = "motion_state"
META_KEY_MOTION_SCENE = "motion_scene"
META_KEY_DEPTH_MAP = {
    META_KEY_LEVEL_SOURCE: [1,2,3,4,5,6,7,8,9,10],
    META_KEY_LEVEL_THRESHOLD: [1,2,3,4,5,6,7,8,9,10],
    META_KEY_LEVEL_HIGH: [1,2,3,4,5,6,7,8,9,10],
    META_KEY_LEVEL_LOW: [1,2,3,4,5,6,7,8,9,10],
    META_KEY_STATE: [1,2,3,5,7,9],
    META_KEY_STATE_ABOVE: [1,2,3,5,7,9],
    META_KEY_STATE_BELOW: [1,2,3,5,7,9],
    META_KEY_STATE_HIGH: [1,2,3,5,7,9],
    META_KEY_STATE_LOW: [1,2,3,5,7,9],
    META_KEY_MOTION_SOURCE: [1,2,3,4,5,6,7,8,9,10],
    META_KEY_MOTION_ACTIVE: [1,2,3,4,5,6,7,8,9,10],
    META_KEY_MOTION_STATE: [1,2,3,5,7,9],
    META_KEY_MOTION_SCENE: [1,2,3,4,5,6,7,8,9,10]
}

LIGHT_TYPE_SWITCH = "switch"
LIGHT_TYPE_DIMMER = "dimmer"
LIGHT_TYPE_COLOR = "color"
LIGHT_TYPE_MAP = {"color": LIGHT_TYPE_COLOR, "dimmer": LIGHT_TYPE_DIMMER, "number": LIGHT_TYPE_DIMMER, "switch": LIGHT_TYPE_SWITCH}

SCENE_TYPE_FIXED = "fixed"
SCENE_TYPE_THRESHOLD = "threshold"
SCENE_TYPE_SCALED = "scaled"
SCENE_PARENT = "parent"
SCENE_MANUAL = "manual"
SCENE_ON = "on"
SCENE_OFF = "off"

_global_settings = {
    LIGHT_TYPE_SWITCH: {
        SCENE_ON: { META_KEY_STATE: "ON" },
        SCENE_OFF: { META_KEY_STATE: "OFF" },
        META_KEY_STATE: "OFF",
        META_KEY_STATE_ABOVE: "OFF",
        META_KEY_STATE_BELOW: "ON",
        META_KEY_MOTION_SCENE: "on"
    },
    LIGHT_TYPE_DIMMER: {
        SCENE_ON: { META_KEY_STATE: 100 },
        SCENE_OFF: { META_KEY_STATE: 0 },
        META_KEY_STATE: 0,
        META_KEY_STATE_HIGH: 0,
        META_KEY_STATE_LOW: 100,
        META_KEY_MOTION_SCENE: "on"
    },
    LIGHT_TYPE_COLOR: {
        SCENE_ON: { META_KEY_STATE: 100 },
        SCENE_OFF: { META_KEY_STATE: 0 },
        META_KEY_STATE: 0,
        META_KEY_STATE_HIGH: 0,
        META_KEY_STATE_LOW: 100,
        META_KEY_MOTION_SCENE: "on"
    }
}

__all__ = [
    "CONF_KEY_MASTER_GROUP", "CONF_KEY_SCENE_PREFIX", "CONF_KEY_SCENE_SUFFIX",
    "CONF_KEY_GLOBAL_SETTINGS", "CONF_KEY_REINIT_ITEM", "CONF_KEY_LOG_TRACE",

    "META_NAME_EOS", "META_STRING_FALSE",
    "META_KEY_FOLLOW_PARENT", "META_KEY_LEVEL_SOURCE", "META_KEY_LEVEL_THRESHOLD",
    "META_KEY_LEVEL_HIGH", "META_KEY_LEVEL_LOW", "META_KEY_STATE",
    "META_KEY_STATE_ABOVE", "META_KEY_STATE_BELOW", "META_KEY_STATE_HIGH",
    "META_KEY_STATE_LOW", "META_KEY_MOTION_SOURCE", "META_KEY_MOTION_ACTIVE",
    "META_KEY_MOTION_STATE", "META_KEY_MOTION_SCENE", "META_KEY_DEPTH_MAP",

    "LIGHT_TYPE_SWITCH", "LIGHT_TYPE_DIMMER", "LIGHT_TYPE_COLOR", "LIGHT_TYPE_MAP",

    "SCENE_TYPE_FIXED", "SCENE_TYPE_THRESHOLD", "SCENE_TYPE_SCALED", "SCENE_PARENT",
    "SCENE_MANUAL", "SCENE_ON", "SCENE_OFF",

    "itemtypesScene", "itemtypesLight", "itemtypesSwitch", "itemtypesDimmer",
    "itemtypesColor", "itemtypesGroup",

    "META_KEY_LIST", "DEPTH_NAME_MAP", "LIGHT_TYPE_LIST", "META_KEY_OPTION_LIST"
]

###### used only in editor ######

META_KEY_LIST = [META_KEY_LEVEL_SOURCE, META_KEY_LEVEL_THRESHOLD, META_KEY_LEVEL_HIGH, META_KEY_LEVEL_LOW,
    META_KEY_STATE, META_KEY_STATE_ABOVE, META_KEY_STATE_BELOW, META_KEY_STATE_HIGH, META_KEY_STATE_LOW,
    META_KEY_MOTION_SOURCE, META_KEY_MOTION_ACTIVE, META_KEY_MOTION_STATE, META_KEY_MOTION_SCENE]
META_KEY_OPTION_LIST = [META_KEY_FOLLOW_PARENT]

DEPTH_NAME_MAP = ["", "item-scene", "item", "group-type-scene", "group-scene", "group-type", "group",
    "global-type-scene", "global-scene", "global-type", "global"]

LIGHT_TYPE_LIST = [LIGHT_TYPE_SWITCH, LIGHT_TYPE_DIMMER, LIGHT_TYPE_COLOR]

itemtypesScene = ["String"]
itemtypesLight = ["Color", "Dimmer", "Number", "Switch"]
itemtypesSwitch = ["Switch"]
itemtypesDimmer = ["Color", "Dimmer", "Number"]
itemtypesColor = ["Color"]
itemtypesGroup = ["Group"]
