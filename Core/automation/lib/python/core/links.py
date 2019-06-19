"""
This module allows runtime creation and removal of links. This module requires
the JythonItemChannelLinkProvider component script.
"""

from core.jsr223 import scope
scope.scriptExtension.importPreset(None)

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

__all__ = ["add_link", "remove_link"]

def add_link(item_or_item_name, channel_uid_or_string):# returns Link
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
