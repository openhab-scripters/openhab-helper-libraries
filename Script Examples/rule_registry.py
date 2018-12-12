# This example demonstrates using the rule registry, getting a rule's status, enabling/disabling
# rules, and manually running a rule. This will require a rule with a "Test tag" tag. Tags can
# be set in rule constructors (self.tags = ["tag1", "tag2"]), or in the rule decorator.

import time

from core.osgi import get_service
from core.log import logging, LOG_PREFIX

log = logging.getLogger("registry_example")
rule_registry = get_service(LOG_PREFIX + ".rule_registry")
rules_with_tag = rule_registry.getByTag("Test tag")

for rule in rules:
    rule_status = rule_registry.getStatusInfo(rule.UID)
    log.info("rule_status=[{}]".format(rule_status))
    
    # disable a rule
    rule_registry.setEnabled(rule.UID, False)
    
    # later...
    time.sleep(5)
    
    # reenable the rule
    rule_registry.setEnabled(rule.UID, True)
    
    # fire the rule manually (with inputs)
    log.info("Triggering rule manually")
    rule_registry.runNow(rule.UID, False, {'name': 'EXAMPLE'})