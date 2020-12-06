# pylint: disable=exec-used
"""
This script creates and implementation of a `TransformationService <https://github.com/openhab/openhab-core/blob/master/bundles/org.openhab.core.transform/src/main/java/org/openhab/core/transform/TransformationService.java>`_
(identified by "JYTHON") which transforms the input using Jython.
"""
from os import path

#scriptExtension.importPreset(None)# fix for compatibility with Jython > 2.7.0

#import core
import core.osgi
reload(core.osgi)
from core.osgi import register_service, unregister_service
from core.log import logging, LOG_PREFIX

TRANSFORMATION_CLASS = None

try:
    from org.eclipse.smarthome.core.transform import TransformationService
    from org.eclipse.smarthome.core.transform import TransformationException
    from org.eclipse.smarthome.config.core import ConfigConstants
    TRANSFORMATION_CLASS = "org.eclipse.smarthome.core.transform.TransformationService"
except:
    from org.openhab.core.transform import TransformationService
    from org.openhab.core.transform import TransformationException
    from org.openhab.core.config.core import ConfigConstants
    TRANSFORMATION_CLASS = "org.openhab.core.transform.TransformationService"

jython_transformation_service = None
registered_service = None
LOG = logging.getLogger("{}.core.JythonTransform".format(LOG_PREFIX))


class JythonTransformationService(TransformationService):

    def transform(self, function, input):
        try:
            if function is None or input is None:
                raise TransformationException("Neither of the given parameters, 'function' and 'input', can be None")
            path_name = path.join(ConfigConstants.getConfigFolder(), TransformationService.TRANSFORM_FOLDER_NAME, function)
            with open(path_name, "r") as file_path:
                code = file_path.read()
                exec_namespace = {"input": input, "result": None}
                exec(code, exec_namespace)
                return exec_namespace['result']
        except:
            import traceback
            raise TransformationException("An error occurred while executing script: {}".format(traceback.format_exc()))

jython_transformation_service = JythonTransformationService()


def scriptLoaded(script):
    global jython_transformation_service
    if jython_transformation_service is not None:
        global registered_service
        registered_service = register_service(jython_transformation_service, [TRANSFORMATION_CLASS], {'smarthome.transform': 'JYTHON'})
        LOG.debug("Registered service")


def scriptUnloaded():
    global jython_transformation_service
    global registered_service
    unregister_service(jython_transformation_service)
    jython_transformation_service = None
    registered_service = None
    LOG.debug("Unregistered service")
