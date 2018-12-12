from org.eclipse.smarthome.core.transform import TransformationService

from core.osgi import register_service, unregister_service

class JythonTransformationService(TransformationService):
        def transform(self, pathname, value):
            with open(pathname, "r") as fp:
                code = fp.read()
                return eval(code, globals(), {'value': value})
            
def scriptLoaded(id):
    global service
    service = JythonTransformationService()
    interfaces = ["org.eclipse.smarthome.core.transform.TransformationService"]
    registration = register_service(service, interfaces, {'smarthome.transform': 'JYTHON'})

def scriptUnloaded():
    global service
    unregister_service(service)