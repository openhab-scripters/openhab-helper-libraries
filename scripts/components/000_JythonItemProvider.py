from org.eclipse.smarthome.core.items import ItemProvider

import openhab

class JythonItemProvider(ItemProvider):
    def __init__(self):
        self.listeners = []
        self.items = []
        
    def _refresh(self):
        for listener in self.listeners:
            listener.allItemsChanges(self, None)
        
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

    def addProviderChangeListener(self, listener):
        self.listeners.append(listener)

    def removeProviderChangeListener(self, listener):
        self.listeners.remove(listener)
        
def scriptLoaded(id):
    openhab.JythonItemProvider = JythonItemProvider()
    openhab.osgi.register_service(
        openhab.JythonItemProvider, 
        ["org.eclipse.smarthome.core.items.ItemProvider"])

def scriptUnloaded():
    openhab.osgi.unregister_service(openhab.JythonItemProvider)
    delattr(openhab, 'JythonItemProvider')

