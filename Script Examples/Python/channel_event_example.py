"""
This script displays an example of a rule triggered by Channel events.
"""

# Example Channel event rule (decorators) [description and tags are optional]
from core.triggers import when
from core.rules import rule

@rule("Example Channel event rule (decorators)", description="This is an example rule that is triggered by the sun setting", tags=["Example", "Astro"])
@when("Channel astro:sun:local:set#event triggered START")
def channelEventExampleDecorators(event):
    channelEventExampleDecorators.log.info("Sunset triggered")
