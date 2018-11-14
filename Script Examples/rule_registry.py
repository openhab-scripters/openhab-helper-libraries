# This example will require a rule with an "a" tag

import time

from core.osgi import get_service
from core.log import logging
log = logging.getLogger("registry_example")

rule_registry = get_service("org.eclipse.smarthome.automation.RuleRegistry")

# Get rules by tags
# Tags can be set in rule constructors, or in the rule decorator
# Example: self.tags = ["tag1", "tag2"]

rules = rule_registry.getByTag("Test tag")

for rule in rules:
    rule_status = rule_registry.getStatusInfo(rule.UID)
    log.info("rule_status=%s", rule_status)
    
    # disable a rule
    rule_registry.setEnabled(rule.UID, False)
    
    # later...
    time.sleep(5)
    
    # reenable the rule
    rule_registry.setEnabled(rule.UID, True)
    
    # fire the rule manually (with inputs)
    log.info("triggering rule manually")
    rule_registry.runNow(rule.UID, False, {'name': 'EXAMPLE'})
