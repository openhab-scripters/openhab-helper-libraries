from org.eclipse.smarthome.core.binding import BindingInfoProvider

import openhab
from distutils.log import info

class JythonBindingInfoProvider(BindingInfoProvider):
    def __init__(self):
        self.binding_infos = {}
        
    def getBindingInfo(self, id, locale):
        return self.binding_infos.get(id, None)
    
    def getBindingInfos(self, locale):
        return set(self.binding_infos.values())

    def add(self, info):
        self.binding_infos[info.id] = info
        
    def remove(self, info):
        if info.id in self.binding_infos:
            del self.binding_infos[info.id]
            
openhab.JythonBindingInfoProvider = JythonBindingInfoProvider()

def scriptLoaded(id):
    openhab.osgi.register_service(
        openhab.JythonBindingInfoProvider, 
        ["org.eclipse.smarthome.core.binding.BindingInfoProvider"])
    
def scriptUnloaded():
    openhab.osgi.unregister_service(openhab.JythonBindingInfoProvider)
    delattr(openhab, 'JythonBindingInfoProvider')
