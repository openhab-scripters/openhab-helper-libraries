from openhab import osgi, jsr223
from org.eclipse.smarthome.core.library.items import StringItem
from org.eclipse.smarthome.core.items import Item, ItemProvider

class _ItemBridge(ItemProvider):
    def __init__(self, registry):
        self.registry = registry
        self.items = []
        
    def _refresh(self):
        self.registry.allItemsChanged(self, None)
        
    def add(self, item):
        self.items.append(item)
        self._refresh()
        
    def remove(self, item):
        if isinstance(item, str):
            for i in self.items:
                if i.name == item:
                    self.remove(i)
        else:
            self.items.remove(item)
        self._refresh()
        
    def getAll(self):
        return self.items

_item_registry = osgi.get_service("org.eclipse.smarthome.core.items.ItemRegistry")
_item_factory = osgi.get_service("org.eclipse.smarthome.core.items.ItemFactory")
_items = _ItemBridge(_item_registry)

def add(item, item_type=None):
    if isinstance(item, str):
        if item_type is None:
            raise Exception("Must provide item_type when creating an item by name")
        item = _item_factory.createItem(item_type, item)
    _items.add(item)

def remove(item):
    _items.remove(item)

