"""
Provides automated Group decay timer Item and Rules. When all other Items in
the Group have changed to the same state as the decay Item is configured to
decay to, a timer will be started and the decay Item will be set at the end of
the timer period. Example usage is for presence sensor Groups where you want
the Group to stay ``ON`` for a period after all other Items in the Group have
changed to ``OFF``. Decay will only look at the immediate members of the Group
that has the metadata, it will not recurse into Groups. The Decay Item will be
created if it is not found in the Group.

configuration.py
================

* ``decay_item_prefix``: Prefix to add to decay Item name.
  *Must provide at least one of Item prefix or suffix.*
* ``decay_item_suffix``: Suffix to add to decay Item name.
* ``decay_group_prefix``: Prefix to strip from Group name.
* ``decay_group_suffix``: Suffix to strip from Group name.
* ``decay_reload_item``: Name of a switch Item that will trigger a scan of
  all items for Decay metadata, preserves running timers.

Group Metadata
==============

Decay metadata uses the same parsing as the Expire drop-in replacement script.
Credit to Rich Koschak for that, as the code is taken almost directly from it.

The state or command provided in the metadata will be compared to the states
of the other Items in the Group. When all other Items in the Group match this
state, the decay timer will be started. Items with state ``UNDEF`` or ``NULL``
are ignored.

* ``decay="5m,OFF"``
* ``decay="2m30s,command=OFF``

Example
=======

.. code-block:: Python

    # configuration.py
    decay_group_suffix = "_group"
    decay_item_suffix = "_decay"

.. code-block:: Java

    // example.items
    Group:Switch:OR(ON,OFF) example_group { decay="5m,OFF" }
        Switch example_switch (example_group)  // starting state is ON

The above configuration and Items will create an Item named
``example_decay`` in the Group ``example_group`` and set it to ``ON``. When
``example_switch`` is changed to ``OFF``, a timer is started for 5 minutes
from now that will change ``example_decay`` to ``OFF``.
"""

import re
from datetime import timedelta
from time import sleep
from org.joda.time import DateTime

import configuration
from core.rules import rule
from core.triggers import when
from core.metadata import get_value
from core.items import add_item
from core.actions import ScriptExecution
from core.log import logging, LOG_PREFIX, log_traceback
from core.jsr223.scope import scriptExtension
ruleRegistry = scriptExtension.get("ruleRegistry")

CONF_KEY_GROUP_PREFIX = "decay_group_prefix"
CONF_KEY_GROUP_SUFFIX = "decay_group_suffix"
CONF_KEY_ITEM_PREFIX = "decay_item_prefix"
CONF_KEY_ITEM_SUFFIX = "decay_item_suffix"

regex = re.compile(r'^((?P<days>[\.\d]+?)d)? *((?P<hours>[\.\d]+?)h)? *((?P<minutes>[\.\d]+?)m)? *((?P<seconds>[\.\d]+?)s)?$')
timers = { }



def parse_time(time_str, log):
    """
    Parse a time string e.g. (2h13m) into a timedelta object
    https://stackoverflow.com/questions/4628122/how-to-construct-a-timedelta-object-from-a-simple-string
    Arguments:
        - time_str: A string identifying a duration. Use
            - d: days
            - h: hours
            - m: minutes
            - s: seconds
          All options are optional but at least one needs to be supplied. Float
          values are allowed (e.g. "1.5d" is the same as "1d12h"). Spaces
          between each field is allowed. Examples:
              - 1h 30m 45s
              - 1h05s
              - 55h 59m 12s
    Returns:
        A ``datetime.timedelta`` object representing the supplied time duration
        or ``None`` if ``time_str`` cannot be parsed.
    """
    parts = regex.match(time_str)
    if parts is None:
        log.warn("Could not parse any time information from '{}'. Examples "
                  "of valid strings: '8h', '2d8h5m20s', '2m 4s'"
                   .format(time_str))
        return None
    else:
        time_params = {name: float(param) for name, param in parts.groupdict().items() if param}
        return timedelta(**time_params)


