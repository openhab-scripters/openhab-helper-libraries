'''
# Example Channel event rule (raw API)
scriptExtension.importPreset("RuleSimple")
scriptExtension.importPreset("RuleSupport")

class channelEventExampleRawAPI(SimpleRule):

    def __init__(self):
        triggerName = "Example_Channel_event_trigger"
        config = {
            "channelUID": "astro:sun:local:set#event",
            "event": "START"
        }
        self.triggers = [ TriggerBuilder.create().withId(triggerName).withTypeUID("core.ChannelEventTrigger").withConfiguration(Configuration(config)).build() ]
        self.name = "Example Channel event rule (raw API)"

    def execute(self,modules,inputs):
        self.log.info('Sunset triggered')

automationManager.addRule(channelEventExampleRawAPI())

# Example Channel event rule (extensions)
from core.triggers import ChannelEventTrigger
scriptExtension.importPreset("RuleSimple")
scriptExtension.importPreset("RuleSupport")

class channelEventExampleExtension(SimpleRule):

    def __init__(self):
        self.triggers = [ ChannelEventTrigger("astro:sun:local:set#event", triggerName="Example_Channel_event_trigger", event="START") ]
        self.name = "Example Channel event rule (extension)"

    def execute(self, modules, inputs):
        self.log.info('Sunset triggered')

automationManager.addRule(channelEventExampleExtension())

# Example Channel event rule (extension with rule decorator)
from core.triggers import ChannelEventTrigger
from core.rules import rule

@rule("Example Channel event rule (extension with rule decorator)")
class channelEventExampleExtensionWithRuleDecorator(object):

    def __init__(self):
        self.triggers = [ ChannelEventTrigger("astro:sun:local:set#event", triggerName="Example_Channel_event_trigger", event="START") ]

    def execute(self, modules, inputs):
        self.log.info('Sunset triggered')
'''

# Example Channel event rule (decorators) [description and tags are optional]
from core.triggers import when
from core.rules import rule
from core.log import logging, LOG_PREFIX

log = logging.getLogger(LOG_PREFIX + ".example_Channel_event_rule")

@rule("Example Channel event rule (decorators)", description="This is an example rule that is triggered by the sun setting", tags=["Example", "Astro"])
@when("Channel astro:sun:local:set#event triggered START")
def channelEventExampleDecorators(event):
    log.info("Sunset triggered")