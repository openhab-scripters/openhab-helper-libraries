from community.timer_mgr import TimerMgr
from time import sleep
from core.log import logging, LOG_PREFIX
log = logging.getLogger("{}.TEST.timer_mgr".format(LOG_PREFIX))

timers = TimerMgr()

timer_expired_called = False
timer_running_called = False

def timer_expired():
    global timer_expired_called
    timer_expired_called = True

def timer_running():
    global timer_running_called
    timer_running_called = True

try:
    test_name = "Test"

    # Test that timer get's created
    timers.check(test_name, 1000, timer_expired)
    sleep(0.5)
    assert timers.has_timer(test_name)
    assert not timer_expired_called

    # Test that timer_expired was called when the timer expired, 
    # timer_running_called is not called.
    sleep(0.51)
    assert not timers.has_timer(test_name)
    assert timer_expired_called
    assert not timer_running_called

    # Test for timer_running get's called if checked and timer exists
    timer_expired_called = False
    timer_running_called = False
    timers.check(test_name, 1000, timer_expired, timer_running)
    sleep(0.5)
    assert timers.has_timer(test_name)
    assert not timer_expired_called
    assert not timer_running_called
    timers.check(test_name, 1000, timer_expired, timer_running)
    assert not timers.has_timer(test_name)
    assert not timer_expired_called
    assert timer_running_called
    sleep(0.51)

    # Test timer get's rescheduled and timer_running and timer_expired get's 
    # called.
    timer_expired_called = False
    timer_running_called = False
    timers.check(test_name, 1000, timer_expired, timer_running, True)
    sleep(0.5)
    assert timers.has_timer(test_name)
    assert not timer_expired_called
    assert not timer_running_called
    timers.check(test_name, 1000, timer_expired, timer_running, True)
    sleep(0.5)
    assert timers.has_timer(test_name)
    assert not timer_expired_called
    assert timer_running_called
    sleep(0.51)
    assert not timers.has_timer(test_name)
    assert timer_expired_called
    assert timer_running_called

    # Test cancel_timer
    timer_expired_called = False
    timer_running_called = False
    timers.check(test_name, 1000, timer_running)
    sleep(0.5)
    assert timers.has_timer(test_name)
    timers.cancel(test_name)
    assert not timers.has_timer(test_name)
    sleep(0.51)
    assert not timer_expired_called
    assert not timer_running_called

    # Test cancel_timer on non-existant timer
    assert not timers.has_timer(test_name)
    timers.cancel(test_name)
    assert not timers.has_timer(test_name)

except AssertionError:
    import traceback
    log.error("Exception: {}".format(traceback.format_exc()))
else:
    log.info("TimerMgr tests passed!")