def get_config(group_name, log):
    """
    Parses the config string to extract the time duration, type of event, and
    the necessary state. The config string is stored in an "decay" metadata
    entry. The config takes format of
    ``decay="<duration>[,[command=|state=]<new state>]"``
        - <duration>: a time duration of the format described in parse_time.
        - [,]: if supplying more than just the duration, a comma is required
          here.
        - [command=|state=]: an optional definition of the type of of event to
          send to the decay Item when it expires. If not supplied it defaults to
          "state=".
        - [<new state>]: an optional state that the Item get's updated (state)
          or commanded (command) to when the time expires. Use '' to represent
          the empty String (differs from Expire1 Binding). Use 'UNDEF' or
          'NULL' to represent the String rather than the state.
    Examples (taken from the Expire1 Binding docs):
        - decay="1h,command=STOP" (send the STOP command after one hour)
        - decay="5m,state=0"      (update state to 0 after five minutes)
        - decay="3m12s,Hello"     (update state to Hello after three minutes
                                   and 12 seconds)
        - decay="2h"              (update state to UNDEF 2 hours after the last
                                   value)
    Unique to this implementation:
        - decay="5s,state=''"      (update a String Item to the empty String)
        - decay="5s,state=UNDEF"   (for String Items, expires to UNDEF, not the
                                    string, "UNDEF")
        - decay="5s,state='UNDEF'" (for String Items, expires to the String
                                    "UNDEF")
    """
    cfg = get_value(group_name, "decay")
    if cfg:
        cfg = cfg.split(",")
    else:
        return None

    time = parse_time(cfg[0], log)
    if not time:
        return None
    action = "state"

    # If config has a state len will be 2
    if len(cfg) > 1:
        state = cfg[1].split("=")

        # If config has an event type it will be 2
        if len(state) > 1:
            action = state[0].strip().lower()
            state = state[1]
        else:
            state = state[0]

        # Check for special types
        if state.strip() in ["NULL", "UNDEF"]:
            log.warn("Cannot use {state} as decay {action} for item {item}"
                     .format(state=state.strip(), action=action, item=group_name))
            return None

        # Remove single quotes from state.
        else:
            state = state.strip("'")

        # Force the state to a StringType for StringItems to allow us to set the
        # Item to "UNDEF" and "NULL" as opposed to the UnDefTypes.
        if ir.getItem(group_name).type == "String":
            if isinstance(state, basestring):
                state = StringType(state)
        # Strip whitespace for non String items
        elif isinstance(state, basestring):
            state = state.strip()

    # No state supplied, clear item state
    else:
        log.warn("No state or command provided for item {item}"
                 .format(item=group_name))
        return None

    if action not in ["state", "command"]:
        log.warn("Unrecognized action '{}' for item '{}'"
                 .format(action, group_name))
        return None

    return (time, action, state)


def get_decay_item_name(group_name, log):
    """
    Returns the name of the Decay Item for the Group given
    """
    group_prefix = getattr(configuration, CONF_KEY_GROUP_PREFIX, "")
    group_suffix = getattr(configuration, CONF_KEY_GROUP_SUFFIX, "")
    item_prefix = getattr(configuration, CONF_KEY_ITEM_PREFIX, "")
    item_suffix = getattr(configuration, CONF_KEY_ITEM_SUFFIX, "")
    item_name = ""

    if not item_prefix and not item_suffix:
        log.error("Must provide at least one of '{prefix}' or '{suffix}' in configuration.py"
                  .format(prefix=CONF_KEY_ITEM_PREFIX,
                          suffix=CONF_KEY_ITEM_SUFFIX))
        return ""
    else:
        item_name = "{}{}{}".format(
                item_prefix,
                group_name[len(group_prefix):len(group_name)-len(group_suffix)],
                item_suffix
            )
        return item_name


def get_decay_item(group_name, log):
    """
    Returns the Decay Item for the Group given
    """
    item_name = get_decay_item_name(group_name, log)
    if item_name in items:
        return ir.getItem(item_name)
    else:
        log.warn("Decay item '{}' does not exist".format(item_name))
        return None


