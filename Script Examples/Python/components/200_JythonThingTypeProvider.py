"""
This script adds a ThingTypeProvider.
"""
scriptExtension.importPreset(None)# fix for compatibility with Jython > 2.7.0

import core
from core.osgi import register_service, unregister_service
from core.log import logging, LOG_PREFIX

PROVIDER_CLASS = None

try:
    from org.openhab.core.thing.binding import ThingTypeProvider
    PROVIDER_CLASS = "org.openhab.core.thing.binding.ThingTypeProvider"
except:
    from org.eclipse.smarthome.core.thing.binding import ThingTypeProvider
    PROVIDER_CLASS = "org.eclipse.smarthome.core.thing.binding.ThingTypeProvider"

try:
    class JythonThingTypeProvider(ThingTypeProvider):

        def __init__(self):
            self.thing_types = []

        def getThingTypes(self, locale):
            return self.thing_types

        def getThingType(self, thingTypeUID, locale):
            for thing_type in self.thing_types:
                if thing_type.getUID() == thingTypeUID:
                    return thing_type

        def add(self, thing_type):
            self.thing_types.append(thing_type)

        def remove(self, thing_type):
            if thing_type in self.thing_types:
                self.thing_types.remove(thing_type)

    core.JythonThingTypeProvider = JythonThingTypeProvider()
except:
    core.JythonThingTypeProvider = None
    import traceback
    logging.getLogger("{}.core.JythonThingTypeProvider".format(LOG_PREFIX)).error(traceback.format_exc())

def scriptLoaded(script):
    if core.JythonThingProvider is not None:
        register_service(core.JythonThingTypeProvider, [PROVIDER_CLASS])
        logging.getLogger("{}.core.JythonThingTypeProvider.scriptLoaded".format(LOG_PREFIX)).debug("Registered service")

def scriptUnloaded():
    if core.JythonThingProvider is not None:
        unregister_service(core.JythonThingTypeProvider)
        core.JythonThingTypeProvider = None
        logging.getLogger("{}.core.JythonThingTypeProvider.scriptUnloaded".format(LOG_PREFIX)).debug("Unregistered service")
