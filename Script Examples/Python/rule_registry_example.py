"""
This example shows how to retrieve the RuleRegistry service and use it to query rule instances based on tags, enable and disable rule instances dynamically, and manually fire rules with specified inputs.
Requires a rule with a "Test tag" tag.
Tags can be set in the rule decorator or rule constructors (self.tags = ["tag1", "tag2"]).
"""

import time

from core.osgi import get_service
from core.log import logging, LOG_PREFIX

log = logging.getLogger("{}.registry_example".format(LOG_PREFIX))

# Get rules by tags
# Tags can be set in rule constructors
# Example: self.tags = ["tag1", "tag2"]
rule_registry = get_service("org.openhab.core.automation.RuleRegistry") or get_service("org.eclipse.smarthome.automation.RuleRegistry")
rules_with_tag = rule_registry.getByTag("Test tag")

for rule in rules:
    rule_status = rule_registry.getStatusInfo(rule.UID)
    log.info("Rule name=[{}], description=[{}], tags=[{}], UID=[{}], status=[{}]".format(rule.name, rule.description, rule.tags, rule.UID, rule_status))

    # disable a rule
    rule_registry.setEnabled(rule.UID, False)

    # later...
    time.sleep(5)

    # reenable the rule
    rule_registry.setEnabled(rule.UID, True)

    # fire the rule manually (with inputs)
    log.info("Triggering rule manually")
    rule_registry.runNow(rule.UID, False, {'name': 'EXAMPLE'})
