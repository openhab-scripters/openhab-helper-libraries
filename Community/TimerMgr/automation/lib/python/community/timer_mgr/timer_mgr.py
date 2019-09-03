"""
Author: Rich Koshak

Contains a class used to centralize the management of Timers in 
cases where one has one Timer per Item.

Types:
======
    - TimerMgr: Centralizes management of Timers associated with one single 
    Item (i.e. one Timer per Item).

License:
========
Copyright (c) 2019 Contributors to the openHAB Scripters project 
"""
from core.jsr223.scope import ir
from core.jsr223.scope import items
from core.actions import ScriptExecution
from org.joda.time import DateTime

class TimerMgr(object):
    """Keeps and manages a dictionary of Timers keyed on an Item name.

    Examples:
        .. code-block::
            flapping_timers = TimerMgr()
           
            # In a Rule, check to see if a Timer exists for this Item. If one 
            # exists, log a warning statement that the Item is flapping. 
            # Otherwise, set a half second timer and update the Time Item 
            # associated with the Item.
            flapping_timers.check(event.itemName,
                                  500,
                                  lambda: events.postUpdate("{}_Time".format(event.itemName), str(DateTime.now())),
                                  lambda: my_rule.log.warn("{} is flapping!".format(event.itemName),
                                  reschedule=True)

            reminder_timers = TimerMgr()

            
            # In a Rule, if the door is OPEN, create a timer to go off in 60 
            # minutes to post a message to the Alert Item. If it's NIGHT time, 
            # reschedule the Timer. If the door is CLOSED, cancel the reminder
            # Timer.
            if items[itemName == OPEN]:
                reminder_timers.check(itemName,
                                      60*60*1000,
                                      lambda: events.postUpdate("AlertItem", "{} has been open for an hour!".format(itemName)),
                                      reschedule=items["vTimeOfDay"] == StringType("NIGHT"))
            else:
                reminder_timers.cancel(itemName)

            # Check to see if a Timer exists for the Item.
            if reminder_timers.has_timer(itemName):
                my_rule.log.warn("There already is a timer for {}!".format(itemName))

    Functions:
        - check: Checks to see if there is already a Timer for the passed in
        Item, and reschedules it if desired and calls an optional function,
        otherwise it creates a Timer to call the passed in function.
        - has_timer: Returns True if there is an active Timer for the passed in
        Item.
        - cancel: Cancels the Timer assocaited with the passed in Item, if one 
        exists.
    """

    def __init__(self):
        """ Initialize the timers dict."""
        self.timers = {}

    def __not_flapping(self, itemName):
        """Called when the Timer expires. Call the function and delete the timer 
        from the dict. This function ensures that the dict get's cleaned up.

        Args:
            itemName: the name of the Item associated with the Timer
        """
        try:
            self.timers[itemName]['not_flapping']()
        finally:
            if itemName in self.timers: 
                del self.timers[itemName]

    def check(self, itemName, interval, function, flapping_function=None, 
                    reschedule=False):
        """Call to check whether an Item has a Timer. If no Timer exists, create 
        a new timer to run the passed in function. If a Timer exists, reschedule
        it if reschedule is True and if a flapping_function was passed, run it.

        Arguments:
            - itemName: The name of the Item we want to set a Timer on.
            - interval: How long from now to set the Timer to call function, in 
            milliseconds.
            - function: Function to call when the Timer expires
            - flapping_function: Optional function to call if the Item already 
            has a Timer running. Defaults to None.
            - reschedule: Optional flag that causes the Timer to be rescheduled
            when the Item already has a Timer. Defaults to False.
        """

        # Timer exists, reschedule and call flapping_lambda if necessary, else
        # cancel it. Then call the flapping function.
        timeout = DateTime.now().plusMillis(interval)
        if itemName in self.timers:
            if reschedule:
                self.timers[itemName]['timer'].reschedule(timeout)
            else:
                self.cancel(itemName)
            if flapping_function: flapping_function()

        # No timer exists, create the Timer
        else:
            item = ir.getItem(itemName)
            timer = ScriptExecution.createTimer(timeout, 
                        lambda: self.__not_flapping(itemName)) 
            self.timers[itemName] = { 'orig_state':   item.state,
                                      'timer':        timer,
                                      'flapping':     flapping_function,
                                      'not_flapping': function }

    def has_timer(self, itemName): 
        """Checks to see if a Timer exists for the passed in Item.

        Arguments:
            - itemName: Name of the Item to check if it has a Timer
        Returns: True if there is a Timer for that Item.
        """
        return itemName in self.timers

    def cancel(self, itemName):
        """Cancels the Timer assocaited with this Timer if one exists.

        Arguments:
            - itemName: Name of the Item to cancel the associated Timer.
        """
        if not self.has_timer(itemName): 
            return
        self.timers[itemName]['timer'].cancel() 
        del self.timers[itemName