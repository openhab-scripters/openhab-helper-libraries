"""
This script adds a BindingInfoProvider.
"""

scriptExtension.importPreset(None)

from distutils.log import info

provider_class = None
try:
    from org.openhab.core.binding import BindingInfoProvider
    provider_class = "org.openhab.core.binding.BindingInfoProvider"
except:
    from org.eclipse.smarthome.core.binding import BindingInfoProvider
    provider_class = "org.eclipse.smarthome.core.binding.BindingInfoProvider"

import core
from core import osgi
from core.log import logging, LOG_PREFIX

try:
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

    core.JythonBindingInfoProvider = JythonBindingInfoProvider()
except:
    core.JythonBindingInfoProvider = None
    import traceback
    logging.getLogger(LOG_PREFIX + ".core.JythonBindingInfoProvider".format(LOG_PREFIX)).warn(traceback.format_exc())

def scriptLoaded(id):
    if core.JythonBindingInfoProvider is not None:
        core.osgi.register_service(core.JythonBindingInfoProvider, [provider_class])
        logging.getLogger("{}.core.JythonBindingInfoProvider.scriptLoaded".format(LOG_PREFIX)).debug("Registered service")

def scriptUnloaded():
    if core.JythonBindingInfoProvider is not None:
        core.osgi.unregister_service(core.JythonBindingInfoProvider)
        core.JythonBindingInfoProvider = None
        logging.getLogger("{}.core.JythonBindingInfoProvider.scriptUnloaded".format(LOG_PREFIX)).debug("Unregistered service")
