import org.slf4j.LoggerFactory

def log = LoggerFactory.getLogger("jsr223.groovy.core.startup_delay")

log.info("Checking for initialized context")

while (true) {
    try {
        scriptExtension.importPreset("RuleSupport")
        if (automationManager != null) {
            break
        }
    } catch(Exception ex) {
        log.info("Context not initialized yet... waiting 10s before checking again")
        sleep(10000)
    }
}

log.info("Context initialized... waiting 30s before allowing scripts to load")
sleep(30000)
log.info("Complete")
