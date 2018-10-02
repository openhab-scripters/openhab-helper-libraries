# NOTE: Requires JythonItemProvider component

from openhab import osgi, jsr223, JythonItemProvider
from org.eclipse.smarthome.core.library.items import StringItem
from org.eclipse.smarthome.core.items import Item, ItemProvider

__all__ = ["add", "remove"]

item_factory = osgi.get_service("org.eclipse.smarthome.core.items.ItemFactory")

def add(item, item_type=None):
    if isinstance(item, str):
        if item_type is None:
            raise Exception("Must provide item_type when creating an item by name")
        item = item_factory.createItem(item_type, item)
    JythonItemProvider.add(item)

def remove(item):
    JythonItemProvider.remove(item)

