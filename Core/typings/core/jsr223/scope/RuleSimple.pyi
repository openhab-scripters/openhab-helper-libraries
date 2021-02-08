"""
This is the contents of the ``RuleSimple`` scope, see:
https://www.openhab.org/docs/configuration/jsr223.html#rulesimple-preset
"""

__all__ = [
    "ActionType",
    "ConfigDescriptionParameter",
    "ModuleType",
    "SimpleActionHandler",
    "SimpleConditionHandler",
    "SimpleRule",
    "SimpleTriggerHandler",
    "TriggerType",
    "Visibility",
]

try:
    from org.openhab.core.config.core import ConfigDescriptionParameter
    from org.openhab.core.automation import Visibility
    from org.openhab.core.automation.type import ActionType, ModuleType, TriggerType
    from org.openhab.core.automation.module.script.rulesupport.shared.simple import (
        SimpleActionHandler,
        SimpleConditionHandler,
        SimpleRule,
        SimpleTriggerHandler,
    )
except:
    from org.eclipse.smarthome.core.config.core import ConfigDescriptionParameter
    from org.eclipse.smarthome.core.automation import Visibility
    from org.eclipse.smarthome.core.automation.type import ActionType, ModuleType, TriggerType
    from org.eclipse.smarthome.core.automation.module.script.rulesupport.shared.simple import (
        SimpleActionHandler,
        SimpleConditionHandler,
        SimpleRule,
        SimpleTriggerHandler,

