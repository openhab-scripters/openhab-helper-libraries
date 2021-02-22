"""
One of the challenges of openHAB rule development is verifying that rules are
behaving correctly and haven't broken as the code evolves. This module supports
running automated tests within a runtime context. To run tests directly from
scripts:

.. code-block::

    import unittest # standard Python library
    from core.testing import run_test

    class MyTest(unittest.TestCase):
        def test_something(self):
            "Some test code..."

    run_test(MyTest)

This module also defines a rule class, `TestRunner`. When a switch item is
turned on, it will run a testcase and store the test results in a string item.
"""
from __future__ import absolute_import

import unittest
from tempfile import TemporaryFile
from core.log import logging
from core.triggers import ItemStateUpdateTrigger
from core.jsr223.scope import SimpleRule, scriptExtension, events, OnOffType

scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleSimple")

_RESULT_TEMPLATE = """{{
  "run": {run},
  "errors": {errors},
  "failures": {failures},
  "skipped": {skipped}
}}"""


def _run_test(test_case, out = None, verbosity=None):
    def _format_errors(errors):
        return u"{}".format(",\n    ".join('{{"name":"{}", "stack":"{}"}}'.format(
            test.id(), stack.replace('"', r'\"')) for test, stack in errors))
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(test_case)
    if out is not None:
        runner = unittest.TextTestRunner(out, verbosity=verbosity)
    else:
        runner = unittest.TextTestRunner()
    result = runner.run(suite)
    json_result = _RESULT_TEMPLATE.format(
        run=result.testsRun, errors=_format_errors(result.errors),
        failures=_format_errors(result.failures), skipped=result.skipped)
    return (not (result.errors or result.failures), json_result)


def run_test(test_case, logger=logging.root, verbosity=None):
    logger.info(u"Running tests: '{}'".format(test_case.__name__))
    if verbosity is not None:
        output = TemporaryFile()
        status, result = _run_test(test_case, output, verbosity)
        output.seek(0)
        for line in output.read().splitlines():
            if status:
                logger.info(line)
            else:
                logger.error(line)
        output.close()
    else:
        status, result = _run_test(test_case, verbosity)
        if status:
            logger.info(result)
        else:
            logger.error(result)
    return (status, result)


class TestRunner(SimpleRule):
    """
    A rule that will run a test case when a switch item is turned on. The results of
    the test run are placed in a second string item.
    """

    def __init__(self, test_case, trigger_item_name, result_item_name):
        self.test_case = test_case
        self.trigger_item_name = trigger_item_name
        self.result_item_name = result_item_name
        self.triggers = [ItemStateUpdateTrigger(trigger_item_name, OnOffType.ON)]
        self.logger = logging.getLogger(type(self).__name__)

    def execute(self, module, inputs):
        try:
            events.postUpdate(self.trigger_item_name, str(OnOffType.OFF))
            events.postUpdate(self.result_item_name, None)
            result = _run_test(self.test_case)[1]
            events.postUpdate(self.result_item_name, result)
        except:
            import traceback
            self.logger.error(traceback.format_exc())
