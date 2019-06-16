"""
This script adds an ItemProvider, so that Items can be added and removed at
runtime.
"""

scriptExtension.importPreset(None)

import core
from core import osgi
from core.log import logging, LOG_PREFIX

provider_class = None

try:
    from org.openhab.core.items import ItemProvider
    provider_class = "org.openhab.core.items.ItemProvider"
except:
    from org.eclipse.smarthome.core.items import ItemProvider
    provider_class = "org.eclipse.smarthome.core.items.ItemProvider"

try:
    class JythonItemProvider(ItemProvider):
        def __init__(self):
            self.items_ = []
            self.listeners = []

        def addProviderChangeListener(self, listener):
            self.listeners.append(listener)

        def removeProviderChangeListener(self, listener):
            if listener in self.listeners:
                self.listeners.remove(listener)

        def add(self, item):
            self.items_.append(item)
            for listener in self.listeners:
                listener.added(self, item)

        def remove(self, item):
            if isinstance(item, str):
                for i in self.items_:
                    if i.name == item:
                        self.remove(i)
            elif item in self.items_:
                self.items_.remove(item)

            for listener in self.listeners:
                listener.removed(self, item)

        def update(self, item):
            for listener in self.listeners:
                listener.updated(self, item)

        def getAll(self):
            return self.items_

    core.JythonItemProvider = JythonItemProvider()
except:
    core.JythonItemProvider = None
    import traceback
    logging.getLogger(
        "{}.core.JythonItemProvider".format(LOG_PREFIX)).error(traceback.format_exc())


def scriptLoaded(id):
    if core.JythonItemProvider is not None:
        core.osgi.register_service(core.JythonItemProvider, [provider_class])
        logging.getLogger(
            "{}.core.JythonItemProvider.scriptLoaded".format(LOG_PREFIX)).debug("Registered service")


def scriptUnloaded():
    if core.JythonItemProvider is not None:
        core.osgi.unregister_service(core.JythonItemProvider)
        core.JythonItemProvider = None
        logging.getLogger(
            "{}.core.JythonItemProvider.scriptUnloaded".format(LOG_PREFIX)).debug("Unregistered service")
