from time import sleep

from org.slf4j import Logger, LoggerFactory
log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

log.info("JSR223: Startup: Checking for initialized context")

while True:
    try:
        scriptExtension.importPreset("RuleSupport")
        if automationManager is not None:
            log.info("JSR223: Startup: context initialized... waiting 30s before allowing scripts to load")
            break
    except:
        log.info("JSR223: Startup: exception in startup script")
    log.info("JSR223: Startup: Context not initialized yet... waiting 10s before checking again")
    sleep(10)

sleep(30)
log.info("JSR223: Startup: Complete")