from org.eclipse.smarthome.core.thing import ThingProvider

import openhab
import openhab.osgi

class JythonThingProvider(ThingProvider):
    def __init__(self):
        self.things = []
        self.listeners = []
        
    def addProviderChangeListener(self, listener): # ProviderChangeListener
        self.listeners.append(listener)
    
    def getAll(self):
        return self.things

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

openhab.JythonThingProvider = JythonThingProvider()

def scriptLoaded(id):
    openhab.osgi.register_service(
        openhab.JythonThingProvider, 
        ["org.eclipse.smarthome.core.thing.ThingProvider"])
    
def scriptUnloaded():
    openhab.osgi.unregister_service(openhab.JythonThingProvider)
    delattr(openhab, 'JythonThingProvider')
