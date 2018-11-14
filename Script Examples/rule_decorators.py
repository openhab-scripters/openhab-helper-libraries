"""
This example demonstrates the logging bridge, trigger and rule function decorators. It
also indirectly uses the core.jsr223 module.

Note that Test_Switch_1 must be defined in an items file.
"""

from core.log import logging
from core.triggers import when, EVERY_SECOND
from core.rules import rule

count = 0

@rule("Example cron triggered rule", tags=["Test tag"])
@when(EVERY_SECOND)
def my_periodic_function():
    global count
    logging.info("running periodic function: %d", count)
    count += 1
    if count % 5 == 0:
        events.postUpdate("TestSwitch2", "ON")

@rule("Example Item changed rule", tags=["Test tag"])
@when("Item Test_Switch_1 changed to ON")
def my_item_function():
    if items.Test_Switch_1 == ON:
        logging.info("**** Switch ON ****")
        events.postUpdate("Test_Switch_1", "OFF")
