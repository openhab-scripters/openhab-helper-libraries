"""
This example demonstrates the logging bridge and trigger function decorators.

Note that TestSwitch2 must be defined in an items file.
"""

from openhab.log import logging
from openhab.triggers import time_triggered, EVERY_SECOND, item_triggered

count = 0

@time_triggered(EVERY_SECOND)
def my_periodic_function():
    global count
    logging.info("running periodic function: %d", count)
    count += 1
    if count % 5 == 0:
        events.postUpdate("TestSwitch2", "ON")

@item_triggered("TestSwitch2")
def my_item_function():
    if items.TestSwitch2 == ON:
        logging.info("**** Switch ON ****")
        events.postUpdate("TestSwitch2", "OFF")
