from openhab.jsr223.scope import ScriptExtension
from org.osgi.framework import FrameworkUtil

_bundle = FrameworkUtil.getBundle(type(ScriptExtension))
bundle_context = _bundle.getBundleContext() if _bundle else None

registered_services = {}

def get_service(class_or_name):
    if bundle_context:
        classname = class_or_name.getName() if isinstance(class_or_name, type) else class_or_name
        ref = bundle_context.getServiceReference(classname)
        return bundle_context.getService(ref) if ref else None
    
def register_service(service, interface_names, properties=None):
    ref = bundle_context.registerService(interface_names, service, properties)
    for name in interface_names:
        registered_services[name] = (service, ref)
    return ref
        
def unregister_service(service):
    keys = registered_services.keys()
    for key in keys:
        registered_service, ref = registered_services[key]
        if service == registered_service:
            del registered_services[key]
