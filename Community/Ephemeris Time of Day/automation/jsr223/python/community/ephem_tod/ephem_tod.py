"""
Author: Rich Koshak

Implements the Time of Day Design Pattern using Ephemeris to determine the day
type so one can have a different set of times of day for different day types.

Requirements:
    - openHAB 2.5 M4 or later
    - Ephemeris configured

Limitations:
    - If using the Astro binding, the Rule that creates the Timers may be
      triggered more than once 30 seconds after midnight as Astro updates the
      Items. In testing this doesn't appear to cause any problems.
    - This script needs to be reloaded if Items are added or removed from
      tod_group_ephem or metadata changed on any of the Items this script
      needs to be reloaded.

License
=======
Copyright (c) contributors to the openHAB Scripters project
"""

from core.rules import rule
from core.triggers import when
from core.actions import Ephemeris, ScriptExecution
from core.metadata import get_key_value
from core.utils import send_command_if_different, post_update_if_different
from configuration import tod_group_ephem, tod_item_ephem
import threading
from org.joda.time import DateTime
from time import sleep

# Semiphore for keeping the Rule from triggering while the Items are being
# updated by the tod_update_items function.
updating = threading.BoundedSemaphore(1)

def tod_update_items(log):
    """
    Updates all descendents of tod_item_ephem if they posesses a ToD start_time
    metadata value and that start time string for today is different from the
    current state of the Item. This will thus update the Item's date to today if
    we have passed midnight.

    Arguments:
        - log: Logger passed in from the Rule that calls this function
    """
    # acquire a semiphore to keep these updates from executing the tod Rule
    if not updating.acquire(False):
        log.error("Failed to acquire the semiphore to initialize ToD Items!")
        return

    # loop through all the decendents of the group, for those with metadata
    # refresh the Item with the value in the metadata
    log.debug("Updating ToD Items from metadata")

    now = DateTime.now()
    items_initialized = False
    for start_time in ir.getItem(tod_group_ephem).allMembers:

        # Get the time string from the Item metadata
        time_str = get_key_value(start_time.name, "ToD", "start_time")

        # If there is a value, parse it and set the Item to that time for today
        if time_str:
            log.debug("Handling {}".format(start_time))
            time_parts = time_str.split(':')
            num_parts = len(time_parts)
            if num_parts < 2:
                log.error("{} is malformed metadata to initialize"
                          " {}".format(t, start_time.name))
            else:
                tod_t = now.withTime(int(time_parts[0]),
                                     int(time_parts[1]),
                                     int(time_parts[2]) if num_parts > 2 else 0,
                                     int(time_parts[3]) if num_parts > 3 else 0)
                if str(start_time.state) != str(tod_t):
                    if post_update_if_different(start_time, str(tod_t)):
                        log.debug("Updated {} to {}".format(start_time.name,
                                                            tod_t))
                        items_initialized = True

    # Sleep for a little bit if one or more Items were updated
    try:
        if items_initialized:
            sleep(0.3) # Give Items a chance to update
    except:
        log.warn("Interrupted while sleeping waiting for Items to finsih "
                 "updating! Hoping for the best.")

    finally:
        # release the semiphore
        updating.release()
        log.debug("Done updating ToD Items")

