# pylint: disable=wildcard-import
"""
The ``area_triggers_and_actions`` package provides a mechanism for using group
logic to trigger rules and then perform a particular action.

This package provides the following modules:

* ``area_actions``
"""
__all__ = ['start_action']

from threading import Timer

from core.jsr223.scope import ON, OFF, OPEN, CLOSED
from core.metadata import get_key_value
from core.log import logging, LOG_PREFIX, log_traceback

from community.area_triggers_and_actions.area_actions import light_action, toggle_action

try:
    import sys
    import personal.area_triggers_and_actions.area_actions
    reload(sys.modules['personal.area_triggers_and_actions.area_actions'])
    from personal.area_triggers_and_actions.area_actions import *
except:
    pass

#from org.joda.time import DateTime

LOG = logging.getLogger(u"{}.community.area_triggers_and_actions".format(LOG_PREFIX))

timers = {}
iterations = {}


@log_traceback
def _timer_function(item, active, function_name, timer_type, timer_delay, recurring, function):
    """
    This is the function called by the timers.

    Args:
        item Item: The Item to perform the action on
        active bool: Area activity (True for active and False for inactive)
        function_name str: Name of the action function
        timer_type str: Type of the timer
        timer_delay float: Time to delay the timer
        recurring bool: Whether to repeatedly reschedule the timer after it expires
        function function: The action function
    """
    #LOG.warn(u"_timer_function: item.name: '{}', active: '{}', function_name: '{}', timer_type: '{}', timer_delay: '{}', recurring: '{}', function: '{}'".format(item.name, str(active), function_name, timer_type, timer_delay, str(recurring), function))
    function(item, active)
    if recurring:
        if iterations.get(item.name) is None:
            timers.update({item.name: {function_name: {timer_type: Timer(timer_delay, _timer_function, [item, active, function_name, timer_type, timer_delay, recurring, function])}}})
            timers[item.name][function_name][timer_type].start()
            LOG.debug(u"{}: '{}' second recurring {} {} timer has started".format(item.name, timer_delay, function_name, timer_type))
        elif iterations[item.name][timer_type] > 0:
            iterations[item.name][timer_type] -= 1
            timers.update({item.name: {function_name: {timer_type: Timer(timer_delay, _timer_function, [item, False if active else True, function_name, timer_type, timer_delay, recurring, function])}}})
            timers[item.name][function_name][timer_type].start()
            LOG.debug(u"{}: '{}' iterations of {} have started".format(item.name, iterations[item.name][timer_type] + 1, function_name))
        else:
            iterations[item.name][timer_type] = 0


def _cancel_timer(item_name, function_name, timer_type):
    """
    This function cancels a timer.

    Args:
        item Item: The Item to perform the action on
        function_name str: Name of the action function
        timer_type str: Type of the timer
    """
    #LOG.warn(u"_cancel_timer:  item_name: '{}', function_name: '{}', timer_type: '{}'".format(item_name, function_name, timer_type))
    if timers.get(item_name, {}).get(function_name, {}).get(timer_type) is not None and timers[item_name][function_name][timer_type].isAlive():# if timer exists, stop it
        timers[item_name][function_name][timer_type].cancel()
        if iterations.get(item_name) is not None:
            iterations[item_name][timer_type] = 0
        LOG.debug(u"{}: {} {} timer has been cancelled".format(item_name, function_name, timer_type))


def start_action(item, active, function_name):
    """
    This is the function called by the rule to begin the selected action,
    which may be first passed through a timer.

    Args:
        item Item: The Item to perform the action on
        active bool: Area activity (True for active and False for inactive)
        function_name str: Name of the action function
    """
    #start_time = DateTime.now().getMillis()
    timer_type = "active" if active else "inactive"
    function = globals()[function_name]
    function_metadata = get_key_value(item.name, "area_triggers_and_actions", function_name)
    limited = function_metadata.get("limited")
    timer_metadata = function_metadata.get(timer_type, {})
    if timer_metadata or not limited:# this works since the states are binary
        timer_delay = timer_metadata.get("delay")
        if not timer_delay:
            function(item, active)
        elif timers.get(item.name, {}).get(function_name, {}).get(timer_type) is None or not timers[item.name][function_name][timer_type].isAlive():# if timer does not exist, create it
            recurring = timer_metadata.get("recurring")
            item_iterations = timer_metadata.get("iterations")
            if item_iterations is not None and item_iterations > 0:
                iterations.update({item.name: {timer_type: item_iterations}})
            timers.update({item.name: {function_name: {timer_type: Timer(timer_delay, _timer_function, [item, active, function_name, timer_type, timer_delay, recurring, function])}}})
            timers[item.name][function_name][timer_type].start()
            LOG.debug(u"{}: '{}' second {}{} {} timer has started{}".format(item.name, timer_delay, "recurring " if recurring else "", function_name, timer_type, ", repeating {} times".format(item_iterations) if item_iterations else ""))
    _cancel_timer(item.name, function_name, "inactive" if active else "active")
