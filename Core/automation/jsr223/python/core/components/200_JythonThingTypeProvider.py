"""
This script adds a ThingTypeProvider.
"""

scriptExtension.importPreset(None)

provider_class = None
try:
    from org.openhab.core.thing.binding import ThingTypeProvider
    provider_class = "org.openhab.core.thing.binding.ThingTypeProvider"
except:
    from org.eclipse.smarthome.core.thing.binding import ThingTypeProvider
    provider_class = "org.eclipse.smarthome.core.thing.binding.ThingTypeProvider"

import core
from core import osgi
from core.log import logging, LOG_PREFIX

try:
    class JythonThingTypeProvider(ThingTypeProvider):
        def __init__(self):
            self.thing_types = []

        def getThingTypes(self, locale):
            return self.thing_types

        def getThingType(self, thingTypeUID, locale):
            for type in self.thing_types:
                if type.getUID() == thingTypeUID:
                    return type

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

def scriptLoaded(id):
    if core.JythonThingProvider is not None:
        core.osgi.register_service(core.JythonThingTypeProvider, [provider_class])
        logging.getLogger("{}.core.JythonThingTypeProvider.scriptLoaded".format(LOG_PREFIX)).debug("Registered service")

def scriptUnloaded():
    if core.JythonThingProvider is not None:
        core.osgi.unregister_service(core.JythonThingTypeProvider)
        core.JythonThingTypeProvider = None
        logging.getLogger("{}.core.JythonThingTypeProvider.scriptUnloaded".format(LOG_PREFIX)).debug("Unregistered service")