def get_start_times(log):
    def get_group(type, check, curr, is_day):
        """
        Checks to see if there is a Group defined for type and whether today is
        in that that type.

        Arguments:
            - type: the day type.
            - check: check to perform to see if a Group defines the start times
                     for the given type
            - curr: the currently selected Group of start times.
            - is_day: True if today is of type

        Returns:
            - The first found Group that has metadata that matches type if
              is_day is True.
            - curr if is_day is False or there is no Group found for type.
        """

        # skip if it's not this day type
        if not is_day:
            return curr

        # get the group of start times if one exists
        log.debug("Checking for {}:".format(type))
        grps = [grp for grp in tod_grps if check(grp, type)]
        rval = curr
        if len(grps) > 0:
            rval = grps[0]
        if len(grps) > 1:
            log.warn("There is more than one {} Group! Only using the"
                               " first one {}".format(type, rval.name))
        return rval

    def get_groups(type, check, curr, key, day_check):
        """
        Determines if today is defined in any of the custom daysets or custom
        holiday files.

        Arguments:
            - type: the day type
            - check: the test to find the Groups that represent the day type
                     from the list of members of tod_grps_ephem
            - curr: the current Group of start times selected
            - key: name of the key containing additional relevant information
                ("set" for custom daysets or "file" for custom bank holidays)
            - day_check: function to call to determine if today is in the dayset
                         or custom bank holidays file.

        Returns:
            - One of the Groups if today is in the defined dayset or holiday
            file. If there is more than one, it is not fixed which Group is
            returned.
            - curr if today is not a defined in the dayset or custom bank
              holiday file.
        """
        log.debug("Checking for {}:".format(type))
        rval = curr
        for grp in [grp for grp in tod_grps if check(grp, type)]:
            value = get_key_value(grp.name, "ToD", key)
            if value is None:
                log.error("Group {} doesn't have a key {}!"
                                    .format(grp.name, key))
            elif day_check(value):
                rval = curr
                log.debug("Today is in {}, it's a special day!".format(value))
        return rval

    tod_grps = ir.getItem(tod_group_ephem).members
    check = lambda grp, type: get_key_value(grp.name, "ToD", "type") == type
    start_times = None

    start_times = get_group("default",
                            lambda grp, type: check(grp, type) or not get_key_value(grp.name, "ToD", "type"),
                            start_times,
                            True)

    start_times = get_group("weekday", check, start_times,
                            not Ephemeris.isWeekend())

    start_times = get_group("weekend", check, start_times, Ephemeris.isWeekend())

    start_times = get_groups("dayset", check, start_times, "set",
                             lambda ds: Ephemeris.isInDayset(ds))

    holiday = Ephemeris.getBankHolidayName()
    start_times = get_group("holiday", check, start_times, holiday is not None)
    if holiday is not None:
        ephem_tod.log.debug("It's {}, time to celebrate!".format(holiday))

    start_times = get_groups("custom", check, start_times, "file",
                 lambda file: Ephemeris.isBankHoliday(0, file))

    ephem_tod.log.debug("Creating Time of Day timers using {}".format(start_times.name))
    return start_times

# Time of Day timers to that drive the time of day events.
tod_timers = {}

def clear_timers():
    """ Cancel all the existing time of day timers. """
    for name, timer in tod_timers.items():
        if timer is not None and not timer.hasTerminated():
            timer.cancel()
        del tod_timers[name]

def create_tod_timers(log, start_times):
    """
    Using the passed in Group, create Timers for each start time to command the
    tod_item_ephem to the new time of day state.

    Arguments:
        - log: logger from the Rule
        - start_times: Group with DateTime Items as it's members that indicate
          the start time of a time of day (state) and the name of the state
          defined in metadata.
    """

    now = DateTime.now()
    clear_timers()

    # Create timers for all the members of tod_group.
    most_recent_time = now.minusDays(1)
    most_recent_state = str(items[tod_item_ephem])
    for start_time in start_times.members:

        item_time = DateTime(str(start_time.state))
        trigger_time = now.withTime(item_time.getHourOfDay(),
                                    item_time.getMinuteOfHour(),
                                    item_time.getSecondOfMinute(),
                                    item_time.getMillisOfSecond())

        # Update the Item if it still has yesterday's date.
        if item_time.isBefore(trigger_time):
            events.postUpdate(start_time, str(trigger_time))

        state = get_key_value(start_time.name, "ToD", "tod_state")
        # If there is no state we can't use this Item.
        if state is None:
            log.error("{} does not have tod_state metadata!"
                      .format(start_time.name))

        # If we have already passed this time, keep track of the most recent
        # time and state.
        elif (trigger_time.isBefore(now)
                and trigger_time.isAfter(most_recent_time)):
            most_recent_time = trigger_time
            most_recent_state = state
            log.debug("The most recent state is now {}".format(state))

        # Create future timers
        elif trigger_time.isAfter(now):

            def tod_transition(state, log):
                """
                Called at a time of day transition, commands to the new time of
                day state.
                """
                log.info("Transitioning time of day from {} to {}."
                         .format(items[tod_item_ephem],state))
                events.sendCommand(tod_item_ephem, state)

            log.debug("Setting timer for Item {}, Time {}, and State {}"
                              ".".format(start_time.name, trigger_time, state))
            tod_timers[start_time.name] = ScriptExecution.createTimer(
                                            trigger_time,
                                            lambda s=state: tod_transition(s,
                                                                           log))

        else:
            log.debug("{} is in the past but there is a more recent "
                      "state".format(state))

    # Command the time of day to the current state
    log.info("Ephemeris time of day is now {}".format(most_recent_state))
    send_command_if_different(tod_item_ephem, most_recent_state)

