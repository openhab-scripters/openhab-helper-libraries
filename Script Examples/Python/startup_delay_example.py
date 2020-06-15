"""
This script is designed to delay the loading of other scripts until openHAB is
completely started.
"""
from time import sleep

from org.slf4j import LoggerFactory

LOG = LoggerFactory.getLogger("jsr223.jython.core.startup_delay")

LOG.info("Checking for initialized context")

while True:
    try:
        scriptExtension.importPreset("RuleSupport")
        if automationManager is not None:
            break
    except:
        LOG.info("Context not initialized yet... waiting 10s before checking again")
        sleep(10)

LOG.info("Context initialized... waiting 30s before allowing scripts to load")
sleep(30)
LOG.info("Complete")