def decay_timeout(item, action, state, log):
    """
    Called when a Decay timer fires, postUpdate or sendCommand to the
    configured state.
    Arguments:
        - item: The Decay item.
        - action: The action type, 'state' or 'command'.
        - state: The state to change to.
        - log: Logger from the decay rule.
    """
    log.info("{} decayed to {} '{}'".format(item.name, action, state))

    if action == "state":
        events.postUpdate(item, state)
    elif action == "command":
        events.sendCommand(item, state)
    else:
        log.warn("Unrecognized action '{}' for item '{}'"
                 .format(action, item.name))


def cancel_timer(group_name):
    """
    Cancels the timer for the group
    """
    if (timers[group_name] is not None
            and not timers[group_name].hasTerminated()):
        timers[group_name].cancel()


def decay(event):
    """
    Called when an Item in a Group configured for decay changes. If all Items
    in the Group now match the decay state, the timer will be started. If any
    of the Items differ from the decay state, the decay Item will be set to the
    same state as the Group.
    """
    # Get all decay configured Groups this Item is a member of
    group_names = [name for name in ir.getItem(event.itemName).groupNames if name in timers]
    if group_names:
        process_decay(group_names[0])
    else:
        decay.log.warn("No configured group found for decay item '{item}'"
                       .format(item=event.itemName))


def process_decay(group_name):
    """
    Called when an Item in a Group configured for decay changes. If all Items
    in the Group now match the decay state, the timer will be started. If any
    of the Items differ from the decay state, the decay Item will be set to the
    same state as the Group.
    """

    decay_options = get_config(group_name, decay.log)
    decay_item = get_decay_item(group_name, decay.log)
    if decay_options is None or not decay_item:
        decay.log.warn("Failed to process decay for Group '{group}'".format(group=group_name))
        return
    decay_time = decay_options[0]
    decay_action = decay_options[1]
    decay_state = decay_options[2]
    del decay_options

    # Check the states of all members except the decay Item
    active_state = False
    for item in [item for item in ir.getItem(group_name).members if item.name != decay_item.name]:
        if isinstance(item.state, UnDefType):
            decay.log.debug("Skipping '{item}' in group '{group}' because its state is '{state}'"
                            .format(item=item.name, group=group_name, state=item.state))
        elif unicode(item.state) != decay_state:
            active_state = True

    # Group is active, make sure decay Item is also active and timer is not running
    if active_state:
        cancel_timer(group_name)
        sleep(0.1)
        group_state = decay_state if isinstance(items[group_name], UnDefType) else items[group_name]
        if decay_item.state != items[group_name]:
            if decay_action == "state":
                events.postUpdate(decay_item, group_state)
            elif decay_action == "command":
                events.sendCommand(decay_item, group_state)
            else:
                decay.log.warn("Unrecognized action '{}' for item '{}'"
                               .format(decay_action, decay_item.name))
                return
            decay.log.debug("Group '{group}' is active, setting decay item to '{state}'"
                            .format(group=group_name, state=group_state))
    # Group is inactive, start timer if decay Item is still active
    elif unicode(decay_item.state) != decay_state:
        if timers[group_name] is None or timers[group_name].hasTerminated():
            decay.log.debug("Starting decay timer for '{}' with delay {}"
                            .format(group_name, decay_time))
            timers[group_name] = ScriptExecution.createTimer(
                DateTime.now().plusDays(decay_time.days)
                              .plusSeconds(decay_time.seconds)
                              .plusMillis(int(decay_time.microseconds/1000)),
                lambda: decay_timeout(
                                        decay_item,
                                        decay_action,
                                        decay_state,
                                        decay.log
                                    )
            )


