from openhab.jsr223.scope import scriptExtension
from org.osgi.framework import FrameworkUtil

_bundle = FrameworkUtil.getBundle(type(scriptExtension))
bundle_context = _bundle.getBundleContext() if _bundle else None

registered_services = {}

def get_service(class_or_name):
    if bundle_context:
        classname = class_or_name.getName() if isinstance(class_or_name, type) else class_or_name
        ref = bundle_context.getServiceReference(classname)
        return bundle_context.getService(ref) if ref else None
    
def find_services(class_name, filter):
    if bundle_context:
        refs = bundle_context.getAllServiceReferences(class_name, filter)
        if refs:
            return [bundle_context.getService(ref) for ref in refs]
    
def register_service(service, interface_names, properties=None):
    if properties:
        import java.util
        p = java.util.Hashtable()
        for k, v in properties.iteritems():
            p.put(k, v)
        properties = p
    reg = bundle_context.registerService(interface_names, service, properties)
    for name in interface_names:
        registered_services[name] = (service, reg)
    return reg
        
def unregister_service(service):
    keys = registered_services.keys()
    for key in keys:
        registered_service, reg = registered_services[key]
        if service == registered_service:
            del registered_services[key]
            reg.unregister()
