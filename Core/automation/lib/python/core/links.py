# NOTE: Requires JythonItemChannelLinkProvider component
from core.jsr223 import scope
scope.scriptExtension.importPreset(None)

import core
from core import osgi, JythonItemChannelLinkProvider
from core.log import logging, LOG_PREFIX

try:
    from org.openhab.core.thing import ChannelUID
    from org.openhab.core.thing.link import ItemChannelLink
except:
    from org.eclipse.smarthome.core.thing import ChannelUID
    from org.eclipse.smarthome.core.thing.link import ItemChannelLink

ItemChannelLinkRegistry = osgi.get_service(
        "org.openhab.core.thing.link.ItemChannelLinkRegistry"
    ) or osgi.get_service(
        "org.eclipse.smarthome.core.thing.link.ItemChannelLinkRegistry"
    )

log = logging.getLogger(LOG_PREFIX + ".core.links")

__all__ = ["add_link", "remove_link"]

def validate_item(item_or_item_name):# returns string
    if not isinstance(item_or_item_name, basestring) and not hasattr(item_or_item_name, 'name'):
        raise Exception("\"{}\" is not a string or Item".format(item_or_item_name))
    item_name = item_or_item_name if isinstance(item_or_item_name, basestring) else item_or_item_name.name
    if scope.itemRegistry.getItems(item_name) == []:
        raise Exception("\"{}\" is not in the ItemRegistry".format(item_name))
    return item_name

def validate_channel_uid(channel_uid):# returns ChannelUID
    if isinstance(channel_uid, basestring):
        channel_uid = ChannelUID(channel_uid)
    elif not isinstance(channel_uid, ChannelUID):
        raise Exception("\"{}\" is not a string or ChannelUID".format(channel_uid))
    if scope.things.getChannel(channel_uid) is None:
        raise Exception("\"{}\" is not a valid Channel".format(channel_uid))
    return channel_uid

def add_link(item_or_item_name, channel_uid):# returns Link
    try:
        link = ItemChannelLink(validate_item(item_or_item_name), validate_channel_uid(channel_uid))
        JythonItemChannelLinkProvider.add(link)
        log.debug("Link added: [{}]".format(link))
    except:
        import traceback
        log.error(traceback.format_exc())
        return None
    else:
        return link

def remove_link(item_or_item_name, channel_uid):
    try:
        link = ItemChannelLink(validate_item(item_or_item_name), validate_channel_uid(channel_uid))
        JythonItemChannelLinkProvider.remove(link)
        log.debug("Link removed: [{}]".format(link))
    except:
        import traceback
        log.error(traceback.format_exc())

def remove_all_links(item_or_item_name):
    try:
        item_name = validate_item(item_or_item_name)
        channels = ItemChannelLinkRegistry.getBoundChannels(item_name)
        links = map(lambda channel: ItemChannelLink(item_name, channel), channels)
        for link in links:
            JythonItemChannelLinkProvider.remove(link)
            log.debug("Link removed: [{}]".format(link))
    except:
        import traceback
        log.error(traceback.format_exc())
