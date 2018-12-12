"""
This example demonstrates logging, rue and trigger decorator, and the test runner.

Required Items:
    Number TestNumber1
    Number TestNumber2
"""

import unittest
import time
from core.log import logging
from core.testing import run_test
from core.triggers import when
import core.items

@rule("Example testing rule")
@when("Item TestNumber1 received update")
def double_the_value():
    events.postUpdate("TestNumber2", str(2 * items.TestNumber1.floatValue()))
    
class MyUnitTest(unittest.TestCase):
    def setUp(self):
        core.items.add("TestNumber1", "Number")
        core.items.add("TestNumber2", "Number")
        
    def tearDown(self):
        core.items.remove("TestNumber1")
        core.items.remove("TestNumber2")
        
    def test_item(self):
        events.postUpdate("TestNumber1", str(5))
        time.sleep(1)
        self.assertEqual(items.TestNumber2.floatValue(), 10)

# results are also logged to openHAB log file
# status can be used to take actions like sending notifications
# results is a JSON formatted string (will probably change to return Python dict instead)

print run_test(MyUnitTest)