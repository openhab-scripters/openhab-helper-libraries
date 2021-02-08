"""
This is the contents of the ``RuleFactories`` scope, see:
https://www.openhab.org/docs/configuration/jsr223.html#rulefactories-preset
"""

__all__ = [
    "ActionHandlerFactory",
    "ConditionHandlerFactory",
    "TriggerHandlerFactory",
    "TriggerType",
    "ConfigDescriptionParameter",
    "ModuleType",
    "ActionType",
    "Visibility",
]

try:
    from org.openhab.core.automation import Visibility
    from org.openhab.core.automation.type import ActionType, ModuleType, TriggerType
    from org.openhab.core.automation.module.script.rulesupport.shared.factories import (
        ScriptedActionHandlerFactory,
        ScriptedConditionHandlerFactory,
        ScriptedTriggerHandlerFactory,
    )
    from org.openhab.core.config.core import ConfigDescriptionParameter
except:
    from org.eclipse.smarthome.core.automation import Visibility
    from org.eclipse.smarthome.core.automation.type import ActionType, ModuleType, TriggerType
    from org.eclipse.smarthome.core.automation.module.script.rulesupport.shared.factories import (
        ScriptedActionHandlerFactory,
        ScriptedConditionHandlerFactory,
        ScriptedTriggerHandlerFactory,
    )
    from org.eclipse.smarthome.core.config.core import ConfigDescriptionParameter

ActionHandlerFactory = ScriptedActionHandlerFactory
ConditionHandlerFactory = ScriptedConditionHandlerFactory
TriggerHandlerFactory = ScriptedTriggerHandlerFactory
