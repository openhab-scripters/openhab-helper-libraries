from org.slf4j import Logger, LoggerFactory
from openhab.rules import rule
from openhab.triggers import when, CronTrigger
scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleSimple")

log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")
'''
class RawAPICron(SimpleRule):
    def __init__(self):
        self.triggers = [
            TriggerBuilder.create()
                    .withId("Hello_World_Timer_Trigger")
                    .withTypeUID("timer.GenericCronTrigger")
                    .withConfiguration(
                        Configuration({
                            "cronExpression": "0/10 * * * * ?"
                        })).build()
        ]

    def execute(self, module, inputs):
        log.info("JSR223: This is a 'hello world!' from a Jython rule (raw API): Cron")

automationManager.addRule(RawAPICron())

# make sure you have an item named Test_Switch_1, or swap out the item for one that exists
class RawAPIStateUpdate(SimpleRule):
    def __init__(self):
        self.triggers = [
            TriggerBuilder.create()
                .withId("Hello_World_State_Update_Trigger")
                .withTypeUID("core.ItemStateUpdateTrigger")
                .withConfiguration(
                    Configuration({
                        "itemName": "Test_Switch_1"
                    }))
                .build()
        ]

    def execute(self, module, input):
        log.info("JSR223: This is a 'hello world!' from a Jython rule (raw API): ItemStateUpdateTrigger")

automationManager.addRule(RawAPIStateUpdate())

# requires CronTrigger import
class ExtensionCron(SimpleRule):
    def __init__(self):
        self.triggers = [ CronTrigger("0/10 * * * * ?").trigger ]
    
    def execute(self, module, inputs):
        log.info("JSR223: This is a 'hello world!' from a Jython rule (extension): Cron")

automationManager.addRule(ExtensionCron())
'''
# requires rule and when imports
@rule("Hello World timer rule")
@when("Time cron 0/10 * * * * ?")
def hellowWorldDecorator(event):
    log.info("JSR223: This is a 'hello world!' from a Jython rule (decorator): Cron")