@rule("Time of Day with Ephemeris",
      description=("Reusable Time of Day using Ephemeris to define different "
                   "times of day based on day type."),
      tags=["designpattern"])
@when("System started")
@when("Time cron 0 1 0 * * ? *")
@when("Descendent of {} changed".format(tod_group_ephem))
def ephem_tod(event):
    """
    Time of Day: A time based state machine which commands a state Item
    (tod_item_ephem in configuration.py) with the current time of day as a
    String.

    This Rule uses Ephemeris to determine the type of day (e.g. weekday) and
    selects the Group of start times for each time of day state based on the
    day type. See the Ephemeris documentation for details.

    To create the state machine, first create a Group and populate
    tod_group_ephem with that Group's name in configuration.py. Then create a
    Group for each type of day you have a different set of times of day. Add
    metadata to these Groups to identify what type of day those start times
    define.
    Supported types of days include:
        - default: this Group will be selected if no other type of day is
                   detected. Defined with the following metadata:
                       - Empty (i.e. no metadata)
                       - ToD="day"[type="default"]
        - weekday: this Group will be selected when Ephemeris.isWeekend()
                   returns False. Which days are defined as weekdays can be
                   configred in PaperUI. Defined with the following metadata:
                       - ToD="day"[type="weekday"]
        - weekend: this Group will be selected when Ephemeris.isWeekend()
                   returns True. Which days are defined as weekends can be
                   configured in PaperUI. Defined with the following metadata:
                       - ToD="day"[type="weekend"]
        - dayset: Ephemeris allows you to define custom daysets in
                  $OH_CONF/services/ephemeris.cfg. For example, if you have work
                  days that differ from your weekend/weekday schedule, you can
                  define a "workday" dayset. Defined with the following
                  metadata:
                      - ToD="day"[type="dayset", set="school"]
                  Use the name of the set as it is defined in ephemeris.cfg.
        - holiday: When Ephemeris is configured with country and region (and
                   city if used) in PaperUI, Ephemeris will automatically be
                   populated with the list of bank holidays (see the JollyDay
                   package on github). Defined with the following metadata:
                       - ToD="day"[type="holiday"]
        - custom: The Ephemeris capability allows one to define their own sets
                  of special days (e.g. birthdays and anniversaries) in a
                  specially formatted XML file. This allows you to define
                  additional bank holidays, an alternitive set of bank holidays
                  if the JollyDay list doesn't correspond with your actual
                  special days, or just define special days you want to treat
                  differently. Defined with the following metadata:
                      - ToD="day"[type="custom", file="/openhab/conf/services/custom1.xml"]

    For example, to define times of day that covers the weekend, weekdays, and
    a custom set of bank holidays you might have the following Groups.

        Group Ephem_TimeOfDay_StartTimes
        Group Ephem_Weekday (Ephem_TimeOfDay_StartTimes) { ToD="day"[type="weekday"] }
        Group Ephem_Weekend (Ephem_TimeOfDay_StartTimes) { ToD="day"[type="weekend"] }
        Group Ephem_Custom1 (Ephem_TimeOfDay_StartTimes) { ToD="day"[type="custom", file="/openhab/conf/services/custom1.xml"] }

    You must be sure to define a Group for every type of day about. It can be
    handy to define the default Group to ensure that happens. The day types are
    checked in the order listed above. So, for example, if you have all of the
    above types defined, on a day that is a work day (custom dataset) that is a
    custom holiday, the custom holiday Group will be chosen.

    You can define multiple Groups for dayset and custom. If you define more
    than one Group for any of the rest, only the first one found will be used.

    Now that you have the days defined, you must define a set of DateTime Items
    which hold the start times for each time of day state used on that day and
    add those Item to the given day's Group. For example, the start times for
    the weekend would be added to the Ephem_Weekend Group above.

    The values stored in the Items can come from anywhere but the two most
    common will be from Astro or statically defined. For Astro, just link the
    Item to the appropriate Astro Channel. For statically defined the time is
    defined and the Item initialized through metadata.

    The expected metadata is : Tod="init"[start_time="HH:MM:SS:MS", tod_state="EXAMPLE"]
    where
        - HH is hours
        - MM is minutes
        - SS is seconds and optional
        - MS is milliseconds and optional
        - EXAMPLE is the State String

    All members of tod_group are required to have a tod_state metadata entry.
    Only static Items require the start_time metadata entry.

    This Rule triggeres at system started, one minute after midnight, and if any
    member of tod_group_ephem changes. When the Rule triggers, it creates timers
    to go off at the indicated times.

    For example, they full set of Groups and Items for a weekend, weekday and
    standard bank holiday system might be something like the following:

        Group Ephem_TimeOfDay_StartTimes
        Group Ephem_Weekday (Ephem_TimeOfDay_StartTimes) { ToD="day"[type="weekday"] }
        Group Ephem_Weekend (Ephem_TimeOfDay_StartTimes) { ToD="day"[type="weekend"] }
        Group Ephem_Holiday (Ephem_TimeOfDay_StartTimes) { ToD="day"[type="holiday] }

        DateTime vMorning_Time "Morning [%1$tH:%1$tM]"
            <sunrise> (Ephem_Weekday)
            { ToD="init"[start_time="06:00",tod_state="MORNING"] }

        DateTime vDay_Time "Day1 [%1$tH:%1$tM]"
            <sun> (Ephem_Weekend, Ephem_Holiday)
            { channel="astro:sun:local:rise#start",
              ToD="init"[tod_state="DAY"] }

        DateTime vAfternoon_Time "Afternoon [ %1$tH:%1$tM]"
            <sunset> (Ephem_Weekday, Ephem_Weekend, Ephem_Holiday)
            { channel="astro:sun:set120:set#start",
              ToD="init"[tod_state="AFTERNOON"] }

        DateTime vEvening_Time "Evening [%1$tH:%1$tM]"
            <sunset> (Ephem_Weekday, Ephem_Weekend, Ephem_Holiday)
            { channel="astro:sun:local:set#start",
              ToD="init"[tod_state="EVENING"] }

        DateTime vNight_Time "Night [%1$tH:%1$tM]"
            <moon> (Ephem_Weekday)
            { ToD="init"[start_time="23:00", tod_state="NIGHT"] }

        DateTime vBed_Time "Bed [%1$tH:%1$tM]"
            <bedroom_blue> (Ephem_Weekend, Ephem_Holiday)
            { ToD="init"[start_time="00:02",tod_state="BED"] }

        DateTime vBed_Time_Weekend "Holiday Bed [%1$tH:%1$tM]"
            <bedroom_blue> (Ephem_Weekend, Ephem_Holiday)

    Take notice that one DateTime Item can be a member of more than one Group.
    Also take notice that each day has a different set of times of day defined.
    Finally notice that some of the times are static and others driven by Astro.
"""

    # Initialize ToD Items from their metadata. First check to see if this Rule
    # triggered because the Items are being updated by trying to actuire the
    # updating semiphore. If we succeed in grabbing the semiphore, make sure to
    # release it before calling the function to initiate the update.
    if not updating.acquire(False):
        ephem_tod.log.debug("Items are updating, ignoring rule trigger")
        return
    updating.release()
    tod_update_items(ephem_tod.log)

    # Determine the type of day and select the right Group of Items
    start_times = get_start_times(ephem_tod.log)
    if start_times is None:
        ephem_tod.log.error("No start times were found for today, please check "
                            "your Time of Day Items and Groups configurations.")
        return

    # Create the Timers
    create_tod_timers(ephem_tod.log, start_times)

def scriptUnloaded():
    """ Clears out all existing timers on script unload."""
    clear_timers()
