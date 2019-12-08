"""
Selector allows you to have a group of Sources that can be linked to
any of the Endpoints in the Endpoints group. This allows you to quickly
repurpose automation devices without having to edit your configuration.

- Command Sources are items that receive commands to be forwarded to Endpoints.
- Command Endpoints are items that receive commands from Command Sources.
- Update Sources are items that receive updates to be forwarded to Endpoints.
- Update Endpoints are items that receive updates from Update Sources.

Selector will automatically generate a sitemap that will display a list of
Command and Update Endpoints that allows you to select any Source to link to
any Endpoint. For Command Endpoints, once a Source is selected the Endpoint
will received the Source's current state as a command, then any commands sent
to the Source will be repeated to the Endpoint. For Update Endpoints, when a
Source is selected, the Endpoint will be updated with the Source's current
state, and any updates to the Source will be forwarded to the Endpoint.

I created this to simplify the repurposing of some Sonoff S31 outlets I got.
Using this I can quickly change what part of my automation they are linked to
without having to change any configuration or channel links.


configuration.py
================

- ``selector_command_sources_group``: Group of Command Source Items.
- ``selector_command_endpoints_group``: Group of Command Endpoint Items.
- ``selector_update_sources_group``: Group of Update Source Items.
- ``selector_update_endpoints_group``: Group of Update Endpoint Items.
- ``selector_links_group``: Group to add newly created Link Items to.
- ``selector_links_additional_groups``: List of additional groups to add Link
  Items to. *Ex.* restore on startup persistence group.
- ``selector_links_format``: String to use to compose Link Item names. Must
  have keys ``{action}`` and ``{item_name}`` somewhere in it.
  *Ex.* ``selector_link_{action}_{item_name}``.
- ``selector_update_cron``: Cron expression used to create a trigger for the
  Selector update rule that checks for new Source and Endpoint Items.
  *Ex.* ``22 */30 * * * ?`` for updating every 30min at 22sec past the
  minute mark.
- ``selector_update_item``: Name of an Item to watch for ``ON`` commands that
  will cause Selector to check for new Source and Endpoint Items.
- ``selector_link_icon_none``: Icon name for Link items not currently linked.
  *Default* ``none``.
- ``selector_link_icon_good``: Icon name for Link items that are linked.
  *Default* ``switch-on``.
- ``selector_link_icon_error``: Icon name for Link items that have a Source
  selected but the Source Item no longer exists.
  *Default* ``error``.


Example
=======

.. code-block:: python

    # configuration.py
    selector_command_sources_group = "selector_command_sources_group"
    selector_command_endpoints_group = "selector_command_endpoints_group"
    selector_update_sources_group = "selector_update_sources_group"
    selector_update_endpoints_group = "selector_update_endpoints_group"
    selector_links_group = "selector_links_group"
    selector_links_additional_groups = ["persist_restore"]
    selector_links_format = "selector_link_{action}_{item_name}"
    selector_update_cron = "22 */30 * * * ?"
    selector_update_item = "selector_update"

.. code-block:: java

    // selector.items
    Group selector_group "Selector"
        Switch selector_update "Update Selector" (selector_group) { autoupdate="false" }
        Group selector_command_sources_group "Selector Command Sources" (selector_group)
        Group selector_command_endpoints_group "Selector Command Endpoints" (selector_group)
        Group selector_update_sources_group "Selector Update Sources" (selector_group)
        Group selector_update_endpoints_group "Selector Update Endpoints" (selector_group)
        Group selector_links_group "Selector Link Items" (selector_group)

    // connect this item to your device channel
    Switch device_channel (selector_command_endpoints_group, selector_update_sources_group) { autoupdate="false" }

    // have your automation control this item
    Switch proxy_item (selector_command_sources_group, selector_update_endpoints_group) { selector="Custom Label", autoupdate="false" }

Selector will then create 2 Link Items named ``selector_link_command_device_channel``
and ``selector_link_update_proxy_item`` and put them in the Selector sitemap.
In the sitemap, select each Source Item from the selection menu for each Link.
Now any commands received by ``proxy_item`` will be passed to ``device_channel``
and any updates received by ``device_channel`` will be passed to ``proxy_item``.


Copyright (c) contributors to the openHAB Scripters project
"""

