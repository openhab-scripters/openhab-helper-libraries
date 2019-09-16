from personal.latch import Latch
import time
from core.log import logging, LOG_PREFIX

log = logging.getLogger("{}.TEST.Latch".format(LOG_PREFIX))
func_called = False

def test():
    global func_called
    func_called = True

try:
    latch = Latch()

    latch.run(test, secs=2)
    assert func_called

    func_called = False
    latch.run(test, secs=2)
    assert not func_called

    time.sleep(2)
    latch.run(test, secs=2)
    assert func_called

except AssertionError:
    import traceback
    log.error("Exception: {}".format(traceback.format_exc()))
else:
    log.info("Latch tests passed!")
