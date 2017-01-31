"""
This example demonstrates logging, item trigger decorator and the test runner.

Required Items:
    Number TestNumber1
    Number TestNumber2
"""

import unittest
import time
from openhab.log import logging
from openhab.testing import run_test
from openhab.triggers import item_triggered, ITEM_UPDATE
import openhab.items

@item_triggered("TestNumber1", ITEM_UPDATE)
def double_the_value():
    events.postUpdate("TestNumber2", str(2 * items.TestNumber1.floatValue()))
    
class MyUnitTest(unittest.TestCase):
    def setUp(self):
        openhab.items.add("TestNumber1", "Number")
        openhab.items.add("TestNumber2", "Number")
        
    def tearDown(self):
        openhab.items.remove("TestNumber1")
        openhab.items.remove("TestNumber2")
        
    def test_item(self):
        events.postUpdate("TestNumber1", str(5))
        time.sleep(1)
        self.assertEqual(items.TestNumber2.floatValue(), 10)


# results are also logged to openHAB log file
# status can be used to take actions like sending notifications
# results is a JSON formatted string (will probably change to return Python dict instead)

print run_test(MyUnitTest)
