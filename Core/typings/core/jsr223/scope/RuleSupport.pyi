"""
This is the contents of the ``RuleSupport`` scope, see:
https://www.openhab.org/docs/configuration/jsr223.html#rulesupport-preset
"""

__all__ = [
    "Action",
    "ActionBuilder",
    "Condition",
    "ConditionBuilder",
    "Configuration",
    "ModuleBuilder",
    "Rule",
    "Trigger",
    "TriggerBuilder",
    "automationManager",
    "ruleRegistry",
]

try:
    from org.openhab.core.automation import (
        Action,
        Condition,
        Rule,
        Trigger,
    )
    from org.openhab.core.automation.util import (
        ActionBuilder,
        ConditionBuilder,
        ModuleBuilder,
        TriggerBuilder,
    )
    from org.openhab.core.automation.module.script.rulesupport.shared import (
        RuleSupportRuleRegistryDelegate,
        ScriptedAutomationManager,
    )
    from org.openhab.core.config.core import Configuration
except:
    from org.eclipse.smarthome.core.automation import (
        Action,
        Condition,
        Rule,
        Trigger,
    )
    from org.eclipse.smarthome.core.automation.util import (
        ActionBuilder,
        ConditionBuilder,
        ModuleBuilder,
        TriggerBuilder,
    )
    from org.eclipse.smarthome.core.automation.module.script.rulesupport.shared import (
        RuleSupportRuleRegistryDelegate,
        ScriptedAutomationManager,
    )
    from org.eclipse.smarthome.core.config.core import Configuration

automationManager: ScriptedAutomationManager = ...

ruleRegistry: RuleSupportRuleRegistryDelegate = ...