import os
from java.lang import System

from core.rules import rule
from core.triggers import when
from core.items import add_item
from core.metadata import get_value
from core.utils import sendCommand, postUpdate
from core.log import logging, LOG_PREFIX, log_traceback
ruleRegistry = scriptExtension.get("ruleRegistry")


SELECTOR_SOURCES = "sources"
SELECTOR_ENDPOINTS = "endpoints"
SELECTOR_TYPES = [SELECTOR_SOURCES, SELECTOR_ENDPOINTS]
SELECTOR_COMMAND = "command"
SELECTOR_UPDATE = "update"
SELECTOR_ACTIONS = [SELECTOR_COMMAND, SELECTOR_UPDATE]
SELECTOR_LINKS = "links"
SELECTOR_LINKS_GROUPS = "link groups"
SELECTOR_ACTION_FUNCS = {
    SELECTOR_COMMAND: sendCommand,
    SELECTOR_UPDATE: postUpdate
}


groups = {
    SELECTOR_SOURCES: {
        SELECTOR_COMMAND: None,
        SELECTOR_UPDATE: None
    },
    SELECTOR_ENDPOINTS: {
        SELECTOR_COMMAND: None,
        SELECTOR_UPDATE: None
    },
    SELECTOR_LINKS: None,
    SELECTOR_LINKS_GROUPS: []
}

members = {
    SELECTOR_SOURCES: {
        SELECTOR_COMMAND: {},
        SELECTOR_UPDATE: {}
    },
    SELECTOR_ENDPOINTS: {
        SELECTOR_COMMAND: {},
        SELECTOR_UPDATE: {}
    }
}

link_name_format = None
update_cron_expr = None
update_item_name = None
link_icon_none = None
link_icon_good = None
link_icon_error = None



def load_config(log):
    """
    Loads group names from configuration.py
    """
    config_good = True
    import configuration
    reload(configuration)
    import configuration

    # get source and endpoint groups
    for type_key in SELECTOR_TYPES:
        for action_key in SELECTOR_ACTIONS:
            value = getattr(configuration, "selector_{}_{}_group".format(action_key, type_key), None)
            if not value:
                log.error("Missing 'selector_{}_{}_group' in configuration.py".format(action_key, type_key))
                config_good = False
            elif value not in items:
                log.error("{} {} group '{}' does not exist".format(action_key.capitalize(), type_key.capitalize(), value))
                config_good = False
            else:
                groups[type_key][action_key] = value

    # get groups to put links in
    value = getattr(configuration, "selector_links_group", None)
    if not value:
        log.error("Missing 'selector_links_group' in configuration.py")
        config_good = False
    elif value not in items:
        log.error("Links group '{}' does not exist".format(value))
        config_good = False
    else:
        groups[SELECTOR_LINKS] = value

    # get additional groups to put links in
    value = getattr(configuration, "selector_links_additional_groups", None)
    if isinstance(value, str):
        value = [value]
    if value:
        for group_name in [name for name in value]:
            if group_name not in items:
                log.warn("Links additional group '{}' does not exist".format(value))
                value.remove(group_name)
        if groups[SELECTOR_LINKS]:
            value.append(groups[SELECTOR_LINKS])
            groups[SELECTOR_LINKS_GROUPS] = value
    elif groups[SELECTOR_LINKS]:
        groups[SELECTOR_LINKS_GROUPS] = [groups[SELECTOR_LINKS]]
    else:
        groups[SELECTOR_LINKS_GROUPS] = []

    # get update vectors
    global update_cron_expr, update_item_name
    update_cron_expr = getattr(configuration, "selector_update_cron", None)
    update_item_name = getattr(configuration, "selector_update_item", None)
    if update_item_name and update_item_name not in items:
        log.warn("Update item '{}' does not exist, no update rule will be generated".format(
            update_item_name))
        update_item_name = None

    # get link item name format string and link status icons
    global link_name_format, link_icon_none, link_icon_good, link_icon_error
    link_name_format = getattr(configuration, "selector_links_format", "selector_link_{}")
    link_icon_none = getattr(configuration, "selector_link_icon_none", "none")
    link_icon_good = getattr(configuration, "selector_link_icon_good", "switch-on")
    link_icon_error = getattr(configuration, "selector_link_icon_error", "error")

    return config_good


