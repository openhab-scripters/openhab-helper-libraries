# NOTE: Requires JythonItemProvider component

from core import osgi, jsr223, JythonItemProvider
from core.jsr223 import scope
from core.log import logging, LOG_PREFIX

log = logging.getLogger(LOG_PREFIX + ".items")

__all__ = ["add", "remove"]

def add(item, item_type=None, category=None, groups=None, label=None, gi_base_type=None, group_function=None):
    try:
        if isinstance(item, basestring):
            if item_type is None:
                raise Exception("Must provide item_type when creating an item by name")

            itemBuilderFactory = osgi.get_service("org.eclipse.smarthome.core.items.ItemBuilderFactory")
            baseItem = None if item_type != "Group" or gi_base_type is None else itemBuilderFactory.newItemBuilder( gi_base_type       \
                                                                                                                  , item + "_baseItem")\
                                                                                                   .build()
            group_function = None if item_type != "Group" else group_function
            item = itemBuilderFactory.newItemBuilder(item_type, item)  \
                                     .withCategory(category)           \
                                     .withGroups(groups)               \
                                     .withLabel(label)                 \
                                     .withBaseItem(baseItem)           \
                                     .withGroupFunction(group_function)\
                                     .build()
        JythonItemProvider.add(item)
    except:
        import traceback
        log.error(traceback.format_exc())
        return None
    else:
        return item

def remove(item):
    JythonItemProvider.remove(item)
