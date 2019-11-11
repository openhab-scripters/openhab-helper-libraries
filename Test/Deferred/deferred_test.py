from community.deferred import deferred, cancel_all, cancel
from core.log import log_traceback, logging, LOG_PREFIX
from org.joda.time import DateTime
import time

log = logging.getLogger("{}.TEST.deferred".format(LOG_PREFIX))

# Create an Item to test with
from core.items import add_item
log.info("Creating test Item")
item = "Deferred_Test"
add_item(item, item_type="Switch")

try:
    events.postUpdate(item, "OFF")
    time.sleep(0.1)
    assert items[item] == OFF, "Item didn't initialize to OFF"

    # Schedule based on DT
    t = DateTime.now().plusSeconds(1)
    deferred(item, "ON", log, dt=t)
    time.sleep(1.1)
    assert items[item] == ON, "Item didn't go to ON after a second with specific time"

    # Schedule based on duration
    deferred(item, "OFF", log, delay="1s")
    time.sleep(1.1)
    assert items[item] == OFF, "Item didn't go to OFF after a second with duration"

    # Reschedule
    deferred(item, "ON", log, delay="1s")
    time.sleep(0.1)
    assert items[item] == OFF, "Item isn't still OFF after initial schedule"
    deferred(item, "ON", log, delay="2s")
    time.sleep(1)
    assert items[item] == OFF, "Timer didn't get rescheduled!"
    time.sleep(1.1)
    assert items[item] == ON, "Timer didn't reschedule on time!"

    # Cancel
    deferred(item, "OFF", log, delay="1s")
    assert items[item] == ON, "Item isn't still ON after last test"
    cancel(item)
    time.sleep(1.1)
    assert items[item] == ON, "Timer didn't cancel!"

    # Cancel All
    deferred(item, "OFF", log, delay="1s")
    cancel_all()
    time.sleep(1.1)
    assert items[item] == ON, "Timer didn't cancel all"


except AssertionError:
    import traceback
    log.error("Exception: {}".format(traceback.format_exc()))
else:
    log.info("Deferred tests passed!")
finally:
    log.info("Deleting test Item")
    from core.items import remove_item
    remove_item(item)
