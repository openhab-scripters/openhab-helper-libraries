import time
from community.countdown_timer import CountdownTimer
from core.log import log_traceback, logging, LOG_PREFIX
from datetime import datetime, timedelta
log = logging.getLogger("{}.TEST.util".format(LOG_PREFIX))

func_called = False

def test():
    global func_called
    func_called = True

# Create a couple of Items to test with
from core.items import add_item
log.info("Creating test Items")
number = "Countdown_Timer_Test_Number"
string = "Countdown_Timer_Test_String"
add_item(number, item_type="Number")
add_item(string, item_type="String")

try:
    # Test that func_called on even seconds.
    log.info("--------------------------- seconds")
    timer = CountdownTimer(log, (datetime.now() + timedelta(seconds=2)), test, number)
    time.sleep(2.1)
    assert func_called

    # Test that func_called on fraction of seconds.
    log.info("--------------------------- milliseconds")
    func_called = False
    timer = CountdownTimer(log, (datetime.now() + timedelta(seconds=2, microseconds=100000)), test, number)
    time.sleep(2.2)
    assert func_called

    # Test that number gets updated properly
    log.info("--------------------------- number Item")
    log.info("number item is starting at {}".format(items[number]))
    assert items[number] == DecimalType(0)
    timer = CountdownTimer(log, (datetime.now() + timedelta(seconds=5)), test, number)
    time.sleep(0.1)
    log.info("number item is now {}".format(items[number]))
    assert items[number] == DecimalType(4)
    time.sleep(1)
    log.info("number item is now {}".format(items[number]))
    assert items[number] == DecimalType(3)
    time.sleep(1)
    log.info("number item is now {}".format(items[number]))
    assert items[number] == DecimalType(2)
    time.sleep(1)
    log.info("number item is now {}".format(items[number]))
    assert items[number] == DecimalType(1)
    time.sleep(1)
    log.info("number item is finally {}".format(items[number]))
    assert items[number] == DecimalType(0)

    # Test that string gets updated properly.
    log.info("--------------------------- string Item")
    log.info("string item is starting at {}".format(items[string]))
    timer = CountdownTimer(log, (datetime.now() + timedelta(seconds=5)), test, string)
    time.sleep(0.1)
    log.info("string item is now {}".format(items[string]))
    assert str(items[string]).startswith("0:00:04")

    time.sleep(1)
    log.info("string item is now {}".format(items[string]))
    assert str(items[string]).startswith("0:00:03")

    time.sleep(1)
    log.info("string item is now {}".format(items[string]))
    assert str(items[string]).startswith("0:00:02")

    time.sleep(1)
    log.info("string item is now {}".format(items[string]))
    assert str(items[string]).startswith("0:00:01")

    time.sleep(1)
    log.info("string item is finally {}".format(items[string]))
    assert str(items[string]) == "0:00:00"

    # Test that hasTerminated works
    log.info("--------------------------- hasTerminated()")
    timer = CountdownTimer(log, (datetime.now() + timedelta(seconds=2)), test, number)
    assert not timer.hasTerminated()
    time.sleep(2)
    assert timer.hasTerminated()

    # Test that cancel works.
    log.info("--------------------------- cancel()")
    timer = CountdownTimer(log, (datetime.now() + timedelta(seconds=2)), test, number)
    time.sleep(0.1)
    old_val = items[number]
    timer.cancel()
    time.sleep(2)
    assert items[number] == DecimalType(0)

except AssertionError:
    import traceback
    log.error("Exception: {}".format(traceback.format_exc()))
    timer.cancel()

else:
    log.info("CountdownTimer tests passed!")
finally:
    log.info("Deleting test Items")
    from core.items import remove_item
    remove_item(number)
    remove_item(string)
