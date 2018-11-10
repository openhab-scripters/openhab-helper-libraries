# NOTE: Requires JythonItemProvider component

from org.slf4j import Logger, LoggerFactory

from openhab import osgi, jsr223, JythonItemProvider
from openhab.jsr223 import scope

__all__ = ["add", "remove"]


logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules.jsr232.openhab")

def add(item, item_type=None, category=None, groups=None, label=None, gi_base_type=None, group_function=None):
    try:
        if isinstance(item, basestring):
            if item_type is None:
                raise Exception("Must provide item_type when creating an item by name")

            baseItem = None if item_type != "Group" or gi_base_type is None else scope.itemRegistry.newItemBuilder( gi_base_type       \
                                                                                                                  , item + "_baseItem")\
                                                                                                   .build()
            group_function = None if item_type != "Group" else group_function
            item = scope.itemRegistry.newItemBuilder(item_type, item)  \
                                     .withCategory(category)           \
                                     .withGroups(groups)               \
                                     .withLabel(label)                 \
                                     .withBaseItem(baseItem)           \
                                     .withGroupFunction(group_function)\
                                     .build()
        JythonItemProvider.add(item)
    except:
        import traceback
        logger.error(traceback.format_exc())
        return None
    else:
        return item

def remove(item):
    JythonItemProvider.remove(item)
