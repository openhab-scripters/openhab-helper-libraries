"""
This script defines a transformation service (identified by "JYTHON") that will
process a value using a Jython script. This is similar to the Javascript
transformation service.
"""

scriptExtension.importPreset(None)

transformation_class = None
try:
    from org.openhab.core.transform import TransformationService
    transformation_class = "org.openhab.core.transform.TransformationService"
except:
    from org.eclipse.smarthome.core.transform import TransformationService
    transformation_class = "org.eclipse.smarthome.core.transform.TransformationService"

import core
from core import osgi
from core.log import logging, LOG_PREFIX

try:
    class JythonTransformationService(TransformationService):
        def transform(self, pathname, value):
            with open(pathname, "r") as fp:
                code = fp.read()
                return eval(code, globals(), {'value': value})

    core.JythonTransformationService = JythonTransformationService()
except:
    core.JythonTransformationService = None
    import traceback
    logging.getLogger("{}.core.JythonTransformationService".format(LOG_PREFIX)).error(traceback.format_exc())

def scriptLoaded(id):
    if core.JythonTransformationService is not None:
        core.osgi.register_service(core.JythonTransformationService, [transformation_class], {'smarthome.transform': 'JYTHON'})
        logging.getLogger("{}.core.JythonTransformationService.scriptLoaded".format(LOG_PREFIX)).debug("Registered service")

def scriptUnloaded():
    if core.JythonTransformationService is not None:
        core.osgi.unregister_service(core.JythonTransformationService)
        core.JythonTransformationService = None
        logging.getLogger("{}.core.JythonTransformationService.scriptUnloaded".format(LOG_PREFIX)).debug("Unregistered service")
