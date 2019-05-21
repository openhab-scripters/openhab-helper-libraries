scriptExtension.importPreset(None)

provider_class = None
try:
    from org.openhab.core.thing.binding import ThingTypeProvider
    provider_class = "org.openhab.core.thing.binding.ThingTypeProvider"
except:
    from org.eclipse.smarthome.core.thing.binding import ThingTypeProvider
    provider_class = "org.eclipse.smarthome.core.thing.binding.ThingTypeProvider"

import core

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
    logging.getLogger(LOG_PREFIX + ".core.JythonThingTypeProvider").error(traceback.format_exc())

def scriptLoaded(id):
    if core.JythonThingProvider is not None:
        core.osgi.register_service(core.JythonThingTypeProvider, [provider_class])
        logging.getLogger(LOG_PREFIX + ".core.JythonThingTypeProvider.scriptLoaded").debug("Registered service")

def scriptUnloaded():
    if core.JythonThingProvider is not None:
        core.osgi.unregister_service(core.JythonThingTypeProvider)
        core.JythonThingTypeProvider = None
        logging.getLogger(LOG_PREFIX + ".core.JythonThingTypeProvider.scriptUnloaded").debug("Unregistered service")
