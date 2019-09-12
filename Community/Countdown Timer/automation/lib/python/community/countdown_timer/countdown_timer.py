"""
Author: Rich Koshak

Contains a class that implements a countdown timer. A countdown timer is one
that updates an Item every second with how much time is remaining on the timer.

Types:
======
    - CountdownTimer: A Class that wraps a Timer and updates the passed in Item
    with how much time is left on the Timer every second until the Timer
    expires.

License:
========
Copyright (c) 2019 Contributors to the openHAB Scripters project
"""
from core.actions import ScriptExecution
from core.date import to_joda_datetime, to_python_datetime
from datetime import datetime, timedelta
from core.jsr223.scope import ir, events
from org.eclipse.smarthome.core.library.items import NumberItem, StringItem
from org.joda.time import DateTime

class CountdownTimer(object):
    """
    Implements a Timer that updates an Item every second with the amount of time
    remaining until the Timer expires. The value reported to the Item is rounded
    to the nearsed second. Either a Number Item or a String Item can be used. If
    a Number Item is passed to the class the number of seconds left on the timer
    is reported. If a String Item is passed to the class, a String of the format
    [D day[s], ][H]H:MM:SS.

    Example Usage:
        .. code-block::
            # Pass in the logger, the datetime the Timer should go off, any
            # DateTime type supported by the core.date library functions are
            # allowed, the function to call, and the name of the Item to update
            # are passed Object. The Timer starts immediately.
            timer = CountdownTimer(log,
                                   (datetime.now() +
                                       timedelta(seconds=2,
                                       microseconds=100000)),
                                   func,
                                   number_item_name)

    Functions:
        - hasTerminated: Returns true when the Timer has expired, false
        otherwise.
        - cancel: Cancels the running Timer.
    """

    def __init__(self, log, time, func, count_item):
        """
        Initializes the CountdownTimer Object and starts the Timer running.

        Arguments:
            - log: The logger from the Rule that created the Timer.
            - time: The DateTime when the Timer should expire.
            - func: The function or lambda to call when the Timer expires.
            - count_item: The name of the Item to update with the amount of time
            until the Timer expires.
        """
        self.log = log
        self.func = func
        self.count_item = count_item
        self.ONE_SEC = timedelta(seconds=1)
        self.ZERO_SEC = timedelta()
        self.timer = None
        self.start = datetime.today()

        try:
            self.end_time = to_python_datetime(time)
        except TypeError:
            self.log.error("Time is not a recognized DateTime type")

        self.time_left = self.end_time - self.start
        self.__iterate__()

    def __update_item__(self):
        """
        Rounds the remaining time on the Timer to the nearest second and updates
        the Item based on the Item's type.
        """
        item = ir.getItem(self.count_item)
        if isinstance(item, NumberItem):
            events.postUpdate(self.count_item,
                              str(round(self.time_left.total_seconds())))
        else:
            rounded_secs = round(self.time_left.total_seconds())
            rounded = timedelta(seconds=rounded_secs)
            events.postUpdate(self.count_item, str(rounded))

    def __iterate__(self):
        """
        Implements the main loop for the Timer. This function is called every
        second until the Timer expires, updating the Item with the amount of
        time left on the Timer each time. When the time is up it sets the Item
        to 0 and calls the function.
        """
        self.log.debug("There is {} left on the timer"
                       .format(self.time_left))

        # Subtract a second from the time left.
        self.time_left = self.time_left - self.ONE_SEC

        # We have more time left, reschedule for a second into the future and
        # update the time_left Item.
        if self.time_left > self.ZERO_SEC:
            self.log.debug("Rescheduling the timer!")
            # Update the count Item.
            self.__update_item__()

            # Reschedule the Timer. If there is more than a second left,
            # reschedule for a second from now. If there is less than a second
            # this is the last iteration and schedule the Timer for the number
            # of milliseconds left.
            next_time = DateTime.now().plusSeconds(1)
            if self.time_left < self.ONE_SEC:
                next_time =  DateTime.now().plusMillis(
                    int(round(self.time_left.total_seconds() * 1000)))
            self.log.debug("Next timer will go off at {}".format(next_time))
            self.timer = ScriptExecution.createTimer(next_time,self.__iterate__)

        # Time's up, call the passed in function.
        else:
            self.log.debug("Time's up!")
            self.time_left = self.ZERO_SEC
            self.__update_item__()
            self.func()

    def hasTerminated(self):
        """
        Returns: True if the timer has expired and called the passed in
        function naturally. False otherise.
        """
        return self.timer.hasTerminated()

    def cancel(self):
        """ Cancels the Timer and resets the Item to 0. """
        self.time_left = self.ZERO_SEC
        self.__update_item__()
        return self.timer.cancel()
