"""
This script adds a ThingProvider.
"""

scriptExtension.importPreset(None)

provider_class = None
try:
    from org.openhab.core.thing import ThingProvider
    provider_class = "org.openhab.core.thing.ThingProvider"
except:
    from org.eclipse.smarthome.core.thing import ThingProvider
    provider_class = "org.eclipse.smarthome.core.thing.ThingProvider"

import core
from core import osgi
from core.log import logging, LOG_PREFIX

try:
    class JythonThingProvider(ThingProvider):
        def __init__(self):
            self.things = []
            self.listeners = []

        def addProviderChangeListener(self, listener): # ProviderChangeListener
            self.listeners.append(listener)

        def removeProviderChangeListener(self, listener):
            if listener in self.listeners:
                self.listeners.remove(listener)

        def add(self, thing):
            self.things.append(thing)
            for listener in self.listeners:
                listener.added(self, thing)

        def remove(self, thing):
            if thing in self.things:
                self.things.remove(thing)
                for listener in self.listeners:
                    listener.removed(self, thing)

        def update(self, thing):
            for listener in self.listeners:
                listener.updated(self, thing)

        def getAll(self):
            return self.things

    core.JythonThingProvider = JythonThingProvider()
except:
    core.JythonThingProvider = None
    import traceback
    logging.getLogger("{}.core.JythonThingProvider".format(LOG_PREFIX)).error(traceback.format_exc())

def scriptLoaded(id):
    if core.JythonThingProvider is not None:
        core.osgi.register_service(core.JythonThingProvider, [provider_class])
        logging.getLogger("{}.core.JythonThingProvider.scriptLoaded".format(LOG_PREFIX)).debug("Registered service")

def scriptUnloaded():
    if core.JythonThingProvider is not None:
        core.osgi.unregister_service(core.JythonThingProvider)
        core.JythonThingProvider = None
        logging.getLogger("{}.core.JythonThingProvider.scriptUnloaded".format(LOG_PREFIX)).debug("Unregistered service")
