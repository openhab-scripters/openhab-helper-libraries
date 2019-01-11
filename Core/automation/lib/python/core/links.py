# NOTE: Requires JythonItemChannelLinkProvider component
from core import osgi, jsr223, JythonItemChannelLinkProvider
from core.jsr223 import scope
from core.log import logging, LOG_PREFIX

log = logging.getLogger(LOG_PREFIX + ".core.links")

__all__ = ["add_link", "remove_link"]

def validate_item(item):
    if hasattr(item, 'name') and scope.itemRegistry.getItems(item.name):
        item = item.name
    elif not (isinstance(item, basestring) and scope.itemRegistry.getItems(item)):
        raise Exception("The 'item' argument must be a string or an existing Item")
    return item

def validate_channel_uid(channel_uid):
    from org.eclipse.smarthome.core.thing import ChannelUID
    if isinstance(channel_uid, basestring) and scope.things.getChannel(ChannelUID(channel_uid)) is not None:
        channel_uid = ChannelUID(channel_uid)
    elif not (isinstance(channel_uid, ChannelUID) and scope.things.getChannel(channel_uid) is not None):
        raise Exception("The 'channel_uid' argument must be a string or an existing ChannelUID")
    return channel_uid

def add_link(item, channel_uid):
    try:
        item = validate_item(item)
        channel_uid = validate_channel_uid(channel_uid)
        from org.eclipse.smarthome.core.thing.link import ItemChannelLink
        link = ItemChannelLink(item, channel_uid)
        JythonItemChannelLinkProvider.add(link)
        log.debug("Link added: [{}]".format(link))
    except:
        import traceback
        log.error(traceback.format_exc())
        return None
    else:
        return link

def remove_link(item, channel_uid):
    try:
        item = validate_item(item)
        channel_uid = validate_channel_uid(channel_uid)
        from org.eclipse.smarthome.core.thing.link import ItemChannelLink
        link = ItemChannelLink(item, channel_uid)
        JythonItemChannelLinkProvider.remove(link)
        log.debug("Link removed: [{}]".format(link))
    except:
        import traceback
        log.error(traceback.format_exc())

def remove_all_links(item):
    try:
        item = validate_item(item)
        ItemChannelLinkRegistry = osgi.get_service("org.eclipse.smarthome.core.thing.link.ItemChannelLinkRegistry")
        channels = ItemChannelLinkRegistry.getBoundChannels(item)
        from org.eclipse.smarthome.core.thing.link import ItemChannelLink
        links = map(lambda channel: ItemChannelLink(item, channel), channels)
        for link in links:
            JythonItemChannelLinkProvider.remove(link)
            log.debug("Link removed: [{}]".format(link))
    except:
        import traceback
        log.error(traceback.format_exc())