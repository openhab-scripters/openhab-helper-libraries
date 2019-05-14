from core.rules import rule
from core.triggers import when

@rule("Jython Hello World (cron decorators)", description="This is an example cron triggered rule using decorators", tags=["Test tag", "Hello World"])# [description and tags are optional]
@when("Time cron 0/10 * * * * ?")
def hellowWorldCronDecorators(event):
    hellowWorldCronDecorators.log.info("Hello World!")

# The following cron triggered rules are for demonstration of how the Jython helper libraries have evolved
'''
from core.triggers import CronTrigger
from core.rules import rule

@rule("Jython Hello World (CronTrigger extension with rule decorator)", description="This is an example rule using a CronTrigger extension and rule decorator", tags=["Example rule tag"])
class CronExtensionWithRuleDecorator(object):
    def __init__(self):
        self.triggers = [CronTrigger("0/10 * * * * ?").trigger]

    def execute(self, module, inputs):
        self.log.info("Hello World!")
'''
'''
from core.triggers import CronTrigger
from core.log import logging, LOG_PREFIX

scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleSimple")

class CronTriggerExtension(SimpleRule):
    def __init__(self):
        self.triggers = [CronTrigger("0/10 * * * * ?").trigger]
        self.name = "Jython Hello World (CronTrigger extension)"
        self.description = "This is an example Jython rule using a CronTrigger extension"
        self.tags = set("Example rule tag")
        self.log = logging.getLogger("{}.Hello World (CronTrigger extension)".format(LOG_PREFIX))

    def execute(self, module, inputs):
        self.log.info("Hello World!")

automationManager.addRule(CronTriggerExtension())
'''
'''
from org.slf4j import Logger, LoggerFactory

scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleSimple")

class GenericCronTriggerRawAPI(SimpleRule):
    def __init__(self):
        self.triggers = [
            TriggerBuilder.create()
                    .withId("Hello_World_Cron_Trigger")# no spaces akkowed in trigger ID
                    .withTypeUID("timer.GenericCronTrigger")
                    .withConfiguration(
                        Configuration({
                            "cronExpression": "0/10 * * * * ?"
                        })).build()
        ]
        self.name = "Jython Hello World (GenericCronTrigger raw API)"
        self.description = "This is an example Jython cron rule using the raw API"
        self.tags = set("Example rule tag")
        self.log = LoggerFactory.getLogger("jython.Hello World (GenericCronTrigger raw API)")

    def execute(self, module, inputs):
        self.log.info("Hello World!")

automationManager.addRule(GenericCronTriggerRawAPI())
'''

# These rules require an Item named Test_Switch_1
'''
from core.rules import rule
from core.triggers import when

@rule("Jython Hello World (Item update decorators)", description="This is an example Item update triggered rule using decorators", tags=["Example rule tag"])
@when("Item Test_Switch_1 received update")
def hellowWorldItemUpdateDecorators(event):
    hellowWorldItemUpdateDecorators.log.info("Hello World!")
'''
# The following Item update triggered rules are for demonstration of how the Jython helper libraries have evolved
'''
from core.triggers import ItemStateUpdateTrigger
from core.rules import rule

@rule("Jython Hello World (ItemStateUpdateTrigger extension with rule decorator)", description="This is an example rule using a ItemStateUpdateTrigger extension and rule decorator", tags=["Example rule tag"])
class ItemStateUpdateTriggerExtensionWithRuleDecorator(object):
    def __init__(self):
        self.triggers = [ItemStateUpdateTrigger("Test_Switch_1").trigger]
    
    def execute(self, module, inputs):
        self.log.info("Hello World!")
'''
'''
from core.triggers import ItemStateUpdateTrigger
from core.log import logging, LOG_PREFIX

scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleSimple")

class ItemStateUpdateTriggerExtension(SimpleRule):
    def __init__(self):
        self.triggers = [ItemStateUpdateTrigger("Test_Switch_1").trigger]
        self.name = "Jython Hello World (ItemStateUpdateTrigger extension)"
        self.description = "This is an example rule using an ItemStateUpdateTrigger extension"
        self.tags = set("Example rule tag")
        self.log = logging.getLogger("{}.Hello World (ItemStateUpdateTrigger extension)".format(LOG_PREFIX))

    def execute(self, module, inputs):
        self.log.info("Hello World!")

automationManager.addRule(ItemStateUpdateTriggerExtension())
'''
'''
from org.slf4j import Logger, LoggerFactory

scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleSimple")

class ItemStateUpdateTriggerRawAPI(SimpleRule):
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
        self.name = "Jython Hello World (ItemStateUpdateTrigger raw API)"
        self.description = "This is an example Jython cron rule using the raw API"
        self.tags = set("Example rule tag")
        self.log = logging.getLogger("{}.Hello World (ItemStateUpdateTrigger raw API)".format(LOG_PREFIX))

    def execute(self, module, input):
        self.log.info("Hello World!")

automationManager.addRule(ItemStateUpdateTriggerRawAPI())
'''
