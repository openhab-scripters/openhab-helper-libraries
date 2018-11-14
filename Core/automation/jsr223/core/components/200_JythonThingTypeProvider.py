from org.eclipse.smarthome.core.thing.binding import ThingTypeProvider

import core

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

def scriptLoaded(id):
    core.osgi.register_service(
        core.JythonThingTypeProvider, 
        ["org.eclipse.smarthome.core.thing.binding.ThingTypeProvider"])
    
def scriptUnloaded():
    core.osgi.unregister_service(core.JythonThingTypeProvider)
    delattr(core, 'JythonThingTypeProvider')
