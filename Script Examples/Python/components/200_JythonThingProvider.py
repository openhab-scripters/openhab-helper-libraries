"""
This script adds a ThingProvider.
"""
scriptExtension.importPreset(None)# fix for compatibility with Jython > 2.7.0

import core
from core.osgi import register_service, unregister_service
from core.log import logging, LOG_PREFIX

PROVIDER_CLASS = None

try:
    from org.openhab.core.thing import ThingProvider
    PROVIDER_CLASS = "org.openhab.core.thing.ThingProvider"
except:
    from org.eclipse.smarthome.core.thing import ThingProvider
    PROVIDER_CLASS = "org.eclipse.smarthome.core.thing.ThingProvider"

try:
    class JythonThingProvider(ThingProvider):

        def __init__(self):
            self.things = []
            self.listeners = []

        def addProviderChangeListener(self, listener):
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

def scriptLoaded(script):
    if core.JythonThingProvider is not None:
        register_service(core.JythonThingProvider, [PROVIDER_CLASS])
        logging.getLogger("{}.core.JythonThingProvider.scriptLoaded".format(LOG_PREFIX)).debug("Registered service")

def scriptUnloaded():
    if core.JythonThingProvider is not None:
        unregister_service(core.JythonThingProvider)
        core.JythonThingProvider = None
        logging.getLogger("{}.core.JythonThingProvider.scriptUnloaded".format(LOG_PREFIX)).debug("Unregistered service")
