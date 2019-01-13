# NOTE: Requires JythonItemProvider component
from core import osgi, jsr223, JythonItemProvider
from core.jsr223 import scope
from core.log import logging, LOG_PREFIX
from core.links import remove_all_links

log = logging.getLogger(LOG_PREFIX + ".core.items")

__all__ = ["add_item", "remove_item"]

def add_item(item, item_type=None, category=None, groups=None, label=None, tags=[], gi_base_type=None, group_function=None):
    try:
        if isinstance(item, basestring):
            if item_type is None:
                raise Exception("Must provide item_type when creating an item by name")

            itemBuilderFactory = osgi.get_service("org.eclipse.smarthome.core.items.ItemBuilderFactory")
            baseItem = None if item_type != "Group" or gi_base_type is None else itemBuilderFactory.newItemBuilder(gi_base_type, item + "_baseItem").build()
            group_function = None if item_type != "Group" else group_function
            item = itemBuilderFactory.newItemBuilder(item_type, item)   \
                                    .withCategory(category)             \
                                    .withGroups(groups)                 \
                                    .withLabel(label)                   \
                                    .withBaseItem(baseItem)             \
                                    .withGroupFunction(group_function)  \
                                    .withTags(set(tags))                \
                                    .build()

        JythonItemProvider.add(item)
        log.debug("Item added: [{}]".format(item))
    except:
        import traceback
        log.error(traceback.format_exc())
        return None
    else:
        return item

def remove_item(item):
    try:
        from org.eclipse.smarthome.core.items import GenericItem
        if isinstance(item, basestring):
            if scope.itemRegistry.getItems(item) == []:
                raise Exception("\"{}\" is not in the ItemRegistry".format(item))
            else:
                item = scope.ir.getItem(item)
        elif not isinstance(item, GenericItem):
            raise Exception("\"{}\" is not a string or Item".format(item))
        elif scope.itemRegistry.getItems(item.name) == []:
            raise Exception("\"{}\" is not in the ItemRegistry".format(item))
        remove_all_links(item)
        JythonItemProvider.remove(item)
        log.debug("Item removed: [{}]".format(item))
    except:
        import traceback
        log.error(traceback.format_exc())
