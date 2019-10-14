"""
Author: Rich Koshak

Provides a class to implement the Gatekeeper Design Pattern. This
will implement a pause after calling a command lambda before the nest one can be
called.

Types
=====
    - Gatekeeper: Implements the Gatekeeper Design Pattering without blocking.

License
=======
Copyright (c) 2019 Contributors to the openHAB Scripters project
"""

from collections import deque
from core.actions import ScriptExecution
from org.joda.time import DateTime
from Queue import Queue

class Gatekeeper(object):
    """Keeps a queue of commands and makes sure that the commands to not get
    executed too quickly. Adding a command to the queue is non-blocking.

    Examples:
        .. code-block::

            gk = gatekeeper(logger)
            # Execute a command and wait 1 second before allowing the next.
            gk.add_command(1000, lambda: events.sendCommand("MyItem", "ON"))
            # Adds a command that will wait unti the previous command has
            # expired and then will block for 1 1/2 second.
            gk.add_command(1500, lambda: events.sendCommand("MyTTSItem", "Hello world")

    Functions:
        - add_command: Called to add a command to the queue to be executed when
        the time is right.
    """

    def __init__(self):
        """Initializes the queue and timer that drive the gatekeeper."""
        self.commands = Queue()
        self.timer = None

    def _proc_command(self):
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
            self._proc_command()
