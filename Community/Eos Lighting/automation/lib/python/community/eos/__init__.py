"""
Eos Lighting System
"""

from core.log import logging, LOG_PREFIX, log_traceback
log = logging.getLogger("{prefix}.community.eos".format(prefix=LOG_PREFIX))

from community.eos.system import init, uninit
from community.eos.update import update_light, update_group, update_scene
from community.eos.constants import RULE_REINIT_NAME, RULE_SCENE_NAME, RULE_LIGHT_NAME, RULE_LEVEL_SOURCE_NAME

__all__ = [ "log", "init", "uninit",
    "update_light", "update_group", "update_scene" ]
