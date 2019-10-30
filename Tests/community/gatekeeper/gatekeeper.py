# Testing code is below.
from time import sleep, time
from core.log import logging, LOG_PREFIX
from community.gatekeeper import Gatekeeper

log = logging.getLogger("{}.TEST.gatekeeper".format(LOG_PREFIX))

gk = Gatekeeper(log)

test1 = None
test2 = None
test3 = None
test4 = None

def test1_func():
    global test1
    test1 = time()
def test2_func():
    global test2
    test2 = time()
def test3_func():
    global test3
    test3 = time()
def test4_func():
    global test4
    test4 = time()
try:
    start = time()
    gk.add_command(1000, test1_func)
    gk.add_command(2000, test2_func)
    gk.add_command(3000, test3_func)
    gk.add_command(500, test4_func)

    sleep(6.5)
    assert start < test1
    assert test1+1.0 <= test2 < test1+1.1
    assert test2+2.0 <= test3 < test2+2.1
    assert test3+3.0 <= test4 < test3+3.1

    # Test cancel_all
    test1 = None
    test2 = None
    test3 = None
    test4 = None

    gk.add_command(1000, test1_func)
    gk.add_command(2000, test2_func)
    gk.add_command(3000, test3_func)
    gk.add_command(4000, test4_func)

    sleep(2.5)
    assert test1 is not None, "Test1 didn't run!"
    assert test2 is not None, "Test2 didn't run!"
    assert test3 is None, "Test3 ran instead of being cancelled!"
    assert test4 is None, "Test4 ran instead of being cancelled!"

except AssertionError:
    import traceback
    log.error("Exception: {}".format(traceback.format_exc()))
else:
    log.info("Gatekeeper tests passed!")
