"""
Example of unit testing.
"""
import unittest
import time
import core.items
from core.log import logging, LOG_PREFIX
from core.rules import rule
from core.testing import run_test
from core.triggers import when
from core.utils import getItemValue, postUpdateCheckFirst

RESPONSE_TIME = 5

log = logging.getLogger("{}.testing_2_example".format(LOG_PREFIX))

class ItemPostUpdater(object):
    def __init__(self, item1, item2):
        self.item1 = item1
        self.item2 = item2

        # create the rule.
        self.myrule=rule(self.__class__.__name__ + " " + item1.name)(
            when("Item {} received update".format(item1.name))
            (self))

    # this method gets called when the rule executes
    def __call__(self, event):
        log.debug("rule {} triggered by {}, state {}".format(self.__class__.__name__, event.itemName, event.itemState))
        events.postUpdate(self.item2.name, str(2 * getItemValue(self.item1.name, 0.1)))


    def cleanup(self):
        pass


class MyUnitTest(unittest.TestCase):

    ITEM1NAME = "TestNumber1"
    ITEM2NAME = "TestNumber2"


    def setUp(self):
        self.item1 = core.items.add_item(self.ITEM1NAME, "Number")
        self.item2 = core.items.add_item(self.ITEM2NAME, "Number")
        self.test = ItemPostUpdater(self.item1, self.item2)

    def tearDown(self):
        core.items.remove_item(self.item1)
        core.items.remove_item(self.item2)
        self.test.cleanup()

    def test_item(self):
        events.postUpdate(self.item1, str(5))
        time.sleep(RESPONSE_TIME)
        self.assertEqual(self.item2.state.floatValue(), 10.0)

# results are also logged to the openHAB log file
# status can be used to take actions like sending notifications
# results are a JSON formatted string (will probably change to return Python dict instead)

def scriptLoaded(id):
    log.info(run_test(MyUnitTest))