def scan_group(type_key, action_key, log):
    """
    Scans the passed group for new or removed members and updates the local
    list of item names.
    Returns ``True`` if any items were added or removed.
    """
    log.debug("Scanning {} {} group for new or removed items".format(action_key.capitalize(), type_key.capitalize()))
    dirty = False
    group_members = [item.name for item in ir.getItem(groups[type_key][action_key]).members if item.type != "Group"]
    members_list = members[type_key][action_key]

    for item_name in [name for name in group_members if name not in members_list]:
        dirty = True
        members_list[item_name] = members_list.get(item_name, [])
        log.debug("Added '{}' to {} {}".format(item_name, action_key.capitalize(), type_key.capitalize()))

    for item_name in [name for name in members_list if name not in group_members]:
        dirty = True
        members_list.pop(item_name, None)
        log.debug("Removed '{}' from {} {}".format(item_name, action_key.capitalize(), type_key.capitalize()))

    return dirty


def generate_rule(target, triggers, rule_name, rule_desc, log):
    """
    Generates a rule and removes any existing ones beforehand
    """
    # pre-generate trigger decorators
    triggers = [when(trigger) for trigger in triggers]
    if not triggers:
        log.debug("Rule '{}' not created, no triggers".format(rule_name))
        return

    # Remove existing rule
    if hasattr(target, "UID"):
        #rules.remove(target.UID) NOT WORKING
        ruleRegistry.remove(target.UID)
        delattr(target, "UID")
        delattr(target, "triggers")

    # attach triggers to rule function
    for trigger in triggers:
        trigger(target)

    # Create rule
    if hasattr(target, "triggers"):
        rule(
            rule_name,
            description=rule_desc,
            tags=["selector"]
        )(target)
        if hasattr(target, "UID"):
            log.debug("Rule '{}' created successfully".format(rule_name))
        else:
            log.error("Failed to create rule '{}'".format(rule_name))
    else:
        log.debug("Rule '{}' not created, no triggers".format(rule_name))


def update_link_items(log):
    """
    Adds link items as needed and updates icons
    """
    log.debug("Updating link items")

    for action_key in SELECTOR_ACTIONS:
        # make sure all endpoints have link items
        for endpoint_item_name in members[SELECTOR_ENDPOINTS][action_key]:
            link_item_name = link_name_format.format(
                action=action_key, item_name=endpoint_item_name)
            if link_item_name not in items:
                add_item(
                    item_or_item_name=link_item_name,
                    item_type="String",
                    category=link_icon_none,
                    groups=groups[SELECTOR_LINKS_GROUPS],
                    label=get_value(endpoint_item_name, "selector") or ir.getItem(endpoint_item_name).label
                )
                postUpdate(link_item_name, "none")
                log.debug("Created Link item '{}'".format(link_item_name))
            else:
                ir.getItem(link_item_name).setLabel(
                    get_value(endpoint_item_name, "selector") or ir.getItem(endpoint_item_name).label
                )

        # clear all cached source links
        members_list = members[SELECTOR_SOURCES][action_key]
        for source_item_name in members_list:
            members_list[source_item_name] = []

    for link_item_name in [item.name for item in ir.getItem(groups[SELECTOR_LINKS]).members]:
        if str(items[link_item_name]) == "none":
            ir.getItem(link_item_name).setCategory(link_icon_none)  # set icon
        else:
            source_item_name = str(items[link_item_name])
            if source_item_name in items:
                members[SELECTOR_SOURCES][link_item_name.split("_")[2]][source_item_name].append("_".join(link_item_name.split("_")[3:]))
                ir.getItem(link_item_name).setCategory(link_icon_good)  # set icon
            elif "_".join(link_item_name.split("_")[3:]) in members[SELECTOR_ENDPOINTS][link_item_name.split("_")[2]]:
                log.warn("{} Endpoint item '{}' is linked to non-existant Source item '{}'".format(
                    link_item_name.split("_")[2].capitalize(),
                    "_".join(link_item_name.split("_")[3:]),
                    source_item_name
                ))
                ir.getItem(link_item_name).setCategory(link_icon_error)  # set icon


