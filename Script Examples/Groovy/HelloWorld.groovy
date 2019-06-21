import org.slf4j.LoggerFactory

def log = LoggerFactory.getLogger("jsr223.groovy")

import org.openhab.core.automation.Action
import org.openhab.core.automation.module.script.rulesupport.shared.simple.SimpleRule
import org.eclipse.smarthome.config.core.Configuration

scriptExtension.importPreset("RuleSupport")

def rawAPIRule = new SimpleRule() {
    String name = "Groovy Hello World (GenericCronTrigger raw API)"
    String description = "This is an example Hello World rule using the raw API"
    Object execute(Action module, Map<String, ?> inputs) {
        log.info("Hello World!")
    }
}

rawAPIRule.setTriggers([
    TriggerBuilder.create()
        .withId("aTimerTrigger")
        .withTypeUID("timer.GenericCronTrigger")
        .withConfiguration(new Configuration([cronExpression: "0/10 * * * * ?"]))
        .build()
    ])
    
automationManager.addRule(rawAPIRule)