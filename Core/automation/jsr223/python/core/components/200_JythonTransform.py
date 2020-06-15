"""
This script defines a transformation service (identified by "JYTHON") that will
process a value using a Jython script. This is similar to the Javascript
transformation service.
"""
scriptExtension.importPreset(None)# fix for compatibility with Jython > 2.7.0

import core
from core.osgi import register_service, unregister_service
from core.log import logging, LOG_PREFIX

TRANSFORMATION_CLASS = None

try:
    from org.openhab.core.transform import TransformationService
    TRANSFORMATION_CLASS = "org.openhab.core.transform.TransformationService"
except:
    from org.eclipse.smarthome.core.transform import TransformationService
    TRANSFORMATION_CLASS = "org.eclipse.smarthome.core.transform.TransformationService"

try:
    class JythonTransformationService(TransformationService):

        def transform(self, pathname, value):
            with open(pathname, "r") as file_path:
                code = file_path.read()
                return eval(code, globals(), {'value': value})

    core.JythonTransformationService = JythonTransformationService()
except:
    core.JythonTransformationService = None
    import traceback
    logging.getLogger("{}.core.JythonTransformationService".format(LOG_PREFIX)).error(traceback.format_exc())

def scriptLoaded(script):
    if core.JythonTransformationService is not None:
        register_service(core.JythonTransformationService, [TRANSFORMATION_CLASS], {'smarthome.transform': 'JYTHON'})
        logging.getLogger("{}.core.JythonTransformationService.scriptLoaded".format(LOG_PREFIX)).debug("Registered service")

def scriptUnloaded():
    if core.JythonTransformationService is not None:
        unregister_service(core.JythonTransformationService)
        core.JythonTransformationService = None
        logging.getLogger("{}.core.JythonTransformationService.scriptUnloaded".format(LOG_PREFIX)).debug("Unregistered service")