def generate_sitemap(log):
    """
    Generates the Selector sitemap
    """
    def get_mappings(item_name):
        mappings = ['"none"="None"']
        endpoint_item = ir.getItem(item_name)
        for source_name in sorted(members[SELECTOR_SOURCES][action_key], key=lambda name: get_value(name, "selector") or ir.getItem(name).label):
            source_item = ir.getItem(source_name)
            compat = False
            if source_item.type == endpoint_item.type:
                compat = True # same item types are compatible
            elif action_key == SELECTOR_UPDATE:
                if source_item.acceptedDataTypes[0] in endpoint_item.acceptedDataTypes:
                    compat = True # source preferred state accepted by endpoint
            elif action_key == SELECTOR_COMMAND:
                compat = True
                for command_type in source_item.acceptedCommandTypes:
                    if command_type not in endpoint_item.acceptedCommandTypes:
                        compat = False # skip if source can accept a command that endpoint cannot

            if compat:
                mappings.append('"{}"="{}"'.format(
                    source_item.name,
                    get_value(source_name, "selector") or source_item.label
                ))
        return "[{}]".format(", ".join(mappings))

    log.debug("Updating Selector sitemap")
    sitemap_data = 'sitemap selector label="Selector" {\n'

    if update_item_name:
        sitemap_data += '    Switch item={} mappings=[ON="Update Selector"]\n'.format(update_item_name)

    for action_key in SELECTOR_ACTIONS:
        members_list = sorted(members[SELECTOR_ENDPOINTS][action_key], key=lambda name: get_value(name, "selector") or ir.getItem(name).label)
        if members_list:
            sitemap_data += '    Group item={} label="{} Endpoint Links" {{\n'.format(groups[SELECTOR_ENDPOINTS][action_key], action_key.capitalize())
            sitemap_data += '        Text icon=none label="Endpoint [Source]"\n'
            for endpoint_item_name in members_list:
                link_item_name = link_name_format.format(
                    action=action_key, item_name=endpoint_item_name)
                sitemap_data += '        Selection item={} mappings={}\n'.format(
                    link_item_name, get_mappings(endpoint_item_name))
            sitemap_data += '    }\n'

    sitemap_data += '}'

    sitemap_path = System.getProperties().get("openhab.conf", None)
    if not sitemap_path:
        log.error("Failed to generate sitemap: unable to get openHAB conf path from JVM")
    else:
        sitemap_path = os.path.join(sitemap_path, "sitemaps", "selector.sitemap")
        sitemap_fd = open(sitemap_path, "w")
        sitemap_fd.write(sitemap_data)
        sitemap_fd.close()
        log.debug("Successfully wrote Selector sitemap")


