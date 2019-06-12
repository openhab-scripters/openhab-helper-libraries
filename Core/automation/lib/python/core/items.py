"""
This module allows runtime creation and removal of items. It will also remove
any links from an Item before it is removed. This module requires the
JythonItemProvder and JythonItemChannelLinkProvider component scripts.
"""

from core.jsr223 import scope
scope.scriptExtension.importPreset(None)

import core
from core import osgi, JythonItemProvider
from core.log import logging, LOG_PREFIX
from core.links import remove_all_links

ItemBuilderFactory = osgi.get_service(
        "org.openhab.core.items.ItemBuilderFactory"
    ) or osgi.get_service(
        "org.eclipse.smarthome.core.items.ItemBuilderFactory"
    )

ManagedItemProvider = osgi.get_service(
        "org.openhab.core.items.ManagedItemProvider"
    ) or osgi.get_service(
        "org.eclipse.smarthome.core.items.ManagedItemProvider"
    )

log = logging.getLogger("{}.core.items".format(LOG_PREFIX))

__all__ = ["add_item", "remove_item"]

def add_item(item_or_item_name, item_type=None, category=None, groups=None, label=None, tags=[], gi_base_type=None, group_function=None):
    try:
        if not isinstance(item_or_item_name, basestring) and not hasattr(item_or_item_name, 'name'):
            raise Exception("\"{}\" is not a string or Item".format(item_or_item_name))
        item = item_or_item_name
        if isinstance(item_or_item_name, basestring):
            item_name = item_or_item_name
            if item_type is None:
                raise Exception("Must provide item_type when creating an Item by name")

            base_item = None if item_type != "Group" or gi_base_type is None else ItemBuilderFactory.newItemBuilder(gi_base_type, item_name + "_baseItem").build()
            group_function = None if item_type != "Group" else group_function
            item = ItemBuilderFactory.newItemBuilder(item_type, item_name)\
                                                    .withCategory(category)\
                                                    .withGroups(groups)\
                                                    .withLabel(label)\
                                                    .withBaseItem(base_item)\
                                                    .withGroupFunction(group_function)\
                                                    .withTags(set(tags))\
                                                    .build()

        JythonItemProvider.add(item)
        ManagedItemProvider.add(item)
        log.debug("Item added: [{}]".format(item))
    except:
        import traceback
        log.error(traceback.format_exc())
        return None
    else:
        return item

def remove_item(item_or_item_name):
    try:
        item = item_or_item_name
        if isinstance(item, basestring):
            if scope.itemRegistry.getItems(item) == []:
                raise Exception("\"{}\" is not in the ItemRegistry".format(item))
            else:
                item = scope.ir.getItem(item_or_item_name)
        elif not hasattr(item_or_item_name, 'name'):
            raise Exception("\"{}\" is not a string or Item".format(item_or_item_name))
        
        if scope.itemRegistry.getItems(item.name) == []:
            raise Exception("\"{}\" is not in the ItemRegistry".format(item.name))
        remove_all_links(item)
        JythonItemProvider.remove(item)
        ManagedItemProvider.remove(item.name)
        log.debug("Item removed: [{}]".format(item))
    except:
        import traceback
        log.error(traceback.format_exc())
