"""
This script adds a BindingInfoProvider.
"""
scriptExtension.importPreset(None)# fix for compatibility with Jython > 2.7.0

import core
from core.osgi import register_service, unregister_service
from core.log import logging, LOG_PREFIX

PROVIDER_CLASS = None
try:
    from org.openhab.core.binding import BindingInfoProvider
    PROVIDER_CLASS = "org.openhab.core.binding.BindingInfoProvider"
except:
    from org.eclipse.smarthome.core.binding import BindingInfoProvider
    PROVIDER_CLASS = "org.eclipse.smarthome.core.binding.BindingInfoProvider"

try:
    class JythonBindingInfoProvider(BindingInfoProvider):
        def __init__(self):
            self.binding_infos = {}

        def getBindingInfo(self, binding_id, locale):
            return self.binding_infos.get(binding_id, None)

        def getBindingInfos(self, locale):
            return set(self.binding_infos.values())

        def add(self, info):
            self.binding_infos[info.id] = info

        def remove(self, info):
            if info.id in self.binding_infos:
                del self.binding_infos[info.id]

    core.JythonBindingInfoProvider = JythonBindingInfoProvider()
except:
    core.JythonBindingInfoProvider = None
    import traceback
    logging.getLogger("{}.core.JythonBindingInfoProvider".format(LOG_PREFIX)).warn(traceback.format_exc())

def scriptLoaded(script):
    if core.JythonBindingInfoProvider is not None:
        register_service(core.JythonBindingInfoProvider, [PROVIDER_CLASS])
        logging.getLogger("{}.core.JythonBindingInfoProvider.scriptLoaded".format(LOG_PREFIX)).debug("Registered service")

def scriptUnloaded():
    if core.JythonBindingInfoProvider is not None:
        unregister_service(core.JythonBindingInfoProvider)
        core.JythonBindingInfoProvider = None
        logging.getLogger("{}.core.JythonBindingInfoProvider.scriptUnloaded".format(LOG_PREFIX)).debug("Unregistered service")