def decay_load(event):
    """
    Called on script load and when decay_reload_item is commanded to ON.
    Scans the Item Registry for Groups with a valid decay config and adds an
    update trigger to the decay rule for the Group members. Timers will be
    dropped for Groups that no longer have a valid decay config.
    This load will not cancel any running timers for Groups that have a valid
    decay config.
    """
    log = logging.getLogger("{}.Decay Load".format(LOG_PREFIX))
    log.debug("Decay loading...")

    # Keep track of items configured this pass
    new_groups = []

    # Scan for items with valid expire config
    for group in ir.getItemsOfType("Group"):
        decay_options = get_config(group.name, log)
        decay_item_name = get_decay_item_name(group.name, log)
        # Skip if configuration is not valid or decay item name cannot be resolved
        if not decay_options or not decay_item_name:
            continue
        if group.baseItem is None:
            log.warn("Failed to configure group '{group}'. Decay only works for groups with base items."
                     .format(group=group.name))
            continue
        initial_state = decay_options[2] if isinstance(group.state, UnDefType) else group.state
        # Create decay Item if it does not exist
        if decay_item_name not in items:
            try:
                add_item(
                    decay_item_name,
                    item_type=group.baseItem.type,
                    label="{} Decay [%s]".format(group.label),
                    groups=[group.name]
                )
            except:
                log.error("An error occurred while trying to create decay item '{}'"
                                .format(decay_item_name))
                continue
            else:
                sleep(0.1)
                events.postUpdate(ir.getItem(decay_item_name), initial_state)
                log.info("Created decay item '{item}' for group '{group}' with initial state '{state}'"
                               .format(item=decay_item_name, group=group.name, state=initial_state))
        elif group.name not in ir.getItem(decay_item_name).groupNames:
            log.warn("Found decay item '{item}' for group '{group}' but it is not a member of the group"
                     .format(item=decay_item_name, group=group.name))
            continue
        elif isinstance(items[decay_item_name], UnDefType):
            log.info("Setting '{item}' to initial state '{state}'"
                     .format(item=decay_item_name, state=initial_state))

        new_groups.append(group.name)
        timers[group.name] = timers.get(group.name, None) # don't clobber
        log.debug("Decay configured for '{}' with timeout {} to {} '{}'"
                  .format(group.name, decay_options[0],
                  decay_options[1], decay_options[2]))

    # Remove existing rule
    if hasattr(decay, "UID"):
        ruleRegistry.remove(decay.UID)
        delattr(decay, "triggers")
        delattr(decay, "UID")

    # Generate triggers
    for group_name in new_groups:
        when("Member of {} changed".format(group_name))(decay)

    # Create decay rule
    if hasattr(decay, "triggers"):
        rule(
            "Decay",
            description=("Provides a Group activity decay timeout, commands or "
                         "updates a decay Item after all members of the group "
                         "become inactive"),
            tags=["decay"]
        )(decay)
        if hasattr(decay, "UID"):
            log.info("Decay loaded successfully")
        else:
            log.error("Failed to create Decay rule")
    else:
        log.info("Decay found no configured items")

    # Drop items that no longer exist or no longer have decay config
    for group_name in timers:
        if group_name not in new_groups:
            if group_name in items:
                log.debug("Removing item '{}' as it no longer has a valid decay config"
                          .format(group_name))
            else:
                log.debug("Removing item '{}' as it no longer exists"
                          .format(group_name))
            cancel_timer(group_name)
            timers.pop(group_name, None)

    # Process all groups to populate initial states
    for group_name in new_groups:
        process_decay(group_name)


@log_traceback
def scriptLoaded(*args):
    """
    Called at script load, sets up the reload rule.
    """
    log = logging.getLogger("{}.Decay Init".format(LOG_PREFIX))
    reload_item = getattr(configuration, "decay_reload_item", None)

    if reload_item is None:
        log.debug("Decay Reload rule not created, no 'decay_reload_item' "
                  "defined in 'configuration.py'")
    elif reload_item in items:
        when("Item {} received command ON".format(reload_item))(decay_load)
        rule(
            "Decay Reload",
            description=("Reloads the Decay script, adding groups that did not "
                         "have a valid decay config and removing items that have "
                         "been deleted or no longer have a valid decay config"),
            tags=["decay"]
        )(decay_load)
        if hasattr(decay_load, "UID"):
            log.info("Decay Reload rule created successfully")
        else:
            log.error("Failed to create Decay Reload rule")
    else:
        log.warn("Unable to create Decay Reload rule, item '{}' does not exist"
                 .format(reload_item))

    decay_load(None)


@log_traceback
def scriptUnloaded(*args):
    """
    Called at script unload, cancel all running timers.
    """
    for group_name in timers:
        cancel_timer(group_name)
