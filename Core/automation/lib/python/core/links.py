"""
This module allows runtime creation and removal of links.
"""
__all__ = ["add_link", "remove_link"]

from core.jsr223.scope import scriptExtension
scriptExtension.importPreset(None)

try:
    from org.openhab.core.thing.link import ItemChannelLink
except:
    from org.eclipse.smarthome.core.thing.link import ItemChannelLink

import core
from core import osgi
from core.log import logging, LOG_PREFIX
from core.utils import validate_item, validate_channel_uid

ItemChannelLinkRegistry = osgi.get_service(
        "org.openhab.core.thing.link.ItemChannelLinkRegistry"
    ) or osgi.get_service(
        "org.eclipse.smarthome.core.thing.link.ItemChannelLinkRegistry"
    )

ManagedItemChannelLinkProvider = osgi.get_service(
        "org.openhab.core.thing.link.ManagedItemChannelLinkProvider"
    ) or osgi.get_service(
        "org.eclipse.smarthome.core.thing.link.ManagedItemChannelLinkProvider"
    )

log = logging.getLogger("{}.core.links".format(LOG_PREFIX))

def add_link(item_or_item_name, channel_uid_or_string):
    """
    This function adds a Link to an Item using a
    ManagedItemChannelLinkProvider.

    Args:
        item_or_item_name (Item or str): the Item object or name to create
            the Link for
        channel_uid_or_string (ChannelUID or str): the ChannelUID or string
            representation of a ChannelUID to link the Item to

    Returns:
        Item or None: the Item that the Link was added to or None
    """
    try:
        item = validate_item(item_or_item_name)
        channel_uid = validate_channel_uid(channel_uid_or_string)
        if item is None or channel_uid is None:
            return None

        link = ItemChannelLink(item.name, channel_uid)
        ManagedItemChannelLinkProvider.add(link)
        log.debug("Link added: [{}]".format(link))
        return item
    except:
        import traceback
        log.error(traceback.format_exc())
        return None

def remove_link(item_or_item_name, channel_uid_or_string):
    """
    This function removes a Link from an Item using a
    ManagedItemChannelLinkProvider.

    Args:
        item_or_item_name (Item or str): the Item object or name to create
            the Link for
        channel_uid_or_string (ChannelUID or str): the ChannelUID or string
            representation of a ChannelUID to link the Item to

    Returns:
        Item or None: the Item that the Link was removed from or None
    """
    try:
        item = validate_item(item_or_item_name)
        channel_uid = validate_channel_uid(channel_uid_or_string)
        if item is None or channel_uid is None:
            return None

        link = ItemChannelLink(item.name, channel_uid)
        ManagedItemChannelLinkProvider.remove(str(link))
        log.debug("Link removed: [{}]".format(link))
        return item
    except:
        import traceback
        log.error(traceback.format_exc())
        return None

def remove_all_links(item_or_item_name):
    """
    This function removes all Links from an Item using a
    ManagedItemChannelLinkProvider.

    Args:
        item_or_item_name (Item or str): the Item object or name to create
            the Link for

    Returns:
        Item or None: the Item that the Links were removed from or None
    """
    try:
        item = validate_item(item_or_item_name)
        if item is None:
            return None

        channels = ItemChannelLinkRegistry.getBoundChannels(item.name)
        links = map(lambda channel: ItemChannelLink(item.name, channel), channels)
        for link in links:
            ManagedItemChannelLinkProvider.remove(str(link))
            log.debug("Link removed: [{}]".format(link))
        return item
    except:
        import traceback
        log.error(traceback.format_exc())
        return None
