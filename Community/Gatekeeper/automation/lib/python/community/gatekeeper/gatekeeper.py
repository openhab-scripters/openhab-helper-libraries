"""
License
========
Copyright (c) 2019 Richard Koshak
This program and accomanying materials are made available under the terms of 
the Eclipse Public License 2.0 which is available at 
http://www.eclipse.org/legal/epl-2.0
"""
from collections import deque
from core.actions import ScriptExecution
from org.joda.time import DateTime
from core.log import log_traceback
from Queue import Queue

class Gatekeeper(object):
    """Keeps a queue of commands and makes sure that the commands to not get 
    executed too quickly. Adding a command to the queue is non-blocking.

    Usage:
        gk = gatekeeper(logger)
        # Execute a command and wait 1 second before allowing the next.
        gk.add_command(1000, lambda: events.sendCommand("MyItem", "ON"))

    Functions:
        - add_command: Called to add a command to the queue to be executed when
        the time is right.
    """

    @log_traceback
    def __init__(self):
        """Initializes the queue and timer that drive the gatekeeper."""
        self.commands = Queue()
        self.timer = None

    @log_traceback
    def __proc_command__(self):
        """
        Called when it is time to execute another command. This function 
        simply returns if the queue is empty. Otherwise it pops the next 
        command, executes that command, and then sets a Timer to go off the 
        given number of milliseconds and call _proc_command__ again to process 
        the next command.
        """
        # No more commands
        if self.commands.empty(): 
            self.timer = None
            return

        # Pop the next command and run it
        cmd = self.commands.get()
        funct = cmd[1]
        before = DateTime.now().millis
        funct()
        after = DateTime.now().millis

        # Calculate how long to sleep
        delta = after - before
        pause = cmd[0]
        delay = pause - delta
        trigger_time = DateTime.now().plusMillis(delay if delay > 0 else 0)

        # Create/reschedule the Timer
        if not self.timer:
            self.timer = ScriptExecution.createTimer(trigger_time, 
                                                     self.__proc_command__)
        else:
            self.timer.reschedule(trigger_time)

    @log_traceback
    def add_command(self, pause, command):
        """
        Adds a new command to the queue. If it has been long enough since the 
        last command executed immediately execute this command. If not it waits
        until enough time has passed. The time required to execute command is
        included in the amount of time to wait. For example, if the command 
        takes 250 msec and the pause is 1000 msec, the next command will be
        allowed to execute 750 msec after the command returns.

        Args:
            - pause: Time in milliseconds to wait until the next command will be
            allowed to execute.
            - command: Lambda or function to call to execute the command.
        """
        self.commands.put((pause, command))
        if self.timer is None or self.timer.hasTerminated():
            self.__proc_command__()

# Testing code is below.
from time import sleep, time
from core.log import logging, LOG_PREFIX
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
except AssertionError:
    import traceback
    log.error("Exception: {}".format(traceback.format_exc()))
else:
    log.info("Gatekeeper tests passed!")