def update(event):
    """
    Updates the Selector rules, links, and sitemap
    """
    log = logging.getLogger("{}.Selector".format(LOG_PREFIX))
    log.debug("Updating Selector")

    # cache update vectors
    old_update_cron_expr = update_cron_expr
    old_update_item_name = update_item_name

    # reload config values
    if not load_config(log):
        return

    # compare update vectors
    update_vector_dirty = False
    if update_cron_expr != old_update_cron_expr:
        update_vector_dirty = True
    if update_item_name != old_update_item_name:
        update_vector_dirty = True
    del old_update_cron_expr, old_update_item_name

    # scan command groups, regenerate rule if there are any changes
    command_dirty = False
    for type_key in SELECTOR_TYPES:
        command_dirty |= scan_group(type_key, SELECTOR_COMMAND, log)
    if command_dirty:
        generate_rule(
            rule_command_source_command,
            ["Item {} received command".format(name) for name in members[SELECTOR_SOURCES][SELECTOR_COMMAND]],
            "Selector Command Source",
            "**AUTOMATICALLY GENERATED RULE** "
            "This rule is triggered when any Selector Command Source item receives a command",
            log
        )

    # scan update groups, regenerate rule if there are any changes
    update_dirty = False
    for type_key in SELECTOR_TYPES:
        update_dirty |= scan_group(type_key, SELECTOR_UPDATE, log)
    if update_dirty:
        generate_rule(
            rule_update_source_update,
            ["Item {} received update".format(name) for name in members[SELECTOR_SOURCES][SELECTOR_UPDATE]],
            "Selector Update Source",
            "**AUTOMATICALLY GENERATED RULE** "
            "This rule is triggered when any Selector Update Source item receives an update",
            log
        )

    # regenerate endpoint changed rule
    update_link_items(log)
    if command_dirty or update_dirty:
        generate_rule(
            rule_endpoint_link_changed,
            ["Item {} changed".format(item.name) for item in ir.getItem(groups[SELECTOR_LINKS]).members],
            "Selector Endpoint Link",
            "**AUTOMATICALLY GENERATED RULE** "
            "This rule is triggered when any Endpoint Link is changed",
            log
        )

        # regenerate sitemap
        generate_sitemap(log)

    # regenerate update rule
    if update_vector_dirty:
        trigs = []
        if update_cron_expr:
            trigs.append("Time cron {}".format(update_cron_expr))
        if update_item_name:
            trigs.append("Item {} received command ON".format(update_item_name))
        generate_rule(
            update,
            trigs,
            "Selector Update",
            "**AUTOMATICALLY GENERATED RULE** "
            "This rule is generated for the update switch item and cron expression if specified",
            log
        )

    if command_dirty or update_dirty or update_vector_dirty:
        log.info("Selector updated successfully")


def rule_command_source_command(event):
    """
    Dynamically generated rule triggered by any Command Source item receiving
    a command.
    """
    log = rule_command_source_command.log
    for endpoint_item_name in members[SELECTOR_SOURCES][SELECTOR_COMMAND][event.itemName]:
        log.debug("Forwarding command '{}' from source '{}' to endpoint '{}'".format(
            event.itemCommand, event.itemName, endpoint_item_name))
        sendCommand(endpoint_item_name, event.itemCommand)


def rule_update_source_update(event):
    """
    Dynamically generated rule triggered by any Update Source item receiving
    an update.
    """
    log = rule_update_source_update.log
    for endpoint_item_name in members[SELECTOR_SOURCES][SELECTOR_UPDATE][event.itemName]:
        if not isinstance(event.itemState, UnDefType):
            log.debug("Forwarding update '{}' from source '{}' to endpoint '{}'".format(
                event.itemState, event.itemName, endpoint_item_name))
            postUpdate(endpoint_item_name, event.itemState)


def rule_endpoint_link_changed(event):
    """
    Dynamically generated rule triggered by any Link item being changed.
    """
    log = rule_endpoint_link_changed.log
    link_item_name = event.itemName
    action_key = link_item_name.split("_")[2]
    endpoint_item_name = "_".join(link_item_name.split("_")[3:])

    if str(event.itemState) == "none":
        try:
            members[SELECTOR_SOURCES][action_key][str(event.oldItemState)].remove(endpoint_item_name)
        except ValueError:
            pass
        ir.getItem(link_item_name).setCategory(link_icon_none)  # set icon
    else:
        source_item_name = str(event.itemState)
        if source_item_name in items:
            members[SELECTOR_SOURCES][action_key][source_item_name].append(endpoint_item_name)
            ir.getItem(link_item_name).setCategory(link_icon_good)  # set icon
            # forward current Source state to Endpoint
            if not isinstance(items[source_item_name], UnDefType):
                SELECTOR_ACTION_FUNCS[action_key](endpoint_item_name, items[source_item_name])
                log.debug("Forwarding {} '{}' from source '{}' to endpoint '{}'".format(
                    action_key, items[source_item_name], source_item_name, endpoint_item_name))
        elif endpoint_item_name in members[SELECTOR_ENDPOINTS][action_key]:
            log.warn("{} Endpoint item '{}' is linked to non-existant Source item '{}'".format(
                action_key.capitalize(),
                endpoint_item_name,
                source_item_name
            ))
            ir.getItem(link_item_name).setCategory(link_icon_error)  # set icon


@log_traceback
def scriptLoaded(*args):
    """
    Runs at script load to initialize
    """
    logging.getLogger("{}.Selector".format(LOG_PREFIX)).info("Selector Loading")
    update(None)
