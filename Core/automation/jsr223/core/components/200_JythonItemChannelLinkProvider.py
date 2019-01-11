from org.eclipse.smarthome.core.thing.link import ItemChannelLinkProvider

import core
import core.osgi

class JythonItemChannelLinkProvider(ItemChannelLinkProvider):
    def __init__(self):
        self.listeners = []
        self.links = []

    def add(self, link):
        self.links.append(link)
        for listener in self.listeners:
            listener.added(self, link)

    def remove(self, link):
        if link in self.links:
            self.links.remove(link)
            for listener in self.listeners:
                listener.removed(self, link)

    def getAll(self):
        return self.links

    def update(self, link):
        for listener in self.listeners:
            listener.updated(self, link)

    def addProviderChangeListener(self, listener):
        self.listeners.append(listener)

    def removeProviderChangeListener(self, listener):
        if listener in self.listeners:
            self.listeners.remove(listener)

core.JythonItemChannelLinkProvider = JythonItemChannelLinkProvider()

def scriptLoaded(id):
    core.osgi.register_service(
        core.JythonItemChannelLinkProvider, 
        ["org.eclipse.smarthome.core.thing.link.ItemChannelLinkProvider"])
    
def scriptUnloaded():
    core.osgi.unregister_service(core.JythonItemChannelLinkProvider)
    delattr(core, 'JythonItemChannelLinkProvider')
