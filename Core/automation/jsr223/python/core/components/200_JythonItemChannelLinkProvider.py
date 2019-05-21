scriptExtension.importPreset(None)

provider_class = None
try:
    from org.openhab.core.thing.link import ItemChannelLinkProvider
    provider_class = "org.openhab.core.thing.link.ItemChannelLinkProvider"
except:
    from org.eclipse.smarthome.core.thing.link import ItemChannelLinkProvider
    provider_class = "org.eclipse.smarthome.core.thing.link.ItemChannelLinkProvider"

import core
from core import osgi
from core.log import logging, LOG_PREFIX

try:
    class JythonItemChannelLinkProvider(ItemChannelLinkProvider):
        def __init__(self):
            self.listeners = []
            self.links = []


        def addProviderChangeListener(self, listener):
            self.listeners.append(listener)

        def removeProviderChangeListener(self, listener):
            if listener in self.listeners:
                self.listeners.remove(listener)

        def add(self, link):
            self.links.append(link)
            for listener in self.listeners:
                listener.added(self, link)

        def remove(self, link):
            if link in self.links:
                self.links.remove(link)
                for listener in self.listeners:
                    listener.removed(self, link)

        def update(self, link):
            for listener in self.listeners:
                listener.updated(self, link)

        def getAll(self):
            return self.links

    core.JythonItemChannelLinkProvider = JythonItemChannelLinkProvider()
except:
    core.JythonItemChannelLinkProvider = None
    import traceback
    logging.getLogger(LOG_PREFIX + ".core.JythonItemChannelLinkProvider").warn(traceback.format_exc())

def scriptLoaded(id):
    if core.JythonItemChannelLinkProvider is not None:
        core.osgi.register_service(core.JythonItemChannelLinkProvider, [provider_class])
        logging.getLogger(LOG_PREFIX + ".core.JythonItemChannelLinkProvider.scriptLoaded").debug("Registered service")

def scriptUnloaded():
    if core.JythonItemChannelLinkProvider is not None:
        core.osgi.unregister_service(core.JythonItemChannelLinkProvider)
        core.JythonItemChannelLinkProvider = None
        logging.getLogger(LOG_PREFIX + ".core.JythonItemChannelLinkProvider.scriptUnloaded").debug("Unregistered service")
