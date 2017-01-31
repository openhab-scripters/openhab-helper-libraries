from org.eclipse.smarthome.core.items import ItemProvider

import openhab

class JythonItemProvider(ItemProvider):
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

item_registry = openhab.osgi.get_service("org.eclipse.smarthome.core.items.ItemRegistry")
openhab.JythonItemProvider = JythonItemProvider(item_registry)

def scriptLoaded(id):
    #openhab.osgi.register_service(
    #    openhab.JythonItemProvider, 
    #    ["org.eclipse.smarthome.core.items.ItemProvider"])
    pass

def scriptUnloaded():
    #openhab.osgi.unregister_service(openhab.JythonItemProvider)
    delattr(openhab, 'JythonItemProvider')

